"""CDCNSA - Streamlit version (backup deployment for Streamlit Community Cloud).

Same brains as the FastAPI site (server.py + index.html): it calls the very same
inference/runtime.py (crop disease models + Qwen-VL + lesion-segmentation severity) and
chatbot/chat_service.py (Groq chatbot), only the screens are built with Streamlit.

Run locally:   streamlit run streamlit_app.py
Secrets (Streamlit Cloud -> App settings -> Secrets, TOML):
    GROQ_API_KEY = "..."            # chatbot (+ photo check if no vision key)
    GROQ_VISION_API_KEY = "..."     # optional, separate key for the Qwen photo check
    CDCNSA_HF_REPO = "user/cdcnsa-models"   # optional, Hugging Face repo with the model files
"""
from __future__ import annotations

import asyncio
import hashlib
import html
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="CDCNSA - Crop Health Assistant", page_icon="🌱", layout="wide")

# ---------------------------------------------------------------- secrets -> environment
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, (str, int, float, bool)):
            os.environ.setdefault(_k, str(_v))
except Exception:  # no secrets file (local run with .env)
    pass
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass
os.environ.setdefault("CDCNSA_DIAGNOSIS_MODE", "hybrid")
os.environ.setdefault("CDCNSA_MAX_CACHED_MODELS", "2")  # disease + severity model in memory (Streamlit has ~2.7 GB)

from inference.errors import ImageDecodeError, ModelUnavailable  # noqa: E402

MODEL_ROOT = Path(os.getenv("CDCNSA_MODEL_ROOT", str(ROOT))).expanduser().resolve()

# ---------------------------------------------------------------- static data
CROPS = [  # same order as the website: strongest models first
    ("cotton", "Cotton", "کپاس"), ("mango", "Mango", "آم"), ("apple", "Apple", "سیب"),
    ("grape", "Grape", "انگور"), ("rice", "Rice", "چاول"), ("eggplant", "Eggplant / Brinjal", "بینگن"),
    ("cucumber", "Cucumber", "کھیرا"), ("corn", "Corn / Maize", "مکئی"), ("tomato", "Tomato", "ٹماٹر"),
    ("peas", "Peas", "مٹر"),
]
CROP_NAME = {c: (en, ur) for c, en, ur in CROPS}
LIBRARY: dict = json.loads((ROOT / "chatbot" / "app_disease_library.json").read_text(encoding="utf-8"))

