# Plant Health AI — Disease Library Verification / Pakistan Safety

Verified build date: 2026-09-01

This build contains **75 deployed disease/condition cards** across the 12 project crops. Healthy outputs are classifier states, not disease cards. A healthy disease prediction forces severity and severity confidence to `N/A`.

## Disease-detail experience

Each disease/condition card opens a detail drawer with:

- disease/condition-specific reference image when a sufficiently matched Wikimedia Commons image can be verified;
- source/license for the reference image;
- no-image fallback instead of a misleading generic crop image;
- what it is / likely cause;
- disease type;
- risk conditions;
- appearance / typical signs;
- immediate field action / treatment;
- prevention / IPM;
- fertilizer and nutrition guidance;
- Pakistan pesticide/chemical evidence status;
- economic threshold/action point where supported;
- collapsed disease-specific source links;
- separate current Pakistan DPP registration, banned-list and Punjab soil/plant-testing links.

## Pakistan safety policy

1. Integrated and cultural management comes before chemistry.
2. Fertilizer is not described as a disease cure. Soil/plant testing is the basis for site-specific nutrient recommendations.
3. An active ingredient is named only where reviewed Pakistan/Punjab crop-target evidence supports it.
4. A named example is not a prescription: current DPP registration and the exact product crop/target label still govern use.
5. No dose, concentration, tank mix, PHI, REI, application interval or maximum applications are supplied.
6. Pakistan-banned pesticides are never recommended.
7. Viral and other non-curable systemic conditions do not receive fictitious curative pesticide recommendations.

## Principal Pakistan sources

- Department of Plant Protection — current registered pesticide lists: https://plantprotection.gov.pk/services/pesticide-registration/list-of-registered-pesticides-in-pakistan/
- Department of Plant Protection — banned pesticides: https://plantprotection.gov.pk/services/pesticide-registration/list-of-banned-pesticides-in-pakistan/
- Department of Plant Protection — registration procedures: https://plantprotection.gov.pk/services/pesticide-registration/registration-procedures/
- Punjab Plant Pathology Research Institute, Faisalabad: https://agripunjab.gov.pk/node/9682
- Punjab AARI soil/water/plant testing and fertilizer recommendations: https://agripunjab.gov.pk/index.php/aari-services

## Bilingual interaction verification

The Urdu-mode disease-card issue has been corrected using stable event delegation and stable crop/disease identifiers. The disease drawer opens synchronously and survives language re-rendering.

Automated interaction audit:

- English: 75/75 disease cards opened successfully.
- Urdu: 75/75 disease cards opened successfully.
- Switching Urdu ↔ English while a drawer is open: PASS.

See `URDU_DISEASE_CARD_TEST.json` and `DEEP_DISEASE_LIBRARY_VERIFICATION_PK.md` for the detailed record.
