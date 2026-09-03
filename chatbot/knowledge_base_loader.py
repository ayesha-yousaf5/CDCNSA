"""
Knowledge base loader for CDCNSA knowledge base.

Loads JSONL RAG data and provides TF-IDF search over topics and symptoms.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "Plant_Health_AI_Knowledge_Base_Final" / "rag" / "plant_health_rag_knowledge.jsonl"

_knowledge_records: List[Dict] = []
_topic_vectors = None
_vectorizer: Optional[TfidfVectorizer] = None
_initialized = False


def _initialize():
    """Load JSONL and build TF-IDF index."""
    global _initialized, _knowledge_records, _topic_vectors, _vectorizer

    if _initialized:
        return

    if not KNOWLEDGE_BASE_PATH.exists():
        print(f"Warning: Knowledge base not found at {KNOWLEDGE_BASE_PATH}")
        _initialized = True
        return

    print("Loading plant health knowledge base...")
    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                _knowledge_records.append(json.loads(line))

    print(f"Loaded {len(_knowledge_records)} knowledge records")

    # Build search index over topic + symptoms
    search_texts = []
    for record in _knowledge_records:
        topic = record.get("topic", "")
        symptoms = " ".join(record.get("symptoms", []))
        crop = record.get("crop", "")
        search_texts.append(f"{crop} {topic} {symptoms}")

    _vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))
    _topic_vectors = _vectorizer.fit_transform(search_texts)

    print("Knowledge base search index ready")
    _initialized = True


def search_knowledge_base(query: str, crop: Optional[str] = None, top_k: int = 3) -> List[Dict]:
    """Search the knowledge base for relevant records.

    Args:
        query: User's question
        crop: Optional crop filter
        top_k: Number of results to return

    Returns:
        List of matching records with similarity scores
    """
    _initialize()

    if not _knowledge_records or _topic_vectors is None:
        return []

    user_vector = _vectorizer.transform([query])
    similarities = cosine_similarity(user_vector, _topic_vectors)[0]

    # Boost records matching the crop if specified
    if crop:
        crop_lower = crop.lower()
        for i, record in enumerate(_knowledge_records):
            record_crop = record.get("crop", "").lower()
            if crop_lower in record_crop or record_crop in crop_lower:
                similarities[i] += 0.15

    top_indexes = similarities.argsort()[-top_k:][::-1]

    results = []
    for index in top_indexes:
        score = similarities[index]
        if score < 0.05:
            continue
        record = _knowledge_records[index].copy()
        record["score"] = float(score)
        results.append(record)

    return results


def format_knowledge_context(records: List[Dict]) -> str:
    """Format knowledge base records into context string for LLM."""
    if not records:
        return ""

    parts = []
    parts.append("\n=== PLANT HEALTH KNOWLEDGE BASE ===")

    for i, record in enumerate(records, 1):
        parts.append(f"\n--- Record {i} (relevance: {record.get('score', 0):.2f}) ---")
        parts.append(f"Crop: {record.get('crop', 'N/A')}")
        parts.append(f"Topic: {record.get('topic', 'N/A')}")
        parts.append(f"Category: {record.get('category', 'N/A')}")

        if record.get("symptoms"):
            parts.append(f"Symptoms:")
            for s in record["symptoms"]:
                parts.append(f"  - {s}")

        if record.get("risk_factors"):
            parts.append(f"Risk factors:")
            for r in record["risk_factors"]:
                parts.append(f"  - {r}")

        if record.get("immediate_actions"):
            parts.append(f"Immediate actions:")
            for a in record["immediate_actions"]:
                parts.append(f"  - {a}")

        if record.get("prevention_ipm"):
            parts.append(f"Prevention (IPM):")
            for p in record["prevention_ipm"]:
                parts.append(f"  - {p}")

        if record.get("chemical_decision_support"):
            parts.append(f"Chemical decision support:")
            for c in record["chemical_decision_support"]:
                parts.append(f"  - {c}")

        if record.get("low_cost_options"):
            parts.append(f"Low-cost options:")
            for l in record["low_cost_options"][:3]:
                parts.append(f"  - {l}")

        if record.get("escalation"):
            parts.append(f"Escalation:")
            for e in record["escalation"][:2]:
                parts.append(f"  - {e}")

        if record.get("safety"):
            parts.append(f"Safety: {record['safety']}")

    parts.append("\n=== END KNOWLEDGE BASE ===\n")
    return "\n".join(parts)