T = {
    "en": {
        "title": "CDCNSA - Crop Health Assistant", "tag": "Crop disease check, severity and farming advice for Pakistan",
        "nav": "Menu", "diagnose": "📷 Check a crop", "library": "📚 Disease library", "chat": "💬 Ask the assistant",
        "history": "🕘 Recent checks", "lang": "Language", "crop": "Choose the crop",
        "detects": "Diseases this crop's model can detect", "upload": "Upload photo", "camera": "Use camera",
        "upload_lbl": "Photo of one affected leaf (JPG, PNG, WEBP, HEIC)", "camera_lbl": "Take a photo of one affected leaf",
        "analyze": "Analyze photo", "analyzing": "Analyzing the photo...", "need_photo": "Please add a photo first.",
        "result": "Result", "disease": "Disease", "confidence": "Confidence", "severity": "Severity",
        "leaf_area": "Leaf area affected", "healthy": "Healthy", "uncertain": "Uncertain", "detected": "Disease detected",
        "none_healthy": "None (healthy)", "na": "Not available", "guidance": "What to do",
        "details": "Full disease details", "uncert_note": "The models are not confident about this photo. Take a clear, close photo "
        "of one affected leaf in daylight, or ask a local agriculture expert.",
        "ask_about": "Ask the assistant about this result", "chat_ph": "Ask about crop diseases, in English, Urdu or Roman Urdu...",
        "voice": "🎤 Speak your question", "speak": "🔊 Listen", "copy": "📋 Copy", "auto_speak": "Read answers aloud",
        "new_chat": "New conversation", "context": "Using your latest check", "no_hist": "No checks yet.",
        "preparing": "Preparing the models (the first start downloads them, about 1-2 minutes)...",
        "models_missing": "Some model files could not be downloaded: {m}. Photos of these crops use the online check only.",
        "no_key": "GROQ_API_KEY is not set, so the chatbot and the online photo check are off. Add it in the app's Secrets.",
        "heard": "You said", "stt_fail": "Could not understand the recording. Please try again or type your question.",
        "cause": "Cause", "symptoms": "Symptoms", "risk": "When it spreads", "management": "Management",
        "prevention": "Prevention", "chemical": "Chemical control", "type": "Type", "time": "Time",
        "lib_intro": "Only the diseases our models are trained to detect are listed.",
        "source_note": "Diagnosis source",
    },
    "ur": {
        "title": "CDCNSA - فصل صحت معاون", "tag": "فصل کی بیماری کی جانچ، شدت اور پاکستان کے لیے زرعی مشورہ",
        "nav": "مینو", "diagnose": "📷 فصل چیک کریں", "library": "📚 بیماریوں کی لائبریری", "chat": "💬 معاون سے پوچھیں",
        "history": "🕘 حالیہ جانچ", "lang": "زبان", "crop": "فصل منتخب کریں",
        "detects": "اس فصل کا ماڈل یہ بیماریاں پہچان سکتا ہے", "upload": "تصویر اپلوڈ کریں", "camera": "کیمرہ",
        "upload_lbl": "ایک متاثرہ پتے کی تصویر (JPG, PNG, WEBP, HEIC)", "camera_lbl": "ایک متاثرہ پتے کی تصویر لیں",
        "analyze": "تصویر کی جانچ کریں", "analyzing": "تصویر کی جانچ ہو رہی ہے...", "need_photo": "پہلے تصویر شامل کریں۔",
        "result": "نتیجہ", "disease": "بیماری", "confidence": "اعتماد", "severity": "شدت",
        "leaf_area": "متاثرہ پتے کا رقبہ", "healthy": "صحت مند", "uncertain": "غیر یقینی", "detected": "بیماری کی نشاندہی",
        "none_healthy": "کوئی نہیں (صحت مند)", "na": "دستیاب نہیں", "guidance": "کیا کریں",
        "details": "بیماری کی مکمل تفصیل", "uncert_note": "ماڈل اس تصویر کے بارے میں پُر اعتماد نہیں۔ دن کی روشنی میں ایک متاثرہ پتے کی "
        "واضح، قریب سے تصویر لیں یا مقامی زرعی ماہر سے رجوع کریں۔",
        "ask_about": "اس نتیجے کے بارے میں معاون سے پوچھیں", "chat_ph": "فصل کی بیماریوں کے بارے میں اردو، انگریزی یا رومن اردو میں پوچھیں...",
        "voice": "🎤 بول کر سوال کریں", "speak": "🔊 سنیں", "copy": "📋 کاپی", "auto_speak": "جواب بول کر سنائیں",
        "new_chat": "نئی گفتگو", "context": "آپ کی آخری جانچ استعمال ہو رہی ہے", "no_hist": "ابھی کوئی جانچ نہیں۔",
        "preparing": "ماڈل تیار ہو رہے ہیں (پہلی بار ڈاؤن لوڈ میں 1-2 منٹ لگتے ہیں)...",
        "models_missing": "کچھ ماڈل فائلیں ڈاؤن لوڈ نہیں ہو سکیں: {m}۔ ان فصلوں کی تصاویر صرف آن لائن جانچ سے دیکھی جائیں گی۔",
        "no_key": "GROQ_API_KEY موجود نہیں، اس لیے چیٹ بوٹ اور آن لائن تصویر جانچ بند ہیں۔",
        "heard": "آپ نے کہا", "stt_fail": "ریکارڈنگ سمجھ نہیں آئی۔ دوبارہ کوشش کریں یا سوال لکھ دیں۔",
        "cause": "وجہ", "symptoms": "علامات", "risk": "کب پھیلتی ہے", "management": "انتظام",
        "prevention": "بچاؤ", "chemical": "کیمیائی کنٹرول", "type": "قسم", "time": "وقت",
        "lib_intro": "صرف وہ بیماریاں دکھائی گئی ہیں جنہیں ہمارے ماڈل پہچان سکتے ہیں۔",
        "source_note": "تشخیص کا ذریعہ",
    },
}
SEV_UR = {"MILD": "ہلکی", "MODERATE": "درمیانی", "SEVERE": "شدید"}
REASONS = {
    "image_not_a_plant": ("This photo does not look like a plant. Please take a clear photo of the affected leaf.",
                          "یہ تصویر پودے کی نہیں لگتی۔ براہ کرم متاثرہ پتے کی واضح تصویر لیں۔"),
    "image_does_not_match_selected_crop": ("This photo does not seem to match the selected crop. Please check the crop selection.",
                                           "یہ تصویر منتخب فصل سے میل نہیں کھاتی۔ براہ کرم فصل کا انتخاب چیک کریں۔"),
    "disease_not_recognised": ("The problem is not one of the diseases this app covers for this crop. Please consult a local agriculture expert.",
                               "یہ مسئلہ اس فصل کی شامل بیماریوں میں نہیں۔ براہ کرم مقامی زرعی ماہر سے رجوع کریں۔"),
    "diagnosis_unavailable_try_again": ("The disease could not be identified right now (the online check is busy). Severity was still measured. Please try again in a minute.",
                                        "اس وقت بیماری کی شناخت نہیں ہو سکی (آن لائن جانچ مصروف ہے)۔ شدت پھر بھی ناپی گئی ہے۔ ایک منٹ بعد دوبارہ کوشش کریں۔"),
    "image_too_small": ("The photo is too small. Please take a closer, sharper photo.", "تصویر بہت چھوٹی ہے۔ قریب سے واضح تصویر لیں۔"),
    "image_too_uniform": ("The photo looks blank or blurred. Please take a clear photo of the leaf.", "تصویر خالی یا دھندلی ہے۔ پتے کی واضح تصویر لیں۔"),
}

