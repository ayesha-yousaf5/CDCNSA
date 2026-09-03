# Plant Health AI — Deep Disease Library Verification (Pakistan)

**Build date:** 2026-09-01  
**Scope:** 12 active crops, 75 deployed disease/condition cards, English + Urdu disease-library interaction.

## What changed in this build

This pass was made after reviewing the disease-detail experience for repetition and after reproducing the Urdu-mode card-opening failure path.

1. Every one of the 75 disease/condition cards now has a deeper disease-specific layer that supplies a **type / likely cause** and a **risk context**, in addition to its disease-specific appearance, immediate field action, prevention/IPM, nutrition guidance, Pakistan chemical-safety status, reference image and source record.
2. Long source lists are no longer displayed as a large block. The drawer shows at most three disease-specific references under a collapsed **View disease-specific sources** control. Pakistan regulatory checks are separated into three compact verification links.
3. Generic pesticide wording was reduced. Where a Pakistan/Punjab crop-target example was found, the card identifies the active ingredient(s) as an **evidence example**, not a prescription. Where it was not found, the card does not invent one.
4. The disease-image resolver was tightened. A Wikimedia result is no longer accepted merely because the crop name matches; at least one disease/condition term must also match the image title/metadata. If a sufficiently matched image is not found, the interface deliberately shows no substitute image.
5. Urdu card interaction was rebuilt around stable event delegation and stable crop/disease keys. The drawer now opens synchronously so an RTL/LTR re-render cannot lose the click.
6. A latent initialization-order error in the presentation shell was corrected by moving `init()` until after presentation-shell lexical state is declared.

## Functional Urdu verification

A headless DOM interaction test was run across **every disease card in every crop**, in both languages.

- English cards tested: **75 / 75**
- English drawer-opening failures: **0**
- Urdu cards tested: **75 / 75**
- Urdu drawer-opening failures: **0**
- Changing language while a disease drawer is open: **PASS**
- Citrus Canker drawer title changed from Urdu (`سِٹرس کینکر`) to English (`Citrus Canker`) while remaining open: **PASS**
- Each opened card contained a cause section, a collapsible disease-source section and the three Pakistan verification links: **PASS**

Machine-readable test output is stored in `URDU_DISEASE_CARD_TEST.json`.

> Environment note: direct localhost navigation in the available Chromium environment is blocked by an organization policy. The interaction test therefore loaded the same `index.html` and `app.js` into a headless DOM and exercised the real event handlers and drawer logic there.

## Knowledge-quality policy

The library separates three questions that should not be conflated:

### 1. What is the model class?
The disease/condition card represents a class retained in the project model ontology. Healthy remains a classifier state and is not displayed as a disease card.

### 2. What does it usually look like and how should it be managed?
Appearance, causal-agent context, field action and prevention are disease-specific. Broad visual model classes (for example a generic pest-damage or syndrome class) are explicitly treated as broad classes instead of being assigned a falsely precise pathogen.

### 3. What chemical or fertilizer action is justified in Pakistan?
Chemical and fertilizer guidance is deliberately more conservative than general disease-management text.

- IPM / cultural action is presented first.
- Fertilizer is not described as a cure for infectious disease.
- Site-specific fertilizer decisions should follow soil/plant testing and a local fertilizer recommendation.
- A pesticide active ingredient is named only where reviewed Pakistan/Punjab evidence supports that crop/target context.
- A named active ingredient is still **not** treated as proof that every formulation containing it is currently legal for that crop/target. The user is directed to check the current Department of Plant Protection (DPP) registration and exact product label.
- No dose, concentration, tank mix, PHI, REI, spray interval or maximum number of applications is supplied by the application.
- Pakistan-banned pesticides are not recommended.

## Pakistan sources reviewed

### Federal regulatory authority

- **Department of Plant Protection (DPP) — registered pesticide lists.** DPP publishes registered pesticide lists under its pesticide-registration service (Forms 1, 16 and 17).
- **DPP — pesticide registration procedures and legal framework.** The registration process is administered under Pakistan's agricultural pesticide framework.
- **DPP — banned pesticide list.** This is used as a negative safety gate; a banned active ingredient must never be recommended by the application.

### Punjab technical / advisory sources

- **Plant Pathology Research Institute (PPRI), Faisalabad.** Reviewed for Pakistan/Punjab disease-management research and crop-target chemical examples, including rice brown spot/blast/bacterial leaf blight, tomato early/late blight, cotton bacterial leaf blight, cucurbit downy mildew and citrus canker.
- **Punjab Agriculture / AARI soil, water and plant testing.** Used to support the policy that fertilizer recommendations should be based on measured nutrient/soil status rather than prescribed as a disease cure.
- **Punjab Pest Warning / crop advisories.** Used where a same-crop disease-management example was available.

## Cards with a Pakistan/Punjab chemical evidence example in this build

The following ten cards contain a Pakistan/Punjab technical example. They still require current DPP crop/target label verification before field use.

| Crop | Model class | Evidence example shown in UI |
|---|---|---|
| Cotton | Bacterial Blight | streptomycin sulfate |
| Tomato | Early Blight | pyraclostrobin + tebuconazole; azoxystrobin + difenoconazole |
| Tomato | Late Blight | metalaxyl-M + mancozeb; azoxystrobin + difenoconazole |
| Rice | Bacterial Leaf Blight | kasugamycin; copper oxychloride; kasugamycin + copper oxychloride |
| Rice | Brown Spot | tebuconazole; azoxystrobin + difenoconazole; epoxiconazole + pyraclostrobin |
| Rice | Rice Blast | azoxystrobin + difenoconazole; pyraclostrobin; isoprothiolane |
| Mango | Anthracnose | Bordeaux mixture / copper-based fungicides |
| Mango | Die Back | metalaxyl + mancozeb only in the diagnosed wound/gummosis/dieback context described by the provincial advisory |
| Cucumber | Downy Mildew | metalaxyl-M + mancozeb for cucurbit downy mildew |
| Lemon | Citrus Canker | copper-based options / kasugamycin context; exact current DPP citrus-canker label still required |

These entries are **evidence examples**, not dosage or brand recommendations.

## Repetition audit

The disease-specific clinical/agronomic sections are no longer boilerplate:

- Appearance / typical signs: **75 unique texts / 75 cards**
- Immediate field action / treatment: **75 unique texts / 75 cards**
- Prevention / IPM: **74 unique texts / 75 cards**
- Risk context: **75 unique texts / 75 cards**
- Likely-cause text: **74 unique texts / 75 cards**
- Pakistan chemical guidance: **50 unique texts / 75 cards**

Nutrition remains intentionally conservative. For many diseases the correct statement is that no disease-specific fertilizer is a cure and measured deficiency should be corrected through soil/plant testing. The application does not manufacture disease-specific NPK prescriptions merely to make cards look different.

## Healthy -> severity invariant

The previous hard safety rule remains unchanged:

```text
if disease == healthy:
    do not run severity model
    severity = N/A
    severity_confidence = N/A
```

The same state is carried through the diagnosis result, history, chatbot context and API-facing context.

## Files relevant to this verification

- `app.js` — ontology, disease knowledge, deep detail layer, Pakistan chemical policy and Urdu interaction logic.
- `styles.css` — disease drawer, RTL and Urdu presentation.
- `URDU_DISEASE_CARD_TEST.json` — all-card bilingual interaction test result.
- `DISEASE_LIBRARY_VERIFICATION.md` — earlier verification note retained for provenance.
