"""
Comprehensive plant disease knowledge base with treatment information.

This module provides detailed information about each disease the ML model
can detect, including symptoms, causes, treatments (organic and chemical),
and prevention methods.
"""

DISEASE_KNOWLEDGE = {
    # =========================================================
    # TOMATO DISEASES
    # =========================================================
    "tomato_early_blight": {
        "crop": "tomato",
        "disease": "Early Blight",
        "pathogen": "Alternaria solani (fungus)",
        "symptoms": [
            "Dark brown spots with concentric rings (target board appearance)",
            "Lower leaves affected first",
            "Spots have yellow halo around them",
            "Leaves turn yellow and drop prematurely"
        ],
        "causes": [
            "Warm, humid weather (24-29°C)",
            "Prolonged leaf wetness",
            "Infected plant debris in soil",
            "Splashing water from rain or irrigation"
        ],
        "treatment_organic": [
            "Remove and destroy infected leaves immediately",
            "Apply neem oil spray (2-3 ml/L water) every 7-10 days",
            "Use copper-based fungicide (Bordeaux mixture)",
            "Improve air circulation by pruning lower leaves",
            "Mulch around plants to prevent soil splash"
        ],
        "treatment_chemical": [
            "Chlorothalonil (2 g/L water) - apply every 7-10 days",
            "Mancozeb (2.5 g/L water) - preventive spray",
            "Azoxystrobin + Difenoconazole (as per label)",
            "Alternate fungicides to prevent resistance"
        ],
        "prevention": [
            "Rotate crops (3-year rotation)",
            "Use disease-resistant varieties",
            "Water at base, avoid overhead irrigation",
            "Remove plant debris after harvest",
            "Space plants properly for airflow"
        ],
        "severity_indicators": {
            "mild": "Few spots on lower leaves, no yellowing",
            "moderate": "Multiple leaves with spots, some yellowing",
            "severe": "Defoliation, spots on stems and fruit"
        }
    },

    "tomato_late_blight": {
        "crop": "tomato",
        "disease": "Late Blight",
        "pathogen": "Phytophthora infestans (oomycete)",
        "symptoms": [
            "Water-soaked dark green to black lesions on leaves",
            "White fuzzy growth on underside of leaves in humid conditions",
            "Rapid spread to stems and fruit",
            "Firm, dark brown spots on fruit"
        ],
        "causes": [
            "Cool, wet weather (15-23°C)",
            "High humidity (>90%)",
            "Rainy periods with moderate temperatures",
            "Infected potato tubers or plant debris"
        ],
        "treatment_organic": [
            "Remove and destroy all infected plant parts immediately",
            "Apply copper fungicide (Bordeaux mixture) preventively",
            "Use baking soda spray (1 tbsp/L water + few drops soap)",
            "Improve drainage and reduce humidity",
            "Destroy infected plants in severe cases"
        ],
        "treatment_chemical": [
            "Metalaxyl + Mancozeb (Ridomil Gold) - 2.5 g/L",
            "Cymoxanil + Mancozeb - 3 g/L",
            "Dimethomorph - 2 ml/L",
            "Apply immediately when symptoms appear, repeat every 5-7 days"
        ],
        "prevention": [
            "Use certified disease-free seeds/transplants",
            "Avoid planting near potato fields",
            "Water early in the day",
            "Ensure good air circulation",
            "Monitor weather conditions closely"
        ],
        "severity_indicators": {
            "mild": "Few lesions on lower leaves",
            "moderate": "Lesions spreading to stems, some fruit affected",
            "severe": "Complete plant collapse, fruit rot"
        }
    },

    "tomato_leaf_mold": {
        "crop": "tomato",
        "disease": "Leaf Mold",
        "pathogen": "Passalora fulva (fungus)",
        "symptoms": [
            "Pale green to yellow spots on upper leaf surface",
            "Olive-green to gray fuzzy mold on leaf underside",
            "Leaves curl, wither, and drop",
            "Rarely affects fruit"
        ],
        "causes": [
            "High humidity (>85%)",
            "Poor air circulation",
            "Moderate temperatures (22-24°C)",
            "Greenhouse or densely planted conditions"
        ],
        "treatment_organic": [
            "Reduce humidity by improving ventilation",
            "Remove and destroy infected leaves",
            "Apply neem oil spray",
            "Water at base to keep foliage dry",
            "Space plants further apart"
        ],
        "treatment_chemical": [
            "Chlorothalonil - 2 g/L",
            "Copper hydroxide - 2 g/L",
            "Mancozeb - 2.5 g/L",
            "Apply every 7-10 days during humid weather"
        ],
        "prevention": [
            "Use resistant varieties",
            "Ensure good greenhouse ventilation",
            "Avoid overhead irrigation",
            "Stake and prune for airflow",
            "Rotate crops annually"
        ],
        "severity_indicators": {
            "mild": "Few spots on lower leaves",
            "moderate": "Multiple leaves with mold, some defoliation",
            "severe": "Severe defoliation, yield loss"
        }
    },

    "tomato_mosaic_virus": {
        "crop": "tomato",
        "disease": "Mosaic Virus",
        "pathogen": "Tobacco Mosaic Virus (TMV) / Tomato Mosaic Virus (ToMV)",
        "symptoms": [
            "Mosaic pattern of light and dark green on leaves",
            "Leaf curling and distortion",
            "Stunted growth",
            "Reduced fruit set and malformed fruit"
        ],
        "causes": [
            "Spread by contact (tools, hands, clothing)",
            "Infected seeds",
            "Contaminated tobacco products",
            "Weeds as virus reservoirs"
        ],
        "treatment_organic": [
            "No cure - remove and destroy infected plants",
            "Disinfect tools in 10% bleach solution",
            "Wash hands with soap before handling plants",
            "Control weed hosts",
            "Use virus-free seeds"
        ],
        "treatment_chemical": [
            "No chemical treatment available",
            "Focus on prevention and removal of infected plants"
        ],
        "prevention": [
            "Use virus-resistant varieties",
            "Test seeds for virus",
            "Disinfect tools regularly",
            "Avoid smoking near plants",
            "Remove infected plants immediately",
            "Control aphids and other vectors"
        ],
        "severity_indicators": {
            "mild": "Mosaic pattern on few leaves, normal growth",
            "moderate": "Widespread mosaic, some stunting",
            "severe": "Severe stunting, leaf distortion, poor fruit set"
        }
    },

    "tomato_septoria_leaf_spot": {
        "crop": "tomato",
        "disease": "Septoria Leaf Spot",
        "pathogen": "Septoria lycopersici (fungus)",
        "symptoms": [
            "Small circular spots with dark margins and gray centers",
            "Tiny black dots (fruiting bodies) in spot centers",
            "Lower leaves affected first",
            "Severe defoliation"
        ],
        "causes": [
            "Warm, wet weather",
            "Splashing water from infected debris",
            "Dense foliage",
            "Poor air circulation"
        ],
        "treatment_organic": [
            "Remove infected leaves immediately",
            "Apply copper fungicide preventively",
            "Mulch heavily to prevent soil splash",
            "Improve air circulation",
            "Water at soil level"
        ],
        "treatment_chemical": [
            "Chlorothalonil - 2 g/L",
            "Mancozeb - 2.5 g/L",
            "Azoxystrobin - as per label",
            "Apply every 7-10 days, especially after rain"
        ],
        "prevention": [
            "Rotate crops (3-4 year rotation)",
            "Remove plant debris",
            "Use resistant varieties",
            "Mulch around plants",
            "Water early in the day"
        ],
        "severity_indicators": {
            "mild": "Few spots on lower leaves",
            "moderate": "Multiple leaves spotted, some yellowing",
            "severe": "Complete defoliation, exposed fruit sunburn"
        }
    },

    # =========================================================
    # POTATO DISEASES
    # =========================================================
    "potato_early_blight": {
        "crop": "potato",
        "disease": "Early Blight",
        "pathogen": "Alternaria solani (fungus)",
        "symptoms": [
            "Dark brown spots with concentric rings on leaves",
            "Lower leaves affected first",
            "Yellow halo around spots",
            "Tuber lesions: dark, sunken, leathery"
        ],
        "causes": [
            "Warm temperatures (24-29°C)",
            "Humid conditions",
            "Nutrient stress (especially nitrogen)",
            "Old or weak plants"
        ],
        "treatment_organic": [
            "Remove infected leaves",
            "Apply copper-based fungicide",
            "Ensure adequate nutrition",
            "Improve air circulation",
            "Mulch to reduce soil splash"
        ],
        "treatment_chemical": [
            "Mancozeb - 2.5 g/L",
            "Chlorothalonil - 2 g/L",
            "Difenoconazole - 0.5 ml/L",
            "Apply every 7-10 days"
        ],
        "prevention": [
            "Use certified disease-free seed potatoes",
            "Rotate crops (3-year rotation)",
            "Maintain proper nutrition",
            "Adequate irrigation",
            "Harvest at maturity"
        ],
        "severity_indicators": {
            "mild": "Few spots on older leaves",
            "moderate": "Multiple leaves affected, some tuber infection",
            "severe": "Defoliation, significant tuber damage"
        }
    },

    "potato_late_blight": {
        "crop": "potato",
        "disease": "Late Blight",
        "pathogen": "Phytophthora infestans (oomycete)",
        "symptoms": [
            "Water-soaked pale green to black leaf lesions",
            "White mold on leaf undersides in humid conditions",
            "Dark brown irregular tuber rot",
            "Rapid plant collapse"
        ],
        "causes": [
            "Cool, wet weather (15-23°C)",
            "High humidity",
            "Infected seed tubers",
            "Rainfall during growing season"
        ],
        "treatment_organic": [
            "Remove and destroy infected plants immediately",
            "Apply copper fungicide preventively",
            "Improve drainage",
            "Hill potatoes to protect tubers",
            "Harvest early if epidemic threatens"
        ],
        "treatment_chemical": [
            "Metalaxyl + Mancozeb - 2.5 g/L",
            "Cymoxanil + Mancozeb - 3 g/L",
            "Dimethomorph - 2 ml/L",
            "Apply immediately, repeat every 5-7 days"
        ],
        "prevention": [
            "Use certified disease-free seed",
            "Plant resistant varieties",
            "Hill potatoes properly",
            "Avoid overhead irrigation",
            "Destroy cull piles and volunteer plants"
        ],
        "severity_indicators": {
            "mild": "Few lesions on leaves",
            "moderate": "Stems affected, some tuber infection",
            "severe": "Complete vine death, tuber rot in storage"
        }
    },

    # =========================================================
    # RICE DISEASES
    # =========================================================
    "rice_bacterial_leaf_blight": {
        "crop": "rice",
        "disease": "Bacterial Leaf Blight",
        "pathogen": "Xanthomonas oryzae pv. oryzae (bacterium)",
        "symptoms": [
            "Water-soaked streaks on leaf edges",
            "Streaks turn yellow then white/gray",
            "Lesions spread from leaf tip",
            "Wilting and drying of leaves"
        ],
        "causes": [
            "Warm, humid conditions",
            "Excessive nitrogen fertilization",
            "Wounds from wind or insects",
            "Infected seeds or plant debris"
        ],
        "treatment_organic": [
            "Drain fields to reduce humidity",
            "Reduce nitrogen fertilizer",
            "Apply copper-based bactericide",
            "Remove infected plant debris",
            "Use biocontrol agents (Pseudomonas)"
        ],
        "treatment_chemical": [
            "Copper hydroxide - 2 g/L",
            "Streptomycin sulfate - 0.5 g/L",
            "Kasugamycin - as per label",
            "Apply at first symptoms, repeat in 7-10 days"
        ],
        "prevention": [
            "Use resistant varieties",
            "Use certified clean seeds",
            "Balanced fertilization",
            "Proper water management",
            "Remove crop residues"
        ],
        "severity_indicators": {
            "mild": "Few leaves with streaks",
            "moderate": "Multiple tillers affected, some yield loss",
            "severe": "Widespread blighting, significant yield loss"
        }
    },

    "rice_blast": {
        "crop": "rice",
        "disease": "Rice Blast",
        "pathogen": "Magnaporthe oryzae (fungus)",
        "symptoms": [
            "Diamond-shaped lesions with gray centers",
            "Lesions on leaves, nodes, and panicles",
            "Node rot causes stem breaking",
            "Panicle blast causes empty grains"
        ],
        "causes": [
            "Cool temperatures (20-25°C)",
            "High humidity",
            "Excessive nitrogen",
            "Drought stress followed by rain"
        ],
        "treatment_organic": [
            "Reduce nitrogen fertilizer",
            "Maintain water level in field",
            "Apply silicon-based amendments",
            "Use biocontrol (Trichoderma)",
            "Remove infected straw"
        ],
        "treatment_chemical": [
            "Tricyclazole - 0.6 g/L",
            "Isoprothiolane - 1.5 ml/L",
            "Carbendazim - 1 g/L",
            "Apply at booting and heading stages"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Balanced fertilization",
            "Avoid drought stress",
            "Proper water management",
            "Remove crop residues"
        ],
        "severity_indicators": {
            "mild": "Few leaf lesions, no node/panicle infection",
            "moderate": "Multiple leaf lesions, some node infection",
            "severe": "Widespread infection, panicle blast, lodging"
        }
    },

    "rice_brown_spot": {
        "crop": "rice",
        "disease": "Brown Spot",
        "pathogen": "Bipolaris oryzae (fungus)",
        "symptoms": [
            "Oval to circular brown spots on leaves",
            "Spots have gray centers",
            "Spots surrounded by yellow halo",
            "Seeds may be discolored"
        ],
        "causes": [
            "Poor soil fertility",
            "Potassium deficiency",
            "Drought stress",
            "Old or weak plants"
        ],
        "treatment_organic": [
            "Improve soil fertility",
            "Apply potash fertilizer",
            "Use farmyard manure",
            "Proper water management",
            "Remove infected residues"
        ],
        "treatment_chemical": [
            "Mancozeb - 2.5 g/L",
            "Propiconazole - 1 ml/L",
            "Carbendazim - 1 g/L",
            "Apply at tillering and booting stages"
        ],
        "prevention": [
            "Balanced fertilization (NPK)",
            "Use healthy seeds",
            "Proper water management",
            "Crop rotation",
            "Soil testing"
        ],
        "severity_indicators": {
            "mild": "Few spots on lower leaves",
            "moderate": "Multiple leaves affected, some grain discoloration",
            "severe": "Defoliation, poor grain filling"
        }
    },

    # =========================================================
    # MAIZE DISEASES
    # =========================================================
    "maize_common_rust": {
        "crop": "maize",
        "disease": "Common Rust",
        "pathogen": "Puccinia sorghi (fungus)",
        "symptoms": [
            "Small circular to elongated pustules",
            "Reddish-brown spores on both leaf surfaces",
            "Pustules rupture releasing powdery spores",
            "Severe infection causes leaf drying"
        ],
        "causes": [
            "Cool, humid weather (16-23°C)",
            "Dew formation on leaves",
            "Wind-borne spores",
            "Late planting"
        ],
        "treatment_organic": [
            "Plant early to avoid peak rust season",
            "Use resistant hybrids",
            "Remove volunteer corn plants",
            "Crop rotation",
            "Balanced fertilization"
        ],
        "treatment_chemical": [
            "Propiconazole - 1 ml/L",
            "Tebuconazole - 1 ml/L",
            "Mancozeb - 2.5 g/L (preventive)",
            "Apply at first signs, repeat in 10-14 days"
        ],
        "prevention": [
            "Plant resistant hybrids",
            "Early planting",
            "Crop rotation",
            "Destroy crop residues",
            "Monitor fields regularly"
        ],
        "severity_indicators": {
            "mild": "Few pustules on lower leaves",
            "moderate": "Pustules on ear leaf and above",
            "severe": "Extensive leaf coverage, premature drying"
        }
    },

    "maize_gray_leaf_spot": {
        "crop": "maize",
        "disease": "Gray Leaf Spot",
        "pathogen": "Cercospora zeae-maydis (fungus)",
        "symptoms": [
            "Rectangular gray to tan lesions",
            "Lesions bounded by leaf veins",
            "Lesions coalesce in severe cases",
            "Lower leaves affected first"
        ],
        "causes": [
            "Warm, humid weather",
            "Continuous corn cultivation",
            "Reduced tillage",
            "Infected crop residues"
        ],
        "treatment_organic": [
            "Rotate crops (non-host crops)",
            "Till crop residues",
            "Use resistant hybrids",
            "Balanced nutrition",
            "Proper spacing"
        ],
        "treatment_chemical": [
            "Azoxystrobin - 0.5 ml/L",
            "Propiconazole - 1 ml/L",
            "Pyraclostrobin - as per label",
            "Apply at VT-R1 stage if needed"
        ],
        "prevention": [
            "Plant resistant hybrids",
            "Rotate crops",
            "Till infested residues",
            "Adequate plant spacing",
            "Scout fields regularly"
        ],
        "severity_indicators": {
            "mild": "Lesions below ear leaf",
            "moderate": "Lesions on ear leaf and above",
            "severe": "Extensive leaf damage before grain fill"
        }
    },

    "maize_northern_leaf_blight": {
        "crop": "maize",
        "disease": "Northern Leaf Blight",
        "pathogen": "Exserohilum turcicum (fungus)",
        "symptoms": [
            "Long, elliptical gray-green lesions",
            "Lesions 2-6 inches long",
            "Lesions resemble cigar shape",
            "Upper leaves affected in severe cases"
        ],
        "causes": [
            "Moderate temperatures (20-27°C)",
            "High humidity",
            "Infected crop residues",
            "Continuous corn"
        ],
        "treatment_organic": [
            "Rotate crops",
            "Till crop residues",
            "Use resistant hybrids",
            "Balanced fertilization",
            "Proper plant population"
        ],
        "treatment_chemical": [
            "Azoxystrobin + Propiconazole",
            "Pyraclostrobin - as per label",
            "Mancozeb - 2.5 g/L (preventive)",
            "Apply at tasseling if disease present"
        ],
        "prevention": [
            "Plant resistant hybrids",
            "Rotate with non-host crops",
            "Till residues",
            "Avoid continuous corn",
            "Scout from V8 stage"
        ],
        "severity_indicators": {
            "mild": "Lesions on lower leaves only",
            "moderate": "Lesions reaching ear leaf",
            "severe": "Lesions on upper leaves before dent stage"
        }
    },

    # =========================================================
    # APPLE DISEASES
    # =========================================================
    "apple_scab": {
        "crop": "apple",
        "disease": "Apple Scab",
        "pathogen": "Venturia inaequalis (fungus)",
        "symptoms": [
            "Olive-green to dark spots on leaves",
            "Velvety texture on leaf spots",
            "Scabby lesions on fruit",
            "Premature leaf drop"
        ],
        "causes": [
            "Cool, wet spring weather",
            "Prolonged leaf wetness",
            "Infected fallen leaves",
            "High humidity"
        ],
        "treatment_organic": [
            "Rake and destroy fallen leaves",
            "Apply copper fungicide in fall",
            "Use sulfur sprays in spring",
            "Prune for air circulation",
            "Plant resistant varieties"
        ],
        "treatment_chemical": [
            "Captan - 2 g/L",
            "Myclobutanil - 0.5 g/L",
            "Dodine - 1-2 g/L",
            "Apply from green tip to fruit set"
        ],
        "prevention": [
            "Plant scab-resistant varieties",
            "Remove fallen leaves",
            "Prune for airflow",
            "Apply fungicides preventively",
            "Avoid overhead irrigation"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots, minimal fruit damage",
            "moderate": "Multiple leaves affected, some fruit scab",
            "severe": "Defoliation, extensive fruit damage"
        }
    },

    "apple_black_rot": {
        "crop": "apple",
        "disease": "Black Rot",
        "pathogen": "Botryosphaeria obtusa (fungus)",
        "symptoms": [
            "Frog-eye leaf spots (purple margin, tan center)",
            "Fruit rot: brown, firm, with black pycnidia",
            "Cankers on branches",
            "Mummified fruit"
        ],
        "causes": [
            "Warm, humid weather",
            "Pruning wounds",
            "Winter injury",
            "Infected branches and fruit"
        ],
        "treatment_organic": [
            "Prune out dead branches and cankers",
            "Remove mummified fruit",
            "Improve tree vigor",
            "Apply copper fungicide in dormancy",
            "Proper pruning techniques"
        ],
        "treatment_chemical": [
            "Captan - 2 g/L",
            "Myclobutanil - 0.5 g/L",
            "Apply from pink bud through summer",
            "Post-harvest sprays if needed"
        ],
        "prevention": [
            "Remove dead wood and mummies",
            "Proper pruning and training",
            "Avoid winter injury",
            "Maintain tree vigor",
            "Fungicide sprays during growing season"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots, minimal fruit rot",
            "moderate": "Multiple branches with cankers, some fruit loss",
            "severe": "Extensive cankers, major fruit loss"
        }
    },

    "apple_cedar_apple_rust": {
        "crop": "apple",
        "disease": "Cedar Apple Rust",
        "pathogen": "Gymnosporangium juniperi-virginianae (fungus)",
        "symptoms": [
            "Bright orange-yellow spots on leaves",
            "Tube-like structures on leaf undersides",
            "Spots on fruit (green to orange)",
            "Requires juniper as alternate host"
        ],
        "causes": [
            "Presence of juniper trees nearby",
            "Wet spring weather",
            "Spores from juniper galls",
            "Wind dispersal"
        ],
        "treatment_organic": [
            "Remove nearby juniper trees if possible",
            "Rake and destroy fallen leaves",
            "Apply sulfur sprays",
            "Prune juniper galls in spring",
            "Plant resistant varieties"
        ],
        "treatment_chemical": [
            "Myclobutanil - 0.5 g/L",
            "Triadimefon - 0.5 g/L",
            "Apply from pink bud to petal fall",
            "Repeat every 10-14 days if wet"
        ],
        "prevention": [
            "Plant resistant apple varieties",
            "Remove junipers within 4 miles",
            "Fungicide sprays in spring",
            "Monitor weather conditions",
            "Prune juniper galls"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots, minimal defoliation",
            "moderate": "Multiple leaves spotted, some fruit infection",
            "severe": "Defoliation, fruit drop, reduced vigor"
        }
    },

    # =========================================================
    # MANGO DISEASES
    # =========================================================
    "mango_anthracnose": {
        "crop": "mango",
        "disease": "Anthracnose",
        "pathogen": "Colletotrichum gloeosporioides (fungus)",
        "symptoms": [
            "Black spots on leaves, flowers, and fruit",
            "Leaf spots enlarge and coalesce",
            "Flower blight and drop",
            "Fruit rot with tear-streak pattern"
        ],
        "causes": [
            "Warm, wet weather",
            "High humidity",
            "Rainfall during flowering",
            "Infected plant debris"
        ],
        "treatment_organic": [
            "Prune and destroy infected parts",
            "Apply copper fungicide after harvest",
            "Improve air circulation",
            "Remove fallen leaves and fruit",
            "Hot water treatment of fruit (52°C for 5 min)"
        ],
        "treatment_chemical": [
            "Carbendazim - 1 g/L",
            "Mancozeb - 2.5 g/L",
            "Azoxystrobin - 0.5 ml/L",
            "Apply at flowering and fruit development"
        ],
        "prevention": [
            "Prune for airflow",
            "Remove infected debris",
            "Fungicide sprays during wet season",
            "Post-harvest hot water treatment",
            "Plant in well-drained areas"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots, minimal fruit damage",
            "moderate": "Flower infection, some fruit rot",
            "severe": "Complete flower blight, extensive fruit rot"
        }
    },

    "mango_powdery_mildew": {
        "crop": "mango",
        "disease": "Powdery Mildew",
        "pathogen": "Oidium mangiferae (fungus)",
        "symptoms": [
            "White to gray powdery growth on flowers and young fruit",
            "Flower drop and fruit malformation",
            "Leaf curling and distortion",
            "Affected parts turn brown and die"
        ],
        "causes": [
            "Cool, dry weather",
            "High humidity but no rain",
            "Dense canopy",
            "Moderate temperatures (20-25°C)"
        ],
        "treatment_organic": [
            "Apply sulfur dust or wettable sulfur",
            "Improve air circulation",
            "Prune dense canopy",
            "Use biocontrol (Ampelomyces quisqualis)",
            "Neem oil spray"
        ],
        "treatment_chemical": [
            "Carbendazim - 1 g/L",
            "Hexaconazole - 1 ml/L",
            "Wettable sulfur - 2 g/L",
            "Apply at panicle emergence and flowering"
        ],
        "prevention": [
            "Prune for airflow",
            "Avoid dense planting",
            "Sulfur sprays during dry cool weather",
            "Monitor during flowering",
            "Remove infected parts"
        ],
        "severity_indicators": {
            "mild": "Few panicles affected",
            "moderate": "Multiple panicles with mildew, some fruit drop",
            "severe": "Complete panicle infection, major fruit loss"
        }
    },

    "mango_bacterial_canker": {
        "crop": "mango",
        "disease": "Bacterial Canker",
        "pathogen": "Xanthomonas campestris pv. mangiferaeindicae (bacterium)",
        "symptoms": [
            "Brown cankers on branches",
            "Leaf spots with yellow halo",
            "Fruit spots with cracking",
            "Gum oozing from cankers"
        ],
        "causes": [
            "Warm, humid weather",
            "Rain and wind dispersal",
            "Pruning wounds",
            "Infected tools"
        ],
        "treatment_organic": [
            "Prune infected branches 15 cm below canker",
            "Disinfect tools between cuts",
            "Apply copper fungicide after pruning",
            "Improve tree vigor",
            "Avoid overhead irrigation"
        ],
        "treatment_chemical": [
            "Copper oxychloride - 3 g/L",
            "Streptomycin sulfate - 0.1 g/L + Copper",
            "Apply after pruning and before monsoon",
            "Repeat every 15 days during wet season"
        ],
        "prevention": [
            "Use disease-free planting material",
            "Disinfect pruning tools",
            "Prune during dry weather",
            "Copper sprays before and after monsoon",
            "Maintain tree health"
        ],
        "severity_indicators": {
            "mild": "Few branch cankers",
            "moderate": "Multiple branches affected, some fruit damage",
            "severe": "Extensive cankering, branch death, fruit loss"
        }
    },

    # =========================================================
    # GRAPE DISEASES
    # =========================================================
    "grape_black_rot": {
        "crop": "grape",
        "disease": "Black Rot",
        "pathogen": "Guignardia bidwellii (fungus)",
        "symptoms": [
            "Circular tan spots on leaves with dark borders",
            "Black pycnidia in spot centers",
            "Fruit: brown rot progressing to black mummies",
            "Shoot lesions"
        ],
        "causes": [
            "Warm, wet weather",
            "Infected mummified fruit",
            "Overwintering in cane lesions",
            "Rain splash dispersal"
        ],
        "treatment_organic": [
            "Remove and destroy mummified fruit",
            "Prune out infected canes",
            "Apply copper fungicide in dormancy",
            "Improve air circulation",
            "Clear leaf debris"
        ],
        "treatment_chemical": [
            "Myclobutanil - 0.5 g/L",
            "Mancozeb - 2.5 g/L",
            "Captan - 2 g/L",
            "Apply from shoot growth to veraison"
        ],
        "prevention": [
            "Remove mummies and debris",
            "Proper pruning for airflow",
            "Fungicide sprays during wet weather",
            "Sanitation is critical",
            "Plant resistant varieties"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots, minimal fruit rot",
            "moderate": "Multiple leaves and some fruit affected",
            "severe": "Extensive fruit rot, major crop loss"
        }
    },

    "grape_esca": {
        "crop": "grape",
        "disease": "Esca (Black Measles)",
        "pathogen": "Complex: Phaeomoniella chlamydospora, Fomitiporia mediterranea",
        "symptoms": [
            "Interveinal chlorosis and necrosis",
            "Tiger-stripe pattern on leaves",
            "Black streaks in wood",
            "Sudden vine decline (apoplexy)"
        ],
        "causes": [
            "Wounds from pruning",
            "Old vineyards",
            "Multiple fungal pathogens",
            "Stressed vines"
        ],
        "treatment_organic": [
            "No effective cure once established",
            "Prune out infected wood (5 cm below symptoms)",
            "Apply biological control (Trichoderma)",
            "Improve vine vigor",
            "Remove severely infected vines"
        ],
        "treatment_chemical": [
            "No effective chemical control",
            "Preventive: fungicide on pruning wounds",
            "Sodium arsenite (restricted use)",
            "Focus on prevention"
        ],
        "prevention": [
            "Disinfect pruning tools",
            "Prune during dry weather",
            "Apply protectants to pruning wounds",
            "Avoid excessive pruning",
            "Maintain vine vigor"
        ],
        "severity_indicators": {
            "mild": "Few leaves with tiger-stripe",
            "moderate": "Multiple shoots affected, reduced vigor",
            "severe": "Vine decline, apoplexy, death"
        }
    },

    "grape_leaf_blight": {
        "crop": "grape",
        "disease": "Leaf Blight",
        "pathogen": "Pseudocercospora vitis (fungus)",
        "symptoms": [
            "Brown necrotic spots on leaves",
            "Spots coalesce causing blighting",
            "Premature defoliation",
            "Reduced vine vigor"
        ],
        "causes": [
            "Warm, humid conditions",
            "Poor air circulation",
            "Dense canopy",
            "Infected debris"
        ],
        "treatment_organic": [
            "Remove infected leaves",
            "Improve air circulation",
            "Apply copper fungicide",
            "Clear fallen debris",
            "Proper canopy management"
        ],
        "treatment_chemical": [
            "Mancozeb - 2.5 g/L",
            "Captan - 2 g/L",
            "Myclobutanil - 0.5 g/L",
            "Apply during wet weather"
        ],
        "prevention": [
            "Proper pruning for airflow",
            "Remove debris",
            "Fungicide sprays in wet seasons",
            "Canopy management",
            "Balanced nutrition"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots",
            "moderate": "Multiple leaves blighted, some defoliation",
            "severe": "Extensive defoliation, reduced yield"
        }
    },

    # =========================================================
    # COTTON DISEASES
    # =========================================================
    "cotton_bacterial_blight": {
        "crop": "cotton",
        "disease": "Bacterial Blight",
        "pathogen": "Xanthomonas citri pv. malvacearum (bacterium)",
        "symptoms": [
            "Angular water-soaked leaf spots",
            "Spots turn brown with yellow halo",
            "Black veins and stem lesions",
            "Boll rot with yellowish exudate"
        ],
        "causes": [
            "Warm, wet weather",
            "Infected seeds",
            "Rain splash dispersal",
            "Infected crop debris"
        ],
        "treatment_organic": [
            "Use certified disease-free seeds",
            "Remove infected plant debris",
            "Apply copper-based sprays",
            "Crop rotation",
            "Proper spacing"
        ],
        "treatment_chemical": [
            "Copper hydroxide - 2 g/L",
            "Streptomycin + Copper combination",
            "Apply at first symptoms",
            "Repeat every 10-14 days if wet"
        ],
        "prevention": [
            "Use certified clean seeds",
            "Treat seeds with hot water",
            "Rotate crops",
            "Remove crop residues",
            "Plant resistant varieties"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots, minimal boll infection",
            "moderate": "Multiple leaves and some bolls affected",
            "severe": "Defoliation, extensive boll rot"
        }
    },

    "cotton_leaf_curl_virus": {
        "crop": "cotton",
        "disease": "Leaf Curl Virus",
        "pathogen": "Cotton leaf curl virus (CLCuV) - transmitted by whitefly",
        "symptoms": [
            "Upward curling of leaves",
            "Thickening of leaf veins",
            "Stunted plant growth",
            "Reduced boll formation"
        ],
        "causes": [
            "Whitefly vector (Bemisia tabaci)",
            "Infected planting material",
            "Weed hosts",
            "Warm, dry weather favoring whiteflies"
        ],
        "treatment_organic": [
            "No cure - remove infected plants",
            "Control whiteflies with neem oil",
            "Use yellow sticky traps",
            "Remove weed hosts",
            "Reflective mulches"
        ],
        "treatment_chemical": [
            "No direct treatment for virus",
            "Control whiteflies: Imidacloprid 0.5 ml/L",
            "Thiamethoxam - 0.3 g/L",
            "Spray early to prevent spread"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Control whitefly vectors",
            "Remove infected plants early",
            "Destroy weed hosts",
            "Use healthy seeds"
        ],
        "severity_indicators": {
            "mild": "Few plants with leaf curl",
            "moderate": "Multiple plants affected, some yield loss",
            "severe": "Widespread infection, severe yield loss"
        }
    },

    "cotton_boll_rot": {
        "crop": "cotton",
        "disease": "Boll Rot",
        "pathogen": "Multiple: Phytophthora, Rhizopus, Alternaria, bacteria",
        "symptoms": [
            "Water-soaked spots on bolls",
            "Bolls turn brown/black and rot",
            "Cotton fibers stained and degraded",
            "Foul odor in bacterial rot"
        ],
        "causes": [
            "Warm, humid weather",
            "Excessive rainfall",
            "Dense canopy",
            "Insect damage to bolls"
        ],
        "treatment_organic": [
            "Improve drainage",
            "Reduce plant density",
            "Remove infected bolls",
            "Apply copper sprays",
            "Control bollworms"
        ],
        "treatment_chemical": [
            "Mancozeb - 2.5 g/L",
            "Carbendazim - 1 g/L",
            "Copper oxychloride - 3 g/L",
            "Apply during wet weather"
        ],
        "prevention": [
            "Proper spacing",
            "Good drainage",
            "Control insect pests",
            "Balanced fertilization",
            "Timely harvesting"
        ],
        "severity_indicators": {
            "mild": "Few bolls affected",
            "moderate": "Multiple bolls rotting, some yield loss",
            "severe": "Extensive boll rot, major yield loss"
        }
    },

    # =========================================================
    # PEAS DISEASES
    # =========================================================
    "peas_powdery_mildew": {
        "crop": "peas",
        "disease": "Powdery Mildew",
        "pathogen": "Erysiphe pisi (fungus)",
        "symptoms": [
            "White powdery growth on leaves and stems",
            "Leaves curl and wither",
            "Premature defoliation",
            "Reduced pod formation"
        ],
        "causes": [
            "Warm, dry days with cool nights",
            "High humidity",
            "Dense canopy",
            "Moderate temperatures (20-25°C)"
        ],
        "treatment_organic": [
            "Apply sulfur dust or spray",
            "Neem oil spray (2-3 ml/L)",
            "Baking soda spray (1 tbsp/L)",
            "Improve air circulation",
            "Remove infected parts"
        ],
        "treatment_chemical": [
            "Carbendazim - 1 g/L",
            "Hexaconazole - 1 ml/L",
            "Wettable sulfur - 2 g/L",
            "Apply at first symptoms"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Proper spacing",
            "Avoid late planting",
            "Good air circulation",
            "Crop rotation"
        ],
        "severity_indicators": {
            "mild": "Few leaves with powdery growth",
            "moderate": "Multiple leaves and stems affected",
            "severe": "Complete coverage, defoliation, yield loss"
        }
    },

    "peas_rust": {
        "crop": "peas",
        "disease": "Rust",
        "pathogen": "Uromyces pisi (fungus)",
        "symptoms": [
            "Small circular rust-colored pustules",
            "Pustules on leaves, stems, and pods",
            "Surrounded by yellow halo",
            "Premature leaf drop"
        ],
        "causes": [
            "Cool, moist weather",
            "Dew formation",
            "Infected crop debris",
            "Moderate temperatures (15-22°C)"
        ],
        "treatment_organic": [
            "Remove infected plant parts",
            "Apply sulfur sprays",
            "Improve air circulation",
            "Crop rotation",
            "Remove crop debris"
        ],
        "treatment_chemical": [
            "Mancozeb - 2.5 g/L",
            "Propiconazole - 1 ml/L",
            "Carbendazim - 1 g/L",
            "Apply at first symptoms"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Rotate crops",
            "Proper spacing",
            "Remove crop debris",
            "Early planting"
        ],
        "severity_indicators": {
            "mild": "Few pustules on lower leaves",
            "moderate": "Multiple leaves and pods affected",
            "severe": "Extensive infection, defoliation, reduced yield"
        }
    },

    "peas_bacterial_blight": {
        "crop": "peas",
        "disease": "Bacterial Blight",
        "pathogen": "Pseudomonas syringae pv. pisi (bacterium)",
        "symptoms": [
            "Water-soaked spots on leaves",
            "Spots turn brown with yellow halo",
            "Stem lesions and wilting",
            "Pod spots with yellow border"
        ],
        "causes": [
            "Cool, wet weather",
            "Infected seeds",
            "Rain splash",
            "Infected debris"
        ],
        "treatment_organic": [
            "Use disease-free seeds",
            "Remove infected plants",
            "Apply copper sprays",
            "Crop rotation",
            "Proper spacing"
        ],
        "treatment_chemical": [
            "Copper hydroxide - 2 g/L",
            "Streptomycin + Copper",
            "Apply at first symptoms",
            "Repeat in 7-10 days"
        ],
        "prevention": [
            "Use certified clean seeds",
            "Treat seeds with hot water",
            "Rotate crops (3 years)",
            "Remove crop debris",
            "Avoid working in wet fields"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots",
            "moderate": "Multiple leaves and stems affected",
            "severe": "Widespread blighting, yield loss"
        }
    },

    # =========================================================
    # SUNFLOWER DISEASES
    # =========================================================
    "sunflower_downy_mildew": {
        "crop": "sunflower",
        "disease": "Downy Mildew",
        "pathogen": "Plasmopara halstedii (oomycete)",
        "symptoms": [
            "Chlorosis along veins",
            "White downy growth on leaf undersides",
            "Stunted, distorted plants",
            "Systemic infection causes dwarfing"
        ],
        "causes": [
            "Cool, wet conditions",
            "Infected seeds",
            "Soil-borne oospores",
            "Moderate temperatures (15-20°C)"
        ],
        "treatment_organic": [
            "Use resistant hybrids",
            "Treat seeds with biocontrol agents",
            "Improve drainage",
            "Crop rotation",
            "Remove infected plants"
        ],
        "treatment_chemical": [
            "Metalaxyl seed treatment",
            "Fosetyl-Al - 2 g/L",
            "Mancozeb - 2.5 g/L",
            "Apply preventively in wet seasons"
        ],
        "prevention": [
            "Plant resistant hybrids",
            "Use fungicide-treated seeds",
            "Rotate crops",
            "Good drainage",
            "Avoid early planting in cold soils"
        ],
        "severity_indicators": {
            "mild": "Few plants with systemic infection",
            "moderate": "Multiple plants affected, some stunting",
            "severe": "Widespread dwarfing, major yield loss"
        }
    },

    "sunflower_rust": {
        "crop": "sunflower",
        "disease": "Rust",
        "pathogen": "Puccinia helianthi (fungus)",
        "symptoms": [
            "Small orange-brown pustules on leaves",
            "Pustules on stems and petioles",
            "Premature senescence",
            "Reduced seed size and yield"
        ],
        "causes": [
            "Moderate temperatures (15-25°C)",
            "High humidity",
            "Dew formation",
            "Wind-borne spores"
        ],
        "treatment_organic": [
            "Plant resistant hybrids",
            "Remove volunteer sunflowers",
            "Crop rotation",
            "Balanced fertilization",
            "Remove crop debris"
        ],
        "treatment_chemical": [
            "Propiconazole - 1 ml/L",
            "Tebuconazole - 1 ml/L",
            "Mancozeb - 2.5 g/L (preventive)",
            "Apply at first signs"
        ],
        "prevention": [
            "Plant resistant hybrids",
            "Rotate crops",
            "Destroy volunteer plants",
            "Balanced nutrition",
            "Scout fields regularly"
        ],
        "severity_indicators": {
            "mild": "Few pustules on lower leaves",
            "moderate": "Pustules on multiple leaves and stems",
            "severe": "Extensive infection, premature death"
        }
    },

    "sunflower_leaf_spot": {
        "crop": "sunflower",
        "disease": "Leaf Spot",
        "pathogen": "Alternaria helianthi (fungus)",
        "symptoms": [
            "Circular to irregular brown spots",
            "Spots with yellow halo",
            "Spots coalesce in severe cases",
            "Premature defoliation"
        ],
        "causes": [
            "Warm, humid weather",
            "Infected crop debris",
            "Rain splash",
            "Dense canopy"
        ],
        "treatment_organic": [
            "Remove infected leaves",
            "Apply copper sprays",
            "Improve air circulation",
            "Crop rotation",
            "Remove debris"
        ],
        "treatment_chemical": [
            "Mancozeb - 2.5 g/L",
            "Chlorothalonil - 2 g/L",
            "Carbendazim - 1 g/L",
            "Apply at first symptoms"
        ],
        "prevention": [
            "Rotate crops",
            "Proper spacing",
            "Remove crop debris",
            "Balanced fertilization",
            "Avoid overhead irrigation"
        ],
        "severity_indicators": {
            "mild": "Few spots on lower leaves",
            "moderate": "Multiple leaves affected, some defoliation",
            "severe": "Extensive defoliation, yield loss"
        }
    },

    # =========================================================
    # PEPPER DISEASES
    # =========================================================
    "pepper_thrips_damage": {
        "crop": "pepper",
        "disease": "Thrips Damage",
        "pathogen": "Thrips palmi / Scirtothrips dorsalis (insect pest)",
        "symptoms": [
            "Silvering of leaves",
            "Leaf curling and distortion",
            "Scarring on fruit",
            "Transmission of virus diseases"
        ],
        "causes": [
            "Hot, dry weather",
            "Weed hosts nearby",
            "Infested planting material",
            "Poor field sanitation"
        ],
        "treatment_organic": [
            "Neem oil spray (3 ml/L)",
            "Yellow sticky traps",
            "Blue sticky traps",
            "Reflective mulches",
            "Biocontrol: predatory mites"
        ],
        "treatment_chemical": [
            "Imidacloprid - 0.5 ml/L",
            "Thiamethoxam - 0.3 g/L",
            "Spinosad - 0.5 ml/L",
            "Spray undersides of leaves"
        ],
        "prevention": [
            "Remove weed hosts",
            "Use reflective mulches",
            "Monitor with sticky traps",
            "Encourage natural enemies",
            "Avoid overhead irrigation"
        ],
        "severity_indicators": {
            "mild": "Few leaves with silvering",
            "moderate": "Multiple leaves and some fruit affected",
            "severe": "Extensive damage, virus transmission"
        }
    },

    "pepper_blight": {
        "crop": "pepper",
        "disease": "Blight",
        "pathogen": "Phytophthora capsici (oomycete)",
        "symptoms": [
            "Water-soaked lesions on leaves",
            "Rapid wilting and collapse",
            "Stem lesions and girdling",
            "Fruit rot with water-soaked appearance"
        ],
        "causes": [
            "Warm, wet weather",
            "Poor drainage",
            "Infected soil",
            "Rain splash"
        ],
        "treatment_organic": [
            "Improve drainage",
            "Remove infected plants",
            "Apply copper fungicide",
            "Raise beds",
            "Crop rotation"
        ],
        "treatment_chemical": [
            "Metalaxyl + Mancozeb - 2.5 g/L",
            "Fosetyl-Al - 2 g/L",
            "Copper hydroxide - 2 g/L",
            "Apply preventively in wet weather"
        ],
        "prevention": [
            "Well-drained fields",
            "Raised beds",
            "Crop rotation (3-4 years)",
            "Resistant varieties",
            "Avoid overhead irrigation"
        ],
        "severity_indicators": {
            "mild": "Few plants with leaf lesions",
            "moderate": "Multiple plants wilting, some fruit rot",
            "severe": "Plant collapse, extensive fruit rot"
        }
    },

    "pepper_mites": {
        "crop": "pepper",
        "disease": "Mites",
        "pathogen": "Polyphagotarsonemus latus / Tetranychus spp. (mite pests)",
        "symptoms": [
            "Bronzing of leaves",
            "Leaf curling downward",
            "Fine webbing on undersides",
            "Reduced plant vigor"
        ],
        "causes": [
            "Hot, dry weather",
            "Dust on leaves",
            "Stressed plants",
            "Broad mite transmission"
        ],
        "treatment_organic": [
            "Spray with water to dislodge mites",
            "Neem oil spray (3 ml/L)",
            "Sulfur dust",
            "Predatory mites (biocontrol)",
            "Maintain plant health"
        ],
        "treatment_chemical": [
            "Abamectin - 0.5 ml/L",
            "Spiromesifen - 0.5 ml/L",
            "Dicofol - 2 ml/L",
            "Spray undersides of leaves"
        ],
        "prevention": [
            "Avoid dust accumulation",
            "Maintain humidity",
            "Monitor regularly",
            "Healthy plant nutrition",
            "Encourage natural enemies"
        ],
        "severity_indicators": {
            "mild": "Few leaves with bronzing",
            "moderate": "Multiple leaves affected, some curling",
            "severe": "Extensive bronzing, defoliation"
        }
    },

    "pepper_spot": {
        "crop": "pepper",
        "disease": "Bacterial Spot",
        "pathogen": "Xanthomonas campestris pv. vesicatoria (bacterium)",
        "symptoms": [
            "Small water-soaked spots on leaves",
            "Spots turn brown with yellow halo",
            "Raised scabby spots on fruit",
            "Defoliation in severe cases"
        ],
        "causes": [
            "Warm, wet weather",
            "Infected seeds",
            "Rain splash",
            "Infected debris"
        ],
        "treatment_organic": [
            "Use disease-free seeds",
            "Remove infected plants",
            "Copper sprays",
            "Crop rotation",
            "Proper spacing"
        ],
        "treatment_chemical": [
            "Copper hydroxide - 2 g/L",
            "Streptomycin + Copper",
            "Mancozeb - 2.5 g/L",
            "Apply at first symptoms"
        ],
        "prevention": [
            "Certified clean seeds",
            "Hot water seed treatment",
            "Rotate crops",
            "Avoid working in wet fields",
            "Remove crop debris"
        ],
        "severity_indicators": {
            "mild": "Few leaf spots",
            "moderate": "Multiple leaves and some fruit affected",
            "severe": "Defoliation, extensive fruit scabbing"
        }
    }
}