# ---------------------------------------------------------------- state
ss = st.session_state
ss.setdefault("lang", "en")
ss.setdefault("crop", CROPS[0][0])
ss.setdefault("latest", None)
ss.setdefault("history", [])
ss.setdefault("messages", [])
ss.setdefault("session_id", uuid.uuid4().hex)
ss.setdefault("last_audio", None)
ss.setdefault("auto_speak", False)
ss.setdefault("tts", {})
ss.setdefault("pending_audio", None)


def tr(key: str) -> str:
    return T[ss.lang][key]


def has_urdu(text: str) -> bool:
    return bool(re.search(r"[؀-ۿ]", text or ""))


def md(text: str, rtl: bool | None = None) -> None:
    """Markdown with right-to-left direction for Urdu."""
    rtl = has_urdu(text) if rtl is None else rtl
    if rtl:
        st.markdown(f'<div dir="rtl" class="urdu">\n\n{text}\n\n</div>', unsafe_allow_html=True)
    else:
        st.markdown(text)


def norm_key(v: str) -> str:
    v = str(v or "").lower()
    v = re.sub(r"^[^/]+/\s*", "", v)
    v = re.sub(r"[_\-]+", " ", v)
    v = re.sub(r"[^a-z0-9\s]", " ", v)
    return re.sub(r"\s+", " ", v).strip()


def find_disease(crop: str, name: str | None) -> dict | None:
    key = norm_key(name)
    if not key:
        return None
    for e in LIBRARY.get(crop, []):
        if any(norm_key(x) == key for x in [e["name"], *(e.get("aliases") or [])]):
            return e
    return None


def disease_label(crop: str, name: str | None) -> str:
    e = find_disease(crop, name)
    if e:
        return (e.get("name_ur") or e["name"]) if ss.lang == "ur" else e["name"]
    return str(name or "")


def crop_label(c: str) -> str:
    en, ur = CROP_NAME[c]
    return f"{ur} ({en})" if ss.lang == "ur" else en


# ---------------------------------------------------------------- heavy resources (once per server)
@st.cache_resource(show_spinner=False)
def get_runtime():
    missing = []
    if os.getenv("CDCNSA_SKIP_DOWNLOAD", "0").lower() not in ("1", "true", "yes"):
        from download_models import ensure_models
        _, missing = ensure_models(MODEL_ROOT)
    from inference.runtime import ModelRuntime
    return ModelRuntime(MODEL_ROOT), missing


@st.cache_resource(show_spinner=False)
def get_chat():
    from chatbot import chat_service
    try:
        chat_service.warm_up()
    except Exception as exc:
        print("chat warm-up failed:", exc)
    return chat_service


def run_async_gen(agen):
    """Turn the chatbot's async stream into a normal generator for st.write_stream."""
    loop = asyncio.new_event_loop()
    try:
        while True:
            try:
                chunk = loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                break
            if chunk:
                yield chunk if isinstance(chunk, str) else str(chunk)
    finally:
        loop.close()


