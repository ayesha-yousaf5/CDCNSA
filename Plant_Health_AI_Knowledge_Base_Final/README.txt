PLANT HEALTH AI - 12 CROP FARMER KNOWLEDGE BASE

Contents
- docx/: master guide + 12 human-readable crop handbooks
- markdown/: RAG-friendly versions
- rag/plant_health_rag_knowledge.jsonl: structured retrieval records
- source_catalog/authoritative_sources.csv: source links

Critical rules
1. Model coverage and knowledge coverage are different.
2. healthy -> severity N/A.
3. Knowledge-only topics are never visual-model diagnoses.
4. Do not index official ML TEST data into chatbot development knowledge.
5. Do not invent pesticide dose, PHI, REI, tank mix, or legal use.
6. Verify current Pakistan pesticide registration and the exact product label.
7. Use IPM and economic thresholds before chemical advice where possible.
