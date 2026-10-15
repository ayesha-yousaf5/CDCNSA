"""
Chat service - Groq-powered chatbot with RAG retrieval.

Uses Groq API for fast LLM inference. All RAG logic (TF-IDF, knowledge base,
Urdu handling) is preserved from the original Streamlit version.
"""

import asyncio
import os
import re
from pathlib import Path

from groq import Groq

from chatbot.disease_knowledge import (
    get_disease_info, get_treatment_info, get_crop_diseases,
    CROP_SEASONAL_GUIDE, HOMEMADE_REMEDIES, FERTILIZER_GUIDE, PESTICIDE_GUIDE,
    match_urdu_to_knowledge, PEST_KNOWLEDGE
)
from chatbot.knowledge_base_loader import search_knowledge_base, format_knowledge_context


# =========================================================
# CONFIGURATION
# =========================================================

GROQ_API_KEY = None
GROQ_MODEL = None

# =========================================================
# LAZY INITIALIZATION
# =========================================================
_initialized = False
client = None
data = None
questions = None
question_vectors = None
vectorizer = None

conversation_context = {
    "crop": None,
    "disease": None,
    "severity": None,
    "healthy": False,
}

conversation_history: list[dict] = []
MAX_HISTORY = 6

# One conversation per browser tab (session_id from the website). Before, every visitor shared ONE global
# context + history, so two people chatting at the same time mixed crops, diseases and answers.
import threading
from collections import OrderedDict
_SESSIONS: "OrderedDict[str, dict]" = OrderedDict()
_SESSION_LOCK = threading.RLock()
MAX_SESSIONS = 300


def _new_state() -> dict:
    return {"ctx": {"crop": None, "disease": None, "severity": None, "severity_percent": None, "healthy": False},
            "history": [], "ui_sig": None}


def _bind_session(session_id: str | None) -> dict:
    """Point the module-level conversation_context / conversation_history at this session's own objects."""
    global conversation_context, conversation_history, _CURRENT_STATE
    sid = str(session_id or "default")[:80]
    with _SESSION_LOCK:
        st = _SESSIONS.get(sid)
        if st is None:
            st = _SESSIONS[sid] = _new_state()
            while len(_SESSIONS) > MAX_SESSIONS:
                _SESSIONS.popitem(last=False)
        _SESSIONS.move_to_end(sid)
        conversation_context = st["ctx"]
        conversation_history = st["history"]
        _CURRENT_STATE = st
        return st

def _is_follow_up(text: str) -> bool:
    """True only for whole words/phrases (old substring test fired on 'with', 'fruit', 'spit'...)."""
    t = " " + re.sub(r"[^a-z\s]", " ", str(text).lower()) + " "
    return any(f" {w} " in t for w in FOLLOW_UP_WORDS)


FOLLOW_UP_WORDS = [
    "it", "its", "this", "that", "these", "those",
    "the disease", "the plant", "the crop"
]


_CURRENT_STATE: dict = {}


def _update_context_from_request(context: dict | None) -> None:
    """Apply the website's crop / diagnosis context - but only when it CHANGED (new crop selected or a new
    photo result). Before, the same UI context was re-applied on every message, so after the farmer switched
    crop in chat ("my rice has brown spots") the next "how do I treat it?" jumped back to the selected crop."""
    if not context:
        return
    sig = tuple(str(context.get(k)) for k in ("crop", "disease", "severity", "severity_percent", "healthy", "uncertainty"))
    if _CURRENT_STATE.get("ui_sig") == sig:
        return
    _CURRENT_STATE["ui_sig"] = sig

    if context.get("crop"):
        conversation_context["crop"] = str(context["crop"])

    raw_disease = str(context.get("disease") or "").strip()
    normalized_disease = raw_disease.lower().replace("_", " ")
    abstained = (
        bool(context.get("healthy"))
        or bool(context.get("uncertainty"))
        or normalized_disease in {"healthy", "uncertain"}
    )
    conversation_context["healthy"] = bool(context.get("healthy")) or normalized_disease == "healthy"
    if abstained:
        conversation_context["disease"] = None
        conversation_context["severity"] = None
    elif raw_disease:
        conversation_context["disease"] = raw_disease

    severity = context.get("severity")
    conversation_context["severity_percent"] = None
    if not abstained and severity and str(severity).upper() != "N/A":
        conversation_context["severity"] = str(severity)
        if context.get("severity_percent") is not None:
            try:
                conversation_context["severity_percent"] = round(float(context["severity_percent"]), 1)
            except (TypeError, ValueError):
                pass


def _resolve_pronouns(message: str) -> str:
    """Replace vague pronouns with the disease/crop from conversation context
    so that dataset searches target the right entity."""
    disease = conversation_context.get("disease")
    crop = conversation_context.get("crop")
    if not disease:
        return message

    if not _is_follow_up(message):
        return message

    resolved = message
    replacement = disease
    if crop:
        replacement = f"{crop} {disease}"

    for word in ["it", "its", "this", "that", "these", "those"]:
        resolved = resolved.replace(f" {word} ", f" {replacement} ")
        resolved = resolved.replace(f" {word}.", f" {replacement}.")
        resolved = resolved.replace(f" {word}?", f" {replacement}?")
        if resolved.lower().endswith(f" {word}"):
            resolved = resolved[: -(len(word))] + replacement

    for phrase in ["the disease", "the plant", "the crop"]:
        resolved = resolved.replace(phrase, replacement)

    return resolved


URDU_RANGE = "\u0600-\u06ff"

URDU_CROP_NAMES = {
    "\u0679\u0645\u0627\u0679\u0631": "tomato",
    "\u0622\u0644\u0648": "potato",
    "\u0686\u0627\u0648\u0644": "rice",
    "\u067e\u062f\u06cc": "rice",
    "\u0645\u06a9\u06c1": "maize",
    "\u0628\u06be\u0679\u0627": "maize",
    "\u06a9\u067e\u0627\u0633": "cotton",
    "\u0631\u0648\u0626\u06cc": "cotton",
    "\u06af\u0646\u062f\u0645": "wheat",
    "\u0633\u06cc\u0628": "apple",
    "\u0622\u0645": "mango",
    "\u0627\u0646\u06af\u0648\u0631": "grape",
    "\u0645\u0679\u0631": "peas",
    "\u0633\u0648\u0631\u062c \u0645\u06a9\u06be\u06cc": "sunflower",
    "\u0645\u0631\u0686": "pepper",
    "\u0634\u0645\u0644\u06c1 \u0645\u0631\u0686": "pepper",
}


def _detect_urdu_crop(text: str):
    for urdu_name, crop_id in URDU_CROP_NAMES.items():
        if urdu_name in text:
            return crop_id
    return None


def _is_urdu(text: str) -> bool:
    return bool(re.search(f"[{URDU_RANGE}]", text))

