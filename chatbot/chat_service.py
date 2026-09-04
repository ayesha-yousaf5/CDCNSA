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
}

conversation_history: list[dict] = []
MAX_HISTORY = 6

FOLLOW_UP_WORDS = [
    "it", "its", "this", "that", "these", "those",
    "the disease", "the plant", "the crop"
]


def _update_context_from_request(context: dict | None) -> None:
    """Apply diagnosis context without turning abstentions into diseases."""
    if not context:
        return

    if context.get("crop"):
        conversation_context["crop"] = str(context["crop"])

    raw_disease = str(context.get("disease") or "").strip()
    normalized_disease = raw_disease.lower().replace("_", " ")
    abstained = (
        bool(context.get("healthy"))
        or bool(context.get("uncertainty"))
        or normalized_disease in {"healthy", "uncertain"}
    )
    if abstained:
        conversation_context["disease"] = None
        conversation_context["severity"] = None
    elif raw_disease:
        conversation_context["disease"] = raw_disease

    severity = context.get("severity")
    if not abstained and severity and str(severity).upper() != "N/A":
        conversation_context["severity"] = str(severity)


def _resolve_pronouns(message: str) -> str:
    """Replace vague pronouns with the disease/crop from conversation context
    so that dataset searches target the right entity."""
    disease = conversation_context.get("disease")
    crop = conversation_context.get("crop")
    if not disease:
        return message

    question_lower = message.lower()
    if not any(word in question_lower for word in FOLLOW_UP_WORDS):
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
}

def _is_roman_urdu(text: str) -> bool:
    """Detect if text is Roman Urdu (Urdu written in Latin script)."""
    if _is_urdu(text):
        return False
    words = set(re.findall(r'[a-zA-Z]+', text.lower()))
    roman_urdu_count = len(words & ROMAN_URDU_WORDS)
    total_words = len(words)
    return total_words > 0 and (roman_urdu_count / total_words) > 0.3


def _message_language(message: str) -> str:
    """Choose reply language from the farmer's message, not the UI toggle."""
    return 'ur' if _is_urdu(message) or _is_roman_urdu(message) else 'en'


def _initialize():
    global _initialized, client, data, questions, question_vectors, vectorizer
    global GROQ_API_KEY, GROQ_MODEL

    if _initialized:
        return

    from datasets import load_from_disk
    from sklearn.feature_extraction.text import TfidfVectorizer as _TfidfVectorizer

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # Keep generation lightweight; retrieval supplies the factual content.
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

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

    print("Building chatbot knowledge search...")
    vectorizer = _TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))
    question_vectors = vectorizer.fit_transform(questions)
    print(f"Knowledge search ready! Using Groq model: {GROQ_MODEL}")

    _initialized = True