# =========================================================
# CROP-SPECIFIC SEASONAL GUIDANCE FOR PAKISTAN
# =========================================================
CROP_SEASONAL_GUIDE = {
    "tomato": {
        "seasons": {
            "spring": {
                "planting": "February-March",
                "harvest": "May-July",
                "disease_risks": ["Early Blight", "Late Blight", "Leaf Mold"],
                "weather_concerns": "Spring rains increase fungal disease risk. Ensure drainage.",
                "prevention_tips": "Apply preventive fungicide before monsoon. Space plants 60cm apart."
            },
            "autumn": {
                "planting": "August-September",
                "harvest": "November-January",
                "disease_risks": ["Late Blight", "Mosaic Virus", "Septoria Leaf Spot"],
                "weather_concerns": "Cool nights with warm days create condensation. Morning fog increases humidity.",
                "prevention_tips": "Use resistant varieties. Avoid overhead irrigation in evening."
            }
        },
        "fertilizer_schedule": "Apply NPK 13-40-13 at transplanting (50kg/acre). Top dress with urea (30kg/acre) at flowering. Add potassium sulfate (25kg/acre) for fruit quality.",
        "common_mistakes": "Over-watering, planting too close, ignoring lower leaf symptoms"
    },
    "potato": {
        "seasons": {
            "winter": {
                "planting": "October-November",
                "harvest": "January-March",
                "disease_risks": ["Late Blight", "Early Blight"],
                "weather_concerns": "Fog and dew in December-January create ideal blight conditions.",
                "prevention_tips": "Use certified seed tubers. Apply Ridomil preventively when humidity >90%."
            }
        },
        "fertilizer_schedule": "Apply DAP (100kg/acre) and urea (50kg/acre) at planting. Earthing up at 30 days. Add potash (40kg/acre) for tuber size.",
        "common_mistakes": "Using infected seed potatoes, delayed blight spray, waterlogging"
    },
    "rice": {
        "seasons": {
            "kharif": {
                "planting": "June-July",
                "harvest": "October-November",
                "disease_risks": ["Rice Blast", "Bacterial Leaf Blight", "Brown Spot"],
                "weather_concerns": "High humidity and temperature (30-35°C) during monsoon. Excessive nitrogen increases blast risk.",
                "prevention_tips": "Use resistant varieties (Basmati 385, Super Basmati). Avoid excess urea. Ensure field drainage."
            }
        },
        "fertilizer_schedule": "Apply DAP (80kg/acre) at transplanting. Split urea application: 40kg at transplanting, 40kg at tillering, 30kg at panicle initiation. Add zinc sulfate (10kg/acre) if deficient.",
        "common_mistakes": "Excess nitrogen, stagnant water, late planting"
    },
    "maize": {
        "seasons": {
            "kharif": {
                "planting": "April-May (spring), June-July (monsoon)",
                "harvest": "August-September (spring), October-November (monsoon)",
                "disease_risks": ["Common Rust", "Gray Leaf Spot", "Northern Leaf Blight"],
                "weather_concerns": "Rust spreads in warm humid weather (25-30°C). Leaf spots thrive in rain.",
                "prevention_tips": "Plant resistant hybrids. Apply fungicide at tasseling if rust appears."
            }
        },
        "fertilizer_schedule": "Apply NPK 18-46-0 (50kg/acre) at planting. Top dress with urea (60kg/acre) at knee-high stage. Split application for better uptake.",
        "common_mistakes": "Late planting, excess nitrogen, ignoring rust symptoms"
    },
    "cotton": {
        "seasons": {
            "kharif": {
                "planting": "April-May",
                "harvest": "September-November",
                "disease_risks": ["Leaf Curl Virus", "Bacterial Blight", "Boll Rot"],
                "weather_concerns": "Whitefly spreads virus in hot dry weather. Monsoon humidity causes boll rot.",
                "prevention_tips": "Use virus-resistant varieties. Control whitefly early with imidacloprid. Avoid late-season irrigation."
            }
        },
        "fertilizer_schedule": "Apply DAP (80kg/acre) at planting. Top dress with urea (50kg/acre) at flowering. Add potash (30kg/acre) for boll development.",
        "common_mistakes": "Late sowing, ignoring whitefly, excess irrigation during boll formation"
    },
    "wheat": {
        "seasons": {
            "rabi": {
                "planting": "November-December",
                "harvest": "April-May",
                "disease_risks": ["Rust (leaf, stem, stripe)", "Powdery Mildew", "Septoria Glume Blotch"],
                "weather_concerns": "Cool moist weather (15-22°C) favors rust. Late sowing increases disease risk.",
                "prevention_tips": "Use resistant varieties (Punjab-11, Faisalabad-08). Apply fungicide at boot stage if rust appears."
            }
        },
        "fertilizer_schedule": "Apply DAP (100kg/acre) at planting. Top dress with urea (75kg/acre) in two splits: at tillering and boot stage.",
        "common_mistakes": "Late sowing, single urea application, ignoring early rust symptoms"
    }
}

