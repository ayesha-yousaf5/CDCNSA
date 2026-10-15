# CDCNSA — Kaggle training kit (overfit-safe)

11 notebooks: one disease classifier per crop + one severity model. Everything downloads **inside Kaggle**; nothing goes to your laptop except the small finished model files.

## Dataset check (done before release)
Every Mendeley/OSF/Hugging Face source used by corn, rice, tomato, apple and mango was opened file-by-file (zip directory read remotely) and every real folder name was run through the label rules before these notebooks were handed over.

## Run a notebook (same steps for every file)
1. kaggle.com → **Create → New Notebook**.
2. **File → Import Notebook** → upload e.g. `01_corn_disease.ipynb`.
3. Right panel → **Session options**:
   - **Accelerator: GPU T4 x2** (or P100)
   - **Internet: On** (needs a phone-verified account)
4. **Run All** (or *Save Version → Save & Run All* so it keeps running after you close the tab — recommended).
5. When it finishes, scroll to the bottom and **copy the FINAL REPORT block** + the **"ORIGINAL, DE-DUPLICATED IMAGES PER SOURCE x CLASS"** table and the **DOWNLOAD STATUS** and send them to Claude.
6. Output panel → download `cdcnsa_<crop>_export.zip` (16–95 MB: the model file + `registry_snippet.json` + `final_report.json`).

Kaggle gives ~30 GPU hours/week; each disease notebook takes ~30–90 min. You can run 2 notebooks at the same time.

## Order (most important / best data first)
| # | Notebook | Train sources | Held-out test source |
|---|---|---|---|
| 01 | Corn | Common Rust, Gray Leaf Spot, Northern Leaf Blight, Healthy: half of PlantCity Pakistan (GLS + healthy), CD&S Dataset_Original (Purdue), Bangladesh corn, Bangladesh multi-format (RAW_Image), PlantVillage corn capped at 300/class (only large rust source) | PlantDoc corn + other half of PlantCity Pakistan |
| 02 | Cotton | SAR-CLD-2024 (Data in Brief 2024; its 7 classes) **+ half of CoSEV's Pakistani leaf-curl/healthy photos** (incl. leaf enation) | Cotton severity-levels set + real-world Pakistan tests: Southern Punjab field set (all) and the other half of CoSEV |
| 03 | Rice | Sambalpur/Odisha (Sethy 2020), DIU 5-class + pest sets (original folders only), Dhan-Shomadhan white-background half. >= 150 photos from >= 2 datasets per class | RiceLeafBD (field, 2025) + Dhan-Shomadhan field photos |
| 11 | **Severity** (all crops) | PlantSeg (Zenodo) | PlantSeg test split + labelled cotton severity set |
| 04 | Tomato | Tomato-Village (India field photos, Multimedia Systems 2023), DIU Bangladesh field set, half of PlantCity Pakistan tomato. The 'Pakistan tomato' Mendeley set is NOT used (all augmented / internet images) | PlantDoc tomato + other half of PlantCity Pakistan |
| 05 | Apple | 5 Pakistan/Kashmir-relevant classes (Apple Scab, Alternaria Leaf Blotch, Powdery Mildew, Apple Mosaic, Healthy): **half of PlantCity Pakistan apple (Chitral/Charsadda)**, **half of the Indigenous Kashmir set** (its augmented copies are grouped back to one photo per leaf), AppleLeaf9 (Agronomy 2022, ~94% in-the-wild photos) | PlantDoc apple + real-world tests: other halves of PlantCity Pakistan and Kashmir |
| 06 | Mango | MangoLeafBD's 8 classes: MangoLeafBD (Data in Brief 2023; zoom/rotate copies grouped back to one per leaf), MLD24 (6.4k orchard photos), MLDID, Ashulia field set. A class is kept only with >= 150 photos from >= 2 datasets | Pabna & Savar field photos 2024 (different orchards and season) |
| 07 | Grape | Half of PlantCity Pakistan grape (anthracnose, downy, powdery, healthy), NGLD Nashik India (Data in Brief 2025: downy, powdery, healthy), PlantVillage grape capped 300/class (black rot, esca, leaf blight) | GVLiD field photos (Data in Brief; black rot, esca, leaf blight, healthy) + PlantDoc grape + other half of PlantCity Pakistan |
| 08 | Eggplant | 9 classes from 5 checked Bangladesh sets: Eggplant Disease Recognition v2, white-background detection set, Dhaka field set (2024), 'Comprehensive' original set, Brinjal 2025 phone set (capped). jv6tnm4t5c (byte-identical copy) and mn8vfr9bw2 (copies of the hi-res set) NOT used | High-resolution DSLR field set, Savar/Gazipur 2025 (6 classes) |
| 09 | Cucumber | Cucumber BD (Hugging Face) | none — single source (less trustworthy) |
| 10 | Peas | Pisum sativum (Mendeley) | none — single source (less trustworthy) |