ROMAN_URDU_WORDS = {
    'mujhe', 'tum', 'kya', 'hai', 'hain', 'ka', 'ki', 'ke', 'mein', 'ne', 'ko',
    'se', 'par', 'kaise', 'kab', 'kahan', 'batao', 'bataiye', 'kapat', 'kapas',
    'bimari', 'bimariyon', 'bare', 'mein', 'ho', 'sakti', 'hain', 'kaun', 'kaun',
    'si', 'hain', 'aur', 'tumhare', 'system', 'mein', 'jaan', 'sakti', 'hain',
    'paisa', 'paise', 'dost', 'dosti', 'khet', 'kheti', 'fasal', 'zameen', 'pani',
    'dawa', 'spray', 'ilaj', 'karu', 'karen', 'kaise', 'kya', 'kab', 'kahan',
    'kyun', 'kyon', 'kitna', 'kitni', 'kitne', 'kaun', 'kaunsa', 'kaunsi',
    'yeh', 'ye', 'woh', 'wo', 'aur', 'ya', 'lekin', 'magar', 'isliye', 'kyunki',
    'agar', 'to', 'toh', 'phir', 'ab', 'kal', 'aaj', 'abhi', 'pehle', 'baad',
    'upar', 'neeche', 'andar', 'bahar', 'paas', 'door', 'yahan', 'wahan',
    'sab', 'kuch', 'koi', 'kuch', 'kisi', 'kisi', 'sab', 'har', 'koi',
    'karun', 'karoon', 'karna', 'kare', 'karein', 'patte', 'patta', 'pattay', 'patton', 'paude', 'poda', 'podha',
    'keera', 'keeray', 'keere', 'dhabbe', 'dhabay', 'daag', 'peela', 'peeli', 'peele', 'sookh', 'sukh', 'raha', 'rahi',
    'rahe', 'gaye', 'gaya', 'hua', 'hui', 'ilaaj', 'bimaar', 'beemari', 'bemari', 'kis', 'kaisay', 'kyu', 'nahi',
    'nahin', 'bhi', 'hum', 'mera', 'meri', 'mere', 'apna', 'apni', 'iska', 'iski', 'uska', 'uski', 'chahiye', 'lagi',
    'laga', 'lag', 'kaunsa', 'konsa', 'konsi', 'kesay', 'dalein', 'dalna', 'dawai', 'khaad', 'sufaid', 'makhi',
    'tamatar', 'makai', 'makki', 'chawal', 'dhan', 'angoor', 'baingan', 'kheera', 'matar', 'aloo', 'gandum', 'mirch',
    'ganna', 'seb', 'aam', 'phal', 'phool', 'jar', 'tana',
}

# words that are also normal English (or English loan words farmers use in both languages) - they prove nothing
_ROMAN_AMBIGUOUS = {'spray', 'system', 'to', 'ab', 'har', 'kal', 'par', 'door', 'paas', 'ho', 'so', 'ya', 'ye', 'woh', 'wo'}

def _is_roman_urdu(text: str) -> bool:
    """Detect if text is Roman Urdu (Urdu written in Latin script). Needs >= 2 clear Roman-Urdu words
    (before, 'cotton whitefly spray' was taken as Roman Urdu because of the word 'spray')."""
    if _is_urdu(text):
        return False
    words = re.findall(r'[a-zA-Z]+', text.lower())
    if not words:
        return False
    hits = [w for w in words if w in ROMAN_URDU_WORDS and w not in _ROMAN_AMBIGUOUS]
    return len(hits) >= 2 and len(hits) / len(words) > 0.25 or (len(words) <= 3 and len(hits) >= 1 and len(hits) / len(words) > 0.5)


_ASK_URDU = re.compile(r"\b(in|into|to)\s+urdu\b|\burdu\s+(me|mein|main|mai|mey)\b|\burdu\b.*\b(batao|bataen|bataein|likho|likhen|samjhao|translate|karo|karein)\b|اردو\s*(میں|مے)", re.I)
_ASK_ENGLISH = re.compile(r"\b(in|into|to)\s+english\b|\b(english|angrezi|angrezi)\s+(me|mein|main|mai)\b|انگریزی\s*(میں|مے)", re.I)
_TRANSLATE_WORDS = re.compile(r"\btranslat\w*|\btarjuma|ترجمہ|\bconvert\b|\bsame\s+in\b|\bthis\s+in\b|\bit\s+in\b|\bisko\b|\biska\b|\byahi\b|اس\s*کا|اسے", re.I)


def _requested_language(message: str):
    """'ur' / 'en' when the farmer explicitly asks for a language ("in Urdu", "Urdu mein batao", "اردو میں")."""
    if _ASK_URDU.search(message or ""):
        return "ur"
    if _ASK_ENGLISH.search(message or ""):
        return "en"
    return None


def _is_translate_request(message: str) -> bool:
    """'translate it into Urdu', 'urdu mein batao', 'iska tarjuma', 'اردو میں' - a short request about the LAST answer."""
    words = re.findall(r"\w+", message or "")
    return _requested_language(message) is not None and len(words) <= 9 and (
        bool(_TRANSLATE_WORDS.search(message)) or len(words) <= 4)


def _message_language(message: str) -> str:
    """Reply language: what the farmer asked for ("in Urdu"), else the language the message is written in."""
    asked = _requested_language(message)
    if asked:
        return asked
    return 'ur' if _is_urdu(message) or _is_roman_urdu(message) else 'en'


def _photo_advice(message: str) -> str | None:
    """Answer the common photo-help prompt directly and consistently."""
    text = message.lower()
    photo_terms = ("photo", "photograph", "picture", "image", "tasveer", "تصویر")
    quality_terms = ("better", "clear", "good", "improve", "lighting", "behtar", "saaf", "صاف", "اچھی")
    if not any(term in text for term in photo_terms) or not any(term in text for term in quality_terms):
        return None
    if _message_language(message) == 'ur':
        return (
            "**بہتر تصویر کے لیے**\n\n"
            "اچھی قدرتی روشنی میں متاثرہ پتے کی صاف تصویر لیں۔\n"
            "• پتے کو فوکس میں رکھیں اور تصویر دھندلی نہ ہو۔\n"
            "• سادہ پس منظر رکھیں اور بہت زیادہ زوم نہ کریں۔\n"
            "• ایک قریب سے اور ایک پورے پودے کی تصویر بھیجیں۔"
        )
    return (
        "**For a better photo**\n\n"
        "Use good natural lighting and keep the affected leaf sharply in focus.\n"
        "• Use a clear, simple background.\n"
        "• Avoid blur, glare, and extreme zoom.\n"
        "• If possible, include one close-up and one whole-plant photo."
    )


_INIT_LOCK = threading.Lock()


def warm_up():
    """Load the dataset + search index in the background at server start, so the first farmer question
    is fast (before: the first question took ~100 s and froze the whole server while it loaded)."""
    try:
        _initialize()
        search_knowledge_base("warm up", top_k=1)
        print("Chatbot ready.")
    except Exception as exc:
        print(f"Chatbot warm-up skipped: {exc}")


_REASONING_OK: dict = {}   # model -> True/False after its first call
# Fast free models first. Groq free limits are PER MODEL (each: 30 requests/min, 8K tokens/min, 1K requests/day),
# so when one model is at its limit the next one answers at once instead of the farmer waiting.
CHAT_MODELS = [m.strip() for m in os.getenv(
    "CHAT_MODELS", "openai/gpt-oss-20b,openai/gpt-oss-120b,qwen/qwen3.8-27b").split(",") if m.strip()]