def speech_bytes(text: str) -> bytes | None:
    key = hashlib.sha1(text.encode("utf-8")).hexdigest()
    if key in ss.tts:
        return ss.tts[key]
    from chatbot import voice_service
    try:
        audio = asyncio.run(voice_service.text_to_speech_async(text, "urdu" if has_urdu(text) else "english"))
    except Exception as exc:
        print("tts failed:", exc)
        audio = None
    if audio:
        ss.tts[key] = audio
    return audio


def transcribe(audio: bytes) -> str:
    """Voice question -> text with Groq Whisper (free tier)."""
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=30.0)
    res = client.audio.transcriptions.create(
        file=("question.wav", audio),
        model=os.getenv("STT_MODEL", "whisper-large-v3-turbo"),
        language="ur" if ss.lang == "ur" else "en",
    )
    return (getattr(res, "text", "") or "").strip()


# ---------------------------------------------------------------- diagnosis helpers
def normalize(r: dict) -> dict:
    conf = float(r.get("confidence") or r.get("disease_confidence") or 0.0)
    uncertain = bool(r.get("uncertain")) or conf < 0.55
    raw = str(r.get("disease") or r.get("prediction") or "Uncertain").strip()
    disease = "Uncertain" if uncertain else raw
    healthy = (not uncertain) and (bool(r.get("healthy")) or disease.lower() == "healthy")
    seg = r.get("severity_method") == "lesion_segmentation"
    pct = None if healthy or r.get("severity_percent") is None else float(r["severity_percent"])
    severity = "N/A" if healthy else ("N/A" if (uncertain and not seg) else (r.get("severity") or "N/A"))
    return {
        "crop": r.get("crop") or ss.crop, "disease": disease, "confidence": conf, "uncertain": uncertain,
        "healthy": healthy, "severity": severity, "severity_percent": pct, "severity_method": r.get("severity_method"),
        "severity_reliability": r.get("severity_reliability"), "severity_note": r.get("severity_note"),
        "severity_confidence": None if (healthy or uncertain) else r.get("severity_confidence"),
        "source": r.get("diagnosis_source") or "cnn", "vlm_disease": r.get("vlm_disease"), "cnn_disease": r.get("cnn_disease"),
        "models_agree": r.get("models_agree"), "symptoms": r.get("visible_symptoms"),
        "symptoms_ur": r.get("visible_symptoms_ur"), "reason": r.get("reason"),
    }


def severity_text(d: dict) -> str:
    if d["healthy"]:
        return tr("none_healthy")
    s = str(d["severity"] or "N/A").upper()
    if s == "N/A":
        return tr("na")
    return SEV_UR.get(s, s) if ss.lang == "ur" else s