# =========================================================
# HOMEMADE / ORGANIC REMEDIES WITH SPECIFIC RECIPES
# =========================================================
HOMEMADE_REMEDIES = {
    "neem_oil_spray": {
        "recipe": "Mix 5ml neem oil + 2ml liquid soap in 1 liter water",
        "uses": ["Fungal diseases", "Insect control", "Preventive spray"],
        "application": "Spray every 7-10 days in early morning or evening",
        "crops": ["tomato", "potato", "rice", "vegetables"]
    },
    "baking_soda_spray": {
        "recipe": "1 tbsp baking soda + 1 tsp liquid soap + 1 tsp vegetable oil in 4 liters water",
        "uses": ["Powdery mildew", "Leaf spot", "Early blight"],
        "application": "Spray every 7-14 days. Test on few leaves first.",
        "crops": ["tomato", "potato", "grape", "apple"]
    },
    "garlic_chili_spray": {
        "recipe": "Blend 100g garlic + 50g chili + 1 liter water. Strain. Dilute to 10 liters.",
        "uses": ["Insect repellent", "Fungal diseases", "Virus vector control"],
        "application": "Spray thoroughly on leaves, especially undersides. Repeat weekly.",
        "crops": ["all vegetables", "cotton", "wheat"]
    },
    "milk_spray": {
        "recipe": "Mix 1 part milk with 9 parts water",
        "uses": ["Powdery mildew", "Virus diseases", "Boosts plant immunity"],
        "application": "Spray every 10-14 days. Best as preventive.",
        "crops": ["tomato", "potato", "pepper", "cucumber"]
    },
    "bordeaux_mixture": {
        "recipe": "Dissolve 1kg copper sulfate in 10 liters water. In separate container, slake 1kg lime in 10 liters water. Mix both solutions slowly.",
        "uses": ["Late blight", "Early blight", "Bacterial diseases", "Downy mildew"],
        "application": "Apply preventively. Reapply after rain. Do not use on ripe fruit.",
        "crops": ["tomato", "potato", "grape", "apple", "citrus"]
    },
    "buttermilk_spray": {
        "recipe": "Mix 2 liters buttermilk in 10 liters water",
        "uses": ["Powdery mildew", "Leaf spot", "Nutrient boost"],
        "application": "Spray every 10 days. Good for organic farming.",
        "crops": ["all vegetables", "wheat", "rice"]
    },
    "ash_and_lime_dust": {
        "recipe": "Mix wood ash and slaked lime in 1:1 ratio",
        "uses": ["Snail and slug control", "Fungal prevention", "Potassium boost"],
        "application": "Dust around plant base. Apply in dry weather.",
        "crops": ["all vegetables", "potato", "tomato"]
    }
}