CHAT_MAX_TOKENS = int(os.getenv("CHAT_MAX_TOKENS", "600"))


def _rate_limit_wait(exc):
    """Seconds Groq asks us to wait on a 429 (None if not a short per-minute limit)."""
    m = re.search(r"try again in ([0-9.]+)s", str(exc))
    return float(m.group(1)) if m and float(m.group(1)) <= 20 else None


def _busy_message(urdu=False):
    if urdu:
        return "معاون اس وقت مصروف ہے (مفت API کی فی منٹ حد)۔ براہ کرم ایک منٹ بعد دوبارہ پوچھیں۔"
    return "The assistant is busy right now (free API per-minute limit). Please ask again in a minute."


def _is_rate_limit(exc):
    t = str(exc).lower()
    return "429" in t or "rate limit" in t or "rate_limit" in t


def _llm(**kw):
    """Try the chat models in order; a model at its free per-minute limit -> the next one immediately.
    Only if ALL are busy: wait what the API asks (<= 20 s) and try the first again once."""
    last = None
    first_wait = None
    for i, model in enumerate(CHAT_MODELS):
        try:
            return _llm_once(**{**kw, "model": model})
        except Exception as exc:
            if not _is_rate_limit(exc) and "model_not_found" not in str(exc) and "decommissioned" not in str(exc):
                raise
            last = exc
            if i == 0:
                first_wait = _rate_limit_wait(exc)
    if first_wait is not None:
        import time
        time.sleep(first_wait + 0.5)
        return _llm_once(**{**kw, "model": CHAT_MODELS[0]})
    raise last


def _llm_once(**kw):
    """Groq call with the model's hidden 'thinking' switched off (it made every answer take 20-30 s).
    If this model/API rejects the switch, retry once without it and remember that."""
    model = kw.get("model", "")
    if _REASONING_OK.get(model) is not False:
        try:
            # qwen: thinking off; gpt-oss models only accept low/medium/high
            effort = "low" if "gpt-oss" in model else "none"
            r = client.chat.completions.create(**kw, extra_body={"reasoning_effort": effort})
            _REASONING_OK[model] = True
            return r
        except Exception as exc:
            msg = str(exc).lower()
            if model not in _REASONING_OK and not _is_rate_limit(exc) and ("reasoning" in msg or "400" in msg or "invalid" in msg):
                _REASONING_OK[model] = False
                print(f"[chatbot] {model}: reasoning_effort not supported, continuing without it: {str(exc)[:160]}")
            else:
                raise
    return client.chat.completions.create(**kw)


def _initialize():
    with _INIT_LOCK:
        _initialize_locked()


def _initialize_locked():
    global _initialized, client, data, questions, question_vectors, vectorizer
    global GROQ_API_KEY, GROQ_MODEL

    if _initialized:
        return

    from datasets import load_from_disk
    from sklearn.feature_extraction.text import TfidfVectorizer as _TfidfVectorizer

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # Retrieval supplies the factual content; this deployed Groq model is verified.
    GROQ_MODEL = CHAT_MODELS[0]

    api_key = GROQ_API_KEY
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Set it in .env file or environment."
        )

    client = Groq(api_key=api_key, timeout=30.0)

    DATASET_PATH = Path(__file__).parent / "hf_dataset"
    print("Loading plant disease dataset...")
    dataset = load_from_disk(str(DATASET_PATH))
    split_name = list(dataset.keys())[0]
    data = dataset[split_name]
    print(f"Using split: {split_name}, records: {data.num_rows}")

    questions = []
    for q in data["question"]:
        questions.append("" if q is None else str(q))
    global _COL_CROP, _COL_DISEASE
    _COL_CROP = [str(c or "").lower() for c in data["crop"]]
    _COL_DISEASE = [str(d or "").lower() for d in data["disease"]]

    print("Building chatbot knowledge search...")
    vectorizer = _TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))
    question_vectors = vectorizer.fit_transform(questions)
    print(f"Knowledge search ready! Using Groq model: {GROQ_MODEL}")

    _initialized = True


# =========================================================
# SYSTEM INSTRUCTIONS
# =========================================================
URDU_SPELLING = """URDU SPELLING (VERY IMPORTANT):
- Use CORRECT Urdu spellings for agricultural terms. Common mistakes to avoid:
  * \u06a9\u0627\u0634\u062a (cultivation) \u2014 NOT \u06a9\u0634\u062a
  * \u0641\u0635\u0644 (crop) \u2014 NOT \u0641\u0635\u0644\u062a
  * \u0628\u06cc\u062c (seed) \u2014 NOT \u0628\u06cc\u062c\u06be
  * \u067e\u0627\u0646\u06cc (water) \u2014 NOT \u067e\u0627\u0646\u06cc\u06ba
  * \u0632\u0645\u06cc\u0646 (land/soil) \u2014 NOT \u0632\u0645\u06cc\u06ba
  * \u06c1\u0648\u0627 (air) \u2014 NOT \u06c1\u0648\u06c1
  * \u062f\u0648\u0627 (medicine/spray) \u2014 NOT \u062f\u0648\u0627\u06ba
  * \u067e\u062a\u06be\u0648\u06ba (leaves) \u2014 NOT \u067e\u062a\u0648\u06ba
  * \u062c\u0691 (roots) \u2014 NOT \u062c\u0691\u06be
  * \u067e\u06be\u0644 (fruit) \u2014 NOT \u067e\u06be\u0644\u06be
- Double-check Urdu words before outputting. Use proper Urdu diacritics where needed.
"""

system_message = """You are Kisan Dost, the CDCNSA crop health assistant for Pakistani farmers.

LANGUAGE RULE (CRITICAL):
- You MUST respond in the SAME LANGUAGE the farmer uses.
- If the farmer writes in Urdu, you MUST respond entirely in Urdu script. Do not mix English words.
- If the farmer writes in English, respond in English.
- Urdu responses must use proper Urdu script (not Roman Urdu). Use everyday Urdu that a farmer would understand.
- When responding in Urdu about a disease or pest, ALWAYS give the name in BOTH Urdu and English. For example: "\u067e\u062a\u06cc\u0648\u06ba \u06a9\u0627 \u067e\u06be\u067e\u0648\u0646\u062f\u06cc (Leaf Mold)" or "\u0633\u0641\u06cc\u062f \u0645\u06a9\u06be\u06cc (Whitefly)". This helps the farmer learn the technical name too.
- Product names (brand names, chemical names) can stay in English \u2014 farmers need to recognize them at the shop.

RESPONSE FORMAT (CRITICAL - MUST FOLLOW):
Format responses with clear visual structure:

**Heading**
Text content with proper spacing.

**Another Heading**
• Bullet point 1
• Bullet point 2

FORMATTING RULES:
- Use **bold** for headings (double asterisks)
- Add blank line after each heading before text starts
- Use bullet points (•) for lists
- Add spacing between sections (blank lines)
- Never write text immediately after a heading without a line break

RESPONSE LENGTH - ADAPT TO QUESTION:
- Simple greeting or short question: 20-40 words
- Basic "how to" or "what is" question: 40-80 words with 2-3 bullet points
- Complex question asking for details, comparisons, or multiple topics: 100-200 words with multiple sections
- If user asks for "detailed explanation", "tell me more", "describe", or similar: give comprehensive response with multiple headings and detailed bullet points

Match response depth to question complexity. Don't give short answers to complex questions.

Core behavior:
- Give SPECIFIC advice about the exact disease. Never give generic filler.
- Use simple, everyday language. Avoid jargon.
- Be direct: lead with the most actionable information first.
- Include product names and dosages when available.
- If the farmer mentions a pest, give pest-specific advice.

What to avoid:
- Do NOT write long paragraphs or detailed explanations.
- Do not repeat the same generic advice for different diseases.
- Do not say "consult an expert" as the only advice.
- Do not invent disease names or treatments.
- Do not answer non-agriculture questions.

Conversation memory:
- Remember the disease being discussed. If the user says "it", "this disease", or "its treatment", refer to the current disease.
- If the user names a different disease, switch to that topic.
"""

