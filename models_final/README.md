# CDCNSA final models

One folder per crop in the app's layout (`models/<crop>/disease/...`). Each folder holds the model file,
`registry_snippet.json` (paste its "disease" block into `model_registry.json`) and `final_report.json`.
Model files are copied in by running **COPY_MODELS.bat** (double-click) - it also applies the cucumber fix below.

`.pt` = torchvision model (`runtime_kind: classification`), `.ts` = DINOv2 TorchScript (`runtime_kind: torchscript`) - the app loads both.

| Crop | Model | Classes | Verdict | Never-seen test results |
|---|---|---|---|---|
| cotton | ResNet50 `.pt` | 7 | approved | Pakistan CoSEV leaf curl 81%, healthy 100%; S. Punjab healthy 98% |
| corn | DenseNet121 `.pt` | GLS, NLB, healthy | WEAK (PlantDoc 0.66) | Pakistan: GLS 100%, healthy 84% |
| apple | DINOv2 `.ts` | 5 | PASS (0.80) | Kashmir: Alternaria 97%, Mosaic 100%, healthy 100%; Pakistan healthy 100% |
| tomato | DINOv2 `.ts` | 5 | WEAK (PlantDoc 0.56) | Pakistan: healthy 100%, Bact. spot 100%, TYLCV 99%, Early blight 91%, Late blight 83% |
| mango | DINOv2 `.ts` | 8 | PASS (0.88) | Pabna/Savar held-out source 88% |
| grape | DINOv2 `.ts` | 6 | PASS (0.78) | Pakistan: healthy 100%, downy 91%, powdery 69%; GVLID field: black rot 91%, esca 79%, leaf blight 64% |
| eggplant | EfficientNet-B0 `.pt` | 9 | PASS (0.74) | held-out source 75% |
| cucumber | ResNet50 `.pt` | Anthracnose, Downy, healthy | PASS (0.88) | Kazakhstan diseased leaves flagged only 45% -> confidence fix applied, keep Qwen hybrid |
| rice | DINOv2 `.ts` | 6 (BLB, Brown Spot, Leaf Scald, Blast, Tungro, Sheath Blight) | PASS (0.76) | held-out source accuracy 86% (answered 94%) |

Not trained (Qwen handles them): peas (existing old model only - trained on pod photos), dropped classes listed in each final_report.json.
Cucumber fix: its calibration hit the 0.05 limit (every answer ~100% confident); `fix_cucumber_temperature.py` restores the raw model.

## Severity (one model for every crop)

`severity/lesion_seg_unet_r34.ts` - U-Net ResNet34 lesion segmentation trained on PlantSeg (copy it in with **COPY_SEVERITY_MODEL.bat**).
Severity % = diseased area / leaf area -> MILD <10%, MODERATE 10-30%, SEVERE >30%. The app shows the band **and** the % of leaf.

| Check | Result |
|---|---|
| PlantSeg test (2,295 unseen photos) | IoU 0.65, Dice 0.79 |
| Per crop IoU | corn 0.73, eggplant 0.65, grape 0.64, apple 0.61, cucumber 0.58, tomato 0.57, citrus 0.54, rice 0.42 |
| Band vs expert masks (1,000 photos) | 77% same band, mean error 8.1 % points |
| Cotton (never trained on) | over-estimates bacterial blight (exact band 29%, within one band 79%) |

App rules: runs only after a confident, non-healthy diagnosis; "validated" for apple/corn/cucumber/eggplant/grape/tomato,
"approx." for rice/cotton/mango/peas; virus, wilt and pest damage are measured but marked "approx."; an unconfirmed disease still gets the measured %; leaf not visible -> no severity.
If the model file is missing, the app falls back to its old severity source (Qwen-VL estimate).

Rice is connected (model_registry.json -> models_final/rice/disease/rice_disease_dinov2_srcsplit.ts).