# =========================================================
# FERTILIZER GUIDE FOR PAKISTANI CROPS
# =========================================================
FERTILIZER_GUIDE = {
    "nitrogen_deficiency": {
        "symptoms": "Yellowing of older leaves, stunted growth, pale green color",
        "quick_fix": "Apply urea (30-50kg/acre) or ammonium sulfate. Foliar spray 2% urea solution.",
        "crops_affected": ["wheat", "rice", "maize", "vegetables"]
    },
    "phosphorus_deficiency": {
        "symptoms": "Purple or reddish leaves, poor root development, delayed maturity",
        "quick_fix": "Apply DAP (50-100kg/acre) or single super phosphate. Band placement near roots.",
        "crops_affected": ["wheat", "potato", "tomato", "maize"]
    },
    "potassium_deficiency": {
        "symptoms": "Brown leaf margins, weak stems, poor fruit quality, lodging",
        "quick_fix": "Apply potassium sulfate (30-50kg/acre) or muriate of potash. Foliar spray 1% KCl.",
        "crops_affected": ["tomato", "potato", "fruit trees", "cotton"]
    },
    "zinc_deficiency": {
        "symptoms": "Small leaves, interveinal chlorosis, rosette formation in rice",
        "quick_fix": "Apply zinc sulfate (10-15kg/acre) or foliar spray 0.5% zinc sulfate solution.",
        "crops_affected": ["rice", "maize", "wheat", "fruit trees"]
    }
}