# =========================================================
# SEARCH DATASET
# =========================================================
_COL_CROP: list = []
_COL_DISEASE: list = []

def search_dataset(user_question, top_k=3, crop=None):
    """TF-IDF search over the Q&A dataset. When the farmer's crop is known, answers about OTHER crops are
    not used (before, 'early blight in tomato' returned potato and 'cotton leaf curl' returned papaya)."""
    import numpy as _np
    from sklearn.metrics.pairwise import cosine_similarity

    _initialize()

    previous_disease = conversation_context.get("disease")
    previous_crop = conversation_context.get("crop")
    is_follow_up = _is_follow_up(user_question)

    search_question = user_question
    if previous_disease and is_follow_up:
        search_question += " " + str(previous_disease)
    if previous_crop and is_follow_up:
        search_question += " " + str(previous_crop)

    user_vector = vectorizer.transform([search_question])
    similarities = cosine_similarity(user_vector, question_vectors)[0]

    if previous_disease and is_follow_up:
        pd_low = previous_disease.lower()
        similarities = similarities + _np.array([0.20 if pd_low in d else 0.0 for d in _COL_DISEASE])

    pats = CROP_DATASET_NAMES.get(crop or "", [])
    if pats:
        in_crop = _np.array([any(p in c for p in pats) for c in _COL_CROP])
        if in_crop.any() and similarities[in_crop].max() >= 0.10:
            similarities = _np.where(in_crop, similarities, -1.0)

    top_indexes = similarities.argsort()[-top_k:][::-1]

    results = []
    for index in top_indexes:
        score = similarities[index]
        if score < 0:
            continue
        record = {
            "score": float(score),
            "question": data["question"][index],
            "answer": data["answer"][index],
            "crop": data["crop"][index],
            "disease": data["disease"][index],
            "severity": data["severity"][index],
            "category": data["category"][index],
            "question_category": data["question_category"][index]
        }
        results.append(record)

    return results


def _build_knowledge_context(disease_info, user_question):
    parts = []
    crop_id = disease_info.get("crop", "")
    parts.append(f"\n=== DISEASE KNOWLEDGE FOR: {disease_info['disease'].upper()} ===")
    parts.append(f"Pathogen: {disease_info['pathogen']}")

    parts.append(f"\nSymptoms:")
    for s in disease_info['symptoms']:
        parts.append(f"- {s}")

    parts.append(f"\nCauses and spread:")
    for c in disease_info['causes']:
        parts.append(f"- {c}")

    parts.append(f"\nOrganic / Biological treatments:")
    for t in disease_info['treatment_organic']:
        parts.append(f"- {t}")

    parts.append(f"\nChemical treatments:")
    for t in disease_info['treatment_chemical']:
        parts.append(f"- {t}")

    parts.append(f"\nPrevention methods:")
    for p in disease_info['prevention']:
        parts.append(f"- {p}")

    if 'severity_indicators' in disease_info:
        parts.append(f"\nSeverity levels:")
        for level, desc in disease_info['severity_indicators'].items():
            parts.append(f"- {level.capitalize()}: {desc}")

    parts.append(f"\n=== RECOMMENDED PRODUCTS ===")
    disease_lower = disease_info['disease'].lower()
    for category, products in PESTICIDE_GUIDE.get("fungicides", {}).items():
        for product in products:
            targets = [t.lower() for t in product.get("target", [])]
            if any(disease_lower in t or t in disease_lower for t in targets) or "all fungal" in " ".join(targets):
                parts.append(f"- {product['name']} ({product['brand']}): {product['dose']}, PHI: {product['phi']}")

    parts.append(f"=== END KNOWLEDGE ===\n")
    return "\n".join(parts)


def _format_pest_answer(pest_info, user_question):
    lines = []
    lines.append(f"**{pest_info['pest']}** ({pest_info['urdu_name']})")
    lines.append(f"*Damage: {pest_info['damage']}*\n")

    lines.append("**How to identify:**")
    for item in pest_info['identification']:
        lines.append(f"- {item}")

    lines.append("\n**Organic treatments:**")
    for t in pest_info['treatment_organic']:
        lines.append(f"- {t}")

    lines.append("\n**Chemical treatments:**")
    for t in pest_info['treatment_chemical']:
        lines.append(f"- {t}")

    lines.append("\n**Prevention:**")
    for p in pest_info['prevention']:
        lines.append(f"- {p}")

    lines.append("\n*Confirm product choice and dosage with your local agricultural extension officer.*")
    return "\n".join(lines)


def _format_knowledge_base_answer(disease_info, user_question):
    question_lower = user_question.lower()

    lines = []
    lines.append(f"**{disease_info['disease']}**")
    lines.append(f"*Caused by: {disease_info['pathogen']}*\n")

    is_treatment_q = any(w in question_lower for w in ['treat', 'control', 'manage', 'cure', 'spray', 'what should i do', 'help', 'remove', 'kill'])
    is_prevention_q = any(w in question_lower for w in ['prevent', 'avoid', 'protect', 'stop spread', 'stop it'])
    is_symptom_q = any(w in question_lower for w in ['symptom', 'sign', 'look', 'appear', 'identify', 'spot'])
    is_cause_q = any(w in question_lower for w in ['cause', 'why', 'how', 'reason', 'spread', 'come from'])

    answered_section = False

    if is_symptom_q:
        lines.append("**Symptoms to look for:**")
        for s in disease_info['symptoms']:
            lines.append(f"- {s}")
        answered_section = True

    if is_cause_q:
        if answered_section:
            lines.append("")
        lines.append("**What causes it:**")
        for c in disease_info['causes']:
            lines.append(f"- {c}")
        answered_section = True

    if is_treatment_q:
        if answered_section:
            lines.append("")
        lines.append("**Organic treatments:**")
        for t in disease_info['treatment_organic']:
            lines.append(f"- {t}")
        lines.append("")
        lines.append("**Chemical treatments:**")
        for t in disease_info['treatment_chemical']:
            lines.append(f"- {t}")
        answered_section = True

    if is_prevention_q:
        if answered_section:
            lines.append("")
        lines.append("**How to prevent it:**")
        for p in disease_info['prevention']:
            lines.append(f"- {p}")
        answered_section = True

    if not answered_section:
        lines.append("**Key symptoms:**")
        for s in disease_info['symptoms'][:3]:
            lines.append(f"- {s}")
        lines.append("")
        lines.append("**First steps:**")
        lines.append(f"- {disease_info['treatment_organic'][0]}")
        lines.append(f"- {disease_info['treatment_organic'][1]}")
        lines.append("")
        lines.append("**Prevention:**")
        lines.append(f"- {disease_info['prevention'][0]}")

    lines.append("\n*Confirm product choice and dosage with your local agricultural extension officer.*")
    return "\n".join(lines)