def source_lines(d: dict) -> list[str]:
    ur = ss.lang == "ur"
    out = []
    if d["reason"] in REASONS:
        out.append(REASONS[d["reason"]][1 if ur else 0])
    sym = (d["symptoms_ur"] or d["symptoms"]) if ur else d["symptoms"]
    if sym:
        out.append(("تصویر میں نظر آنے والی علامات: " if ur else "What we see: ") + sym)
    crop = d["crop"]
    if d["source"] == "trained_model":
        v = d["vlm_disease"]
        extra = ""
        if v:
            agree = disease_label(crop, v) == disease_label(crop, d["disease"])
            extra = (" · Qwen-VL بھی متفق ہے" if ur else " · Qwen-VL agrees") if agree else \
                (f" · Qwen-VL کا اندازہ: {disease_label(crop, v)}" if ur else f" · Qwen-VL suggested: {disease_label(crop, v)}")
        out.append(("تشخیص: ہمارا تربیت یافتہ ماڈل" if ur else "Diagnosed by our trained model") + extra)
    elif d["source"] == "cnn":
        out.append("تشخیص: ہمارا تربیت یافتہ ماڈل (آن لائن جانچ اس وقت دستیاب نہیں)" if ur
                   else "Diagnosed by our trained model (online second check not available right now)")
    elif d["source"] == "qwen_vl":
        extra = ""
        if d["models_agree"] is True:
            extra = " · CNN ماڈل بھی متفق ہے" if ur else " · CNN model agrees"
        elif d["cnn_disease"]:
            extra = (f" · CNN ماڈل کا اندازہ: {disease_label(crop, d['cnn_disease'])}" if ur
                     else f" · CNN model suggested: {disease_label(crop, d['cnn_disease'])}")
        out.append(("تشخیص: Qwen-VL بصری ماڈل" if ur else "Diagnosed by Qwen-VL vision model") + extra)
    if not d["healthy"] and d["severity_method"] == "lesion_segmentation" and d["severity_percent"] is not None:
        p = d["severity_percent"]
        if ur:
            line = f"شدت: ہمارے لیژن سیگمنٹیشن ماڈل نے پتے کا {p:.1f}% حصہ متاثر ناپا (ہلکی <10%، درمیانی 10–30%، شدید >30%)"
            if d["severity_note"] == "disease_not_confirmed":
                line += "۔ بیماری کا نام یقینی نہیں، لیکن متاثرہ حصہ ناپا گیا ہے۔"
            elif d["severity_note"] == "not_spot_disease":
                line += "۔ یہ دھبوں والی بیماری نہیں (وائرس / مرجھاؤ / کیڑے)، اس لیے اندازاً ہے۔"
            elif d["severity_reliability"] == "approximate":
                line += "۔ اس فصل کے لیے یہ اندازاً ہے اور زیادہ بتا سکتا ہے۔"
        else:
            line = (f"Severity: our lesion-segmentation model measured {p:.1f}% of the leaf area as diseased "
                    "(Mild <10%, Moderate 10–30%, Severe >30%)")
            if d["severity_note"] == "disease_not_confirmed":
                line += ". The disease name is not confirmed, but the damaged area is measured."
            elif d["severity_note"] == "not_spot_disease":
                line += ". Approximate: this is not a spot disease (virus / wilt / pest damage)."
            elif d["severity_reliability"] == "approximate":
                line += ". Approximate for this crop - it may over-estimate."
        out.append(line)
    elif not d["healthy"] and d["severity_note"] == "leaf_not_clearly_visible":
        out.append("شدت: پتا واضح نظر نہیں آ رہا، ایک پتے کی قریب سے تصویر لیں۔" if ur
                   else "Severity: the leaf is not clearly visible - take a close photo of a single leaf.")
    return out


def disease_details(e: dict) -> None:
    ur = ss.lang == "ur"
    if ur:
        md(f"**{tr('symptoms')}:** {e.get('symptoms_ur') or e.get('symptoms', '')}")
    rows = [("type", e.get("type")), ("cause", e.get("cause")), ("symptoms", None if ur else e.get("symptoms")),
            ("risk", e.get("risk")), ("management", e.get("management")), ("prevention", e.get("prevention")),
            ("chemical", e.get("chemical"))]
    for key, val in rows:
        if val:
            st.markdown(f"**{T['en'][key]}:** {val}")
    if e.get("note"):
        st.caption(e["note"])


