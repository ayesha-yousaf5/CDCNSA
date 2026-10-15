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
            # Contents checked file-by-file before release (Mendeley/OSF APIs):
            # PlantCity Pakistan test.zip = the 10,667 originals (train.zip = augmented copies, not downloaded).
            # Its maize part: gray leaf spot 132, normal 142 (+ fungal/holcus leaf spot, unused). Half train, half test.
            {"name": "pakistan_plantcity", "kind": "mendeley", "role": "split", "id": "w8kh2xkspx", "version": 1,
             "only_files": r"^test\.zip$", "require": r"maize|corn"},
            # CD&S (Purdue, arXiv 2110.12084): only Dataset_Original/{train,test}/{gls,nlb,nls}; the no/black/white-
            # background folders are the SAME photos re-rendered, so they are excluded.
            {"name": "cds_purdue", "kind": "osf", "role": "train", "id": "s6ru5", "require": r"dataset original",
             "osf_folders": r"^CD&S(/Dataset_Original)?$",
             "osf_zip_folder": "60be295acb2a5e0501690f31"},   # = CD&S/Dataset_Original
            # Bangladesh: 'Final corn dataset' - common rust 129, gray leaf spot 1,497, healthy 1,038 (+BLS, MCMV unused)
            {"name": "bangladesh_corn", "kind": "mendeley", "role": "train", "id": "vy629dngm8", "version": 1},
            # Bangladesh multi-format: RAW_Image only (Converted/Annotation folders hold the same photos again)
            {"name": "bd_maize_multiformat", "kind": "mendeley", "role": "train", "id": "sb4wwjs8bz", "version": 1,
             "require": r"(^| / )raw image( / |$)", "download_folders": r"RAW_Image"},
            # PlantVillage corn (lab photos, Hughes & Salathe 2015) capped at 300/class: the only clean, large source of
            # Common Rust (field sets give just 143 rust photos). Kept a minority; background-swap augmentation hides the
            # plain lab background. (Checked: Mendeley 'Corn Leaf Disease Classification' hmkd6nbngr is PlantVillage +
            # web images + augmented copies -> not used.)
            {"name": "plantvillage", "kind": "plantvillage", "role": "train", "cap": 300,
             "folders": ["Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
                         "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy"]},
            # PlantDoc (real-world photos, folder-labelled): never trained on -> picks & calibrates the model
            {"name": "plantdoc", "kind": "plantdoc", "role": "heldout", "require": r"corn"},
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
        # Field photos from paper-backed sets; a class is kept only with >= 150 photos from >= 2 datasets
        # (so classes that exist in one dataset only - Hispa, Narrow Brown Spot, Leaffolder - drop automatically).
        "classes": ["Bacterial Leaf Blight", "Brown Spot", "Leaf Scald", "Narrow Brown Leaf Spot", "Rice Blast",
                    "Rice Hispa", "Rice Leaffolder", "Rice Tungro", "Sheath Blight", "healthy"],
        "min_train_images": 150,
        "min_train_sources": 2,
        "aliases": [
            (r"neck|panicle|stripe|smut|false|^insect$|^rice$", None),
            (r"leaf ?folder", "Rice Leaffolder"),
            (r"narrow", "Narrow Brown Leaf Spot"),
            (r"brown ?spot|browon ?spot", "Brown Spot"),
            (r"sheath|steath|shath", "Sheath Blight"),
            (r"bacterial|\bblb\b|leaf ?blight|^blight$", "Bacterial Leaf Blight"),
            (r"scald|scaled", "Leaf Scald"),
            (r"blast", "Rice Blast"),
            (r"hispa", "Rice Hispa"),
            (r"tungro|turngo|turgro", "Rice Tungro"),
            (r"healthy|normal|fresh", "healthy"),
        ],
        "sources": [
            # RiceLeafBD (Rimi et al. 2025, arXiv 2501.08912): field photos, Sylhet & Dhaka, expert-checked labels.
            # Held out (never trained on) together with Dhan-Shomadhan's field photos -> covers 8 of the classes.
            {"name": "riceleafbd", "kind": "mendeley", "role": "heldout", "id": "kx9rx8p2mz", "version": 1},
            # Sethy et al. 2020 (Computers & Electronics in Agriculture): Odisha field photos
            {"name": "rice_sambalpur", "kind": "mendeley", "role": "train", "id": "fwcj7stb8r", "version": 2},
            {"name": "rice_diu_5class", "kind": "mendeley", "role": "train", "id": "g7tcwvshff", "version": 1},
            {"name": "rice_diu_pest", "kind": "mendeley", "role": "train", "id": "vwv3nry3wr", "version": 1},
            # Dhan-Shomadhan (arXiv 2309.07515): white-background half trains, field half is the never-seen test
            {"name": "dhan_white_bg", "kind": "mendeley", "role": "train", "id": "znsxdctwtt", "version": 1,
             "require": r"(^| / )white"},
            {"name": "dhan_field", "kind": "mendeley", "role": "heldout", "id": "znsxdctwtt", "version": 1,
             "exclude": r"(^| / )white"},
        ],
        "auto_kaggle_inputs": False,
    },
    "apple": {
        "title": "Apple",
        # Pakistan/Kashmir-relevant apple leaf diseases, each with field photos from >= 2 paper-backed sources:
        #  PlantCity (Pakistan: Chitral & Charsadda, Data in Brief 2025), Indigenous Kashmir set (Data in Brief 2024),
        #  AppleLeaf9 (Yang et al., Agronomy 2022: ATLDSD + Plant Pathology 2020/2021 + a little PlantVillage, ~94% in the wild).
        # Dropped: rust (cedar-apple / Gymnosporangium - not a main Pakistani problem), frog-eye/black rot, grey spot,
        # brown spot (Marssonina - one source only), multi-disease 'complex' images.
        "classes": ["Apple Scab", "Alternaria Leaf Blotch", "Powdery Mildew", "Apple Mosaic", "healthy"],
        "min_train_images": 150,
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
            {"name": "pakistan_plantcity", "kind": "mendeley", "role": "split", "id": "w8kh2xkspx", "version": 1, "only_files": r"^test\.zip$",
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
        # Field photos only (no PlantVillage lab images). A class is kept only if it has >= 150 training photos from
        # >= 2 different field datasets (checked automatically in the notebook); the rest are left to Qwen.
        "classes": ["Early Blight", "Late Blight", "Leaf Mold", "Septoria Leaf Spot", "Tomato Yellow Leaf Curl Virus",
                    "Bacterial Spot", "Target Spot", "Tomato Mosaic Virus", "healthy"],
        "min_train_images": 150,
        "min_train_sources": 1,   # Septoria has real photos only in PlantCity; PlantDoc (held out) tests it honestly
        "aliases": [
            # not leaf diseases we can model reliably / tiny classes
            (r"cercospora|black spot|miner|insect|spider|mite|powdery|spotted wilt|nutri|deficien|\bclass 16\b|uncategori|other", None),
            (r"yellow|curl|tylcv", "Tomato Yellow Leaf Curl Virus"),
            (r"mosaic|tomv|tmv", "Tomato Mosaic Virus"),
            (r"target", "Target Spot"),
            (r"septor", "Septoria Leaf Spot"),
            (r"mold|mould", "Leaf Mold"),
            (r"late", "Late Blight"),
            (r"early", "Early Blight"),
            (r"bacterial", "Bacterial Spot"),
            (r"healthy|^tomato leaf$|^h$", "healthy"),
        ],
        "sources": [
            # NOT used: 'Tomato Leaf Disease Classification Dataset in Pakistan' (3mbnb82mxd) - checked file by file:
            # every image is an augmented copy ("..._aug_639.jpg") and many are internet images (Roboflow, CC web photos).
            # Bangladesh field photos (Daffodil Intl. Univ., natural light, ~2.6k)
            {"name": "tomato_bd_diu", "kind": "mendeley", "role": "train", "id": "93h9p62kg4", "version": 1},
            # Tomato-Village (Gehlot et al., Multimedia Systems 2023): Rajasthan (India) field photos, phone camera
            # (IMG2022....jpg, checked). Multiclass variant: early blight 496, late blight 904, healthy 216
            # (+ leaf miner, spotted wilt, nutrient deficiencies - not used).
            {"name": "tomato_village_india", "kind": "git", "role": "train",
             "repo": "https://github.com/mamta-joshi-gehlot/Tomato-Village", "paths": ["Variant-a(Multiclass Classification)"]},
            # Pakistan PlantCity (Data in Brief 2025, Chitral & Charsadda): half train, half real-world Pakistan test
            {"name": "pakistan_plantcity", "kind": "mendeley", "role": "split", "id": "w8kh2xkspx", "version": 1, "only_files": r"^test\.zip$",
             "require": r"tomato"},
            # internet/real-world photos (PlantDoc, CODS-COMAD 2020): never trained on, used to pick & calibrate
            PD(r"tomato"),
        ],
        "auto_kaggle_inputs": False,
    },
    "mango": {
        "title": "Mango",
        # 8 classes of MangoLeafBD (Ahmed et al., Data in Brief 2023) - the de-facto benchmark; these are also the
        # main mango leaf problems in Pakistan (anthracnose, powdery mildew, die-back/decline, sooty mould, canker).
        # No public Pakistani mango leaf set exists (the Multan/MRI set of Tech Science CMC 2021 is not released).
        "classes": ["Anthracnose", "Bacterial Canker", "Cutting Weevil", "Die Back", "Gall Midge",
                    "Powdery Mildew", "Sooty Mould", "healthy"],
        "min_train_images": 150,
        "min_train_sources": 2,
        "aliases": [
            (r"anthrac", "Anthracnose"),
            (r"canker|cancer", "Bacterial Canker"),
            (r"weevil", "Cutting Weevil"),
            (r"die ?b(l)?ack|dieback", "Die Back"),
            (r"gall", "Gall Midge"),
            (r"powdery|mildew", "Powdery Mildew"),
            (r"sooty|mould|mold", "Sooty Mould"),
            (r"healthy|normal|fresh", "healthy"),
        ],
        "sources": [
            # MangoLeafBD (paper-backed): ~1,800 original leaves + zoom/rotate copies -> copies grouped back to 1 per leaf
            {"name": "mangoleafbd", "kind": "hf", "role": "train", "repo": "Project-AgML/MangoLeafBD_disease_classification",
             "split": "train", "collapse_aug": True, "max_minutes": 30},
            # MLD24: 6,400 orchard photos (iPhone, Kushtia & Dhaka), 800 per class
            {"name": "mld24", "kind": "mendeley", "role": "train", "id": "6dvpywm2m2", "version": 1},
            # MLDID: 3,000 photos, 5 classes
            {"name": "mango_mldid", "kind": "mendeley", "role": "train", "id": "jpwtpv2c4s", "version": 1},
            # Ashulia mango garden, natural conditions: 'Original Mango Dataset.zip' used; 'Augmented Mango dataset.zip' skipped
            {"name": "mango_ashulia", "kind": "mendeley", "role": "train", "id": "fn8dgf4hb5", "version": 1},
            # Pabna & Savar field photos (2024): uses 'process data.zip' (2,336 originals); 'Augmented Image.zip' is skipped. Never trained on
            {"name": "mango_pabna_savar", "kind": "mendeley", "role": "heldout", "id": "7ghdbftp54", "version": 1},
        ],
        "auto_kaggle_inputs": False,
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