# =========================================================
# GENERATE ANSWER USING GROQ
# =========================================================
def _build_pest_context(pest_info):
    parts = []
    parts.append(f"=== PEST KNOWLEDGE: {pest_info['pest'].upper()} ===")
    parts.append(f"Urdu name: {pest_info['urdu_name']}")
    parts.append(f"Crops affected: {', '.join(pest_info['crops_affected'])}")
    parts.append(f"Damage: {pest_info['damage']}")

    parts.append(f"\nHow to identify:")
    for item in pest_info['identification']:
        parts.append(f"- {item}")

    parts.append(f"\nOrganic treatments:")
    for t in pest_info['treatment_organic']:
        parts.append(f"- {t}")

    parts.append(f"\nChemical treatments:")
    for t in pest_info['treatment_chemical']:
        parts.append(f"- {t}")

    parts.append(f"\nPrevention:")
    for p in pest_info['prevention']:
        parts.append(f"- {p}")

    parts.append(f"\n=== RECOMMENDED PRODUCTS ===")
    for category, products in PESTICIDE_GUIDE.get("insecticides", {}).items():
        for product in products:
            targets = [t.lower() for t in product.get("target", [])]
            pest_lower = pest_info['pest'].lower()
            if any(pest_lower in t or t in pest_lower for t in targets):
                parts.append(f"- {product['name']} ({product['brand']}): {product['dose']}, PHI: {product['phi']}")

    parts.append(f"=== END PEST KNOWLEDGE ===")
    return "\n".join(parts)


# =========================================================
# APP DISEASE LIBRARY (same verified text as the website's Disease Library)
# =========================================================
import json as _json
_LIB_PATH = Path(__file__).parent / "app_disease_library.json"
try:
    APP_LIBRARY = _json.loads(_LIB_PATH.read_text(encoding="utf-8"))
except Exception:
    APP_LIBRARY = {}