# =========================================================
# PESTICIDE AND INSECTICIDE GUIDE
# =========================================================
PESTICIDE_GUIDE = {
    "fungicides": {
        "contact": [
            {"name": "Mancozeb", "brand": "Dithane M-45", "dose": "2.5 g/L", "target": ["Early blight", "Late blight", "Leaf spot"], "phi": "7 days"},
            {"name": "Chlorothalonil", "brand": "Daconil", "dose": "2 g/L", "target": ["Early blight", "Leaf mold", "Anthracnose"], "phi": "7 days"},
            {"name": "Copper hydroxide", "brand": "Kocide", "dose": "2 g/L", "target": ["Bacterial blight", "Downy mildew"], "phi": "10 days"}
        ],
        "systemic": [
            {"name": "Metalaxyl + Mancozeb", "brand": "Ridomil Gold", "dose": "2.5 g/L", "target": ["Late blight", "Downy mildew"], "phi": "14 days"},
            {"name": "Carbendazim", "brand": "Bavistin", "dose": "1 g/L", "target": ["Powdery mildew", "Wilt", "Root rot"], "phi": "14 days"},
            {"name": "Propiconazole", "brand": "Tilt", "dose": "1 ml/L", "target": ["Rust", "Powdery mildew", "Leaf spot"], "phi": "21 days"},
            {"name": "Azoxystrobin", "brand": "Amistar", "dose": "0.5 ml/L", "target": ["All fungal diseases"], "phi": "14 days"}
        ]
    },
    "insecticides": {
        "for_sucking_pests": [
            {"name": "Imidacloprid", "brand": "Confidor", "dose": "0.3 ml/L", "target": ["Whitefly", "Aphids", "Jassids"], "phi": "14 days"},
            {"name": "Thiamethoxam", "brand": "Actara", "dose": "0.5 g/L", "target": ["Whitefly", "Thrips", "Aphids"], "phi": "14 days"},
            {"name": "Acetamiprid", "brand": "Starke", "dose": "0.5 g/L", "target": ["Whitefly", "Aphids"], "phi": "7 days"}
        ],
        "for_chewing_pests": [
            {"name": "Chlorantraniliprole", "brand": "Coragen", "dose": "0.3 ml/L", "target": ["Bollworm", "Armyworm", "Cutworm"], "phi": "7 days"},
            {"name": "Emamectin benzoate", "brand": "Proclaim", "dose": "0.5 g/L", "target": ["Bollworm", "Leafroller", "Fruit borer"], "phi": "14 days"},
            {"name": "Lambda-cyhalothrin", "brand": "Karate", "dose": "1 ml/L", "target": ["Bollworm", "Armyworm", "Beetle"], "phi": "14 days"}
        ],
        "for_mites": [
            {"name": "Abamectin", "brand": "Vertimec", "dose": "1 ml/L", "target": ["Red mite", "Spider mite"], "phi": "14 days"},
            {"name": "Spiromesifen", "brand": "Oberon", "dose": "1 ml/L", "target": ["Red mite", "White mite"], "phi": "21 days"}
        ]
    }
}

