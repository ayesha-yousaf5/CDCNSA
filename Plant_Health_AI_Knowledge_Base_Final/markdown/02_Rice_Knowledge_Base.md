# Rice Farmer Knowledge Base

> Pakistan-oriented RAG resource. Verify exact pesticide use against the current Pakistan-registered label and local extension guidance.

## Model / Project Status

Checkpoint package reviewed: ResNet50 disease (11 outputs) and EfficientNet-B0 severity (3 outputs). Stored validation disease accuracy 78.67%, Macro-F1 0.8015; severity accuracy 64.18%, Macro-F1 0.5842. Scientific provenance/split notebook still requires full verification.

## Crop Overview

**Regions:** Punjab and Sindh are major rice-producing provinces, with Basmati concentrated strongly in Punjab and coarse/non-Basmati systems across several irrigated rice zones.  
**Season / timing:** Punjab Agriculture lists many coarse varieties for nursery sowing around 20 May-7 June and many Basmati/aromatic varieties around 1-25 June, with variety-specific exceptions. Transplanting follows nursery development and local advisories.  
**Climate:** Warm, humid monsoon conditions suit rice but also favor blast, sheath blight and vector-borne diseases. Cool, wet/dewy conditions can favor blast; dense, highly fertilized canopies favor sheath blight.  
**Soil:** Puddled lowland systems need level fields and managed water; direct-seeded systems need different weed/water strategies. Soil tests guide N-P-K and zinc management.  
**Water:** Water management depends on establishment system. Avoid chronic drought stress; also avoid unnecessarily deep continuous water where alternate wetting/drying or local recommendations are appropriate.  

## Core Agronomy and Farmer Advice

### Crop establishment

- Start with locally adapted, certified or otherwise reliable seed/planting material. Ask province/district, variety/hybrid, planting date and production system before calendar-specific advice.
- Do not extrapolate one province's calendar to all Pakistan. Elevation, tunnel/open-field production, irrigation and cultivar maturity can shift planting and harvest dates.

### Soil fertility and home-scale amendments

- Use a soil test whenever possible. Distinguish nutrient deficiency from disease before recommending fertilizer.
- Well-rotted farmyard manure, compost, disease-safe crop residues and green manures can improve organic matter and water-holding capacity.
- Avoid fresh manure against tree trunks or near harvestable produce. Avoid excessive nitrogen because lush growth can increase sucking pests, lodging or foliar disease.

### Irrigation

- Ask soil type, irrigation method, recent rainfall and crop stage. Generic 'water every X days' advice is unreliable across Pakistan.
- Avoid both drought stress and prolonged saturation. Where foliar disease is important, drip or soil-directed irrigation usually reduces leaf wetness.

### Scouting and diagnosis

- Ask which plant part is affected, whether symptoms start on old/new leaves, field distribution, underside appearance, insects/webbing/mines, recent spray history and weather.
- For serious decisions, request close-up plus whole-plant/field photos and leaf undersides where relevant.

### Integrated pest management

- Use resistant varieties, sanitation, rotation, natural enemies, traps, physical exclusion, irrigation/fertility management and economic thresholds before relying on pesticides.
- Avoid calendar spraying without a target. Repeated broad-spectrum insecticides can destroy natural enemies and trigger secondary pests.

### Chemical-use safety

- Never generate exact dose, tank concentration, PHI, REI or maximum application number from memory. Use the current Pakistan-registered product label.
- Do not recommend pesticides banned in Pakistan. Rotate FRAC/IRAC modes of action where resistance risk exists.
- If the farmer names a brand, verify its active ingredient, formulation and legal crop/target use rather than infer from the brand.

## Project / Dataset Disease and Condition Scope

### Bacterial Leaf Blight

**Category:** bacterial

**Typical signs**
- Water-soaked/yellow lesions from tips or margins, sometimes seedling wilt.

**Risk factors**
- Wind-driven rain, wounds, high nitrogen and warm wet conditions.

**What to do now**
- Avoid excess nitrogen and wet-field movement.

**Prevention / IPM**
- Resistant varieties, clean seed, sanitation and balanced fertility.

**Chemical decision support**
- Bactericides have limited curative value; prevention is more important than routine spraying.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Brown Spot

**Category:** fungal

**Typical signs**
- Leaf spots, blight, mildew, rot, wilt or canker consistent with the named fungal/oomycete problem.

**Risk factors**
- Leaf wetness, humidity, infected residue/seed and susceptible tissue commonly increase pressure.

**What to do now**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.

**Prevention / IPM**
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Leaf Scald

**Category:** fungal

**Typical signs**
- Leaf spots, blight, mildew, rot, wilt or canker consistent with the named fungal/oomycete problem.

**Risk factors**
- Leaf wetness, humidity, infected residue/seed and susceptible tissue commonly increase pressure.

**What to do now**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.

**Prevention / IPM**
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Narrow Brown Leaf Spot

**Category:** fungal

**Typical signs**
- Leaf spots, blight, mildew, rot, wilt or canker consistent with the named fungal/oomycete problem.

**Risk factors**
- Leaf wetness, humidity, infected residue/seed and susceptible tissue commonly increase pressure.

**What to do now**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.

**Prevention / IPM**
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Rice Blast

**Category:** fungal

**Typical signs**
- Spindle/diamond-shaped lesions with gray centers and darker borders; neck/panicle infection can occur.

**Risk factors**
- Cooler conditions, dew/prolonged leaf wetness, susceptible varieties and excessive nitrogen.