def _norm_name(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", str(text or "").lower().replace("_", " "))).strip()


def _name_variants(name):
    """'Leaf Blight / Isariopsis Leaf Spot' -> {'leaf blight isariopsis leaf spot', 'leaf blight', 'isariopsis leaf spot'}"""
    out = {_norm_name(name)}
    for part in re.split(r"[/(),]", str(name or "")):
        n = _norm_name(part)
        # a split-off part must be 2+ words ('isariopsis leaf spot'); single words like 'brown' from
        # 'Brown/white-backed planthoppers' would match any farmer saying "brown spots"
        if len(n) >= 4 and len(n.split()) >= 2 and n not in {"dataset label", "project label", "like symptoms"}:
            out.add(n)
    return {v for v in out if v}


def _library_entry(crop, disease):
    if not crop or not disease:
        return None
    want = _name_variants(disease)
    for e in APP_LIBRARY.get(crop, []):
        names = set().union(*(_name_variants(x) for x in [e["name"], *e.get("aliases", [])]))
        if want & names:
            return e
    return None


def _named_disease(crop, question_en, question_raw=""):
    """Disease the farmer NAMES in the question (library names, KB topics, dataset disease names of this crop).
    Symptom descriptions ('brown spots', 'leaves curling') never lock a disease."""
    q = " " + _norm_name(question_en) + " "
    raw = str(question_raw or "")
    best = None
    names = []
    for e in APP_LIBRARY.get(crop or "", []):
        for x in [e["name"], *e.get("aliases", [])]:
            names.append((x, e["name"]))
        if e.get("name_ur") and e["name_ur"] in raw:
            return e["name"]
    for x, canon in names:
        for v in _name_variants(x):
            if len(v) >= 4 and f" {v} " in q and (best is None or len(v) > best[0]):
                best = (len(v), canon)
    return best[1] if best else None


def _library_context(e, urdu):
    lines = [f"=== APP DISEASE LIBRARY (verified; use FIRST): {e['name']} ({e['name_ur']}) ===",
             f"Type: {e['type']} - {e['cause']}",
             f"Symptoms: {e['symptoms']}"]
    if urdu and e.get("symptoms_ur"):
        lines.append(f"Symptoms in Urdu: {e['symptoms_ur']}")
    lines += [f"When risk is higher: {e['risk']}", f"Management: {e['management']}",
              f"Prevention: {e['prevention']}", f"Chemical guidance: {e['chemical']}"]
    if e.get("note"):
        lines.append(f"Note: {e['note']}")
    lines.append("=== END APP DISEASE LIBRARY ===")
    return "\n".join(lines)


def _build_messages(user_question, retrieved_results, urdu_match=None, kb_records=None, interface_lang='en',
                    search_question=None):
    """Everything the LLM sees. Returns ('reply', text) or ('llm', messages)."""
    urdu_mode = interface_lang == 'ur'
    crop = _canon_crop(conversation_context.get("crop")) or conversation_context.get("crop")
    disease = conversation_context.get("disease")

    resolved_question = user_question
    if disease and _is_follow_up(search_question or user_question):
        resolved_question = f"{user_question}\n[The farmer is referring to {disease} on {crop}]"

    knowledge_context = ""
    disease_info = None
    pest_info = None
    lib = _library_entry(crop, disease)
    if lib:
        knowledge_context += _library_context(lib, urdu_mode) + "\n"

    if urdu_match and urdu_match["type"] == "pest":
        pest_info = urdu_match["pest_info"]
        knowledge_context += _build_pest_context(pest_info)
    elif urdu_match and urdu_match["type"] == "disease":
        disease_info = get_disease_info(urdu_match["crop"], urdu_match["disease"])
        if disease_info:
            knowledge_context += _build_knowledge_context(disease_info, user_question)
    elif crop and disease:
        disease_info = get_disease_info(CROP_DK_IDS.get(crop, crop), disease) or get_disease_info(crop, disease)
        if disease_info:
            knowledge_context += _build_knowledge_context(disease_info, user_question)

    if kb_records is None:
        kb_records = search_knowledge_base(search_question or user_question, crop=conversation_context.get("crop"), top_k=3)
    if kb_records:
        knowledge_context += "\n" + format_knowledge_context(kb_records[:2])[:2400]

    # 'healthy' Q&A rows only help when the photo was healthy (before: 'grape powdery mildew spray' got 3 healthy rows)
    keep_healthy = conversation_context.get("healthy") or "healthy" in str(search_question or user_question).lower()
    retrieved_results = [r for r in (retrieved_results or []) if r["score"] >= 0.10
                         and (keep_healthy or str(r.get("disease", "")).lower() != "healthy")]
    have_context = bool(retrieved_results or kb_records or crop or lib)

    if not retrieved_results and not have_context:
        if disease_info:
            txt = _format_knowledge_base_answer(disease_info, user_question)
            return "reply", (_translate_to_urdu(txt) if urdu_mode else txt)
        if pest_info:
            txt = _format_pest_answer(pest_info, user_question)
            return "reply", (_translate_to_urdu(txt) if urdu_mode else txt)
        txt = ("I don't have enough information to answer this accurately. "
               "Try asking about symptoms, treatments, or prevention for your crop's disease.")
        return "reply", (_translate_to_urdu(txt) if urdu_mode else txt)

    # short context = more answers per free minute and faster replies: 2 Q&A rows, answers cut to 400 characters
    context = "\n---\n".join(
        f"SOURCE {i+1} (relevance: {r['score']:.2f})\nQ: {r['question']}\nA: {str(r['answer'])[:400]}\n"
        f"Crop: {r['crop']}, Disease: {r['disease']}\n" for i, r in enumerate(retrieved_results[:2])
    ) or "(no close match in the Q&A dataset)"

    # notes are ADDED to each other (before, a known severity overwrote the 'answer about THIS crop' rule)
    notes = []
    if conversation_context.get("healthy"):
        notes.append(f"The farmer's latest photo of {crop} was diagnosed as HEALTHY. Do not invent a disease; "
                     "give prevention, monitoring and good-practice advice for this crop.")
    if crop:
        notes.append(f"The farmer's crop is: {crop}. Answer about THIS crop only.")
    else:
        notes.append("The farmer has NOT said which crop this is. Give 2-3 common possible causes briefly, then ask "
                     "which crop it is (or suggest uploading a photo). Do not pick one disease as certain.")
    if crop and disease:
        notes.append(f"The disease being discussed is: {disease}.")
    elif crop and not conversation_context.get("healthy"):
        notes.append("No disease has been confirmed yet. If the farmer describes symptoms, give the 2-3 most likely "
                     "causes for this crop (say they are possibilities, not a diagnosis) and suggest uploading a clear "
                     "photo in the Diagnose page.")
    if conversation_context.get("severity"):
        pct = conversation_context.get("severity_percent")
        notes.append(f"The photo diagnosis severity is {conversation_context['severity']}"
                     + (f" ({pct}% of the leaf area diseased)" if pct is not None else "")
                     + ". Tailor the urgency of your advice to this severity.")
    severity_note = "\n".join(notes)

    if urdu_mode:
        lang_instruction = ("\n" + URDU_SPELLING + "\nCRITICAL LANGUAGE SETTING: The farmer asked in Urdu. You MUST write your ENTIRE "
                            "response in Urdu script (Nastaliq). Do not use English words except for product/brand "
                            "names and the English disease name in brackets. Use correct Urdu spellings. Do not mix languages.\n")
    else:
        lang_instruction = ("\nCRITICAL LANGUAGE SETTING: The farmer asked in English. Write the ENTIRE response in "
                            "clear, natural English. Do not use Urdu, Arabic, or transliterated Urdu - not even in brackets "
                            "after a disease name. Product and scientific names may remain unchanged.\n")

    user_prompt = f"""Farmer's question: {resolved_question}
{severity_note}

Retrieved from plant disease dataset:
{context}
{knowledge_context}

Answer the farmer's question using the information above.
- PRIORITY: 1) APP DISEASE LIBRARY, 2) PLANT HEALTH KNOWLEDGE BASE, 3) DISEASE KNOWLEDGE, 4) the Q&A dataset.
- Use only sources about the farmer's crop; ignore retrieved text about other crops or other diseases.
- Give product names or doses ONLY if they appear in the sources above; never invent a product or dose.
  Remind the farmer to check the product label / local agriculture officer before spraying.
- If the sources above do not cover the question, say so in one line, then give only general, widely accepted
  advice for Pakistan (Rabi/Kharif seasons); never state crop stages, timings or doses you are not sure of.
- If the question is not about crops, farming, plant health, pests or fertilizer, reply with ONE short sentence
  that you can only help with crop health, and nothing else.
{lang_instruction}"""

    messages = [{"role": "system", "content": system_message}]
    # last 2 exchanges, long answers shortened - enough for "it"/"that" follow-ups
    for h in conversation_history[-4:]:
        messages.append({"role": h["role"], "content": h["content"][:600]})
    messages.append({"role": "user", "content": user_prompt})
    return "llm", messages


def _remember(hist, user_question, answer):
    hist.append({"role": "user", "content": user_question})
    hist.append({"role": "assistant", "content": answer})
    if len(hist) > MAX_HISTORY * 2:
        hist[:] = hist[-(MAX_HISTORY * 2):]


def generate_answer(user_question, retrieved_results, urdu_match=None, kb_records=None, interface_lang='en',
                    search_question=None):
    hist = conversation_history
    kind, payload = _build_messages(user_question, retrieved_results, urdu_match, kb_records, interface_lang,
                                    search_question)
    if kind == "reply":
        return payload
    try:
        response = _llm(model=GROQ_MODEL, messages=payload, temperature=0.3, max_tokens=CHAT_MAX_TOKENS)
    except Exception as exc:
        if "429" in str(exc) or "rate limit" in str(exc).lower():
            return _busy_message(interface_lang == "ur")
        return f"Sorry, the assistant encountered an error: {exc}. Please try again."
    answer = _clean(response.choices[0].message.content)
    _remember(hist, user_question, answer)
    return answer


class _ThinkFilter:
    """Removes <think>...</think> from a token stream even when the tags are split across chunks."""
    def __init__(self):
        self.buf, self.inside = "", False

    def feed(self, chunk):
        self.buf += chunk
        out = ""
        while True:
            if self.inside:
                i = self.buf.find("</think>")
                if i < 0:
                    self.buf = self.buf[-8:]
                    return out
                self.buf, self.inside = self.buf[i + 8:].lstrip(), False
            else:
                i = self.buf.find("<think>")
                if i < 0:
                    keep = 0
                    for k in range(1, 7):          # a partial '<think' at the end may continue in the next chunk
                        if self.buf.endswith("<think>"[:k]):
                            keep = k
                    out += self.buf[:len(self.buf) - keep]
                    self.buf = self.buf[len(self.buf) - keep:]
                    return out
                out += self.buf[:i]
                self.buf, self.inside = self.buf[i + 7:], True

    def flush(self):
        rest = "" if self.inside else self.buf
        self.buf = ""
        return rest


async def _stream_llm(messages, hist, user_question):
    """Streams Groq tokens (worker thread) and strips <think> blocks."""
    import queue
    chunk_queue = queue.Queue()

    def process_stream():
        try:
            stream = _llm(model=GROQ_MODEL, messages=messages, temperature=0.3,
                                                    max_tokens=CHAT_MAX_TOKENS, stream=True)
            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    chunk_queue.put(delta)
            chunk_queue.put(None)
        except Exception as e:
            chunk_queue.put(e)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, process_stream)
    flt = _ThinkFilter()
    full_answer = ""
    while True:
        try:
            chunk = await loop.run_in_executor(None, chunk_queue.get, True, 0.1)
        except queue.Empty:
            continue
        if chunk is None:
            break
        if isinstance(chunk, Exception):
            if not full_answer:
                if "429" in str(chunk) or "rate limit" in str(chunk).lower():
                    yield _busy_message(_is_urdu(user_question) or _is_roman_urdu(user_question))
                else:
                    yield f"Sorry, the assistant encountered an error: {chunk}. Please try again."
            return
        text = flt.feed(chunk)
        if text:
            full_answer += text
            yield text
    tail = flt.flush()
    if tail:
        full_answer += tail
        yield tail
    with _SESSION_LOCK:
        _remember(hist, user_question, full_answer.strip())


