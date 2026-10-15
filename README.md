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

## Supported crops and models

Ten crops, listed strongest model first. Every disease model was trained on Kaggle/Colab
(`training/`) and tested on photos from **sources it never saw during training**
(source-held-out test, macro-F1). Full numbers: [models_final/README.md](models_final/README.md).

| Crop | Model | Detects | Held-out-source result |
|---|---|---|---|
| Cotton | ResNet50 | 6 classes | approved (Pakistan photos) |
| Mango | DINOv2 ViT-S/14 | 7 | 0.88 |
| Apple | DINOv2 | 4 | 0.80 |
| Grape | DINOv2 | 5 | 0.78 |
| Rice | DINOv2 | 6 | 0.76 |
| Eggplant / Brinjal | EfficientNet-B0 | 8 | 0.74 |
| Cucumber | ResNet50 | 2 | 0.88 (weak on outside field photos) |
| Corn / Maize | DenseNet121 | 2 | 0.66 (weak) |
| Tomato | DINOv2 | 4 | 0.56 (weak) |
| Peas | ResNet50 (previous model) | 4 | not retrained |

**Severity:** one U-Net (ResNet34) lesion-segmentation model for all crops, trained on
PlantSeg. Severity = diseased area / leaf area; Mild < 10%, Moderate 10-30%, Severe > 30%.
PlantSeg test IoU 0.65, Dice 0.79; band agrees with expert masks on 77% of photos.

**Second opinion:** Qwen vision model (Groq) checks "is this a plant / the selected crop" and
gives a second diagnosis. If it is busy or offline, the trained models answer on their own.

Each model is configured in [model_registry.json](model_registry.json) (crop, architecture,
classes, thresholds, checkpoint path). Model files (`*.pt`, `*.ts`, `*.pth`) are too large
for GitHub; they live in `models_final/` locally (see its README for the copy scripts).

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

Each browser tab is its own conversation (`session_id`), so two users never share chat memory.

## Deployment

Target: Render (`render.yaml`, `python server.py`) or another Python host.
Set `GROQ_API_KEY` (chatbot) and optionally `GROQ_VISION_API_KEY` (photo check) as environment
variables. The trained model files are not in GitHub; without them the app still runs, using the
Qwen photo check and the severity model where available. After deploying, verify:

```text
/api/health
/api/models/status?deep=true
```

## Project structure

```text
CDCNSA-main/
├── server.py                  FastAPI app: website + /api routes
├── index.html  app.js  styles.css   website (UI, disease library, chat panel)
├── model_registry.json        which model each crop uses, classes, thresholds, severity model
├── requirements.txt           pip install -r requirements.txt
├── .env                       GROQ_API_KEY (never commit)
├── inference/                 photo diagnosis
│   ├── runtime.py             crop model -> disease -> severity, uncertainty gates
│   ├── severity_seg.py        lesion-segmentation severity (% of leaf area)
│   ├── vlm.py                 Qwen vision check (plant? right crop? second opinion)
│   └── preprocess.py, registry.py, architectures.py, errors.py
├── chatbot/                   Kisan Dost chatbot
│   ├── chat_service.py        language detection, crop/disease memory, retrieval, Groq call
│   ├── app_disease_library.json   the website's Disease Library (exported, used first by the chatbot)
│   ├── disease_knowledge.py   extra disease / pest / product knowledge
│   ├── knowledge_base_loader.py   search over Plant_Health_AI_Knowledge_Base_Final
│   ├── hf_dataset/            55k plant-disease Q&A pairs
│   └── voice_service.py       text-to-speech
├── Plant_Health_AI_Knowledge_Base_Final/   crop knowledge base (rag/*.jsonl)
├── models_final/              final trained models: <crop>/disease/, severity/
├── training/                  Kaggle/Colab notebooks (*_FINAL.ipynb) + results/
├── tools/                     verify_models.py, test_severity.py, export_library_for_chatbot.js, ...
├── docs/                      project notes and verification reports
```

After editing the Disease Library in `app.js`, run `node tools/export_library_for_chatbot.js`
so the chatbot uses the same text.

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