# ---------------------------------------------------------------- style
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;600&display=swap');
.urdu, .urdu p, .urdu li { font-family: 'Noto Nastaliq Urdu', serif; line-height: 2.1; text-align: right; }
.hero { padding: 1.1rem 1.3rem; border-radius: 14px; background: linear-gradient(120deg,#1f4d2c,#3c7a3f);
        color: #f3f7ef; margin-bottom: 1rem; }
.hero h1 { color: #fff; font-size: 1.7rem; margin: 0 0 .2rem 0; padding: 0; }
.hero p { margin: 0; opacity: .9; }
.status { display:inline-block; padding: .25rem .7rem; border-radius: 999px; font-weight: 600; font-size: .9rem; }
.status.ok { background:#e2f2e3; color:#1f6b2a; } .status.bad { background:#fbe6df; color:#9a3412; }
.status.unc { background:#fdf3d7; color:#8a6400; }
[data-testid="stMetricValue"] { font-size: 1.45rem; white-space: normal; }
[data-testid="stMetricValue"] > div { white-space: normal; overflow: visible; text-overflow: clip; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    lang = st.radio(T["en"]["lang"] + " / زبان", ["English", "اردو"], index=0 if ss.lang == "en" else 1, horizontal=True)
    ss.lang = "en" if lang == "English" else "ur"
    pages = ["diagnose", "library", "chat", "history"]
    page = st.radio(tr("nav"), pages, format_func=tr, key="page")
    st.divider()
    st.caption("CDCNSA · 10 crops · English / اردو")

st.markdown(f'<div class="hero"><h1>🌱 {html.escape(tr("title"))}</h1><p>{html.escape(tr("tag"))}</p></div>',
            unsafe_allow_html=True)

if not os.getenv("GROQ_API_KEY"):
    st.warning(tr("no_key"))

with st.spinner(tr("preparing")):
    runtime, missing_models = get_runtime()
if missing_models:
    st.info(tr("models_missing").format(m=", ".join(missing_models)))


# ---------------------------------------------------------------- pages
def page_diagnose() -> None:
    ids = [c for c, _, _ in CROPS]
    ss.crop = st.selectbox(tr("crop"), ids, index=ids.index(ss.crop), format_func=crop_label, key=f"diag_crop_{ss.lang}")
    with st.expander(tr("detects")):
        names = [(e.get("name_ur") or e["name"]) if ss.lang == "ur" else e["name"] for e in LIBRARY.get(ss.crop, [])]
        md("\n".join(f"- {n}" for n in names), rtl=ss.lang == "ur")

    tab_up, tab_cam = st.tabs([tr("upload"), tr("camera")])
    with tab_up:
        up = st.file_uploader(tr("upload_lbl"), type=["jpg", "jpeg", "png", "webp", "heic", "heif"])
    with tab_cam:
        cam = st.camera_input(tr("camera_lbl"))
    photo = cam or up

    if st.button(tr("analyze"), type="primary", width="stretch"):
        if not photo:
            st.warning(tr("need_photo"))
        else:
            payload = photo.getvalue()
            with st.spinner(tr("analyzing")):
                try:
                    raw = runtime.diagnose(ss.crop, payload, ss.lang)
                    d = normalize(raw)
                    d["image"] = payload
                    d["time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    ss.latest = d
                    ss.history = [d, *ss.history][:12]
                except ImageDecodeError:
                    st.error("The file could not be read as an image." if ss.lang == "en" else "فائل بطور تصویر نہیں کھل سکی۔")
                except ModelUnavailable as exc:
                    st.error(("The models are not available right now: " if ss.lang == "en" else "ماڈل اس وقت دستیاب نہیں: ") + str(exc)[:200])
                except Exception as exc:
                    st.error(("Something went wrong: " if ss.lang == "en" else "کچھ غلط ہو گیا: ") + str(exc)[:200])

    d = ss.latest
    if d and d["crop"] == ss.crop:
        render_result(d)


def render_result(d: dict) -> None:
    st.subheader(tr("result"))
    left, right = st.columns([1, 2])
    with left:
        st.image(d["image"], width="stretch")
    with right:
        if d["uncertain"]:
            st.markdown(f'<span class="status unc">! {tr("uncertain")}</span>', unsafe_allow_html=True)
        elif d["healthy"]:
            st.markdown(f'<span class="status ok">✓ {tr("healthy")}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="status bad">✦ {tr("detected")}</span>', unsafe_allow_html=True)
        name = tr("uncertain") if d["uncertain"] else (tr("healthy") if d["healthy"] else disease_label(d["crop"], d["disease"]))
        c1, c2, c3 = st.columns(3)
        c1.metric(tr("disease"), name)
        c2.metric(tr("confidence"), f"{round(d['confidence'] * 100)}%")
        c3.metric(tr("severity"), severity_text(d))
        if d["severity_percent"] is not None and d["severity_method"] == "lesion_segmentation":
            approx = (" (اندازاً)" if ss.lang == "ur" else " (approx.)") if d["severity_reliability"] == "approximate" else ""
            st.progress(min(d["severity_percent"], 100) / 100, text=f"{tr('leaf_area')}: {d['severity_percent']:.1f}%{approx}")
        if d["uncertain"]:
            md(tr("uncert_note"))
        lines = source_lines(d)
        if lines:
            md("\n\n".join(lines), rtl=ss.lang == "ur")
    e = None if (d["uncertain"] or d["healthy"]) else find_disease(d["crop"], d["disease"])
    if e:
        st.markdown(f"#### {tr('guidance')}")
        md(e.get("symptoms_ur") if ss.lang == "ur" else e.get("management", ""))
        with st.expander(tr("details")):
            disease_details(e)
    st.caption(tr("ask_about") + " → " + tr("chat"))


def page_library() -> None:
    ids = [c for c, _, _ in CROPS]
    crop = st.selectbox(tr("crop"), ids, index=ids.index(ss.crop), format_func=crop_label, key=f"lib_crop_{ss.lang}")
    ss.crop = crop
    st.caption(tr("lib_intro"))
    for e in LIBRARY.get(crop, []):
        title = f"{e.get('name_ur') or e['name']} · {e['name']}" if ss.lang == "ur" else e["name"]
        with st.expander(title):
            disease_details(e)


def chat_context() -> dict:
    d = ss.latest
    ctx = {"crop": ss.crop, "language": ss.lang}
    if d:
        ctx.update({"crop": d["crop"], "disease": d["disease"], "severity": "N/A" if d["healthy"] else d["severity"],
                    "disease_confidence": d["confidence"], "severity_confidence": d["severity_confidence"],
                    "severity_percent": d["severity_percent"], "uncertainty": d["uncertain"], "healthy": d["healthy"]})
    return ctx


def reply_tools(i: int, text: str) -> None:
    c1, c2, _ = st.columns([1.3, 1.3, 5])
    with c1:
        if st.button(tr("speak"), key=f"speak_{i}"):
            audio = speech_bytes(text)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)
    with c2:
        with st.popover(tr("copy")):
            st.code(text, language=None, wrap_lines=True)


def page_chat() -> None:
    top = st.columns([3, 1, 1])
    if ss.latest:
        d = ss.latest
        top[0].caption(f"{tr('context')}: {crop_label(d['crop'])} · "
                       f"{tr('uncertain') if d['uncertain'] else disease_label(d['crop'], d['disease'])}")
    ss.auto_speak = top[1].toggle(tr("auto_speak"), value=ss.auto_speak)
    if top[2].button(tr("new_chat")):
        ss.messages = []
        try:
            get_chat().reset_context(ss.session_id)
        except Exception:
            pass
        st.rerun()

    if ss.pending_audio:
        st.audio(ss.pending_audio, format="audio/mp3", autoplay=True)
        ss.pending_audio = None

    for i, m in enumerate(ss.messages):
        with st.chat_message(m["role"]):
            md(m["content"])
            if m["role"] == "assistant":
                reply_tools(i, m["content"])

    question = None
    audio = st.audio_input(tr("voice"))
    if audio is not None:
        data = audio.getvalue()
        h = hashlib.sha1(data).hexdigest()
        if h != ss.last_audio:
            ss.last_audio = h
            try:
                question = transcribe(data)
            except Exception as exc:
                print("stt failed:", exc)
                question = None
            if not question:
                st.warning(tr("stt_fail"))
    typed = st.chat_input(tr("chat_ph"))
    question = typed or question
    if not question:
        return

    ss.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        md(question)
    with st.chat_message("assistant"):
        try:
            if not os.getenv("GROQ_API_KEY"):
                raise RuntimeError(tr("no_key"))
            chat = get_chat()
            reply = st.write_stream(run_async_gen(chat.ask_stream(question, chat_context(), ss.session_id)))
            if isinstance(reply, list):
                reply = "".join(str(x) for x in reply)
        except Exception as exc:
            reply = ("معاون اس وقت دستیاب نہیں ہے۔ براہ کرم دوبارہ کوشش کریں۔" if ss.lang == "ur"
                     else f"Assistant unavailable: {str(exc)[:200]}")
            md(reply)
        reply = reply or ""
        ss.messages.append({"role": "assistant", "content": reply})
        if ss.auto_speak and reply:
            ss.pending_audio = speech_bytes(reply)  # played after the rerun below, so it is not cut off
    st.rerun()


def page_history() -> None:
    if not ss.history:
        st.info(tr("no_hist"))
        return
    for d in ss.history:
        c1, c2 = st.columns([1, 5])
        with c1:
            st.image(d["image"], width=90)
        with c2:
            name = tr("uncertain") if d["uncertain"] else (tr("healthy") if d["healthy"] else disease_label(d["crop"], d["disease"]))
            pct = f" · {d['severity_percent']:.1f}%" if d["severity_percent"] is not None else ""
            md(f"**{crop_label(d['crop'])}** — {name}  \n{tr('confidence')}: {round(d['confidence'] * 100)}% · "
               f"{tr('severity')}: {severity_text(d)}{pct}  \n{tr('time')}: {d['time']}", rtl=ss.lang == "ur")
        st.divider()


{"diagnose": page_diagnose, "library": page_library, "chat": page_chat, "history": page_history}[page]()
