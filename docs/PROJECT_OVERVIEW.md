# CDCNSA Project Overview

## 1. Project identity

**CDCNSA** means **Crop Disease Classification and Severity Analysis**.

The project is a farmer-focused plant-health system for Pakistan. It helps users
upload or capture a crop image, identify a possible disease, estimate severity
when supported, and receive practical guidance.

The interface is designed for:

- Pakistani farmers and agriculture students;
- English and Urdu users;
- simple mobile-friendly diagnosis workflows;
- farmer-friendly explanations instead of raw machine-learning output.

## 2. Main product features

### Crop diagnosis

The user:

1. Selects a crop.
2. Uploads an image or captures one with the camera.
3. Sends it to the FastAPI diagnosis endpoint.
4. Receives disease, confidence, healthy/uncertain status, and severity when
   available.

The backend does not invent a diagnosis when a model is missing, invalid, or
uncertain. It fails closed or returns `Uncertain`.

### Disease library

The website includes disease and condition cards with appearance, management,
prevention/IPM, nutrition guidance, reference images, and source links.

### English and Urdu interface

The interface supports English and Urdu, including Urdu right-to-left layout.
Diagnosis results and guidance are rendered according to the selected language.

### AI farmer assistant

The chatbot supports:

- crop and disease questions;
- explanations of diagnosis results;
- severity and next-step guidance;
- English, Urdu, and Roman Urdu input handling;
- voice input/output integration;
- local retrieval from the structured plant-health knowledge base.

The checked-in knowledge base contains 186 JSONL records. The chatbot uses
retrieved local context and a hosted language model for response generation.

## 3. Crop coverage

The current interface provides these 10 crops:

1. Corn/Maize
2. Cotton
3. Tomato
4. Apple
5. Rice
6. Mango
7. Grape
8. Eggplant/Brinjal
9. Cucumber
10. Peas

## 4. Current model architecture

The project uses CNN models selected for the crop and task:

- ResNet50 for several disease and severity classification tasks;
- EfficientNet-B0 for disease and severity classification tasks;
- MobileNetV3-Large for lightweight disease and severity tasks;
- DenseNet121 for Cucumber severity analysis.

The model registry preserves the exact architecture, class mapping, image size,
normalization, and confidence rules for each crop. Crop classes are never
substituted across unrelated crops.

## 5. Model selection and validation

The repository contains a model registry that defines, for every crop/task:

- checkpoint path;
- architecture;
- image size;
- class-to-index mapping;
- normalization values;
- enabled state;
- confidence and margin thresholds;
- optional SHA256 protection.

Before inference, the runtime validates the checkpoint structure and output
shape. The deep verification command is:

```powershell
python tools\verify_models.py
```

The API equivalent is:

```text
/api/models/status?deep=true
```

A successful structural check proves that the model can load and execute. It
does **not** prove disease accuracy on real field images.

## 6. Safety and uncertainty behavior

The runtime now:

- rejects empty, tiny, or near-uniform images;
- rejects obvious non-crop graphics such as dark logos;
- applies crop-specific confidence thresholds;
- applies top-1/top-2 confidence-margin thresholds;
- returns `Uncertain` for ambiguous disease predictions;
- skips severity when disease is uncertain;
- skips severity for healthy predictions;
- abstains from low-confidence severity predictions;
- does not claim healthy for models without a healthy class;
- exposes actual model errors instead of returning demo answers.

The basic image gate is a conservative heuristic. It is not a trained
leaf/crop out-of-distribution classifier. Real negative images and labeled field
images are still required for proper accuracy and OOD evaluation.

## 7. Backend and frontend structure

### Frontend

- `index.html` — application shell;
- `app.js` — crop selection, upload/camera flow, diagnosis requests, result
  rendering, chatbot interaction, language behavior, and history;
- `styles.css` — responsive agricultural interface and Urdu RTL styling.

### Backend

- `server.py` — FastAPI application and API routes;
- `inference/runtime.py` — model loading and prediction;
- `inference/registry.py` — registry lookup and checkpoint hashing;
- `inference/preprocess.py` — image decoding and normalization;
- `inference/architectures.py` — supported torchvision model constructors;
- `model_registry.json` — model contract and routing configuration;
- `chatbot/` — retrieval, language detection, generation, and voice services.

Important endpoints:

```text
GET  /api/health
GET  /api/models/status
GET  /api/models/status?deep=true
POST /api/diagnose
POST /api/chat
POST /api/chat/stream
POST /api/tts
```

## 8. Deployment model delivery

Model binaries are not stored in GitHub. Render downloads the project model
archives from Google Drive during deployment:

1. Disease and severity model archive
   - Approved disease classification checkpoints;
   - Approved severity classification checkpoints.

2. Crop model archive
   - Eggplant/Brinjal disease and severity checkpoints;
   - Cucumber disease and severity checkpoints.

`download_models.py` downloads, safely extracts, and validates these archives.
The old all-crops archive is no longer required.

## 9. Memory and Render reliability work

Render previously experienced worker crashes during first model loading.
The runtime was adjusted to:

- use one cached model by default;
- serialize inference;
- limit PyTorch CPU threads;
- load checkpoint weights with memory-saving behavior;
- discard temporary checkpoint state after model construction;
- load disease and severity lazily.

This reduces peak memory use on small Render instances.

## 10. Work completed so far

- Audited frontend, backend, model registry, inference, chatbot, and deployment
  integration.
- Removed silent demo diagnosis behavior.
- Added real checkpoint loading and contract validation.
- Added external model-root support for local testing.
- Added English, Urdu, and Roman Urdu chatbot language handling.
- Added direct photo guidance for common photo questions.
- Fixed stale disease context and repetitive chatbot retrieval behavior.
- Restored a verified hosted chatbot model identifier.
- Added non-crop image rejection and confidence/margin abstention.
- Added memory-safe inference behavior for Render.
- Integrated the approved disease and severity checkpoints for the supported
  crops.
- Preserved the Brinjal and Cucumber model integrations.
- Created separate Google Drive archives for the project model checkpoints.
- Updated the deployment downloader to use the two new archive IDs.
- Tested local health, model status, deep model loading, non-crop rejection, and
  fallback routing.
- Committed and pushed the integration changes to GitHub.

Recent commits include:

- `79fda0a` — Integrate crop disease models
- `b8fa693` — Use split model archives for deployment

## 11. Current limitations

- Structural model validation is not the same as real-world accuracy validation.
- No complete independent labeled field-image benchmark is currently attached.
- Confidence thresholds require calibration per crop and dataset.
- The heuristic image gate is not a trained OOD model.
- Some severity models have weaker validation performance than the disease
  models.
- Combined model support does not automatically mean that every prediction is
  biologically correct; real labeled testing is still necessary.
- Hosted chatbot response time depends on retrieval and external model latency.

## 12. Recommended next steps

1. Redeploy the pushed branch on Render.
2. Confirm both Google Drive archives are shared as accessible files.
3. Test `/api/health` and `/api/models/status?deep=true` after deployment.
4. Test real labeled images for every supported crop.
5. Test negative images: logos, documents, people, screenshots, and unrelated
   objects.
6. Record confidence, margin, disease correctness, severity correctness, and
   response time.
7. Calibrate crop-specific thresholds using the independent test set.
8. Add a trained crop/leaf OOD classifier if production-level rejection is
   required.