# =========================================================
# SYSTEM INSTRUCTIONS
# =========================================================
system_message = """You are Kisan Dost, the CDCNSA crop health assistant for Pakistani farmers.

LANGUAGE RULE (CRITICAL):
- You MUST respond in the SAME LANGUAGE the farmer uses.
- If the farmer writes in Urdu, you MUST respond entirely in Urdu script. Do not mix English words.
- If the farmer writes in English, respond in English.
- Urdu responses must use proper Urdu script (not Roman Urdu). Use everyday Urdu that a farmer would understand.
- When responding in Urdu about a disease or pest, ALWAYS give the name in BOTH Urdu and English. For example: "\u067e\u062a\u06cc\u0648\u06ba \u06a9\u0627 \u067e\u06be\u067e\u0648\u0646\u062f\u06cc (Leaf Mold)" or "\u0633\u0641\u06cc\u062f \u0645\u06a9\u06be\u06cc (Whitefly)". This helps the farmer learn the technical name too.
- Product names (brand names, chemical names) can stay in English \u2014 farmers need to recognize them at the shop.

URDU SPELLING (VERY IMPORTANT):
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
def search_dataset(user_question, top_k=3):
    from sklearn.metrics.pairwise import cosine_similarity

    _initialize()

    previous_disease = conversation_context.get("disease")
    previous_crop = conversation_context.get("crop")
    is_follow_up = any(word in user_question.lower() for word in FOLLOW_UP_WORDS)

    search_question = user_question
    if previous_disease and is_follow_up:
        search_question += " " + str(previous_disease)
    if previous_crop and is_follow_up:
        search_question += " " + str(previous_crop)

    user_vector = vectorizer.transform([search_question])
    similarities = cosine_similarity(user_vector, question_vectors)[0]

    if previous_disease and is_follow_up:
        for i in range(len(similarities)):
            disease_name = str(data["disease"][i]).lower()
            if previous_disease.lower() in disease_name:
                similarities[i] += 0.20

    top_indexes = similarities.argsort()[-top_k:][::-1]

    results = []
    for index in top_indexes:
        score = similarities[index]
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

    if crop_id in CROP_SEASONAL_GUIDE:
        guide = CROP_SEASONAL_GUIDE[crop_id]
        parts.append(f"\n=== SEASONAL GUIDE FOR {crop_id.upper()} ===")
        parts.append(f"Fertilizer schedule: {guide.get('fertilizer_schedule', 'N/A')}")
        parts.append(f"Common mistakes: {guide.get('common_mistakes', 'N/A')}")
        for season, info in guide.get("seasons", {}).items():
            parts.append(f"\n{season.capitalize()} season:")
            parts.append(f"  Planting: {info.get('planting', 'N/A')}")
            parts.append(f"  Disease risks: {', '.join(info.get('disease_risks', []))}")
            parts.append(f"  Weather concerns: {info.get('weather_concerns', 'N/A')}")
            parts.append(f"  Prevention: {info.get('prevention_tips', 'N/A')}")

    parts.append(f"\n=== HOMEMADE REMEDIES ===")
    for remedy_name, remedy in HOMEMADE_REMEDIES.items():
        if crop_id in remedy.get("crops", []) or "all vegetables" in remedy.get("crops", []):
            parts.append(f"\n{remedy_name.replace('_', ' ').title()}:")
            parts.append(f"  Recipe: {remedy['recipe']}")
            parts.append(f"  Uses: {', '.join(remedy['uses'])}")
            parts.append(f"  Application: {remedy['application']}")

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


def generate_answer(user_question, retrieved_results, urdu_match=None, kb_records=None, interface_lang='en'):
    urdu_mode = interface_lang == 'ur'

    resolved_question = user_question

    if conversation_context["disease"]:
        question_lower = user_question.lower()
        if any(word in question_lower for word in FOLLOW_UP_WORDS):
            resolved_question = (
                f"{user_question}\n"
                f"[The user is referring to {conversation_context['disease']} "
                f"on {conversation_context['crop']}]"
            )

    knowledge_context = ""
    disease_info = None
    pest_info = None

    if urdu_match and urdu_match["type"] == "pest":
        pest_info = urdu_match["pest_info"]
        knowledge_context = _build_pest_context(pest_info)
    elif urdu_match and urdu_match["type"] == "disease":
        disease_info = get_disease_info(
            urdu_match["crop"],
            urdu_match["disease"]
        )
        if disease_info:
            knowledge_context = _build_knowledge_context(disease_info, user_question)
    elif conversation_context["crop"] and conversation_context["disease"]:
        disease_info = get_disease_info(
            conversation_context["crop"],
            conversation_context["disease"]
        )
        if disease_info:
            knowledge_context = _build_knowledge_context(disease_info, user_question)

    if kb_records is None:
        kb_crop = conversation_context.get("crop")
        kb_records = search_knowledge_base(user_question, crop=kb_crop, top_k=3)
    if kb_records:
        kb_context = format_knowledge_context(kb_records)
        knowledge_context += "\n" + kb_context

    if not retrieved_results or retrieved_results[0]["score"] < 0.1:
        if disease_info:
            if urdu_mode:
                kb_answer = _format_knowledge_base_answer(disease_info, user_question)
                return _translate_to_urdu(kb_answer)
            return _format_knowledge_base_answer(disease_info, user_question)
        if pest_info:
            if urdu_mode:
                kb_answer = _format_pest_answer(pest_info, user_question)
                return _translate_to_urdu(kb_answer)
            return _format_pest_answer(pest_info, user_question)
        if not retrieved_results or all(r["score"] < 0.05 for r in retrieved_results):
            if urdu_mode:
                return _translate_to_urdu(
                    "I don't have enough information to answer this accurately. "
                    "Try asking about symptoms, treatments, or prevention for your crop's disease."
                )
            return (
                "I don't have enough information to answer this accurately. "
                "Try asking about symptoms, treatments, or prevention for your crop's disease."
            )

    context_parts = []
    for i, result in enumerate(retrieved_results):
        context_parts.append(
            f"SOURCE {i+1} (relevance: {result['score']:.2f})\n"
            f"Q: {result['question']}\n"
            f"A: {result['answer']}\n"
            f"Crop: {result['crop']}, Disease: {result['disease']}\n"
        )
    context = "\n---\n".join(context_parts)

    severity_note = ""
    if conversation_context.get("severity"):
        severity_note = (
            f"\nThe farmer's diagnosis shows severity: {conversation_context['severity']}. "
            f"Tailor your advice to this severity level."
        )

    lang_instruction = ""
    if urdu_mode:
        lang_instruction = (
            "\nCRITICAL LANGUAGE SETTING: The farmer asked in Urdu. "
            "You MUST write your ENTIRE response in Urdu script (Nastaliq). "
            "Do not use English words except for product/brand names. "
            "Use correct Urdu spellings for all agricultural terms. "
            "Do not mix languages.\n"
        )

    user_prompt = f"""Farmer's question: {resolved_question}
{severity_note}