# =========================================================
# URDU-TO-ENGLISH DISEASE / PEST NAME MAP
# =========================================================
# Maps Urdu terms (as farmers say them) to (crop, english_disease_name) pairs.
# Used so that when a farmer asks in Urdu using local names, the chatbot
# can still find the right disease in the knowledge base.
URDU_DISEASE_MAP = {
    # -- Blight / جھلس --
    "جھلس": ("potato", "Late Blight"),
    "جھلس کی بیماری": ("potato", "Late Blight"),
    "آلو کا جھلس": ("potato", "Late Blight"),
    "ٹماٹر کا جھلس": ("tomato", "Late Blight"),
    "لیٹ بلائٹ": ("potato", "Late Blight"),
    "ایرلی بلائٹ": ("tomato", "Early Blight"),
    "ابتدائی جھلس": ("tomato", "Early Blight"),

    # -- Leaf Curl / پتا لپیٹا --
    "پتا لپیٹا": ("cotton", "Leaf Curl Virus"),
    "پتوں کا لپیٹا": ("cotton", "Leaf Curl Virus"),
    "پتے لپیٹنا": ("cotton", "Leaf Curl Virus"),
    "لیف کرل": ("cotton", "Leaf Curl Virus"),

    # -- Whitefly / سفید مکھی --
    "سفید مکھی": ("cotton", "Leaf Curl Virus"),
    "سفید مکھیاں": ("cotton", "Leaf Curl Virus"),
    "وائٹ فلائی": ("cotton", "Leaf Curl Virus"),

    # -- Leaf Mold / پتے پر فنگس --
    "پتے پر فنگس": ("tomato", "Leaf Mold"),
    "پتوں پر پھپھوندی": ("tomato", "Leaf Mold"),
    "لیف مولڈ": ("tomato", "Leaf Mold"),

    # -- Powdery Mildew / سفید پاؤڈر --
    "سفید پاؤڈر": ("mango", "Powdery Mildew"),
    "پاؤڈری میلڈیو": ("mango", "Powdery Mildew"),
    "سفید چپٹ": ("mango", "Powdery Mildew"),
    "آڑ کی بیماری": ("peas", "Powdery Mildew"),

    # -- Mosaic Virus / موزیک --
    "موزیک": ("tomato", "Mosaic Virus"),
    "موزیک وائرس": ("tomato", "Mosaic Virus"),
    "پتوں کا موزیک": ("tomato", "Mosaic Virus"),

    # -- Rust / زنگ --
    "زنگ": ("peas", "Rust"),
    "زنگ کی بیماری": ("peas", "Rust"),
    "رسٹ": ("maize", "Common Rust"),

    # -- Septoria Leaf Spot / سیاہ دھبے --
    "سیاہ دھبے": ("tomato", "Septoria Leaf Spot"),
    "پتوں پر سیاہ دھبے": ("tomato", "Septoria Leaf Spot"),
    "سیپٹوریا": ("tomato", "Septoria Leaf Spot"),

    # -- Bacterial Blight / بیکٹیریل بلائٹ --
    "بیکٹیریل بلائٹ": ("cotton", "Bacterial Blight"),
    "بیکٹیریا کا جھلس": ("cotton", "Bacterial Blight"),

    # -- Boll Rot / بال کی سڑن --
    "بال کی سڑن": ("cotton", "Boll Rot"),
    "بول روٹ": ("cotton", "Boll Rot"),
    "روئی کی بال سڑنا": ("cotton", "Boll Rot"),

    # -- Apple Scab / سیب پر داغ --
    "سیب پر داغ": ("apple", "Apple Scab"),
    "ایپل اسکب": ("apple", "Apple Scab"),

    # -- Black Rot / کالا گل --
    "کالا گل": ("apple", "Black Rot"),
    "بلیک روٹ": ("grape", "Black Rot"),

    # -- Anthracnose / اینتھریکنوز --
    "اینتھریکنوز": ("mango", "Anthracnose"),
    "پھل کا گلنا": ("mango", "Anthracnose"),

    # -- Bacterial Canker / بیکٹیریل کینکر --
    "بیکٹیریل کینکر": ("mango", "Bacterial Canker"),
    "ٹھوٹا گل": ("mango", "Bacterial Canker"),

    # -- Downy Mildew --
    "ڈاؤنی میلڈیو": ("sunflower", "Downy Mildew"),

    # -- Rice Blast / رائس بلاسٹ --
    "رائس بلاسٹ": ("rice", "Rice Blast"),
    "چاول کا جھلس": ("rice", "Rice Blast"),

    # -- Brown Spot --
    "براؤن سپاٹ": ("rice", "Brown Spot"),
    "بھورے دھبے": ("rice", "Brown Spot"),

    # -- General symptom-to-disease mappings --
    "سفید دھبے": ("tomato", "Leaf Mold"),
    "پیلے دھبے": ("potato", "Early Blight"),
    "کالے دھبے": ("potato", "Late Blight"),
    "پتے زرد ہونا": ("tomato", "Mosaic Virus"),
    "پتے موڑنا": ("cotton", "Leaf Curl Virus"),
    "تنا سڑنا": ("cotton", "Boll Rot"),
    "پھل سڑنا": ("apple", "Black Rot"),
}