def _translate_to_urdu(english_text: str) -> str:
    try:
        response = _llm(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": (
                    "You are a translator. Convert the following English text into "
                    "natural Urdu that a Pakistani farmer would understand. "
                    "Use Urdu script. Keep disease names and product names as-is "
                    "if there is no common Urdu equivalent, and keep doses/numbers exactly. "
                    "Keep the same markdown formatting (**headings**, bullet points, line breaks). "
                    "Do not add explanations — just return the Urdu translation."
                )},
                {"role": "user", "content": english_text}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        return _clean(response.choices[0].message.content)
    except Exception:
        return english_text


def _translate_to_english_answer(urdu_text: str) -> str:
    """Previous (Urdu) answer -> English, same formatting."""
    try:
        response = _llm(model=GROQ_MODEL, messages=[
            {"role": "system", "content": "Translate this Urdu answer for a farmer into clear, simple English. Keep the same "
                                          "markdown formatting and all numbers/doses. Return only the translation."},
            {"role": "user", "content": urdu_text}], temperature=0.2, max_tokens=1000)
        return _clean(response.choices[0].message.content)
    except Exception:
        return urdu_text


def _translate_to_english(urdu_text: str) -> str:
    try:
        response = _llm(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": (
                    "You are a translator. Convert the following Urdu text from a "
                    "Pakistani farmer into clear, simple English. Focus on the "
                    "agricultural meaning — what crop, disease, symptom, or treatment "
                    "they are asking about. Return ONLY the English translation, "
                    "nothing else."
                )},
                {"role": "user", "content": urdu_text}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception:
        return urdu_text



# =========================================================
# CROP DETECTION (English / Roman Urdu / Urdu)
# =========================================================
# canonical crop -> words that name it
CROP_WORDS = {
    "corn": ["corn", "maize", "makai", "makki", "makkai", "مکئی", "مکی", "مکہ", "بھٹا", "بھٹہ"],
    "rice": ["rice", "paddy", "chawal", "chawal", "dhan", "dhaan", "چاول", "دھان", "مونجی"],
    "cotton": ["cotton", "kapas", "kapaas", "phutti", "کپاس", "روئی", "پھٹی"],
    "tomato": ["tomato", "tomatoes", "tamatar", "timatar", "ٹماٹر"],
    "apple": ["apple", "apples", "seb", "saib", "سیب"],
    "mango": ["mango", "mangoes", "aam", "آم"],
    "grape": ["grape", "grapes", "grapevine", "angoor", "angur", "انگور"],
    "eggplant": ["eggplant", "brinjal", "baingan", "bengan", "baigan", "بینگن", "بینگن"],
    "cucumber": ["cucumber", "kheera", "khira", "کھیرا", "کھیرے"],
    "peas": ["pea", "peas", "matar", "mattar", "مٹر"],
    "potato": ["potato", "potatoes", "aloo", "alu", "آلو"],
    "wheat": ["wheat", "gandum", "گندم"],
    "pepper": ["pepper", "chilli", "chili", "mirch", "مرچ", "مرچیں"],
    "lemon": ["lemon", "citrus", "kinnow", "kinno", "orange", "malta", "لیموں", "کینو", "مالٹا"],
    "sugarcane": ["sugarcane", "ganna", "گنا", "گنے"],
}
# canonical crop -> how it is written in the Q&A dataset / knowledge base / disease_knowledge.py
CROP_DATASET_NAMES = {"corn": ["corn", "maize"], "eggplant": ["eggplant", "brinjal"], "lemon": ["lemon", "citrus", "orange"],
                      "pepper": ["pepper"], "grape": ["grape"], "peas": ["peas"]}
CROP_KB_NAMES = {"corn": "Corn / Maize", "eggplant": "Eggplant / Brinjal", "lemon": "Lemon / Citrus"}
CROP_DK_IDS = {"corn": "maize"}


