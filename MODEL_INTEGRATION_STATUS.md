# Plant Health AI — Model Runtime Integration Status

This build uses the approved polished 12-crop website as its UI base. The neural-tree variant is not used.

## What is now real

- `/api/diagnose` routes to real PyTorch checkpoints through `model_registry.json`.
- There is **no frontend or backend demo diagnosis fallback**. If a disease checkpoint is absent, diagnosis fails closed with `model_unavailable`.
- Models load lazily on first use and choose CUDA when available, otherwise CPU.
- Checkpoint SHA256 is enforced when a protected hash is available.
- Checkpoint/classifier output count and state-dict architecture are checked before inference.
- Healthy predictions skip severity and return `N/A`.
- Low-confidence disease predictions skip severity.
- Low-confidence severity can abstain to `N/A`.
- `/api/models/status?deep=true` performs a deserialization/contract load check.

## Binary checkpoints physically attached in this ZIP

| Crop | Task | Architecture | Status |
|---|---|---|---|
| Apple | Disease | EfficientNet-B0 | attached + enabled |
| Apple | Severity | DenseNet121 | attached + enabled; 224px input should be cross-checked against original Apple severity training code |
| Grape | Disease | ResNet50 | attached + enabled |
| Mango | Severity | ResNet50 | attached + enabled |
| Rice | Severity | EfficientNet-B0 | attached + enabled |

Mango/Rice diagnosis still fails closed because their **disease** binaries are not physically present in the active runtime. Grape can return disease and will return severity `N/A` until its severity checkpoint is mounted. Apple is the only crop in this build with both disease and severity binaries physically attached.

## Prepared but not enabled model slots

The registry/folder contracts are already prepared for Corn, Cotton, Tomato, Rice disease, Mango disease, Grape severity, Eggplant/Brinjal, Cucumber, Peas, Lemon and Soybean. Their historical/training evidence can be searchable while the actual binary payload is not exposed to this runtime; therefore the package does not pretend those checkpoint bytes are present.

For Corn, the final severity slot is deliberately marked `lesion_area_abstention`; it must not be replaced by an experimental generic severity classifier.

## Files that make the models work

- `model_registry.json` — crop/task router, exact checkpoint path, architecture, image size, classes, normalization, hashes and safety thresholds.
- `inference/architectures.py` — torchvision model constructors and classifier-head replacement.
- `inference/preprocess.py` — image decoding, EXIF orientation, RGB conversion, resize and normalization.
- `inference/registry.py` — registry and SHA256 verification.
- `inference/runtime.py` — lazy loading, checkpoint-contract validation, softmax inference, healthy/uncertainty/severity gates.
- `tools/verify_models.py` — deep load + dummy-forward validation for every enabled checkpoint.
- `models/<crop>/<task>/evidence/` — preserved machine-readable class maps/configs where available.

## Completion procedure for a missing model

1. Put the exact frozen checkpoint in the registry path.
2. Confirm the exact architecture, class-to-index mapping, image size and normalization.
3. Add/verify SHA256 where available.
4. Set `enabled: true`.
5. Run `python tools/verify_models.py`.
6. Only then expose that crop as a working visual diagnosis route.

RAG + Qwen remains a separate next integration boundary; this build focuses on making the vision model router real without changing the approved polished UI.