# =========================================================
# COMMON PEST KNOWLEDGE (not diseases, but farmers ask about them)
# =========================================================
PEST_KNOWLEDGE = {
    "whitefly": {
        "pest": "Whitefly",
        "urdu_name": "سفید مکھی",
        "crops_affected": ["tomato", "cotton", "pepper"],
        "damage": "Sucks sap from leaves, causes yellowing, curling, and wilting. Spreads Leaf Curl Virus.",
        "identification": [
            "Tiny white insects on underside of leaves",
            "Leaves turn yellow and curl upward",
            "Sticky honeydew on leaves, black sooty mold grows on it",
            "Whiteflies fly up when plant is disturbed"
        ],
        "treatment_organic": [
            "Yellow sticky traps — 10-12 per acre",
            "Neem oil 5 ml/L spray on leaf undersides",
            "Release Encarsia formosa (parasitic wasp) — 2000 per acre",
            "Spray water strongly to dislodge whiteflies"
        ],
        "treatment_chemical": [
            "Imidacloprid (Confidor) 0.3 ml/L — spray leaf undersides",
            "Thiamethoxam (Actara) 0.5 g/L",
            "Acetamiprid (Starke) 0.5 g/L",
            "Rotate insecticides every 7 days to prevent resistance"
        ],
        "prevention": [
            "Remove weeds around the field (whitefly breeding ground)",
            "Use reflective mulch to repel whiteflies",
            "Avoid excess nitrogen fertilizer (attracts whiteflies)",
            "Check leaf undersides weekly"
        ]
    },
    "aphids": {
        "pest": "Aphids",
        "urdu_name": "شجرہ کیڑا / افیڈ",
        "crops_affected": ["tomato", "pepper", "peas", "cotton"],
        "damage": "Sucks sap, causes leaf curling, stunted growth, and spreads viruses.",
        "identification": [
            "Small green, black, or brown insects on new growth",
            "Leaves curl and distort",
            "Sticky honeydew on leaves",
            "Ants present (they farm aphids)"
        ],
        "treatment_organic": [
            "Neem oil 5 ml/L spray",
            "Garlic-chili spray (blend 10 garlic + 5 chili in 1L water, strain, dilute 1:10)",
            "Release ladybugs — natural predators",
            "Strong water jet to knock off aphids"
        ],
        "treatment_chemical": [
            "Imidacloprid (Confidor) 0.3 ml/L",
            "Dimethoate 1.5 ml/L",
            "Lambda-cyhalothrin (Karate) 1 ml/L"
        ],
        "prevention": [
            "Control ants (they protect aphids)",
            "Remove infested shoot tips",
            "Avoid excess nitrogen",
            "Plant trap crops like mustard around the field"
        ]
    },
    "jassids": {
        "pest": "Jassids (Leafhoppers)",
        "urdu_name": "جاسیڈ / پتہ چوسنے والا",
        "crops_affected": ["cotton"],
        "damage": "Sucks sap from cotton leaves, causes hopperburn — leaf edges turn yellow then brown and curl.",
        "identification": [
            "Yellowing at leaf edges (hopperburn)",
            "Leaf curls downward",
            "Tiny wedge-shaped insects jump when disturbed",
            "Most damage in hot, dry weather"
        ],
        "treatment_organic": [
            "Neem oil 5 ml/L",
            "Yellow sticky traps",
            "Spray kaolin clay (3%) as barrier"
        ],
        "treatment_chemical": [
            "Imidacloprid (Confidor) 0.3 ml/L",
            "Thiamethoxam (Actara) 0.5 g/L",
            "Profenofos 2 ml/L"
        ],
        "prevention": [
            "Early planting to avoid peak jassid population",
            "Remove alternate weed hosts",
            "Use resistant varieties"
        ]
    },
    "bollworm": {
        "pest": "Cotton Bollworm",
        "urdu_name": "سندرا / بال کا کیڑا",
        "crops_affected": ["cotton"],
        "damage": "Larvae bore into cotton bolls, destroying lint and seeds. Most destructive cotton pest in Pakistan.",
        "identification": [
            "Small holes in bolls with frass (excrement) near entry point",
            "Damaged squares (flower buds) fail to open",
            "Young larvae on tender shoot tips",
            "Moths in field during evening"
        ],
        "treatment_organic": [
            "Pheromone traps — 5 per acre for monitoring",
            "Trichogramma wasp release — 1 lakh/acre at egg stage",
            "Neem oil 5 ml/L on young larvae",
            "Hand-pick damaged bolls"
        ],
        "treatment_chemical": [
            "Chlorantraniliprole (Coragen) 0.3 ml/L",
            "Emamectin benzoate (Proclaim) 0.5 g/L",
            "Lambda-cyhalothrin (Karate) 1 ml/L",
            "Spray when larvae are young — they are hardest to kill when large"
        ],
        "prevention": [
            "Destroy crop residues after harvest",
            "Plant Bt cotton varieties",
            "Maintain refuge crop (non-Bt) to delay resistance",
            "Winter plowing to expose pupae"
        ]
    },
    "thrips": {
        "pest": "Thrips",
        "urdu_name": "تھرپس / چوسنے والا کیڑا",
        "crops_affected": ["pepper", "cotton", "tomato"],
        "damage": "Scrape and suck plant tissue, cause silvering of leaves, deform flowers and fruit.",
        "identification": [
            "Silver or bronze patches on leaves",
            "Deformed flowers and young fruit",
            "Tiny dark slender insects (hard to see without magnification)",
            "Black fecal spots on leaves"
        ],
        "treatment_organic": [
            "Blue sticky traps — 15 per acre",
            "Neem oil 5 ml/L",
            "Spinosad-based biopesticide"
        ],
        "treatment_chemical": [
            "Thiamethoxam (Actara) 0.5 g/L",
            "Spinetoram 0.5 ml/L",
            "Fipronil 1 ml/L"
        ],
        "prevention": [
            "Remove weeds and plant debris",
            "Avoid planting near infested fields",
            "Use reflective mulch"
        ]
    },
    "red_mite": {
        "pest": "Red Spider Mite",
        "urdu_name": "سرخ مکڑی کا کیڑا",
        "crops_affected": ["cotton", "tomato", "pepper"],
        "damage": "Tiny mites suck cell contents, cause stippling and bronzing of leaves. Severe in hot, dry weather.",
        "identification": [
            "Fine webbing on leaf undersides",
            "Tiny yellow/red dots on leaves (stippling)",
            "Leaves turn bronze then brown",
            "Worst in hot, dry conditions"
        ],
        "treatment_organic": [
            "Spray water on leaf undersides (mites hate humidity)",
            "Neem oil 5 ml/L",
            "Release predatory mites (Phytoseiulus)"
        ],
        "treatment_chemical": [
            "Abamectin (Vertimec) 1 ml/L",
            "Spiromesifen (Oberon) 1 ml/L",
            "Propargite 2 ml/L"
        ],
        "prevention": [
            "Maintain humidity around plants",
            "Avoid dust accumulation on leaves",
            "Monitor during hot, dry spells"
        ]
    }
}


