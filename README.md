# Plant Health AI — Professional V6

This build preserves the crop-health product architecture from the earlier interface while rebuilding the presentation layer around a restrained, professional agricultural design system.

## Run locally

```bash
pip install -r requirements.txt
python server.py
```

Open `http://127.0.0.1:8000`.

## What changed

- collapsible desktop sidebar, persisted in local storage;
- deliberately designed deep-forest top navigation;
- cinematic Pakistan-agriculture hero imagery;
- Libre Caslon Display + Manrope typography system;
- warm mineral / parchment canvas with restrained brass accent;
- 2–4px corner geometry rather than rounded SaaS cards;
- photography-first crop gallery;
- sequential looping four-step process stage;
- professional floating AI assistant and restrained message treatment;
- consistent diagnosis, result, disease library and history styling;
- English / Urdu RTL remains supported;
- no initial language gate;
- scientific backend contract remains unchanged.

## Production integration

The included FastAPI backend remains the integration point for the frozen crop disease/severity models and crop-conditioned RAG + Qwen assistant. Demo responses are still placeholders until the model registry and actual checkpoints are wired in.

## Photography

The hero uses free Unsplash agricultural photography including documented Pakistan locations (Punjab, Bahawalpur, Layyah). Crop imagery continues to use Unsplash photography.


## 12-crop mint update

This build is a direct derivative of Professional V6. The layout, component styling, typography, sidebar, topbar, diagnosis flow, camera, disease library, history and chatbot are unchanged. Only the global V6 canvas/background was changed to muted mint green `#E1F0E6`, the visible crop count was updated to 12, and Lemon + Soybean were added to the crop router/library/demo endpoints.

New crop image sources:
- Lemon: https://images.unsplash.com/photo-1724144861106-bbb33df2f50a?auto=format&fit=crop&w=1200&q=84
- Soybean: https://strapi.myplantin.com/large_Depositphotos_309360300_XL_1_866356fe8b.webp


## Verified disease library extension

This build adds 75 model-class disease/condition cards across 12 crops. Opening a card shows a disease reference image, appearance, immediate field action, prevention/IPM, fertilizer/nutrition guidance, Pakistan pesticide/chemical guidance, thresholds where available, and source links. See `DISEASE_LIBRARY_VERIFICATION.md`.

## Verified disease-detail extension (2026-09-01)
The Disease Library now contains 75 model disease/condition cards. Each card opens a verified detail drawer with disease appearance, disease-specific reference imagery when a sufficiently matched Wikimedia Commons image is available, IPM/treatment, nutrition guidance, conservative Pakistan pesticide guidance, and source links. Generic crop photos are never substituted as disease evidence. See `DISEASE_LIBRARY_VERIFICATION.md`.


## Deep verified disease library + Urdu fix

This build deepens all 75 disease/condition detail cards, reduces repetitive source/chemical text, strengthens disease-image matching, and fixes disease-card opening in Urdu/RTL mode. A DOM interaction audit opened all 75 cards successfully in English and all 75 in Urdu. See `DEEP_DISEASE_LIBRARY_VERIFICATION_PK.md` and `URDU_DISEASE_CARD_TEST.json`.

Pakistan chemical guidance is intentionally conservative: IPM first, no pesticide dose/PHI/REI/tank-mix instructions, current DPP crop/target label required, and banned pesticides excluded. Healthy predictions always force severity to N/A.


## Reference-image update
Disease drawers now use curated exact Wikimedia Commons files when available and a stricter disease/pathogen-specific Commons resolver for every remaining model class. The matching algorithm now uses the full scientific image query rather than only the short UI label. See `REFERENCE_IMAGE_POLICY.md`.


## Real model runtime integration

See `MODEL_INTEGRATION_STATUS.md`. Run `python tools/verify_models.py` before launch. The diagnosis endpoint no longer generates demo/fallback predictions.

## Runtime parity audit

`tools/verify_models.py` verifies that checkpoint files load and have the expected output shape. It does not measure semantic accuracy. Use the parity auditor for checkpoint metadata, out-of-distribution behavior, labeled external images, and local-vs-deployed website comparisons:

```bash
python tools/runtime_parity_auditor.py --crops apple corn cotton tomato peas
python tools/runtime_parity_auditor.py \
  --samples-csv tools/parity_samples.example.csv \
  --endpoint http://127.0.0.1:8000 \
  --json-out parity_report.json
```

Copy `tools/parity_samples.example.csv`, replace its example rows with real labeled image paths, and keep those images outside all training, validation, and official test populations.

The runtime defaults to a one-model LRU cache (`CDCNSA_MAX_CACHED_MODELS=1`) because small Render instances cannot retain multiple CNN checkpoints safely. Disease and severity inference are serialized, and checkpoint tensor payloads are discarded immediately after their weights are copied into the model.