**What to do now**
- Avoid excess nitrogen, maintain appropriate water and assess heading-stage risk.

**Prevention / IPM**
- Use resistant varieties, split nitrogen and crop/water management.

**Chemical decision support**
- IRRI notes judicious use of systemic triazole and strobilurin/QoI fungicides; rotate modes of action and use Pakistan-labelled products.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Rice Hispa

**Category:** insect

**Typical signs**
- Adults scrape leaf surfaces causing white streaks; larvae mine leaves.

**Risk factors**
- Dense crop and favorable humid conditions.

**What to do now**
- Punjab threshold: 1 hispa per plant.

**Prevention / IPM**
- Conserve natural enemies and scout before spraying.

**Chemical decision support**
- If threshold is exceeded, use a Pakistan-registered rice insecticide and rotate IRAC groups.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Rice Leaffolder

**Category:** insect

**Typical signs**
- Leaves are folded/rolled and larvae scrape green tissue leaving white areas.

**Risk factors**
- High nitrogen and dense humid canopy.

**What to do now**
- Punjab thresholds: 2 rolled leaves/plant in Jul-Aug and 3 in Sep-Oct.

**Prevention / IPM**
- Avoid excessive nitrogen and conserve beneficial insects.

**Chemical decision support**
- Use a locally registered selective lepidopteran insecticide only after threshold assessment.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Rice Stripes

**Category:** virus

**Typical signs**
- Mosaic, streaking, curling, yellowing, stunting or distorted growth depending on virus/crop.

**Risk factors**
- Infected planting material/alternate hosts and active vectors depending on the virus.

**What to do now**
- Do not promise a cure. Remove strongly infected plants where practical and reduce vector/weed sources.

**Prevention / IPM**
- Use clean seed/transplants, resistant/tolerant varieties and vector-exclusion/IPM.

**Chemical decision support**
- No pesticide cures a virus. Insecticides can only reduce vector pressure in selected systems.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Rice Tungro

**Category:** virus

**Typical signs**
- Yellow/orange leaf discoloration, stunting, fewer tillers and poor panicles; green leafhopper-transmitted.

**Risk factors**
- Young susceptible rice, asynchronous planting and vector pressure.

**What to do now**
- Infected plants cannot be cured.

**Prevention / IPM**
- Use resistant varieties where available, synchronous planting and destroy infected stubble.

**Chemical decision support**
- IRRI notes insecticides often do not reliably stop spread; do not present insecticide as a cure.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Sheath Blight

**Category:** abiotic

**Typical signs**
- Irregular greenish-gray lesions on sheaths near waterline that enlarge; sclerotia may appear.

**Risk factors**
- High temperature, very humid dense canopies, high nitrogen and close spacing.

**What to do now**
- Reduce canopy humidity and avoid excessive nitrogen.

**Prevention / IPM**
- Reasonable plant density, weed control and balanced fertility.

**Chemical decision support**
- Use locally labelled sheath-blight fungicides when warranted; rotate FRAC groups.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### healthy

**Category:** healthy

**Typical signs**
- Normal crop-stage color, canopy density and growth without progressive lesions, mosaic, mining, wilt or pest colonies.

**Risk factors**
- Healthy appearance still requires routine scouting because root or early-stage problems may not be visible.

**What to do now**
- Do not spray simply because the crop looks healthy; maintain crop-stage irrigation, nutrition and scouting.

**Prevention / IPM**
- Clean planting material, sanitation, balanced fertility, drainage and pest monitoring.

**Chemical decision support**
- No pesticide is indicated without a diagnosed target and a threshold/label-supported reason.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

## Additional Farmer-Support Topics

### Stem borers

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Brown/white-backed planthoppers

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Zinc deficiency

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Review irrigation, fertilizer, spray history, weather and roots before using any pesticide.
- Use soil/leaf testing, correct irrigation and balanced fertility.

**Chemical decision support**
- Do not recommend a pesticide unless a pest/pathogen is independently confirmed.

### Nitrogen deficiency

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Review irrigation, fertilizer, spray history, weather and roots before using any pesticide.
- Use soil/leaf testing, correct irrigation and balanced fertility.

**Chemical decision support**
- Do not recommend a pesticide unless a pest/pathogen is independently confirmed.

### Bakanae

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

### False smut

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

## Sources

- Punjab Agriculture - Rice varieties and sowing windows: https://agripunjab.gov.pk/aari-cvrice
- IRRI Rice Knowledge Bank - Diseases: https://www.knowledgebank.irri.org/step-by-step-production/growth/pests-and-diseases/diseases
- IRRI - Rice Blast: https://www.knowledgebank.irri.org/training/fact-sheets/pest-management/diseases/item/blast-leaf-collar
- IRRI - Tungro: https://www.knowledgebank.irri.org/training/fact-sheets/pest-management/diseases/item/tungro
- Punjab Agriculture - Economic Thresholds: https://agripunjab.gov.pk/pw_economic
- Pakistan Department of Plant Protection - Registered Pesticides: https://plantprotection.gov.pk/services/pesticide-registration/list-of-registered-pesticides-in-pakistan/
- Pakistan Department of Plant Protection - Banned Pesticides: https://plantprotection.gov.pk/services/pesticide-registration/list-of-banned-pesticides-in-pakistan/
- Punjab Agriculture - Economic Threshold Levels of Insect Pests: https://agripunjab.gov.pk/pw_economic