Retrieved from plant disease dataset:
{context}
{knowledge_context}

Answer the farmer's question using the information above.
PRIORITIZE the PLANT HEALTH KNOWLEDGE BASE section for specific treatments, risk factors, immediate actions, and prevention steps.
Also use the DISEASE KNOWLEDGE section for additional details on symptoms, causes, and treatments.
Be specific — include product names, dosages, and timing when available.
{lang_instruction}"""

    messages = [{"role": "system", "content": system_message}]
    messages.extend(conversation_history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": user_prompt})

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1024
        )
    except Exception as exc:
        return f"Sorry, the assistant encountered an error: {exc}. Please try again."

    answer = response.choices[0].message.content

    conversation_history.append({"role": "user", "content": user_question})
    conversation_history.append({"role": "assistant", "content": answer})
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history[:] = conversation_history[-(MAX_HISTORY * 2):]

    return answer


async def generate_answer_stream(user_question, retrieved_results, urdu_match=None, kb_records=None, interface_lang='en'):
    """Streaming version of generate_answer that yields chunks as they're generated."""
    urdu_mode = interface_lang == 'ur'

    resolved_question = user_question

    if conversation_context["disease"]:
        question_lower = user_question.lower()
        if any(word in question_lower for word in FOLLOW_UP_WORDS):
            resolved_question = (
                f"{user_question}\n"
                f"[The user is referring to {conversation_context['disease']} "
                f"on {conversation_context['crop']}]"
            )

    knowledge_context = ""
    disease_info = None
    pest_info = None

    if urdu_match and urdu_match["type"] == "pest":
        pest_info = urdu_match["pest_info"]
        knowledge_context = _build_pest_context(pest_info)
    elif urdu_match and urdu_match["type"] == "disease":
        disease_info = get_disease_info(
            urdu_match["crop"],
            urdu_match["disease"]
        )
        if disease_info:
            knowledge_context = _build_knowledge_context(disease_info, user_question)
    elif conversation_context["crop"] and conversation_context["disease"]:
        disease_info = get_disease_info(
            conversation_context["crop"],
            conversation_context["disease"]
        )
        if disease_info:
            knowledge_context = _build_knowledge_context(disease_info, user_question)

    if kb_records is None:
        kb_crop = conversation_context.get("crop")
        kb_records = search_knowledge_base(user_question, crop=kb_crop, top_k=3)
    if kb_records:
        kb_context = format_knowledge_context(kb_records)
        knowledge_context += "\n" + kb_context

    if not retrieved_results or retrieved_results[0]["score"] < 0.1:
        if disease_info:
            if urdu_mode:
                kb_answer = _format_knowledge_base_answer(disease_info, user_question)
                translated = _translate_to_urdu(kb_answer)
                yield translated
                return
            yield _format_knowledge_base_answer(disease_info, user_question)
            return
        if pest_info:
            if urdu_mode:
                kb_answer = _format_pest_answer(pest_info, user_question)
                translated = _translate_to_urdu(kb_answer)
                yield translated
                return
            yield _format_pest_answer(pest_info, user_question)
            return
        if not retrieved_results or all(r["score"] < 0.05 for r in retrieved_results):
            if urdu_mode:
                yield _translate_to_urdu(
                    "I don't have enough information to answer this accurately. "
                    "Try asking about symptoms, treatments, or prevention for your crop's disease."
                )
            else:
                yield (
                    "I don't have enough information to answer this accurately. "
                    "Try asking about symptoms, treatments, or prevention for your crop's disease."
                )
            return

    context_parts = []
    for i, result in enumerate(retrieved_results):
        context_parts.append(
            f"SOURCE {i+1} (relevance: {result['score']:.2f})\n"
            f"Q: {result['question']}\n"
            f"A: {result['answer']}\n"
            f"Crop: {result['crop']}, Disease: {result['disease']}\n"
        )
    context = "\n---\n".join(context_parts)

    severity_note = ""
    if conversation_context.get("severity"):
        severity_note = (
            f"\nThe farmer's diagnosis shows severity: {conversation_context['severity']}. "
            f"Tailor your advice to this severity level."
        )

    lang_instruction = ""
    if urdu_mode:
        lang_instruction = (
            "\nCRITICAL LANGUAGE SETTING: The farmer asked in Urdu. "
            "You MUST write your ENTIRE response in Urdu script (Nastaliq). "
            "Do not use English words except for product/brand names. "
            "Use correct Urdu spellings for all agricultural terms. "
            "Do not mix languages.\n"
        )

    user_prompt = f"""Farmer's question: {resolved_question}
{severity_note}

Retrieved from plant disease dataset:
{context}
{knowledge_context}

Answer the farmer's question using the information above.
PRIORITIZE the PLANT HEALTH KNOWLEDGE BASE section for specific treatments, risk factors, immediate actions, and prevention steps.
Also use the DISEASE KNOWLEDGE section for additional details on symptoms, causes, and treatments.
Be specific — include product names, dosages, and timing when available.
{lang_instruction}"""

    messages = [{"role": "system", "content": system_message}]
    messages.extend(conversation_history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": user_prompt})

    full_answer = ""
    try:
        import asyncio
        import queue
        
        chunk_queue = queue.Queue()
        
        def process_stream():
            try:
                stream = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1024,
                    stream=True
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content if chunk.choices else None
                    if delta:
                        chunk_queue.put(delta)
                chunk_queue.put(None)  # Signal completion
            except Exception as e:
                chunk_queue.put(e)  # Signal error
        
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, process_stream)
        
        while True:
            try:
                chunk = await loop.run_in_executor(None, chunk_queue.get, True, 0.1)
                if chunk is None:
                    break
                if isinstance(chunk, Exception):
                    if not full_answer:
                        yield f"Sorry, the assistant encountered an error: {chunk}. Please try again."
                    break
                full_answer += chunk
                yield chunk
            except queue.Empty:
                continue
    except Exception as exc:
        if not full_answer:
            yield f"Sorry, the assistant encountered an error: {exc}. Please try again."
        return

    conversation_history.append({"role": "user", "content": user_question})
    conversation_history.append({"role": "assistant", "content": full_answer})
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history[:] = conversation_history[-(MAX_HISTORY * 2):]


