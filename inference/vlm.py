"""Qwen-VL (Alibaba Cloud Model Studio) visual diagnosis.

The CNN classifiers trained on PlantInquiryVQA/web-sourced images overfit to the
source dataset of each class, so on real photos they are unreliable. This module
asks a vision-language model to choose a diagnosis from the SAME closed list of
disease names the website's Disease Library uses (plus "Healthy"), and to grade
severity from the visible affected leaf area. It never invents new disease names:
anything outside the list is returned as Unknown -> "Uncertain" in the UI.

Configuration (environment / .env):
    DASHSCOPE_API_KEY   required to enable this path
    QWEN_VL_MODEL       default "qwen3-vl-plus"
    QWEN_VL_BASE_URL    default "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
                        (use https://dashscope.aliyuncs.com/compatible-mode/v1 for a China-region key)
    QWEN_VL_TIMEOUT     seconds, default 45
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from io import BytesIO

from PIL import Image

# Must match the `en` names of diseaseKnowledge in app.js so the result card,
# guidance text and disease library link all resolve.
CROP_LABELS: dict[str, list[str]] = {
    'corn': ['Bacterial Leaf Streak', 'Common Rust', 'Gray Leaf Spot', 'Maize Lethal Necrosis',
             'Maize Streak Virus', 'Northern Leaf Blight'],
    'cotton': ['Alternaria Leaf Spot', 'Bacterial Blight', 'Herbicide Growth Damage', 'Leaf Curl',
               'Leaf Hopper Jassids', 'Leaf Reddening', 'Leaf Variegation', 'Verticillium Wilt'],
    'tomato': ['Bacterial Spot', 'Cercospora Leaf Mold', 'Early Blight', 'General Pest Damage', 'Late Blight',
               'Leaf Miner', 'Leaf Mold', 'Septoria Leaf Spot', 'Shot Hole Disease', 'Spider Mites',
               'Target Spot', 'Tomato Leaf Curl Virus', 'Tomato Mosaic Virus', 'Tomato Yellow Leaf Curl Virus'],
    'apple': ['Alternaria Apple', 'Apple Powdery Mildew', 'Apple Scab', 'Black Rot', 'Cedar Apple Rust'],
    'rice': ['Bacterial Leaf Blight', 'Brown Spot', 'Leaf Scald', 'Narrow Brown Leaf Spot', 'Rice Blast',
             'Rice Hispa', 'Rice Leaffolder', 'Rice Stripes', 'Rice Tungro', 'Sheath Blight'],
    'mango': ['Anthracnose', 'Bacterial Canker', 'Cutting Weevil', 'Die Back', 'Gall Midge', 'Powdery Mildew',
              'Sooty Mould', 'Senescence / Drying'],
    'grape': ['Bacterial Leaf Spot', 'Black Rot', 'Downy Mildew', 'Esca Black Measles',
              'Leaf Blight / Isariopsis Leaf Spot', 'Yellow Leaf Spot'],
    'eggplant': ['General Pest Damage', 'Leaf Spot', 'Mosaic Virus', 'Phomopsis Blight', 'White Mold'],
    'cucumber': ['Bacterial Wilt', 'Belly Rot', 'Downy Mildew', 'Gummy Stem Blight', 'Pythium Fruit Rot'],
    'peas': ['Ascochyta Blight', 'Botrytis Blight', 'Fusarium Wilt', 'Pod Borer Damage'],
}
CROP_NAMES = {'corn': 'corn (maize)', 'eggplant': 'eggplant (brinjal)', 'peas': 'pea'}

SYSTEM_PROMPT = (
    'You are an experienced plant pathologist helping farmers in Pakistan. You examine one crop photo '
    'and answer ONLY with a single JSON object, no markdown, no extra text. Be honest: if the photo is '
    'unclear, not a plant, or shows a different crop, say so instead of guessing.'
)


def available() -> bool:
    return bool(os.getenv('DASHSCOPE_API_KEY')) and os.getenv('CDCNSA_DIAGNOSIS_MODE', 'hybrid').lower() != 'cnn'


def _norm(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', str(text).lower())


def _image_data_url(image: Image.Image, max_side: int = 1024) -> str:
    img = image.copy()
    img.thumbnail((max_side, max_side))
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=88)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')


def _build_prompt(crop: str, labels: list[str]) -> str:
    options = '\n'.join(f'- {x}' for x in labels + ['Healthy'])
    return (
        f'The farmer says this is a {CROP_NAMES.get(crop, crop)} plant.\n'
        f'Choose the diagnosis ONLY from this list (copy the name exactly):\n{options}\n'
        '- Unknown (use when the problem is not in the list or the photo is too unclear)\n\n'
        'Severity rule (based on the visible affected area of the leaf/plant): '
        'MILD = under 10% affected, MODERATE = 10-30%, SEVERE = over 30% or widespread wilting/necrosis. '
        'Use N/A for Healthy or Unknown.\n\n'
        'Return exactly this JSON:\n'
        '{"is_plant_photo": true/false, "matches_selected_crop": true/false, '
        '"diagnosis": "<name from the list>", "confidence": <0.0-1.0>, '
        '"severity": "MILD|MODERATE|SEVERE|N/A", "affected_area_percent": <0-100>, '
        '"visible_symptoms": "<one short sentence in English>", '
        '"visible_symptoms_ur": "<the same sentence in Urdu>"}'
    )


def _parse_json(text: str) -> dict:
    text = re.sub(r'<think>.*?</think>', '', text or '', flags=re.S)
    match = re.search(r'\{.*\}', text, flags=re.S)
    if not match:
        raise ValueError(f'No JSON in model reply: {text[:200]!r}')
    return json.loads(match.group(0))


def _call(image: Image.Image, crop: str, labels: list[str]) -> dict:
    base = os.getenv('QWEN_VL_BASE_URL', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1').rstrip('/')
    body = {
        'model': os.getenv('QWEN_VL_MODEL', 'qwen3-vl-plus'),
        'temperature': 0.1,
        'max_tokens': 400,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': [
                {'type': 'image_url', 'image_url': {'url': _image_data_url(image)}},
                {'type': 'text', 'text': _build_prompt(crop, labels)},
            ]},
        ],
    }
    req = urllib.request.Request(
        base + '/chat/completions',
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {os.environ["DASHSCOPE_API_KEY"]}'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=float(os.getenv('QWEN_VL_TIMEOUT', '45'))) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'Qwen-VL HTTP {exc.code}: {exc.read()[:300]!r}') from exc
    content = payload['choices'][0]['message']['content']
    if isinstance(content, list):  # some SDK versions return content parts
        content = ''.join(part.get('text', '') for part in content if isinstance(part, dict))
    return _parse_json(content)


def diagnose(image: Image.Image, crop: str) -> dict:
    """Return a normalised Qwen-VL opinion. Raises on network/API/parse errors."""
    labels = CROP_LABELS.get(crop)
    if not labels:
        raise ValueError(f'No label list for crop {crop!r}')
    raw = _call(image, crop, labels)
    allowed = {_norm(x): x for x in labels}
    allowed[_norm('Healthy')] = 'Healthy'
    picked = allowed.get(_norm(raw.get('diagnosis', '')))
    try:
        confidence = max(0.0, min(1.0, float(raw.get('confidence', 0))))
    except (TypeError, ValueError):
        confidence = 0.0
    severity = str(raw.get('severity', 'N/A')).upper().strip()
    if severity not in ('MILD', 'MODERATE', 'SEVERE'):
        severity = 'N/A'
    return {
        'is_plant_photo': bool(raw.get('is_plant_photo', True)),
        'matches_selected_crop': bool(raw.get('matches_selected_crop', True)),
        'diagnosis': picked,  # None => Unknown / outside list
        'raw_diagnosis': raw.get('diagnosis'),
        'confidence': confidence,
        'severity': severity,
        'affected_area_percent': raw.get('affected_area_percent'),
        'visible_symptoms': raw.get('visible_symptoms'),
        'visible_symptoms_ur': raw.get('visible_symptoms_ur'),
        'model': os.getenv('QWEN_VL_MODEL', 'qwen3-vl-plus'),
    }
