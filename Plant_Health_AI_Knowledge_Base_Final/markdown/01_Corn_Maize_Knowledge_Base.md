# Corn / Maize Farmer Knowledge Base

> Pakistan-oriented RAG resource. Verify exact pesticide use against the current Pakistan-registered label and local extension guidance.

## Model / Project Status

CLOSED in our project. Final disease system: EfficientNet-B0, official TEST accuracy 93.68%, Macro-F1 0.9342. Severity uses lesion-area/segmentation logic with abstention; official TEST effective accuracy 56.03%, Macro-F1 0.5418.

## Crop Overview

**Regions:** Punjab is the major maize-producing province; maize is also grown in Khyber Pakhtunkhwa and other suitable irrigated/rainfed areas.  
**Season / timing:** Pakistan grows both spring and autumn maize. Punjab research describes both seasons; spring maize is a major production system. Exact sowing windows vary by hybrid, district and previous crop, so the chatbot should ask district and intended spring/autumn season.  
**Climate:** Warm-season cereal. Good establishment needs warm soil; pollination and grain filling are especially sensitive to heat and drought. Punjab research notes temperatures above about 37.3 C can damage grain setting.  
**Soil:** Well-drained loam to silt-loam is generally preferred. Avoid prolonged waterlogging. Soil testing is the best basis for nitrogen, phosphorus, potassium, zinc and organic matter management.  
**Water:** Critical stages include establishment, rapid vegetative growth, tasseling/silking and grain filling. Avoid both drought stress at silking and standing water around roots.  

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

### Bacterial Leaf Streak

**Category:** bacterial

**Typical signs**
- Water-soaked, angular or necrotic lesions; blight/canker may develop depending on crop.

**Risk factors**
- Wet foliage, rain splash, wounds and contaminated planting material.

**What to do now**
- Avoid handling wet plants, improve drying/airflow and remove heavily infected material where appropriate.

**Prevention / IPM**
- Clean planting material, sanitation, rotation and splash reduction.

**Chemical decision support**
- Copper-based bactericides may provide preventive suppression in some crops; they do not cure systemic infection.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Common Rust

**Category:** fungal

**Typical signs**
- Small cinnamon-brown pustules on both leaf surfaces; severe infection reduces green leaf area.

**Risk factors**
- Moderate temperatures, dew/leaf wetness and susceptible hybrids.

**What to do now**
- Confirm rust rather than gray leaf spot; assess crop stage and severity.

**Prevention / IPM**
- Use resistant hybrids and timely planting.

**Chemical decision support**
- Triazole (FRAC 3) and QoI/strobilurin (FRAC 11) fungicides or mixtures are commonly used when economically justified; rotate modes of action and verify Pakistan labels.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Gray Leaf Spot

**Category:** fungal

**Typical signs**
- Rectangular gray/tan lesions restricted by veins, usually progressing from lower leaves upward.

**Risk factors**
- Warm humid weather, prolonged leaf wetness, infected residue and continuous maize.

**What to do now**
- Assess disease on leaves around the ear and protect green leaf area.

**Prevention / IPM**
- Rotate crops, manage infected residue and choose resistant hybrids.

**Chemical decision support**
- Triazole, QoI and SDHI foliar fungicides are common maize options; value depends on crop stage and disease pressure.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Maize Lethal Necrosis

**Category:** virus

**Typical signs**
- Mottling/chlorosis, necrosis, stunting, premature plant death and poor ear fill.

**Risk factors**
- Mixed viral infection, infected sources and insect vectors.

**What to do now**
- There is no curative pesticide. Confirm diagnosis and reduce inoculum/vector sources.

**Prevention / IPM**
- Use clean seed, tolerant germplasm where available, rotation and volunteer/weed control.

**Chemical decision support**
- Insecticides do not cure MLN; vector control is only an IPM component.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Maize Streak Virus

**Category:** virus

**Typical signs**
- Fine chlorotic streaks parallel to veins, stunting and reduced ear development.

**Risk factors**
- Leafhopper vectors, susceptible plants and grass hosts.

**What to do now**
- Rogue strongly symptomatic young plants where practical and reduce vector/host pressure.

**Prevention / IPM**
- Use resistant varieties and synchronize planting.

**Chemical decision support**
- No pesticide cures the virus.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Northern Leaf Blight

**Category:** fungal

**Typical signs**
- Long cigar-shaped gray-green to tan lesions, often beginning on lower leaves.

**Risk factors**
- Cool-to-moderate temperatures, dew/rainfall and infected maize residue.

**What to do now**
- Scout leaves around and above the ear.

**Prevention / IPM**
- Use resistant hybrids, rotate crops and manage residue.

**Chemical decision support**
- Triazole/QoI/SDHI foliar fungicides can suppress NLB where economically justified and locally labelled.

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

### Fall armyworm

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Stem borers

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Aphids/jassids

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Termites

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Heat/drought stress

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Review irrigation, fertilizer, spray history, weather and roots before using any pesticide.
- Use soil/leaf testing, correct irrigation and balanced fertility.

**Chemical decision support**
- Do not recommend a pesticide unless a pest/pathogen is independently confirmed.

### Nitrogen or zinc deficiency

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Review irrigation, fertilizer, spray history, weather and roots before using any pesticide.
- Use soil/leaf testing, correct irrigation and balanced fertility.

**Chemical decision support**
- Do not recommend a pesticide unless a pest/pathogen is independently confirmed.

## Sources

- Punjab Agriculture - Maize & Millets Research Institute: https://agripunjab.gov.pk/aari-inst-MaizeMillets
- Punjab Agriculture - Economic Thresholds: https://agripunjab.gov.pk/pw_economic
- CIMMYT: https://www.cimmyt.org/
- Pakistan Department of Plant Protection - Registered Pesticides: https://plantprotection.gov.pk/services/pesticide-registration/list-of-registered-pesticides-in-pakistan/
- Pakistan Department of Plant Protection - Banned Pesticides: https://plantprotection.gov.pk/services/pesticide-registration/list-of-banned-pesticides-in-pakistan/
- Punjab Agriculture - Economic Threshold Levels of Insect Pests: https://agripunjab.gov.pk/pw_economic