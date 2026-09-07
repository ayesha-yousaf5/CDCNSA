# CDCNSA — Crop Disease Classification and Severity Analysis

CDCNSA is a crop-health assistant for farmers and agriculture users in Pakistan.
It analyzes crop images, identifies possible diseases, estimates severity when
available, and provides practical guidance in English and Urdu.

## Features

- Crop disease classification from uploaded or camera images
- Disease severity analysis
- English and Urdu interface with Urdu RTL support
- AI farmer chatbot for crop-health questions
- English, Urdu, and Roman Urdu chatbot input
- Voice input and text-to-speech support
- Disease reference library with symptoms, management, prevention, and sources
- Diagnosis history and mobile-friendly interface
- Safe uncertainty handling instead of fabricated predictions

## Supported crops

The current interface provides these ten crop diagnosis cards:

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

## Models

The project uses crop-specific disease and severity classifiers. The supported
architectures include:

- **ResNet50**
- **EfficientNet-B0**
- **MobileNetV3-Large**
- **DenseNet121**

Each model is configured through [model_registry.json](model_registry.json),
which defines its crop, task, architecture, image size, class mapping,
normalization, confidence thresholds, and checkpoint path.

Model files are kept outside Git because of their size. During deployment,
`download_models.py` downloads the required model archives from Google Drive and
validates the extracted checkpoints.

## Local setup

### Requirements

- Python 3.10+
- PyTorch and torchvision
- A Windows, Linux, or macOS environment

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the local server:

```powershell
python server.py
```

Open the application:

```text
http://127.0.0.1:8000
```

If models are stored outside the repository, configure the model root:

```powershell
$env:CDCNSA_MODEL_ROOT="D:\hacathon\website deployment\CDCNSA"
python server.py
```

## Model verification

Run the deep model contract check before deployment:

```powershell
python tools\verify_models.py
```

The check verifies checkpoint presence, architecture compatibility, class
mapping, state-dict loading, and output shape. A successful contract check does
not replace accuracy testing on independent real crop images.

The same check is available through the API:

```text
http://127.0.0.1:8000/api/models/status?deep=true
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check server health |
| GET | `/api/models/status` | Show model availability |
| GET | `/api/models/status?deep=true` | Load and validate enabled models |
| POST | `/api/diagnose` | Classify a crop image |
| POST | `/api/chat` | Ask the farmer assistant |
| POST | `/api/chat/stream` | Stream an assistant response |
| POST | `/api/tts` | Generate voice output |
| POST | `/api/chat/reset` | Reset chatbot context |

## Diagnosis safety

The backend:

- rejects empty, tiny, near-uniform, and obvious non-crop images;
- uses crop-specific confidence and top-1/top-2 margin thresholds;
- returns `Uncertain` when a prediction is ambiguous;
- skips severity when disease confidence is insufficient;
- skips severity for healthy results;
- returns `N/A` when severity is unavailable or abstained;
- fails closed when a required model is missing or invalid.

The image gate is a conservative heuristic, not a trained crop/leaf
out-of-distribution detector. Real labeled field images are required to measure
disease accuracy and calibrate thresholds.

## Chatbot and knowledge base

The chatbot combines local retrieval with a hosted language model. The checked-in
knowledge base is:

```text
Plant_Health_AI_Knowledge_Base_Final/rag/plant_health_rag_knowledge.jsonl
```

It contains structured crop-health knowledge used for disease explanations,
prevention, management, and farmer guidance. Chat responses are instructed to
follow the language of the user:

- English question → English answer
- Urdu question → Urdu answer
- Roman Urdu question → Urdu answer

## Deployment

The project is deployed as a FastAPI application on Render. Model binaries are
downloaded during the Render build rather than committed to GitHub.

The deployment downloader:

1. Downloads the project disease/severity model archive.
2. Downloads the Eggplant/Brinjal and Cucumber model archive.
3. Extracts both archives using safe path validation.
4. Verifies that required checkpoints exist.
5. Verifies protected SHA256 hashes where configured.

After changing model archive links or deployment logic, redeploy Render and
verify:

```text
/api/health
/api/models/status?deep=true
```

## Important project files

- [server.py](server.py) — FastAPI application and API routes
- [app.js](app.js) — frontend behavior and API integration
- [model_registry.json](model_registry.json) — model contracts and routing
- [inference/runtime.py](inference/runtime.py) — inference and safety logic
- [inference/preprocess.py](inference/preprocess.py) — image decoding and transforms
- [inference/registry.py](inference/registry.py) — checkpoint lookup and hashing
- [download_models.py](download_models.py) — deployment model download
- [tools/verify_models.py](tools/verify_models.py) — deep model verification
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) — detailed project history and status

## Current limitations

- Model loading proves structural compatibility, not real-world accuracy.
- Accuracy still requires independent labeled images for every crop and disease.
- The image rejection gate is not a trained OOD classifier.
- Confidence thresholds need calibration with field data.
- Some severity classifiers require further validation.


## Recommended validation before release

1. Run the deep model verification locally.
2. Test real labeled images for every supported crop.
3. Test logos, documents, screenshots, people, and unrelated objects.
4. Record disease correctness, severity correctness, confidence, and response time.
5. Redeploy Render only after local and deployment checks pass.