## Why these models should not overfit like the old ones
- **Original photos only** — folders named augmented/aug/synthetic are skipped (the old splits leaked rotated copies into validation).
- **Near-duplicates removed**, including flipped/rotated copies (perceptual hash).
- **Split by source**: the model is chosen, calibrated and scored on a dataset it never trained on. The "OOD TEST" number is the honest one; the "val (same sources)" number is shown only for comparison.
- **Domain-gap augmentation** so every source looks like every other source: leaf pasted onto backgrounds from other datasets / plain / noise (leaf found by green-tissue mask with lesions kept), random shadows, JPEG (cheap phone camera) degradation, perspective, TrivialAugment colour/contrast, plus crops, flips, rotation, blur, erasing. **Augmentation strength adapts per class**: small classes (oversampled by the balanced sampler) get up to 2x stronger augmentation plus extra affine/colour variety, so their few photos cannot be memorised; the notebook prints the strength per class. Class-balanced sampling, label smoothing, early stopping on the held-out source.
- **Only classes with real field data are kept**; lab-only classes (e.g. tomato mosaic / spider mites) are dropped.
- Lab-only PlantVillage is capped at 400 per class so it cannot dominate field photos.
- Four backbones compared fairly: the slides' ResNet50, DenseNet121, EfficientNet-B0 **plus DINOv2 ViT-S/14** (self-supervised on 142M varied images — the most robust to new photo styles). The best on the held-out source is exported (DINOv2 as TorchScript; the app supports it).
- **Extra data:** anything you attach with **+ Add Input** is automatically used as an additional training source (e.g. for cotton: search Kaggle for *cotton plant disease* — Aphids / Army worm / Bacterial blight / Healthy / Powdery mildew / Target spot).
- Confidence is calibrated and the uncertainty threshold is chosen so answered predictions are ≥85% correct on the held-out source.

## Reading the result
`VERDICT: PASS` (held-out macro-F1 ≥ 0.70) → ship this crop's model.
`WEAK` → ship, but Qwen vision stays the primary diagnosis for this crop.
`FAIL` → hide the crop's CNN; Qwen only.

## If something fails
- **A Mendeley source shows FAILED**: open its Mendeley page → *Download All* → copy the link → in Kaggle: **+ Add Input → Datasets → New Dataset → Link**, paste, create. Then in the CONFIG cell change that source to
  `{"name": "...", "kind": "kaggle_input", "role": "<same role>", "path": "/kaggle/input/<your-dataset-name>"}` and re-run.
- **"unmapped folders" list shows real disease folders**: send the list to Claude — the alias rules get one line added.
- **"STOP: fewer than 2 classes"**: downloads failed or folders didn't match — send the output.
- **Out of memory**: set `BATCH = 32` in the CONFIG cell.

## Optional: test on your own photos
Upload your labelled photos as a Kaggle dataset (folders per crop/disease, e.g. `corn/Common_Rust.jpg`), attach it with **+ Add Input**, and set `EXTRA_TEST_DIR = "/kaggle/input/<name>/corn"` in CONFIG.

## Putting the models into the app
Send Claude the export zips (or upload them to Google Drive and share the link). Claude will:
add them to `model_registry.json` with the exported class map and threshold, switch off the old combined model for those crops,
wire the severity model into the runtime, update the website disease lists for added/dropped classes, and redeploy.

## Licence notes
PlantSeg (CC BY-NC-ND 4.0) and MangoLeafBD (CC BY-NC 3.0) are non-commercial: fine for the hackathon, re-check before any commercial launch.
