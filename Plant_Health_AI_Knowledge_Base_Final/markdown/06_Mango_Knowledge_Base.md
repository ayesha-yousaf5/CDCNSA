# Mango Farmer Knowledge Base

> Pakistan-oriented RAG resource. Verify exact pesticide use against the current Pakistan-registered label and local extension guidance.

## Model / Project Status

Checkpoint package reviewed: EfficientNet-B0 disease and ResNet50 severity. Stored validation disease accuracy 90.48%, Macro-F1 0.9149; severity accuracy 74.47%, Macro-F1 0.7371. Split/test provenance still requires notebook verification.

## Crop Overview

**Regions:** Pakistan's major mango production is in Punjab and Sindh, with important commercial belts around Multan, Rahim Yar Khan, Muzaffargarh and Sindh mango districts.  
**Season / timing:** PHDEC describes harvest from roughly end-May to September. Punjab nurseries commonly list February and September as planting seasons for mango planting material.  
**Climate:** Subtropical/tropical perennial. Dry weather around flowering is favorable; rain/high humidity around flowering and fruiting can increase anthracnose and powdery mildew pressure.  
**Soil:** Deep, well-drained loam is preferred. Avoid prolonged waterlogging around the trunk/collar. Orchard floor and organic matter management should maintain infiltration without keeping the stem wet.  
**Water:** Young trees need regular establishment irrigation. Mature trees need irrigation timed to phenology; avoid constantly wet trunk zones and reduce stress during fruit development.  

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

### Anthracnose

**Category:** fungal

**Typical signs**
- Dark sunken lesions on leaves/stems/fruit; fruit spots may develop dark spore masses.

**Risk factors**
- Warm wet conditions, rain splash and infected debris/seed.

**What to do now**
- Remove infected fruit/debris and reduce overhead wetting.

**Prevention / IPM**
- Clean seed/planting material, sanitation, pruning/rotation.

**Chemical decision support**
- Copper/multi-site protectants and FRAC 3/11-type programs are common crop-dependent options; verify crop label.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Bacterial Canker

**Category:** bacterial

**Typical signs**
- Cankers, shoot dieback, leaf lesions and sometimes fruit spots; citrus canker often has raised corky lesions with halos.

**Risk factors**
- Wind-driven rain, wounds, infected planting material and leafminer injury in citrus.

**What to do now**
- Prune infected shoots in dry weather using disinfected tools.

**Prevention / IPM**
- Disease-free nursery stock, sanitation and wind protection where appropriate.

**Chemical decision support**
- Copper-based bactericides are suppressive, not curative; verify crop-specific label.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Cutting Weevil

**Category:** insect

**Typical signs**
- Chewing, mining, sucking injury, distortion, colonies, webbing, galls or frass depending on the pest.

**Risk factors**
- Crop stage, weather, alternate hosts and disruption of natural enemies.

**What to do now**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.

**Prevention / IPM**
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Die Back

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

### Gall Midge

**Category:** insect

**Typical signs**
- Chewing, mining, sucking injury, distortion, colonies, webbing, galls or frass depending on the pest.

**Risk factors**
- Crop stage, weather, alternate hosts and disruption of natural enemies.

**What to do now**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.

**Prevention / IPM**
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Powdery Mildew

**Category:** fungal

**Typical signs**
- White powdery growth, distorted young tissue and reduced flowering/fruit set.

**Risk factors**
- Moderate temperatures and dense susceptible growth.

**What to do now**
- Remove severe infected shoots/leaves and open canopy.

**Prevention / IPM**
- Prune for airflow and avoid excessive nitrogen.

**Chemical decision support**
- Sulfur is a classic option where crop/cultivar permits; rotate other labelled FRAC groups and avoid oil-sulfur conflicts.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Sooty Mould

**Category:** fungal

**Typical signs**
- Black superficial coating that rubs off, usually growing on honeydew.

**Risk factors**
- Whiteflies, scales, aphids or mealybugs.

**What to do now**
- Control the honeydew-producing pest.

**Prevention / IPM**
- Conserve natural enemies and manage ants.

**Chemical decision support**
- Fungicide is usually not the main solution; use insect IPM.

**Low-cost/supportive**
- Use sanitation first: remove diseased debris/fruit where appropriate, disinfect pruning tools, and reduce weed hosts.
- Prefer drip/soil-directed irrigation over routine overhead wetting when the crop allows.
- Well-rotted compost or manure can support soil structure and nutrient supply, but it is not a curative treatment for an active pathogen.
- Neem/azadirachtin, horticultural oil, insecticidal soap, sulfur, copper or biological products can be lower-input options for selected targets only; check crop safety and local registration.

### Senescence / Drying Condition

**Category:** abiotic

**Typical signs**
- Non-infectious discoloration, distortion, drying or growth abnormality; field pattern and crop history are essential.

**Risk factors**
- Nutrient imbalance, chemical injury, water stress, salinity, heat/cold, root damage or natural senescence.

**What to do now**
- Review irrigation, fertilizer, spray history, weather and roots before using any pesticide.

**Prevention / IPM**
- Use soil/leaf testing, correct irrigation and balanced fertility.

**Chemical decision support**
- Do not recommend a pesticide unless a pest/pathogen is independently confirmed.

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

### Mango hopper

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Mealybug

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Fruit fly

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Confirm the pest and quantify infestation before spraying; use an economic threshold where available.
- Conserve natural enemies, manage weeds/alternate hosts and use traps/physical exclusion where appropriate.

**Chemical decision support**
- If economic damage warrants, choose a Pakistan-registered crop-labelled insecticide/acaricide and rotate IRAC modes of action.

### Mango malformation

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

### Stem-end rot

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

### Gummosis/decline

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

### Nutrient deficiencies

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Remove heavily infected tissue where practical, improve airflow and reduce unnecessary leaf wetness.
- Rotation/sanitation, resistant varieties, clean planting material and balanced nutrition.

**Chemical decision support**
- Use a crop-labelled fungicide only after diagnosis and rotate FRAC groups.

### Sunburn

_Knowledge-only unless separately supported by an approved vision model._

**Management**
- Review irrigation, fertilizer, spray history, weather and roots before using any pesticide.
- Use soil/leaf testing, correct irrigation and balanced fertility.

**Chemical decision support**
- Do not recommend a pesticide unless a pest/pathogen is independently confirmed.

## Sources

- PHDEC - Mango season and postharvest: https://phdec.gov.pk/mango-bagging-initiative-boost-pakistans-mango-industrymultan/
- Punjab Agriculture - Mango Research Institute: https://agripunjab.gov.pk/node/9748
- Punjab Agriculture - Fruit planting seasons: https://agripunjab.gov.pk/index.php/aari-services
- Punjab Agriculture - Economic Thresholds: https://agripunjab.gov.pk/pw_economic
- Pakistan Department of Plant Protection - Registered Pesticides: https://plantprotection.gov.pk/services/pesticide-registration/list-of-registered-pesticides-in-pakistan/
- Pakistan Department of Plant Protection - Banned Pesticides: https://plantprotection.gov.pk/services/pesticide-registration/list-of-banned-pesticides-in-pakistan/
- Punjab Agriculture - Economic Threshold Levels of Insect Pests: https://agripunjab.gov.pk/pw_economic