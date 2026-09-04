# Plant Health AI — Model Runtime Integration Status

This build uses the approved polished 12-crop website codebase. The current diagnosis UI exposes 10 crops; Lemon and Soybean remain hidden and disabled because their checkpoint binaries are unavailable.

## What is now real

- `/api/diagnose` routes to real PyTorch checkpoints through `model_registry.json`.
- There is **no frontend or backend demo diagnosis fallback**. If a disease checkpoint is absent, diagnosis fails closed with `model_unavailable`.
- Models load lazily on first use and choose CUDA when available, otherwise CPU.
- Checkpoint SHA256 is enforced when a protected hash is available.
- Checkpoint/classifier output count and state-dict architecture are checked before inference.
- Healthy predictions skip severity and return `N/A`.
- Low-confidence disease predictions return `Uncertain`, hide the candidate label, and skip severity. A low-confidence `healthy` candidate cannot override uncertainty.
- Degenerate, near-uniform images fail closed before model inference.
- Obvious non-crop graphics (such as dark, low-color logos) fail closed before model inference.
- Disease predictions now require both a crop-specific confidence threshold and a top-1/top-2 probability margin.
- Crops whose checkpoints do not contain a healthy class cannot claim healthy; unknown/uncertain handling still requires a separately trained OOD or healthy classifier.
- Low-confidence severity can abstain to `N/A`.
- `/api/models/status?deep=true` performs a deserialization/contract load check.

## Model delivery and active runtime

Model binaries are intentionally excluded from Git. `download_models.py` downloads the shared Google Drive `models.tar.gz` archive during deployment and then verifies that every enabled classification checkpoint is present and every protected hash matches.

| Crop | Task | Architecture | Status |
|---|---|---|---|
| Corn | Disease | EfficientNet-B0 | enabled |
| Corn | Severity | lesion-area/abstention contract | runtime not attached; disabled |
| Cotton | Disease / Severity | MobileNetV3-Large | enabled |
| Tomato | Disease | EfficientNet-B0 | enabled as a single model; frozen three-model ensemble is not deployed |
| Tomato | Severity | MobileNetV3-Large | enabled |
| Apple | Disease | ResNet50 | enabled |
| Apple | Severity | MobileNetV3-Large | enabled |
| Rice | Disease / Severity | ResNet50 / EfficientNet-B0 | enabled |
| Mango | Disease / Severity | EfficientNet-B0 / ResNet50 | enabled |
| Grape | Disease / Severity | ResNet50 / MobileNetV3-Large | enabled |
| Eggplant | Disease / Severity | ResNet50 / ResNet50 | enabled |
| Cucumber | Disease / Severity | ResNet50 / DenseNet121 | enabled |
| Peas | Disease / Severity | ResNet50 / ResNet50 | enabled |
| Lemon | Disease / Severity | — | no binaries; disabled |
| Soybean | Disease / Severity | — | no binaries; disabled |

## Known limitations

- A checkpoint load and dummy-forward pass proves structural compatibility, not real-image accuracy.
- The global disease threshold (`0.55`) and severity threshold (`0.40`) are not per-crop calibrated open-set thresholds.
- The basic uniform-image rejection is not a trained leaf/crop/out-of-distribution detector.
- Tomato's recorded frozen three-model ensemble rule is not implemented by the active single-EfficientNet runtime.
- Several severity checkpoints have weak validation Macro-F1 and must not be described as production-ready.
- The deployment uses a one-model LRU cache by default; retaining every lazily loaded CNN caused Render 502/process restarts during disease-plus-severity requests.
- Use `tools/runtime_parity_auditor.py` with independent labeled field images and the deployed endpoint before accepting a crop.

## Files that make the models work

- `model_registry.json` — crop/task router, exact checkpoint path, architecture, image size, classes, normalization, hashes and safety thresholds.
- `inference/architectures.py` — torchvision model constructors and classifier-head replacement.
- `inference/preprocess.py` — image decoding, EXIF orientation, RGB conversion, resize and normalization.
- `inference/registry.py` — registry and SHA256 verification.
- `inference/runtime.py` — lazy loading, checkpoint-contract validation, softmax inference, healthy/uncertainty/severity gates.
- `tools/verify_models.py` — deep load + dummy-forward validation for every enabled checkpoint.
- `tools/runtime_parity_auditor.py` — metadata, OOD, labeled-image and local-vs-endpoint parity audit.
- `models/<crop>/<task>/evidence/` — preserved machine-readable class maps/configs where available.

## Completion procedure for a missing model

1. Put the exact frozen checkpoint in the registry path.
2. Confirm the exact architecture, class-to-index mapping, image size and normalization.
3. Add/verify SHA256 where available.
4. Set `enabled: true`.
5. Run `python tools/verify_models.py`.
6. Only then expose that crop as a working visual diagnosis route.

RAG + Qwen remains a separate next integration boundary; this build focuses on making the vision model router real without changing the approved polished UI.