def _translate_to_urdu(english_text: str) -> str:
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": (
                    "You are a translator. Convert the following English text into "
                    "natural Urdu that a Pakistani farmer would understand. "
                    "Use Urdu script. Keep disease names and product names as-is "
                    "if there is no common Urdu equivalent. "
                    "Do not add explanations — just return the Urdu translation."
                )},
                {"role": "user", "content": english_text}
            ],
            temperature=0.3,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception:
        return english_text


def _translate_to_english(urdu_text: str) -> str:
    try:
        response = client.chat.completions.create(
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
# MAIN CHAT FUNCTION FOR API
# =========================================================
def ask(message: str, context: dict = None) -> str:
    """Main function for API integration.

    Args:
        message: User's message (English or Urdu)
        context: Optional dict with crop, disease, severity from diagnosis

    Returns:
        AI response string
    """
    message_lower = message.lower().strip()
    words = re.split(r'\s+', message_lower)

    greeting_responses = {
        'assalam': ('وعلیکم السلام! میں آپ کی مدد کے لیے حاضر ہوں۔ آپ اپنے فصل کی صحت کے بارے میں کوئی بھی سوال پوچھ سکتے ہیں۔',
                    'Wa-alaikum-as-salam! I\'m here to help. Ask me about your crop\'s health, diseases, or treatments.'),
        'salam': ('وعلیکم السلام! میں آپ کی مدد کے لیے حاضر ہوں۔ آپ اپنے فصل کی صحت کے بارے میں کوئی بھی سوال پوچھ سکتے ہیں۔',
                  'Wa-alaikum-as-salam! I\'m here to help. Ask me about your crop\'s health, diseases, or treatments.'),
        'good morning': ('صبح بخیر! میں آپ کی مدد کے لیے حاضر ہوں۔',
                        'Good morning! How can I help you with your crops today?'),
        'good evening': ('شام بخیر! میں آپ کی مدد کے لیے حاضر ہوں۔',
                        'Good evening! How can I help you with your crops today?'),
        'good afternoon': ('دوپہر بخیر! میں آپ کی مدد کے لیے حاضر ہوں۔',
                          'Good afternoon! How can I help you with your crops today?'),
        'hello': ('ہیلو! میں آپ کی مدد کے لیے حاضر ہوں۔',
                 'Hey there! How can I help you with your crops today?'),
        'hi': ('ہیلو! میں آپ کی مدد کے لیے حاضر ہوں۔',
              'Hey, hi! What can I help you with today?'),
        'hey': ('ہیلو! میں آپ کی مدد کے لیے حاضر ہوں۔',
               'Hey! What can I help you with today?'),
    }
    for keyword, (urdu_resp, english_resp) in greeting_responses.items():
        if keyword in words:
            if len(words) <= 5:
                if _message_language(message) == 'ur':
                    return urdu_resp
                return english_resp
            break

    _initialize()

    interface_lang = _message_language(message)
    if context:
        _update_context_from_request(context)

    urdu_match = None
    is_urdu_input = _is_urdu(message)
    is_roman_urdu_input = _is_roman_urdu(message)

    if is_urdu_input:
        urdu_match = match_urdu_to_knowledge(message)
        urdu_crop = _detect_urdu_crop(message)
        if urdu_match:
            if urdu_match["type"] == "disease":
                conversation_context["crop"] = urdu_crop or urdu_match["crop"]
                conversation_context["disease"] = urdu_match["disease"]
            elif urdu_match["type"] == "pest":
                pest_info = urdu_match["pest_info"]
                if urdu_crop and urdu_crop in pest_info.get("crops_affected", []):
                    conversation_context["crop"] = urdu_crop
                elif not conversation_context["crop"]:
                    conversation_context["crop"] = pest_info.get("crops_affected", [None])[0]
                conversation_context["disease"] = pest_info["pest"]

    search_message = message
    if (is_urdu_input or is_roman_urdu_input) and not urdu_match:
        try:
            search_message = _translate_to_english(message)
        except Exception:
            search_message = message

    search_message = _resolve_pronouns(search_message)

    results = search_dataset(search_message, top_k=3)

    kb_crop = conversation_context.get("crop")
    kb_records = search_knowledge_base(search_message, crop=kb_crop, top_k=3)

    if results:
        best = results[0]
        if best.get("disease"):
            conversation_context["disease"] = str(best["disease"])
        if best.get("crop"):
            conversation_context["crop"] = str(best["crop"])

    return generate_answer(message, results, urdu_match=urdu_match, kb_records=kb_records, interface_lang=interface_lang)


async def ask_stream(message: str, context: dict = None):
    """Streaming version of ask() that yields response chunks.

    Args:
        message: User's message (English or Urdu)
        context: Optional dict with crop, disease, severity from diagnosis

    Yields:
        Response text chunks as they're generated
    """
    message_lower = message.lower().strip()
    words = re.split(r'\s+', message_lower)

    greeting_responses = {
        'assalam': ('وعلیکم السلام! میں آپ کی مدد کے لیے حاضر ہوں۔ آپ اپنے فصل کی صحت کے بارے میں کوئی بھی سوال پوچھ سکتے ہیں۔',
                    'Wa-alaikum-as-salam! I\'m here to help. Ask me about your crop\'s health, diseases, or treatments.'),
        'salam': ('وعلیکم السلام! میں آپ کی مدد کے لیے حاضر ہوں۔ آپ اپنے فصل کی صحت کے بارے میں کوئی بھی سوال پوچھ سکتے ہیں۔',
                  'Wa-alaikum-as-salam! I\'m here to help. Ask me about your crop\'s health, diseases, or treatments.'),
        'good morning': ('صبح بخیر! میں آپ کی مدد کے لیے حاضر ہوں۔',
                        'Good morning! How can I help you with your crops today?'),
        'good evening': ('شام بخیر! میں آپ کی مدد کے لیے حاضر ہوں۔',
                        'Good evening! How can I help you with your crops today?'),
        'good afternoon': ('دوپہر بخیر! میں آپ کی مدد کے لیے حاضر ہوں۔',
                          'Good afternoon! How can I help you with your crops today?'),
        'hello': ('ہیلو! میں آپ کی مدد کے لیے حاضر ہوں۔',
                 'Hey there! How can I help you with your crops today?'),
        'hi': ('ہیلو! میں آپ کی مدد کے لیے حاضر ہوں۔',
              'Hey, hi! What can I help you with today?'),
        'hey': ('ہیلو! میں آپ کی مدد کے لیے حاضر ہوں۔',
               'Hey! What can I help you with today?'),
    }
    for keyword, (urdu_resp, english_resp) in greeting_responses.items():
        if keyword in words:
            if len(words) <= 5:
                if _message_language(message) == 'ur':
                    yield urdu_resp
                else:
                    yield english_resp
                return
            break

    _initialize()

    interface_lang = _message_language(message)
    if context:
        _update_context_from_request(context)

    urdu_match = None
    is_urdu_input = _is_urdu(message)
    is_roman_urdu_input = _is_roman_urdu(message)

    if is_urdu_input:
        urdu_match = match_urdu_to_knowledge(message)
        urdu_crop = _detect_urdu_crop(message)
        if urdu_match:
            if urdu_match["type"] == "disease":
                conversation_context["crop"] = urdu_crop or urdu_match["crop"]
                conversation_context["disease"] = urdu_match["disease"]
            elif urdu_match["type"] == "pest":
                pest_info = urdu_match["pest_info"]
                if urdu_crop and urdu_crop in pest_info.get("crops_affected", []):
                    conversation_context["crop"] = urdu_crop
                elif not conversation_context["crop"]:
                    conversation_context["crop"] = pest_info.get("crops_affected", [None])[0]
                conversation_context["disease"] = pest_info["pest"]

    search_message = message
    if (is_urdu_input or is_roman_urdu_input) and not urdu_match:
        try:
            search_message = _translate_to_english(message)
        except Exception:
            search_message = message

    search_message = _resolve_pronouns(search_message)

    results = search_dataset(search_message, top_k=3)

    kb_crop = conversation_context.get("crop")
    kb_records = search_knowledge_base(search_message, crop=kb_crop, top_k=3)

    if results:
        best = results[0]
        if best.get("disease"):
            conversation_context["disease"] = str(best["disease"])
        if best.get("crop"):
            conversation_context["crop"] = str(best["crop"])

    async for chunk in generate_answer_stream(message, results, urdu_match=urdu_match, kb_records=kb_records, interface_lang=interface_lang):
        yield chunk


def reset_context():
    conversation_context["crop"] = None
    conversation_context["disease"] = None
    conversation_context["severity"] = None
    conversation_history.clear()
