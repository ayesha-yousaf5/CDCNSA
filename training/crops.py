"""Per-crop configuration for the CDCNSA Kaggle notebooks.

Alias rules are regexes matched against folder/file names (lower-case, _ - . replaced by spaces).
First match wins, so specific rules come before general ones. Target None = drop those images.
"""
HEALTHY = (r"healthy|normal|fresh", "healthy")

PV = lambda *folders: {"name": "plantvillage", "kind": "plantvillage", "role": "train", "cap": 400, "folders": list(folders)}
PD = lambda require: {"name": "plantdoc", "kind": "plantdoc", "role": "heldout", "require": require}

CROPS = {
    "corn": {
        "title": "Corn / Maize",
        # Pakistan-relevant core maize leaf diseases, each backed by >= 2 field datasets (see dataset map).
        "classes": ["Common Rust", "Gray Leaf Spot", "Northern Leaf Blight", "healthy"],
        "aliases": [
            # dropped: single-region or tiny classes, CD&S's Northern Leaf SPOT (different disease), severity sub-folders
            (r"northern leaf spot|\bnls\b|southern|phaeosphaeria|chlorotic|mottle|\bmcmv\b|eyespot|curvularia|"
             r"\bmln\b|lethal|necrosis|\bmsv\b|streak|bacterial|^leaf blight$", None),
            (r"gr[ae]y leaf spot|\bgls\b|cercospora", "Gray Leaf Spot"),
            (r"common rust|\brust\b|\bcr\b", "Common Rust"),
            (r"northern leaf blight|northern corn leaf blight|\bn?clb\b|\bnlb\b|leaf blight|\bblight\b|turcicum", "Northern Leaf Blight"),
            HEALTHY,
        ],
        "sources": [
            # Pakistan field photos (PlantCity, Data in Brief 2025, Chitral & Charsadda): half train, half real-world test
            {"name": "pakistan_plantcity", "kind": "mendeley", "role": "split", "id": "w8kh2xkspx", "version": 1,
             "require": r"maize|corn"},
            {"name": "cds_purdue", "kind": "osf", "role": "train", "id": "s6ru5"},
            {"name": "bangladesh_corn", "kind": "mendeley", "role": "train", "id": "vy629dngm8", "version": 1},
            {"name": "bd_maize_multiformat", "kind": "mendeley", "role": "train", "id": "sb4wwjs8bz", "version": 1},
            {"name": "tanzania_maize", "kind": "dataverse", "role": "train", "doi": "doi:10.7910/DVN/GDON8Q", "cap": 800},
            {"name": "pretoria_field", "kind": "figshare", "role": "heldout", "id": 20237613},
            {"name": "plantdoc", "kind": "plantdoc", "role": "external", "require": r"corn"},
        ],
        "auto_kaggle_inputs": False,
    },
    "cotton": {
        "title": "Cotton",
        # Classes follow the SAR-CLD-2024 paper (Data in Brief 2024) exactly — the dataset the app's cotton classes come from.
        "classes": ["Bacterial Blight", "Leaf Curl", "Herbicide Growth Damage", "Leaf Hopper Jassids",
                    "Leaf Reddening", "Leaf Variegation", "healthy"],
        "aliases": [
            # external Pakistan test sets: generic labels
            (r"diseased cotton leaf|^diseased leaf$", "__DISEASED__"),
            (r"healthy cotton leaf|^fresh cotton leaf$|^healthy leaf$", "healthy"),
            (r"cotton plant|bollworm|mealy|red ant|thrips|fus+arium|alternaria|verticil|aphid|army|powdery|target|boll|mildew", None),
            (r"bacterial|blight", "Bacterial Blight"),
            (r"curl|clcu|enation", "Leaf Curl"),
            (r"herbicide", "Herbicide Growth Damage"),
            (r"jass|hopper", "Leaf Hopper Jassids"),
            (r"redd|red leaf|reddening", "Leaf Reddening"),
            (r"variegat", "Leaf Variegation"),
            HEALTHY,
        ],
        "sources": [
            {"name": "sar_cld_2024", "kind": "mendeley", "role": "train", "id": "b3jy2p6k8w", "version": 2},
            {"name": "cotton_severity_set", "kind": "mendeley", "role": "heldout", "id": "74jsdxtmx2", "version": 2},
            {"name": "pakistan_s_punjab", "kind": "zenodo", "role": "external", "id": "17011709"},
            # CoSEV (Pakistan): half of its leaf-curl/healthy photos train the model on Pakistani leaf curl, half stay a test.
            {"name": "pakistan_cosev", "kind": "mendeley", "role": "split", "id": "y7544ghy3y", "version": 1,
             "exclude": r"cotton / (train|valid|test)"},
        ],
        "auto_kaggle_inputs": False,
    },
    "rice": {
        "title": "Rice",
        "classes": ["Bacterial Leaf Blight", "Brown Spot", "Leaf Scald", "Narrow Brown Leaf Spot", "Rice Blast",
                    "Rice Hispa", "Rice Leaffolder", "Rice Tungro", "Sheath Blight", "healthy"],
        "aliases": [
            (r"neck|panicle|stripe|smut|false|white background|white bg|^insect$|^rice$", None),
            (r"leaf ?folder", "Rice Leaffolder"),
            (r"narrow", "Narrow Brown Leaf Spot"),
            (r"brown ?spot", "Brown Spot"),
            (r"sheath|steath", "Sheath Blight"),
            (r"bacterial|\bblb\b|leaf ?blight|^blight$", "Bacterial Leaf Blight"),
            (r"scald|scaled", "Leaf Scald"),
            (r"blast", "Rice Blast"),
            (r"hispa", "Rice Hispa"),
            (r"tungro|turngo", "Rice Tungro"),
            HEALTHY,
        ],
        "sources": [
            {"name": "riceleafbd", "kind": "mendeley", "role": "train", "id": "sjkptpgv79", "version": 1},
            {"name": "rice_10class", "kind": "mendeley", "role": "train", "id": "zfwkkdj6dk", "version": 2},
            {"name": "rice_sambalpur", "kind": "mendeley", "role": "train", "id": "fwcj7stb8r", "version": 2},
            {"name": "rice_diu_5class", "kind": "mendeley", "role": "train", "id": "g7tcwvshff", "version": 1},
            {"name": "rice_diu_pest", "kind": "mendeley", "role": "train", "id": "vwv3nry3wr", "version": 1},
            {"name": "dhan_shomadhan", "kind": "mendeley", "role": "heldout", "id": "znsxdctwtt", "version": 1,
             "exclude": r"white"},
        ],
    },
    "apple": {
        "title": "Apple",
        # Pakistan/Kashmir-relevant apple leaf diseases, each with field photos from >= 2 paper-backed sources:
        #  PlantCity (Pakistan: Chitral & Charsadda, Data in Brief 2025), Indigenous Kashmir set (Data in Brief 2024),
        #  AppleLeaf9 (Yang et al., Agronomy 2022: ATLDSD + Plant Pathology 2020/2021 + a little PlantVillage, ~94% in the wild).
        # Dropped: rust (cedar-apple / Gymnosporangium - not a main Pakistani problem), frog-eye/black rot, grey spot,
        # brown spot (Marssonina - one source only), multi-disease 'complex' images.
        "classes": ["Apple Scab", "Alternaria Leaf Blotch", "Powdery Mildew", "Apple Mosaic", "healthy"],
        "aliases": [
            (r"complex|rust|frog|black ?rot|gr[ae]y spot|brown spot|marssonina|blotch fruit|cedar", None),
            (r"alternaria", "Alternaria Leaf Blotch"),
            (r"mosaic", "Apple Mosaic"),
            (r"scab", "Apple Scab"),
            (r"powdery|mildew", "Powdery Mildew"),
            (r"\bhealth(y)?\b|normal|fresh|^apple leaf$", "healthy"),
        ],
        "sources": [
            # Pakistan field photos: half train, half real-world test
            {"name": "pakistan_plantcity", "kind": "mendeley", "role": "split", "id": "w8kh2xkspx", "version": 1,
             "require": r"apple"},
            # Kashmir orchards (neighbouring region): the download holds ONLY augmented copies -> DINOv2 grouping keeps one
            # photo per original leaf, then half train / half test
            {"name": "kashmir_apple", "kind": "mendeley", "role": "split", "id": "9m2dcb5mmr", "version": 3,
             "collapse_aug": True, "cap": 3000},
            {"name": "appleleaf9", "kind": "hf", "role": "train", "repo": "Project-AgML/appleleaf9_disease_classification",
             "split": "train", "cap": 1500, "max_minutes": 40},
            PD(r"apple"),
        ],
        "auto_kaggle_inputs": False,
    },
    "tomato": {
        "title": "Tomato",
        "classes": ["Bacterial Spot", "Early Blight", "Late Blight", "Leaf Mold", "Septoria Leaf Spot",
                    "Target Spot", "Tomato Yellow Leaf Curl Virus", "healthy"],
        "aliases": [
            (r"black spot|shot hole|miner|cercospora|powdery|mosaic|spider|mite", None),
            (r"yellow|curl", "Tomato Yellow Leaf Curl Virus"),
            (r"mosaic", "Tomato Mosaic Virus"),
            (r"spider|mite", "Spider Mites"),
            (r"target", "Target Spot"),
            (r"septoria", "Septoria Leaf Spot"),
            (r"mold|mould", "Leaf Mold"),
            (r"late", "Late Blight"),
            (r"early", "Early Blight"),
            (r"bacterial", "Bacterial Spot"),
            (r"healthy|^tomato leaf$", "healthy"),
        ],
        "sources": [
            {"name": "tomato_pakistan_field", "kind": "mendeley", "role": "train", "id": "3mbnb82mxd", "version": 1},
            {"name": "tomato_bd_field", "kind": "mendeley", "role": "train", "id": "bpfd9cns5g", "version": 2},
            PV("Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
               "Tomato___Septoria_leaf_spot", "Tomato___Target_Spot",
               "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___healthy"),
            PD(r"tomato"),
        ],
    },
    "mango": {
        "title": "Mango",
        "classes": ["Anthracnose", "Bacterial Canker", "Cutting Weevil", "Die Back", "Gall Midge",
                    "Powdery Mildew", "Sooty Mould", "healthy"],
        "aliases": [
            (r"anthrac", "Anthracnose"),
            (r"canker", "Bacterial Canker"),
            (r"weevil", "Cutting Weevil"),
            (r"die ?back", "Die Back"),
            (r"gall", "Gall Midge"),
            (r"powdery", "Powdery Mildew"),
            (r"sooty", "Sooty Mould"),
            HEALTHY,
        ],
        "sources": [
            {"name": "mld24", "kind": "mendeley", "role": "train", "id": "6dvpywm2m2", "version": 1},
            {"name": "mango_mldid", "kind": "mendeley", "role": "train", "id": "jpwtpv2c4s", "version": 1},
            {"name": "mangoleafbd", "kind": "hf", "role": "heldout", "repo": "Project-AgML/MangoLeafBD_disease_classification", "split": "train"},
        ],
    },
    "grape": {
        "title": "Grape",
        "classes": ["Black Rot", "Downy Mildew", "Esca Black Measles", "Leaf Blight / Isariopsis Leaf Spot", "healthy"],
        "aliases": [
            (r"brown spot|mite|powdery|anthrac|alternaria", None),
            (r"black ?rot", "Black Rot"),
            (r"downy", "Downy Mildew"),
            (r"esca|measles", "Esca Black Measles"),
            (r"isariopsis|leaf blight", "Leaf Blight / Isariopsis Leaf Spot"),
            (r"healthy|^grape leaf$", "healthy"),
        ],
        "sources": [
            {"name": "grape_field", "kind": "mendeley", "role": "train", "id": "378c69nwk5", "version": 1},
            PV("Grape___Black_rot", "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy"),
            PD(r"grape"),
        ],
    },
    "eggplant": {
        "title": "Eggplant / Brinjal",
        "classes": ["General Pest Damage", "Leaf Spot", "Mosaic Virus", "White Mold", "Wilt", "healthy"],
        "aliases": [
            (r"small ?leaf|phomopsis", None),
            (r"insect|pest", "General Pest Damage"),
            (r"spot", "Leaf Spot"),
            (r"mosaic", "Mosaic Virus"),
            (r"white ?mo", "White Mold"),
            (r"wilt", "Wilt"),
            HEALTHY,
        ],
        "sources": [
            {"name": "eggplant_bd", "kind": "mendeley", "role": "train", "id": "r3tb5mzn4d", "version": 2},
            {"name": "eggplant_hires", "kind": "mendeley", "role": "train", "id": "ss63ftnjnh", "version": 6},
            {"name": "eggplant_detect", "kind": "mendeley", "role": "train", "id": "d3ypkphghb", "version": 1},
            {"name": "eggplant_curated", "kind": "mendeley", "role": "heldout", "id": "jv6tnm4t5c", "version": 1},
        ],
    },
    "cucumber": {
        "title": "Cucumber",
        "classes": ["Anthracnose", "Bacterial Wilt", "Belly Rot", "Downy Mildew", "Gummy Stem Blight",
                    "Pythium Fruit Rot", "healthy"],
        "aliases": [
            (r"anthrac", "Anthracnose"),
            (r"bacterial", "Bacterial Wilt"),
            (r"belly", "Belly Rot"),
            (r"downy", "Downy Mildew"),
            (r"gummy", "Gummy Stem Blight"),
            (r"pythium", "Pythium Fruit Rot"),
            HEALTHY,
        ],
        "sources": [
            {"name": "cucumber_hf", "kind": "hf", "role": "train", "repo": "Project-AgML/cucumber_disease_classification", "split": "train"},
        ],
    },
    "peas": {
        "title": "Peas",
        "classes": ["Ascochyta Blight", "Botrytis Blight", "Fusarium Wilt", "Pod Borer Damage",
                    "Powdery Mildew", "Downy Mildew", "healthy"],
        "aliases": [
            (r"leaf ?roll|stem ?rot|anthrac", None),
            (r"ascochyta", "Ascochyta Blight"),
            (r"botrytis", "Botrytis Blight"),
            (r"fusarium", "Fusarium Wilt"),
            (r"borer", "Pod Borer Damage"),
            (r"powdery", "Powdery Mildew"),
            (r"downy", "Downy Mildew"),
            HEALTHY,
        ],
        "sources": [
            {"name": "pisum_sativum", "kind": "mendeley", "role": "train", "id": "nnv3k3m94k", "version": 1},
        ],
    },
}
