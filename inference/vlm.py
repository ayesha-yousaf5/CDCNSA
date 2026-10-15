"""Qwen-VL (Alibaba Cloud Model Studio) visual diagnosis.

The CNN classifiers trained on PlantInquiryVQA/web-sourced images overfit to the
source dataset of each class, so on real photos they are unreliable. This module
asks a vision-language model to choose a diagnosis from the SAME closed list of
disease names the website's Disease Library uses (plus "Healthy"), and to grade
severity from the visible affected leaf area. It never invents new disease names:
anything outside the list is returned as Unknown -> "Uncertain" in the UI.

Configuration (environment / .env). Provider is chosen automatically:
    1. DASHSCOPE_API_KEY set -> Alibaba Model Studio, model qwen3-vl-plus
         QWEN_VL_BASE_URL default https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    2. otherwise GROQ_API_KEY (the chatbot key) -> Groq, model qwen/qwen3.8-27b (Qwen with vision)
         QWEN_VL_BASE_URL default https://api.groq.com/openai/v1
    QWEN_VL_MODEL / QWEN_VL_BASE_URL override either default.
    QWEN_VL_TIMEOUT seconds, default 45. CDCNSA_DIAGNOSIS_MODE=cnn switches this off.
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
    # = the class names of each crop's FINAL model (models_final, 2026-10-15); peas = previous model
    'corn': ['Gray Leaf Spot', 'Northern Leaf Blight'],
    'cotton': ['Bacterial Blight', 'Leaf Curl', 'Herbicide Growth Damage', 'Leaf Hopper Jassids',
               'Leaf Reddening', 'Leaf Variegation'],
    'tomato': ['Early Blight', 'Late Blight', 'Tomato Yellow Leaf Curl Virus', 'Bacterial Spot'],
    'apple': ['Apple Scab', 'Alternaria Leaf Blotch', 'Powdery Mildew', 'Apple Mosaic'],
    'rice': ['Bacterial Leaf Blight', 'Brown Spot', 'Leaf Scald', 'Rice Blast', 'Rice Tungro', 'Sheath Blight'],
    'mango': ['Anthracnose', 'Bacterial Canker', 'Cutting Weevil', 'Die Back', 'Gall Midge', 'Powdery Mildew',
              'Sooty Mould'],
    'grape': ['Black Rot', 'Downy Mildew', 'Esca Black Measles', 'Leaf Blight / Isariopsis Leaf Spot',
              'Powdery Mildew'],
    'eggplant': ['General Pest Damage', 'Leaf Spot', 'Mosaic Virus', 'Wilt', 'Small Leaf', 'White Mold',
                 'Phomopsis Blight', 'Powdery Mildew'],
    'cucumber': ['Anthracnose', 'Downy Mildew'],
    'peas': ['Ascochyta Blight', 'Botrytis Blight', 'Fusarium Wilt', 'Pod Borer Damage'],
}
CROP_NAMES = {'corn': 'corn (maize)', 'eggplant': 'eggplant (brinjal)', 'peas': 'pea'}

SYSTEM_PROMPT = (
    'You are an experienced plant pathologist helping farmers in Pakistan. You examine one crop photo '
    'and answer ONLY with a single JSON object, no markdown, no extra text. Be honest: if the photo is '
    'unclear, not a plant, or shows a different crop, say so instead of guessing.'
)


def _provider() -> dict | None:
    if os.getenv('DASHSCOPE_API_KEY'):
        return {'name': 'alibaba', 'key': os.environ['DASHSCOPE_API_KEY'],
                'base': os.getenv('QWEN_VL_BASE_URL', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'),
                'model': os.getenv('QWEN_VL_MODEL', 'qwen3-vl-plus')}
    # Own key for the photo check (GROQ_VISION_API_KEY) so its per-minute limit never blocks the chatbot;
    # falls back to the chatbot key GROQ_API_KEY when no separate key is set.
    key = os.getenv('GROQ_VISION_API_KEY') or os.getenv('GROQ_API_KEY')
    if key:
        return {'name': 'groq', 'key': key,
                'base': os.getenv('QWEN_VL_BASE_URL', 'https://api.groq.com/openai/v1'),
                'model': os.getenv('QWEN_VL_MODEL', 'qwen/qwen3.8-27b')}
    return None


def available() -> bool:
    return _provider() is not None and os.getenv('CDCNSA_DIAGNOSIS_MODE', 'hybrid').lower() != 'cnn'


def model_name() -> str | None:
    p = _provider()
    return f"{p['model']} ({p['name']})" if p else None


def _norm(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', str(text).lower())


def _image_data_url(image: Image.Image, max_side: int = int(os.getenv('QWEN_VL_IMAGE_SIDE', '768'))) -> str:
    # 768 px keeps lesions visible and uses ~40% fewer input tokens than 1024 px (Groq free tier: 7,000/min)
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


class _HTTPErr(Exception):
    def __init__(self, code, text):
        super().__init__(f'{code} {text}'); self.code, self.text = code, text


def _call(image: Image.Image, crop: str, labels: list[str]) -> dict:
    prov = _provider()
    base = prov['base'].rstrip('/')
    body = {
        'model': prov['model'],
        'temperature': 0.1,
        # the JSON answer is ~250 tokens; 1500 exceeded Groq's free 1,000 output-tokens-per-minute limit on its own
        'max_tokens': int(os.getenv('QWEN_VL_MAX_TOKENS', '450')),
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': [
                {'type': 'image_url', 'image_url': {'url': _image_data_url(image)}},
                {'type': 'text', 'text': _build_prompt(crop, labels)},
            ]},
        ],
    }
    if prov['name'] == 'groq':
        body['response_format'] = {'type': 'json_object'}
        body['reasoning_effort'] = 'none'      # no hidden 'thinking' -> much faster answer

    # httpx (the HTTP library the Groq SDK itself uses). Plain urllib was refused by the API's Cloudflare
    # front door with "HTTP 403, error code 1010" (it blocks the default Python-urllib client signature).
    import httpx

    def post(b: dict, retry: bool = True) -> dict:
        r = httpx.post(base + '/chat/completions', json=b, timeout=float(os.getenv('QWEN_VL_TIMEOUT', '45')),
                       headers={'Authorization': f'Bearer {prov["key"]}', 'User-Agent': 'CDCNSA/1.0'})
        if r.status_code == 429 and retry:          # per-minute limit: wait the time the API asks for (<= 20 s), once
            m = re.search(r'try again in ([0-9.]+)s', r.text)
            if m and float(m.group(1)) <= float(os.getenv('QWEN_VL_MAX_WAIT', '3')):
                import time
                time.sleep(float(m.group(1)) + 0.5)
                return post(b, retry=False)
        if r.status_code >= 400:
            raise _HTTPErr(r.status_code, r.text[:300])
        return r.json()

    try:
        payload = post(body)
    except _HTTPErr as exc:
        if exc.code == 400 and ('response_format' in body or 'reasoning_effort' in body):
            body.pop('response_format', None)   # JSON mode / no-thinking rejected -> plain request, we parse it
            body.pop('reasoning_effort', None)
            try:
                payload = post(body)
            except _HTTPErr as exc2:
                raise RuntimeError(f'Vision model HTTP {exc2.code}: {exc2.text!r}') from exc2
        else:
            raise RuntimeError(f'Vision model HTTP {exc.code}: {exc.text!r}') from exc
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
        'model': model_name(),
    }