def get_pest_info(pest_name):
    """Look up pest knowledge by English or Urdu name."""
    pest_lower = pest_name.lower().strip()
    if pest_lower in PEST_KNOWLEDGE:
        return PEST_KNOWLEDGE[pest_lower]
    for key, info in PEST_KNOWLEDGE.items():
        if info["urdu_name"] == pest_name or pest_lower in key:
            return info
    return None


def match_urdu_to_knowledge(urdu_text):
    """Try to match Urdu text to a known disease or pest.

    Returns (crop, disease_name) from DISEASE_KNOWLEDGE, or
    pest info dict from PEST_KNOWLEDGE, or None.
    """
    # Check pests first - they're more specific than disease mappings
    for key, info in PEST_KNOWLEDGE.items():
        if info["urdu_name"] in urdu_text:
            return {"type": "pest", "pest_info": info}
        if key in urdu_text.lower():
            return {"type": "pest", "pest_info": info}

    for urdu_term, (crop, disease) in URDU_DISEASE_MAP.items():
        if urdu_term in urdu_text:
            return {"type": "disease", "crop": crop, "disease": disease}

    return None


def get_disease_info(crop_id, disease_name):
    """Get detailed information about a specific disease."""
    key = f"{crop_id}_{disease_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
    return DISEASE_KNOWLEDGE.get(key)

def get_crop_diseases(crop_id):
    """Get all diseases for a specific crop."""
    return {k: v for k, v in DISEASE_KNOWLEDGE.items() if v['crop'] == crop_id}

def get_treatment_info(crop_id, disease_name, severity=None):
    """Get treatment recommendations based on disease and severity."""
    info = get_disease_info(crop_id, disease_name)
    if not info:
        return None
    
    result = {
        "disease": info["disease"],
        "pathogen": info["pathogen"],
        "symptoms": info["symptoms"],
        "treatment_organic": info["treatment_organic"],
        "treatment_chemical": info["treatment_chemical"],
        "prevention": info["prevention"]
    }
    
    if severity and severity in info.get("severity_indicators", {}):
        result["severity_description"] = info["severity_indicators"][severity]
    
    return result