def _canon_crop(name):
    """Map any crop label (UI id, dataset name, diagnosis name) to the canonical crop."""
    if not name:
        return None
    low = str(name).lower()
    for canon, words in CROP_WORDS.items():
        if low == canon or any(re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", low) for w in words if w.isascii()):
            return canon
    return None


def _detect_crop(text):
    """Crop the farmer names in this message (None if none). Urdu matched as whole words."""
    low = str(text).lower()
    tokens = set(re.split(r"[\s،؟?!.,:;()\"'۔]+", str(text)))
    for canon, words in CROP_WORDS.items():
        for w in words:
            if w.isascii():
                if re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", low):
                    return canon
            elif w in tokens:
                return canon
    return None


for _c in CROP_WORDS:
    CROP_DATASET_NAMES.setdefault(_c, [_c])

GREETING_WORDS = {"hi", "hello", "hey", "salam", "salaam", "assalam", "assalamualaikum", "assalamu", "alaikum", "aoa",
                  "good", "morning", "evening", "afternoon", "there", "ji", "sir", "bhai", "dost", "friend", "everyone",
                  "o", "u", "w", "walaikum", "السلام", "علیکم", "سلام", "اسلام", "ہیلو"}


def _greeting_reply(message):
    """Canned greeting ONLY when the message is nothing but a greeting
    (before, 'hi my tomato has spots' got just 'Hey, hi!')."""
    toks = [t for t in re.split(r"[\s,!.?،؟۔]+", message.lower().strip()) if t]
    if not toks or any(t not in GREETING_WORDS for t in toks):
        return None
    if _is_urdu(message):
        return "وعلیکم السلام! میں آپ کی مدد کے لیے حاضر ہوں۔ اپنی فصل کی صحت، بیماری یا علاج کے بارے میں پوچھیں۔"
    if any(t in {"salam", "salaam", "assalam", "assalamualaikum", "assalamu", "aoa"} for t in toks):
        return "Wa-alaikum-as-salam! I'm here to help. Ask me about your crop's health, diseases, or treatments."
    if "morning" in toks:
        return "Good morning! How can I help you with your crops today?"
    if "evening" in toks:
        return "Good evening! How can I help you with your crops today?"
    if "afternoon" in toks:
        return "Good afternoon! How can I help you with your crops today?"
    return "Hello! How can I help you with your crops today?"


def _kb_for_crop(query, crop, k=3):
    """Knowledge-base records for THIS crop only (before, 'apple mosaic' got eggplant/tomato/cucumber records
    because no apple record matched and the code fell back to other crops). 'healthy' records only for a healthy photo."""
    recs = search_knowledge_base(query, crop=CROP_KB_NAMES.get(crop or "", crop), top_k=12 if crop else k)
    if crop:
        kb_name = CROP_KB_NAMES.get(crop, crop).lower()
        recs = [r for r in recs if kb_name in str(r.get("crop", "")).lower() or str(r.get("crop", "")).lower() in kb_name]
    if not conversation_context.get("healthy") and "healthy" not in str(query).lower():
        recs = [r for r in recs if str(r.get("topic", "")).lower() != "healthy"]
    return recs[:k]


def _prepare(message, context=None):
    """Everything before the LLM call, shared by ask() and ask_stream().
    Returns ('reply', text) for a direct answer or ('llm', kwargs) for generate_answer*()."""
    greet = _greeting_reply(message)
    if greet:
        return "reply", greet
    photo_answer = _photo_advice(message)
    if photo_answer:
        return "reply", photo_answer

    # "translate it into Urdu" -> translate the previous answer (before: the English request got the same English answer again)
    if _is_translate_request(message):
        last = next((h["content"] for h in reversed(conversation_history) if h["role"] == "assistant"), None)
        if last:
            _initialize()
            target = _requested_language(message)
            already = _is_urdu(last) if target == "ur" else not _is_urdu(last)
            out = last if already else (_translate_to_urdu(last) if target == "ur" else _translate_to_english_answer(last))
            _remember(conversation_history, message, out)
            return "reply", out

    _initialize()
    interface_lang = _message_language(message)
    if context:
        _update_context_from_request(context)

    is_urdu_input = _is_urdu(message)
    is_roman_urdu_input = _is_roman_urdu(message)

    # Urdu / Roman Urdu -> English for searching (the datasets are English)
    search_message = message
    if is_urdu_input or is_roman_urdu_input:
        try:
            search_message = _translate_to_english(message) or message
        except Exception:
            search_message = message

    # crop named in this message wins; otherwise keep the crop from the diagnosis / earlier turns
    named_crop = _detect_crop(message) or _detect_crop(search_message)
    current = _canon_crop(conversation_context.get("crop"))
    if named_crop and named_crop != current:
        conversation_context["crop"] = named_crop
        conversation_context["disease"] = None          # a new crop -> old disease no longer applies
        conversation_context["severity"] = None
        conversation_context["severity_percent"] = None
        conversation_context["healthy"] = False
    crop = named_crop or current

    urdu_match = None
    if is_urdu_input:
        urdu_match = match_urdu_to_knowledge(message)
        if urdu_match and urdu_match["type"] == "disease":
            m_crop = _canon_crop("corn" if urdu_match["crop"] == "maize" else urdu_match["crop"])
            if crop and m_crop != crop:
                urdu_match = None                       # e.g. 'brown spots' mapped to RICE while asking about tomato
            else:
                conversation_context["crop"] = crop or m_crop
                conversation_context["disease"] = urdu_match["disease"]
        elif urdu_match and urdu_match["type"] == "pest":
            pest_info = urdu_match["pest_info"]
            if not crop:
                conversation_context["crop"] = pest_info.get("crops_affected", [None])[0]
            conversation_context["disease"] = pest_info["pest"]

    follow_up = _is_follow_up(search_message) or _is_follow_up(message)
    search_message = _resolve_pronouns(search_message)
    results = search_dataset(search_message, top_k=3, crop=crop)
    kb_records = _kb_for_crop(search_message, crop)

    # nothing about crops at all -> polite refusal instead of an answer built on unrelated records
    best_ds = results[0]["score"] if results else 0.0
    if not crop and not kb_records and best_ds < 0.30 and not conversation_context.get("disease"):
        if interface_lang == "ur":
            return "reply", "میں صرف فصلوں کی صحت، بیماریوں، کیڑوں اور ان کے علاج کے بارے میں مدد کر سکتا ہوں۔ اپنی فصل کے بارے میں سوال پوچھیں۔"
        return "reply", ("I can only help with crop health - diseases, pests, and their treatment. "
                         "Please ask a question about your crop.")

    # remember a disease only when the farmer NAMES it (before, symptom words locked a guessed disease:
    # 'tomato spots' -> Yellow Leaf Curl Virus, 'eggplant wilt' -> Whiteflies, 'rice brown spots' -> Leaf Scald)
    if crop and not follow_up and not urdu_match:
        dis = _named_disease(crop, search_message, message)
        if not dis:
            q = " " + _norm_name(search_message) + " "
            for r in list(kb_records) + list(results):
                name = str(r.get("topic") or r.get("disease") or "")
                if _canon_crop(r.get("crop")) == crop and name.lower() != "healthy" and \
                        any(len(v) >= 4 and f" {v} " in q for v in _name_variants(name)):
                    dis = name
                    break
        if dis and dis.lower() != "healthy":
            if (conversation_context.get("disease") or "").lower() != dis.lower():
                conversation_context["severity"] = None     # the photo's severity belonged to the old disease
                conversation_context["severity_percent"] = None
            conversation_context["disease"] = dis
            conversation_context["crop"] = crop

    # when a disease is known, search for IT too (before, 'what should I do next?' retrieved random records)
    if conversation_context.get("disease") and crop:
        topic_q = f"{conversation_context['disease']} {search_message}"
        extra = _kb_for_crop(topic_q, crop)
        seen = set()
        kb_records = [r for r in extra + list(kb_records) if not (r.get("topic") in seen or seen.add(r.get("topic")))][:3]
        if not results or results[0]["score"] < 0.2:
            results = search_dataset(topic_q, top_k=3, crop=crop)

    return "llm", dict(user_question=message, retrieved_results=results, urdu_match=urdu_match,
                       kb_records=kb_records, interface_lang=interface_lang, search_question=search_message)

# =========================================================
# MAIN CHAT FUNCTION FOR API
# =========================================================
def ask(message: str, context: dict = None, session_id: str = "default") -> str:
    """Main function for API integration (message in English, Urdu or Roman Urdu;
    context = crop / disease / severity from the photo diagnosis)."""
    with _SESSION_LOCK:
        _bind_session(session_id)
        kind, payload = _prepare(message, context)
        if kind == "reply":
            return payload
        return _clean(generate_answer(**payload))


async def ask_stream(message: str, context: dict = None, session_id: str = "default"):
    """Streaming version of ask(). The slow, blocking part (search, translation) runs in a worker thread so
    the server keeps answering other requests (photo diagnosis, other users) meanwhile."""
    def prepare():
        with _SESSION_LOCK:
            _bind_session(session_id)
            kind, payload = _prepare(message, context)
            if kind == "reply":
                return kind, payload, None
            hist = conversation_history
            kind, payload = _build_messages(**payload)
            return kind, payload, hist

    kind, payload, hist = await asyncio.to_thread(prepare)
    if kind == "reply":
        yield payload
        return
    async for chunk in _stream_llm(payload, hist, message):
        yield chunk


def _clean(text):
    """Drop any <think>...</think> block a reasoning model might emit."""
    return re.sub(r"<think>.*?</think>\s*", "", text or "", flags=re.S).strip()


def reset_context(session_id: str = "default"):
    with _SESSION_LOCK:
        _SESSIONS.pop(str(session_id or "default")[:80], None)
        _bind_session(session_id)
