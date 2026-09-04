const $ = (sel, root=document) => root.querySelector(sel);
const $$ = (sel, root=document) => [...root.querySelectorAll(sel)];

const crops = [
  {id:'corn', en:'Corn / Maize', ur:'مکئی', accent:'#b58b18', soft:'#f6f0d8', image:'https://images.unsplash.com/photo-1464972377689-e7674c48d806?auto=format&fit=crop&w=1200&q=84'},
  {id:'cotton', en:'Cotton', ur:'کپاس', accent:'#8b7459', soft:'#f1ece4', image:'https://images.unsplash.com/photo-1731699317142-2333ff275326?auto=format&fit=crop&w=1200&q=84'},
  {id:'tomato', en:'Tomato', ur:'ٹماٹر', accent:'#a84a45', soft:'#f5e9e7', image:'https://images.unsplash.com/photo-1683009118720-8424c9dd58e8?auto=format&fit=crop&w=1200&q=84'},
  {id:'apple', en:'Apple', ur:'سیب', accent:'#8d4e43', soft:'#f3e9e5', image:'https://images.unsplash.com/photo-1738598667934-64df4b1ea34d?auto=format&fit=crop&w=1200&q=84'},
  {id:'rice', en:'Rice', ur:'چاول', accent:'#7e8c38', soft:'#eef0df', image:'https://images.unsplash.com/photo-1756180347907-0e1d17a9ebf8?auto=format&fit=crop&w=1200&q=84'},
  {id:'mango', en:'Mango', ur:'آم', accent:'#8b7a2a', soft:'#f3eed5', image:'https://images.unsplash.com/photo-1744565172191-7d880276a6c5?auto=format&fit=crop&w=1200&q=84'},
  {id:'grape', en:'Grape', ur:'انگور', accent:'#62566d', soft:'#ece8ef', image:'https://images.unsplash.com/photo-1627923004714-8600ebc9ffb5?auto=format&fit=crop&w=1200&q=84'},
  {id:'eggplant', en:'Eggplant / Brinjal', ur:'بینگن', accent:'#67516f', soft:'#efe9f1', image:'https://images.unsplash.com/photo-1738598665657-192203600dcf?auto=format&fit=crop&w=1200&q=84'},
  {id:'cucumber', en:'Cucumber', ur:'کھیرا', accent:'#4e7556', soft:'#e9f0e9', image:'https://images.unsplash.com/photo-1725369865690-5a1a09f87e56?auto=format&fit=crop&w=1200&q=84'},
  {id:'peas', en:'Peas', ur:'مٹر', accent:'#527053', soft:'#eaf0e7', image:'https://images.unsplash.com/photo-1673232649948-6a247567b8d2?auto=format&fit=crop&w=1200&q=84'},
  // {id:'lemon', en:'Lemon', ur:'لیموں', accent:'#b79a34', soft:'#f4f0d7', image:'https://images.unsplash.com/photo-1724144861106-bbb33df2f50a?auto=format&fit=crop&w=1200&q=84'},
  // {id:'soybean', en:'Soybean', ur:'سویا بین', accent:'#687b42', soft:'#e9efe0', image:'https://strapi.myplantin.com/large_Depositphotos_309360300_XL_1_866356fe8b.webp'}
];

// -----------------------------------------------------------------------------
// Verified disease library (model classes only)
// Knowledge was reviewed for symptom/management accuracy and Pakistan chemical
// safety. Healthy model outputs are intentionally not disease cards.
// Chemical names are shown only when supported by Pakistan/Punjab official
// material; the current DPP crop/target product label still governs legal use.
// -----------------------------------------------------------------------------
const VERIFIED_SOURCES = {
  "dppRegistered": {
    "label": "Pakistan DPP — current registered pesticide lists",
    "url": "https://plantprotection.gov.pk/services/pesticide-registration/list-of-registered-pesticides-in-pakistan/"
  },
  "dppBanned": {
    "label": "Pakistan DPP — banned pesticides",
    "url": "https://plantprotection.gov.pk/services/pesticide-registration/list-of-banned-pesticides-in-pakistan/"
  },
  "punjabThresholds": {
    "label": "Punjab Agriculture — economic threshold levels",
    "url": "https://agripunjab.gov.pk/index.php/pw_economic"
  },
  "punjabSoil": {
    "label": "Punjab AARI — soil, water & plant testing / fertilizer recommendations",
    "url": "https://agripunjab.gov.pk/index.php/aari-services"
  },
  "ppri": {
    "label": "Punjab Plant Pathology Research Institute — crop disease research/advisories",
    "url": "https://agripunjab.gov.pk/node/9682"
  },
  "rice2025": {
    "label": "Punjab Pest Warning — 2025 rice disease management advisory",
    "url": "https://pestwarning.agripunjab.gov.pk/system/files/rice%20updated%20observations_34.pdf"
  },
  "orchard2025": {
    "label": "Punjab Pest Warning — 2025 orchard disease advisory",
    "url": "https://pestwarning.agripunjab.gov.pk/system/files/OBSERVATION%20G.CROP%202025_1.pdf"
  },
  "cornBls": {
    "label": "University of Nebraska CropWatch — bacterial leaf streak of corn",
    "url": "https://cropwatch.unl.edu/plant-disease/corn/bacterial-leaf-streak/"
  },
  "cornGuide": {
    "label": "University of Nebraska CropWatch — corn disease resources",
    "url": "https://cropwatch.unl.edu/corn/disease-management/"
  },
  "tomatoCornell": {
    "label": "Cornell Vegetables — managing tomato diseases",
    "url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/managing-tomato-diseases-successfully/"
  },
  "tomatoUMN": {
    "label": "University of Minnesota Extension — tomato disease diagnostics",
    "url": "https://apps.extension.umn.edu/garden/diagnose/plant/vegetable/tomato/"
  },
  "applePSU": {
    "label": "Penn State Extension — apple disease control/timing",
    "url": "https://extension.psu.edu/apple-disease-control-toolbox-fungicide-timing"
  },
  "riceIRRI": {
    "label": "IRRI Rice Knowledge Bank — rice diseases",
    "url": "https://www.knowledgebank.irri.org/step-by-step-production/growth/pests-and-diseases/diseases"
  },
  "mangoPunjab": {
    "label": "Punjab Agriculture — Mango Research Institute",
    "url": "https://agripunjab.gov.pk/node/9748"
  },
  "grapePSU": {
    "label": "Penn State Extension — grape fungal disease management",
    "url": "https://extension.psu.edu/fundamental-considerations-for-managing-fungal-diseases-of-grapevines"
  },
  "grapePHDEC": {
    "label": "PHDEC / FAO Balochistan — grape orchard management",
    "url": "https://phdec.gov.pk/grapes-orchard-management-for-better-quality-and-high-yield/"
  },
  "cucumberCornell": {
    "label": "Cornell Vegetables — cucumber disease diagnostic key",
    "url": "https://www.vegetables.cornell.edu/pest-management/keys-for-identifying-vegetable-diseases/cucurbit-key/cucumber-disease-key/cucumber-leaf-symptoms/"
  },
  "cucumberFruitCornell": {
    "label": "Cornell Vegetables — cucumber/cucurbit fruit symptoms",
    "url": "https://www.vegetables.cornell.edu/pest-management/keys-for-identifying-vegetable-diseases/cucurbit-key/cucumber-disease-key/diseases-of-cucurbit-fruits/"
  },
  "eggplantCornell": {
    "label": "Cornell Vegetables — eggplant / seed-borne disease resources",
    "url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/managing-pathogens-inside-seed-with-hot-water/"
  },
  "whiteMoldCornell": {
    "label": "Cornell Vegetables — white mold identification and management",
    "url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/white-mold/"
  },
  "peasUMN": {
    "label": "University of Minnesota Extension — pea disease diagnostics",
    "url": "https://apps.extension.umn.edu/garden/diagnose/plant/vegetable/peas/"
  },
  // "soyBacterial": {
  //   "label": "University of Minnesota Extension — soybean bacterial blight",
  //   "url": "https://extension.umn.edu/pest-management/bacterial-blight-soybean"
  // },
  // "soyFrogeye": {
  //   "label": "University of Minnesota Extension — soybean frogeye leaf spot",
  //   "url": "https://extension.umn.edu/agriculture/crop-production/soybean/frogeye-leaf-spot"
  // },
  "phdecCitrus": {
    "label": "PHDEC — Pakistan citrus good agricultural practices",
    "url": "https://phdec.gov.pk/good-agricultural-practices-of-citrus-for-high-yield-and-good-quality/"
  }
};

// Curated disease reference images from verified agricultural sources (PlantVillage, university extensions, USDA).
// These use direct image URLs instead of Wikimedia for more reliable loading.
const CURATED_DISEASE_IMAGES = {
  // Corn/Maize
  'corn|maize lethal necrosis': {url:'https://www.ars.usda.gov/ARSUserFiles/oc/pr/2022/corngermplasm06142022.jpg', author:'USDA ARS', license:'Public Domain'},
  
  // Cotton
  'cotton|bacterial blight': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/98577/file/default-522d511f1078b67867b8a27397b05a61.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'cotton|verticillium wilt': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/2051/file/default-10e50bd5045ab76b6165e4b00ff9bcba.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Tomato
  'tomato|bacterial spot': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/4115/file/default-d1c8a57685cb31a9463c91532e91fd1d.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'tomato|cercospora leaf mold': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/63622/file/default-fc0b41b0fa9a434ffdbe5c0197965b39.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Apple
  'apple|black rot': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/99413/file/default-c0da17b501e279d78b77f8d080893289.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'apple|apple powdery mildew': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/571/file/default-f66adc366080e5f024dec5bc0fbc4350.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Rice
  'rice|bacterial leaf blight': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/62249/file/default-5e92a1c0dd9b31c69855b1f0def811fd.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'rice|narrow brown leaf spot': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/62251/file/default-db26399801f3b5ca919e5bbfcddc5135.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'rice|rice tungro': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/62266/file/default-d4931535a7b821bd5734840d7b7efab0.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Mango
  'mango|anthracnose': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/62374/file/default-99dc0d1fd99d97b5ce81f076c93bb04f.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'mango|bacterial canker': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/62369/file/default-9b8a62054e817b23ccaf97cea76d64f4.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'mango|powdery mildew': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/62376/file/default-38dc1a3506d3e40b4b8f9597e57ef1cd.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'mango|sooty mould': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/62418/file/default-f98c292dc07e6cd302242dced6562303.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Grape
  'grape|black rot': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/665/file/default-4610dfc4de4feb58abc2ad08164d9d4c.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'grape|downy mildew': {url:'https://extension.sdstate.edu/sites/default/files/styles/image_width_800/public/2019-01/W-M10834-03-downy-mildew.jpeg', author:'Penny Bower / SDSU Extension', license:'Educational use'},
  
  // Eggplant
  'eggplant|leaf spot': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/3852/file/default-33b9e3205969d4aed4d01ad4fe1e93f5.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'eggplant|phomopsis blight': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/3542/file/default-050e23f1ef993b0a894e6bb1d4bc2f5c.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Cucumber
  'cucumber|belly rot': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/100279/file/default-00ecf415dcee2a8ed9b7a7260b730610.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'cucumber|downy mildew': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/100304/file/default-0c70bcbdd0642df29c241b4bde09133c.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  'cucumber|gummy stem blight': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/100338/file/default-59191a7a661ff7a35f83dcaa867c6575.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Peas
  'peas|ascochyta blight': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/818/file/default-2e756d67a15b6165c23c7fbea23cd7eb.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Soybean
  'soybean|frogeye leaf spot': {url:'https://plantvillage-production-new.s3.amazonaws.com/image/2212/file/default-6e645f23e5e4f80b6051c76ed77f8606.jpg', author:'PlantVillage / Penn State', license:'Educational use'},
  
  // Legacy Wikimedia entries (kept for backward compatibility)
  'corn|bacterial leaf streak': {file:'Bacterial leaf streak of corn Xanthomonas vasicola.jpg', author:'Vinicius Garnica / Bugwood.org', license:'CC BY 3.0'},
  'corn|common rust': {file:'Puccinia sorghi Schwein. 5465568.jpg', author:'Daren Mueller, Iowa State University', license:'CC BY 3.0 US'},
  'corn|gray leaf spot': {file:'Gray leaf spot Cercospora zeae-maydis 5465607.png', author:'Daren Mueller, Iowa State University / Bugwood.org', license:'CC BY 3.0 US'},
  'corn|maize streak virus': {file:'Good msv 3.jpg', author:'Ed Rybicki / University of Cape Town', license:'Public domain dedication'},
  'corn|northern leaf blight': {file:'Northern corn leaf blight.JPG', author:'Chroanch', license:'CC BY-SA 4.0'},
  'tomato|early blight': {file:'Alternaria solani - leaf lesions.jpg', author:'Clemson University / USDA Cooperative Extension slide series', license:'CC BY 3.0 US'},
  'tomato|late blight': {file:'Tomato late blight foliar lesions (5816740026).jpg', author:'Scot Nelson', license:'CC licensed / Commons'},
  'tomato|leaf miner': {file:'Fig5-Leaf-damages-between-upper-and-lower-epidermis-of-a-leaf-by-Tuta-absoluta-in-Ngabobo-village.jpg', author:'Chidege et al.', license:'Open-access figure / Commons'},
  'tomato|leaf mold': {file:'TomateBlattUnterseiteSamtfleckenCladosporiumfulvum.jpg', author:'Goldlocki', license:'CC BY-SA 3.0'},
  'tomato|septoria leaf spot': {file:'Septoria leaf spot symptoms on tomato leaf (Septoria lycopersici on Solanum lycopersicum leaf).jpg', author:'Wikimedia Commons contributor', license:'See source page'},
  'tomato|target spot': {file:'Corynespora cassiicola Ring-Spot Symptoms in Tomato Leaves.png', author:'Wikimedia Commons / source publication', license:'See source page'},
  'tomato|general pest damage': {file:'Tuta absoluta Tomato loss.jpg', author:'Metin GULESCI', license:'CC BY 3.0 US'},
  'tomato|shot hole disease': {file:'TomatHole (14573566542).jpg', author:'order_242', license:'CC BY-SA 2.0'},
  'tomato|spider mites': {file:'Solanum lycopersicum leaves with spider mite or thrips damage in Dnipro by baby-bear.org.jpg', author:'Natalka Ukraine', license:'CC BY 4.0'},
  'tomato|tomato leaf curl virus': {file:'Tomato leaf curl Taiwan virus.jpg', author:'Cindyhsieh', license:'CC BY-SA 4.0'},
  'tomato|tomato mosaic virus': {file:'12985 2016 676 Fig4 HTML.webp', author:'Yueyue Li et al.', license:'CC BY 4.0'},
  'apple|apple scab': {file:'Apple scab 2017 A.jpg', author:'Wikimedia Commons contributor', license:'See source page'},
  'apple|cedar apple rust': {file:'Cedar apple rust 4159.jpg', author:'Ronincmc', license:'Creative Commons / Commons'},
  'rice|rice blast': {file:'Rice blast symptoms.jpg', author:'US Government / Bugwood source', license:'Public domain'},
  'rice|rice hispa': {file:'Rice Hispa (6282950178).jpg', author:'Wikimedia Commons contributor', license:'See source page'},
  'rice|rice leaffolder': {file:'Rice leaf folder.jpg', author:'Badal Chandra Sarker', license:'CC BY-SA 4.0'},
  'rice|sheath blight': {file:'RiceSheathArk.jpg', author:'Peggy Greb, USDA ARS', license:'Public domain'},
  'rice|brown spot': {file:'Helminthosporium oryzae at Oryza sativa (01).jpg', author:'William M. Brown Jr., Bugwood.org', license:'CC BY 3.0 US'},
  'rice|rice stripes': {file:'Viruses-11-00982-g003.png', author:'Yueyue Li et al.', license:'CC BY 4.0'},
  'mango|cutting weevil': {file:'Mango seed weevil 2.jpg', author:'PJeganathan', license:'CC BY-SA 3.0'},
  'mango|gall midge': {file:'Mango leaf gall midge on leaf.jpg', author:'Gutam2000', license:'CC BY 4.0'},
  'mango|drying': {file:'Dried Mango Leaves.jpg', author:'Useendk', license:'CC BY-SA 4.0'},
  'grape|esca black measles': {file:'ESCA Blattsymptom 1.JPG', author:'Bauer Karl', license:'CC BY-SA 3.0'},
  'grape|isariopsis leaf spot': {file:'Pseudocercospora vitis 154983434.jpg', author:'Wikimedia Commons contributor', license:'See source page'},
  'tomato|tomato yellow leaf curl virus': {file:'Yellow curl leaf disease Pj IMG 3162.jpg', author:'Wikimedia Commons contributor', license:'See source page'},
  'eggplant|general pest damage': {file:'Leucinodes orbonalis (Brinjal Fruit Borer).jpg', author:'Chirag85', license:'CC BY-SA 4.0'},
  'eggplant|white mold': {file:'Solanum melongena - Sclerotinia - Josef Schlaghecken.jpg', author:'Schlaghecken Josef', license:'CC BY 4.0'},
  'cucumber|bacterial wilt': {file:'Erwinia tracheiphila - 5362671.png', author:'Howard F. Schwartz, Colorado State University / Bugwood.org', license:'CC BY 3.0 US'},
  'peas|botrytis blight': {file:'Erbsen Botrytis cinera JS-1.jpg', author:'Schlaghecken Josef', license:'CC BY-SA 4.0'},
  'peas|pod borer damage': {file:'Helicoverpa armigera larva.jpg', author:'Gyorgy Csoka', license:'CC BY 3.0 US'}
};
function commonsFilePage(file){ return `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(String(file||'').replace(/ /g,'_'))}`; }
function commonsFileImage(file){ return `https://commons.wikimedia.org/wiki/Special:Redirect/file/${encodeURIComponent(String(file||''))}?width=1200`; }

const diseaseKnowledge = {
  "corn": [
    {
      "en": "Bacterial Leaf Streak",
      "ur": "بیکٹیریل لیف اسٹریِک",
      "vision": true,
      "icon": "✦",
      "symptoms": "Narrow tan, brown, orange or yellow streaks form between veins; margins are often wavy or jagged and lesions may look brighter when backlit.",
      "urduSymptoms": "رگوں کے درمیان باریک زرد، بھوری یا نارنجی دھاریاں بنتی ہیں جن کے کنارے اکثر لہردار ہوتے ہیں۔",
      "management": "Confirm the diagnosis before spraying because it can resemble gray leaf spot. Remove or break down infected residue where practical and avoid moving contaminated debris between fields.",
      "prevention": "Use rotation/tillage where agronomically suitable, equipment sanitation, and tolerant hybrids when locally available.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "Standard foliar fungicides used for fungal corn diseases are not expected to control this bacterial pathogen.",
      "threshold": "Punjab lists maize diseases for action on appearance after diagnosis.",
      "thresholdUr": "پنجاب میں مکئی کی بیماریوں کے لیے تشخیص کے بعد علامات ظاہر ہوتے ہی کارروائی کی ہدایت ہے.",
      "imageQuery": "corn bacterial leaf streak Xanthomonas leaf",
      "aliases": [
        "bacterial_leaf_streak"
      ],
      "sources": [
        "cornBls",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Common Rust",
      "ur": "کامن رسٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Small cinnamon-brown to reddish pustules develop, usually on both leaf surfaces; pustules may darken as they age.",
      "urduSymptoms": "پتوں کے دونوں طرف دارچینی یا سرخی مائل بھورے چھوٹے ابھرے دھبے بن سکتے ہیں۔",
      "management": "Scout the upper canopy and distinguish common rust from other rusts before treatment. Remove volunteer maize where it contributes to disease carryover.",
      "prevention": "Prefer resistant/tolerant hybrids and maintain balanced crop growth.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "Punjab lists maize diseases for action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "corn common rust Puccinia sorghi leaf",
      "aliases": [
        "common_rust"
      ],
      "sources": [
        "cornGuide",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Gray Leaf Spot",
      "ur": "گرے لیف اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Rectangular gray-tan lesions are usually bounded by leaf veins and often have smoother, straighter margins than bacterial leaf streak.",
      "urduSymptoms": "پتوں کی رگوں کے درمیان مستطیل سرمئی یا بھورے دھبے بنتے ہیں جن کے کنارے نسبتاً سیدھے ہوتے ہیں۔",
      "management": "Reduce prolonged leaf wetness where possible, manage infected residue and confirm the lesion pattern before choosing a fungicide.",
      "prevention": "Use tolerant hybrids, crop rotation and residue management where suitable.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "Punjab lists maize diseases for action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "corn gray leaf spot Cercospora zeae maydis",
      "aliases": [
        "gray_leaf_spot",
        "grey leaf spot"
      ],
      "sources": [
        "cornBls",
        "cornGuide",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Maize Lethal Necrosis",
      "ur": "مکئی لیتھل نیکروسس",
      "vision": true,
      "icon": "✦",
      "symptoms": "Mottling and yellowing can progress to leaf necrosis, stunting, poor ear development and severe whole-plant decline.",
      "urduSymptoms": "چتکبرا پن اور زردی بڑھ کر پتے سوکھنے، پودا چھوٹا رہنے اور بھٹے کی خراب نشوونما کا سبب بن سکتی ہے۔",
      "management": "Do not treat it as a fungal leaf spot. Remove clearly infected plants where feasible and reduce sources of virus/vector pressure.",
      "prevention": "Use clean seed, resistant/tolerant material where available, crop-free periods and integrated vector management.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "No pesticide cures the viral disease complex. Insecticides, if justified, only target confirmed vectors and must meet the current Pakistan crop/target label.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "maize lethal necrosis disease MLND leaf",
      "aliases": [
        "maize_lethal_necrosis",
        "MLN",
        "MLND"
      ],
      "sources": [
        "cornGuide",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Maize Streak Virus",
      "ur": "مکئی اسٹریِک وائرس",
      "vision": true,
      "icon": "✦",
      "symptoms": "Fine pale-yellow to white streaks run parallel to leaf veins; plants infected early may be strongly stunted.",
      "urduSymptoms": "رگوں کے ساتھ باریک سفید یا زرد دھاریاں بنتی ہیں اور ابتدائی انفیکشن میں پودا شدید چھوٹا رہ سکتا ہے۔",
      "management": "Remove obvious volunteer/alternate grass hosts where practical and avoid assuming a nutrient deficiency without checking the streak pattern.",
      "prevention": "Use resistant/tolerant cultivars where available, clean planting material and integrated leafhopper/vector management.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "No pesticide cures maize streak virus. Vector control is preventive only and should be threshold/label based.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "maize streak virus disease leaf streaks",
      "aliases": [
        "maize_streak_virus",
        "MSV"
      ],
      "sources": [
        "cornGuide",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Northern Leaf Blight",
      "ur": "نادرن لیف بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Long, elliptical or cigar-shaped gray-green to tan lesions expand along the leaves and may coalesce when disease is severe.",
      "urduSymptoms": "پتوں پر لمبے بیضوی یا سگار نما سرمئی سبز سے بھورے دھبے بنتے اور آپس میں مل سکتے ہیں۔",
      "management": "Scout before the disease reaches the upper canopy and manage crop residue after harvest.",
      "prevention": "Use resistant hybrids, rotation and residue management; maintain good field airflow where possible.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "Punjab lists maize diseases for action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "northern corn leaf blight Exserohilum turcicum",
      "aliases": [
        "northern_leaf_blight",
        "northern corn leaf blight"
      ],
      "sources": [
        "cornGuide",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    }
  ],
  "cotton": [
    {
      "en": "Alternaria Leaf Spot",
      "ur": "الٹرنیریا لیف اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Brown circular to irregular leaf spots may develop darker margins or concentric zoning and can merge under favorable conditions.",
      "urduSymptoms": "پتوں پر بھورے گول یا بے قاعدہ دھبے بن سکتے ہیں جن کے کنارے گہرے یا حلقہ دار ہوں۔",
      "management": "Remove heavily infected residues where practical, improve canopy aeration and confirm Alternaria rather than a bacterial or physiological spot.",
      "prevention": "Use clean seed, balanced nutrition and avoid prolonged leaf wetness when irrigation can be managed.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cotton Alternaria leaf spot leaf",
      "aliases": [
        "alternaria_leaf_spot"
      ],
      "sources": [
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Bacterial Blight",
      "ur": "بیکٹیریل بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Angular water-soaked leaf lesions can turn dark; veins, petioles, stems or bolls may also develop dark bacterial lesions.",
      "urduSymptoms": "پتوں پر زاویہ دار پانی جیسے دھبے گہرے ہو سکتے ہیں اور رگیں، ڈنٹھل یا ٹینڈے بھی متاثر ہو سکتے ہیں۔",
      "management": "Use clean seed and avoid field operations through wet foliage; remove severely affected residue after harvest.",
      "prevention": "Prefer resistant varieties where available and reduce splash/wound spread.",
      "nutritionNote": "",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "streptomycin sulfate"
      ],
      "chemicalNote": "Punjab Plant Pathology Research Institute reports streptomycin sulfate as a cotton bacterial-leaf-blight treatment example. Treat this as provincial technical evidence, not a universal prescription; verify the current DPP cotton/target label before use.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cotton bacterial blight Xanthomonas leaf",
      "aliases": [
        "bacterial_blight"
      ],
      "sources": [
        "ppri",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Herbicide Growth Damage",
      "ur": "ہربیسائڈ گروتھ ڈیمیج",
      "vision": true,
      "icon": "✦",
      "symptoms": "Twisted, cupped, narrowed or malformed new leaves and abnormal growth can appear after herbicide drift, carryover or dosing injury.",
      "urduSymptoms": "ہربیسائڈ کے بہاؤ یا باقیات سے نئے پتے مڑ، سکڑ یا بگڑ سکتے ہیں اور بڑھوتری غیر معمولی ہو سکتی ہے۔",
      "management": "Stop further exposure, document recent herbicide use and drift, and compare affected field patterns with spray direction or treated rows.",
      "prevention": "Calibrate sprayers, prevent drift, observe rotational restrictions and avoid contaminated tanks.",
      "nutritionNote": "Do not apply fertilizer as an antidote. Check root-zone moisture, salinity and nutrient status before correcting any separate deficiency.",
      "chemStatus": "none",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cotton herbicide injury leaf cupping",
      "aliases": [
        "herbicide_growth_damage",
        "herbicide damage"
      ],
      "sources": [
        "punjabSoil",
        "dppRegistered",
        "dppBanned"
      ],
      "classNote": "This is an injury/abiotic model class, not an infectious disease."
    },
    {
      "en": "Leaf Curl",
      "ur": "لیف کرل",
      "vision": true,
      "icon": "✦",
      "symptoms": "Leaves may curl upward or downward, thicken, darken and develop vein swelling; severe plants can be stunted.",
      "urduSymptoms": "پتے اوپر یا نیچے مڑ، موٹے یا گہرے ہو سکتے ہیں اور رگیں ابھر سکتی ہیں؛ شدید پودے چھوٹے رہ سکتے ہیں۔",
      "management": "Rogue severely affected young plants where locally advised and manage weed/volunteer hosts and whitefly pressure through IPM.",
      "prevention": "Use tolerant varieties and clean planting material; avoid unnecessary broad-spectrum sprays that destroy natural enemies.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "No pesticide cures cotton leaf curl virus. Insecticides can only reduce confirmed whitefly vector pressure when the economic threshold and current Pakistan label justify treatment.",
      "threshold": "Punjab whitefly threshold in cotton: 5 adults or nymphs (or both) per leaf.",
      "thresholdUr": "",
      "imageQuery": "cotton leaf curl virus Pakistan leaf curl",
      "aliases": [
        "leaf_curl",
        "cotton leaf curl",
        "CLCuD"
      ],
      "sources": [
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Leaf Hopper Jassids",
      "ur": "لیف ہاپر / جیسڈز",
      "vision": true,
      "icon": "✦",
      "symptoms": "Leaf margins may yellow, redden or curl; feeding can produce hopper-burn and reduced vigor, with small wedge-shaped jassids often on leaf undersides.",
      "urduSymptoms": "پتوں کے کنارے زرد، سرخ یا مڑ سکتے ہیں؛ شدید رس چوسنے سے ہوپر برن اور کمزور بڑھوتری ہو سکتی ہے۔",
      "management": "Scout leaf undersides and use threshold-based IPM; conserve predators and avoid unnecessary repeated insecticide use.",
      "prevention": "Control weeds/alternate hosts and maintain balanced crop growth without excessive nitrogen.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "If the threshold is exceeded, choose only a current DPP-registered insecticide labelled for cotton jassid; rotate mode of action according to the label.",
      "threshold": "Punjab cotton jassid threshold: 1 adult or nymph per leaf.",
      "thresholdUr": "پنجاب میں کپاس کے جیسڈ کی حد: فی پتہ 1 بالغ یا نمف.",
      "imageQuery": "cotton jassid leafhopper hopper burn",
      "aliases": [
        "leaf_hopper_jassids",
        "jassids",
        "leaf hopper"
      ],
      "sources": [
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Leaf Reddening",
      "ur": "لیف ریڈننگ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Leaves develop red, bronze or purple coloration that may begin at margins or between veins; causes can include nutrient/root stress as well as crop aging.",
      "urduSymptoms": "پتے سرخ، کانسی یا جامنی ہو سکتے ہیں؛ وجہ غذائی، جڑوں کا دباؤ یا فصل کی عمر بھی ہو سکتی ہے۔",
      "management": "Treat this as a symptom class: inspect roots, irrigation, salinity, crop stage and field pattern before assigning a disease.",
      "prevention": "Correct identified agronomic stress and avoid unnecessary pesticide use.",
      "nutritionNote": "This class especially requires soil/plant testing before fertilizer correction; potassium, magnesium or other imbalances can mimic disease but should not be guessed from a photo.",
      "chemStatus": "none",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cotton leaf reddening red leaves",
      "aliases": [
        "leaf_reddening"
      ],
      "sources": [
        "punjabSoil",
        "dppRegistered",
        "dppBanned"
      ],
      "classNote": "This is a symptom/physiological model class; the causal factor must be confirmed."
    },
    {
      "en": "Leaf Variegation",
      "ur": "لیف ویریگیشن",
      "vision": true,
      "icon": "✦",
      "symptoms": "Irregular pale, yellow or differently colored sectors appear in leaves; patterns may reflect genetic, nutritional, viral or chemical injury.",
      "urduSymptoms": "پتوں میں بے قاعدہ ہلکے یا زرد حصے بن سکتے ہیں جن کی وجہ جینیاتی، غذائی، وائرل یا کیمیائی ہو سکتی ہے۔",
      "management": "Do not prescribe a pesticide from the visual class alone. Review field pattern, new versus old growth, spray history and neighboring plants.",
      "prevention": "Use clean planting material and correct only confirmed agronomic causes.",
      "nutritionNote": "Use soil/plant testing if deficiency is suspected; fertilizer choice and rate should follow the measured deficiency, not the image alone.",
      "chemStatus": "none",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cotton leaf variegation mottling",
      "aliases": [
        "leaf_variegation"
      ],
      "sources": [
        "punjabSoil",
        "dppRegistered",
        "dppBanned"
      ],
      "classNote": "This model class is a visual syndrome, not a single pathogen."
    },
    {
      "en": "Verticillium Wilt",
      "ur": "ورٹیسیلیم ولٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Lower leaves may yellow and wilt, vascular tissue can discolor, and plants may decline despite adequate soil moisture.",
      "urduSymptoms": "نچلے پتے زرد اور مرجھا سکتے ہیں، اندرونی نالیاں بھوری ہو سکتی ہیں اور مناسب نمی کے باوجود پودا کمزور ہو سکتا ہے۔",
      "management": "Confirm vascular discoloration and exclude waterlogging/root injury. Remove severely affected residues and limit movement of contaminated soil.",
      "prevention": "Use resistant/tolerant varieties where available, rotation and sanitation; improve drainage.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "There is no reliable foliar pesticide cure for established Verticillium wilt; management is preventive and agronomic.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cotton Verticillium wilt vascular browning",
      "aliases": [
        "verticillium_wilt"
      ],
      "sources": [
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    }
  ],
  "tomato": [
    {
      "en": "Bacterial Spot",
      "ur": "بیکٹیریل اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Small dark brown to black leaf spots often have yellow halos; centers may dry or fall out, and fruit can develop raised scabby spots.",
      "urduSymptoms": "چھوٹے گہرے بھورے یا سیاہ دھبوں کے گرد زرد ہالہ بن سکتا ہے اور پھل پر کھردرے دھبے آ سکتے ہیں۔",
      "management": "Use clean transplants/seed, avoid handling wet plants and reduce splash irrigation. Remove heavily infected debris.",
      "prevention": "Rotate crops, stake/space plants for drying and disinfect tools.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Bacterial spot is not automatically controlled by fungal-disease products. Use only a current Pakistan tomato/bacterial-spot label after diagnosis.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato bacterial spot Xanthomonas leaf fruit",
      "aliases": [
        "bacterial_spot"
      ],
      "sources": [
        "tomatoUMN",
        "tomatoCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Cercospora Leaf Mold",
      "ur": "سرکوسپورا لیف مولڈ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Leaf spotting or blighting attributed to the model's Cercospora class may show tan-brown lesions and progressive leaf decline.",
      "urduSymptoms": "ماڈل کے سرکوسپورا کلاس میں پتوں پر بھورے دھبے اور بتدریج پتیوں کا سوکھنا شامل ہو سکتا ہے۔",
      "management": "Because this dataset label is not a standard single tomato diagnosis, confirm the pathogen with close-up/underside symptoms before chemical treatment.",
      "prevention": "Improve airflow, sanitation and leaf-drying conditions.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato Cercospora leaf spot tomato",
      "aliases": [
        "cercospora_leaf_mold"
      ],
      "sources": [
        "tomatoCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": "Dataset/model label; confirm the exact pathogen before pesticide selection."
    },
    {
      "en": "Early Blight",
      "ur": "ارلی بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Older leaves develop dark brown lesions with concentric target-like rings, often surrounded by yellow tissue; stems and fruit can also be affected.",
      "urduSymptoms": "پرانے پتوں پر ہدف جیسے حلقوں والے گہرے بھورے دھبے بنتے ہیں اور اردگرد زردی ہو سکتی ہے۔",
      "management": "Remove badly infected lower foliage when practical, keep leaves dry and reduce soil splash.",
      "prevention": "Rotate away from solanaceous crops, stake/mulch plants and manage residue.",
      "nutritionNote": "",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "pyraclostrobin + tebuconazole",
        "azoxystrobin + difenoconazole"
      ],
      "chemicalNote": "Punjab PPRI lists these as tomato early-blight research/advisory options. Do not infer a rate from this card.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato early blight Alternaria solani target spots",
      "aliases": [
        "early_blight"
      ],
      "sources": [
        "tomatoUMN",
        "tomatoCornell",
        "ppri",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "General Pest Damage",
      "ur": "جنرل پیسٹ ڈیمیج",
      "vision": true,
      "icon": "✦",
      "symptoms": "Chewing, sucking, mining, frass, webbing or distorted growth may occur depending on the pest.",
      "urduSymptoms": "کیڑے کے مطابق چبانے کے نشان، رس چوسنے، سرنگیں، فضلہ، جالا یا بگڑی بڑھوتری ہو سکتی ہے۔",
      "management": "Identify the pest before treatment: inspect leaf undersides, stems, fruit and field distribution.",
      "prevention": "Use traps, sanitation, natural enemies and pest-specific thresholds before insecticide use.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "No single insecticide is appropriate for a generic pest-damage class. Identify the pest and use its Punjab threshold and current crop label.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato insect pest damage leaf fruit",
      "aliases": [
        "general_pest_damage",
        "pest damage"
      ],
      "sources": [
        "punjabThresholds",
        "tomatoUMN",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Late Blight",
      "ur": "لیٹ بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Rapidly enlarging water-soaked dark lesions occur on leaves and stems in cool humid conditions; white sporulation may appear at lesion margins on leaf undersides.",
      "urduSymptoms": "ٹھنڈے مرطوب موسم میں پتوں اور تنوں پر پانی جیسے گہرے دھبے تیزی سے بڑھتے ہیں اور نیچے سفید پھپھوندی نظر آ سکتی ہے۔",
      "management": "Remove badly infected tissue/plants where feasible, avoid overhead irrigation and act quickly after confirmation because epidemics can progress rapidly.",
      "prevention": "Use clean transplants, spacing/ventilation and avoid prolonged leaf wetness.",
      "nutritionNote": "",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "metalaxyl-M + mancozeb",
        "azoxystrobin + difenoconazole"
      ],
      "chemicalNote": "Punjab PPRI lists these for tomato late blight. Resistance management and current DPP tomato/late-blight registration must be checked.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato late blight Phytophthora infestans leaf",
      "aliases": [
        "late_blight"
      ],
      "sources": [
        "tomatoCornell",
        "ppri",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Leaf Miner",
      "ur": "لیف مائنر",
      "vision": true,
      "icon": "✦",
      "symptoms": "Serpentine pale tunnels or blotch mines form within leaves; larvae or dark frass may be visible inside mines.",
      "urduSymptoms": "پتوں کے اندر سانپ جیسی ہلکی سرنگیں یا دھبہ نما مائنز بنتی ہیں اور اندر لاروا یا فضلہ نظر آ سکتا ہے۔",
      "management": "Remove heavily mined leaves in small plantings, monitor adult activity and conserve parasitoids.",
      "prevention": "Use clean nursery plants, weed management and avoid broad-spectrum sprays that destroy natural enemies.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Use an insecticide only after the miner species is identified and the threshold/label supports treatment.",
      "threshold": "Punjab vegetable leaf-miner threshold: 10% affected leaves.",
      "thresholdUr": "",
      "imageQuery": "tomato leaf miner serpentine mines Liriomyza Tuta",
      "aliases": [
        "leaf_miner"
      ],
      "sources": [
        "punjabThresholds",
        "tomatoUMN",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Leaf Mold",
      "ur": "لیف مولڈ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Pale yellow patches develop on upper leaf surfaces while olive-green to brown velvety growth appears beneath, especially in humid protected crops.",
      "urduSymptoms": "پتے کے اوپر ہلکے زرد دھبے اور نیچے زیتونی سے بھوری مخملی تہہ بنتی ہے، خاص طور پر زیادہ نمی میں۔",
      "management": "Lower humidity, improve ventilation and remove heavily infected leaves.",
      "prevention": "Use resistant varieties where available, wider spacing and avoid prolonged leaf wetness.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato leaf mold Passalora fulva underside olive",
      "aliases": [
        "leaf_mold"
      ],
      "sources": [
        "tomatoUMN",
        "tomatoCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Septoria Leaf Spot",
      "ur": "سیپٹوریا لیف اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Numerous small circular lesions with dark borders and pale centers start commonly on older/lower leaves; tiny black fruiting bodies may be visible.",
      "urduSymptoms": "نچلے یا پرانے پتوں پر گہرے کناروں اور ہلکے مرکز والے بہت سے چھوٹے گول دھبے بنتے ہیں۔",
      "management": "Remove infected lower leaves/debris when practical and minimize splash.",
      "prevention": "Rotate, mulch/stake plants and improve airflow.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato Septoria leaf spot pycnidia",
      "aliases": [
        "septoria_leaf_spot"
      ],
      "sources": [
        "tomatoUMN",
        "tomatoCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Shot Hole Disease",
      "ur": "شاٹ ہول ڈیزیز",
      "vision": true,
      "icon": "✦",
      "symptoms": "Small necrotic spots may dry and fall out, leaving hole-like lesions; several bacterial, fungal or injury causes can create this appearance.",
      "urduSymptoms": "چھوٹے مردہ دھبوں کا مرکز گرنے سے سوراخ جیسے نشان بن سکتے ہیں؛ اس کی کئی مختلف وجوہات ہو سکتی ہیں۔",
      "management": "Treat this as a visual syndrome and confirm the cause before selecting a product. Inspect halos, fruit lesions, recent spray injury and pest feeding.",
      "prevention": "Improve sanitation and avoid unnecessary leaf wetness while diagnosis is being confirmed.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "No single pesticide is valid for a generic shot-hole symptom class; the causal agent must be confirmed.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato leaf shot hole lesions",
      "aliases": [
        "shot_hole_disease"
      ],
      "sources": [
        "tomatoUMN",
        "tomatoCornell",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": "Dataset/model class; “shot hole” is a symptom pattern rather than one guaranteed tomato pathogen."
    },
    {
      "en": "Spider Mites",
      "ur": "اسپائڈر مائٹس",
      "vision": true,
      "icon": "✦",
      "symptoms": "Fine pale stippling progresses to bronzing/yellowing; fine webbing and mites may be visible on leaf undersides.",
      "urduSymptoms": "پتوں پر باریک ہلکے نقطے، پھر کانسی یا زرد رنگ اور نیچے باریک جالا/مائٹس نظر آ سکتے ہیں۔",
      "management": "Scout undersides, reduce dust and water stress, and conserve predatory mites/insects.",
      "prevention": "Avoid repeated broad-spectrum insecticides that can flare mite populations.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "If the threshold is exceeded, use only a current Pakistan tomato/mites acaricide label and rotate modes of action.",
      "threshold": "Punjab vegetable mite threshold: 10 mites per leaf.",
      "thresholdUr": "",
      "imageQuery": "tomato spider mite damage webbing leaf",
      "aliases": [
        "spider_mites",
        "spider mites"
      ],
      "sources": [
        "punjabThresholds",
        "tomatoUMN",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Target Spot",
      "ur": "ٹارگٹ اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Brown lesions can develop concentric rings and yellow halos; severe disease may cause defoliation and fruit spotting.",
      "urduSymptoms": "بھورے دھبوں میں ہدف جیسے حلقے اور زرد ہالہ بن سکتا ہے اور شدید حالت میں پتے گر سکتے ہیں۔",
      "management": "Remove infected debris, reduce prolonged humidity and confirm against early blight/Septoria.",
      "prevention": "Use crop rotation, airflow and sanitation.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato target spot Corynespora cassiicola",
      "aliases": [
        "target_spot"
      ],
      "sources": [
        "tomatoCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Tomato Leaf Curl Virus",
      "ur": "ٹماٹو لیف کرل وائرس",
      "vision": true,
      "icon": "✦",
      "symptoms": "Leaves curl and distort, internodes shorten and plants may become stunted; yellowing may accompany the curling.",
      "urduSymptoms": "پتے مڑ اور بگڑ سکتے ہیں، گانٹھوں کے درمیان فاصلہ کم اور پودا چھوٹا رہ سکتا ہے۔",
      "management": "Remove strongly infected plants where feasible and manage vectors/weed hosts.",
      "prevention": "Use clean transplants, tolerant varieties and physical/vector-exclusion IPM where practical.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "No pesticide cures a plant virus. Insecticides only target confirmed vectors and should be threshold/label based.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato leaf curl virus curled leaves",
      "aliases": [
        "tomato_leaf_curl_virus",
        "leaf curl virus"
      ],
      "sources": [
        "tomatoCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Tomato Mosaic Virus",
      "ur": "ٹماٹو موزیک وائرس",
      "vision": true,
      "icon": "✦",
      "symptoms": "Mosaic light/dark green mottling, leaf distortion, fern-like narrowing and uneven fruit coloration can occur.",
      "urduSymptoms": "پتوں میں ہلکے گہرے سبز چتکبرے نقش، بگاڑ یا باریک پتے اور پھل کا غیر یکساں رنگ ہو سکتا ہے۔",
      "management": "Remove infected plants where practical, sanitize hands/tools and avoid tobacco contamination.",
      "prevention": "Use certified clean seed/transplants and resistant varieties where available.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "No pesticide cures Tomato mosaic virus; vector insecticide is not a substitute for sanitation because ToMV is commonly mechanically transmitted.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato mosaic virus ToMV leaf mosaic",
      "aliases": [
        "tomato_mosaic_virus",
        "mosaic virus"
      ],
      "sources": [
        "tomatoCornell",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Tomato Yellow Leaf Curl Virus",
      "ur": "ٹماٹو یلو لیف کرل وائرس",
      "vision": true,
      "icon": "✦",
      "symptoms": "Young leaves become small, upward-curled and yellowed; plants can be severely stunted with poor flower/fruit set.",
      "urduSymptoms": "نئے پتے چھوٹے، اوپر کو مڑے اور زرد ہو سکتے ہیں اور پودا شدید چھوٹا رہ سکتا ہے۔",
      "management": "Remove strongly infected plants early where feasible and suppress whitefly/weed reservoirs using IPM.",
      "prevention": "Use clean transplants, resistant/tolerant varieties and insect exclusion in nurseries/tunnels.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "No pesticide cures TYLCV. Whitefly insecticides only reduce vector pressure and must follow threshold/current Pakistan label.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "tomato yellow leaf curl virus TYLCV yellow curled leaves",
      "aliases": [
        "tomato_yellow_leaf_curl_virus",
        "yellow leaf curl virus",
        "TYLCV"
      ],
      "sources": [
        "tomatoCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    }
  ],
  "apple": [
    {
      "en": "Alternaria Apple",
      "ur": "الٹرنیریا ایپل",
      "vision": true,
      "icon": "✦",
      "symptoms": "Round brown to dark leaf lesions may have purple margins or target-like zoning; severe infection can cause defoliation.",
      "urduSymptoms": "پتوں پر بھورے یا گہرے گول دھبے بن سکتے ہیں جن کے کنارے جامنی یا حلقہ دار ہوں۔",
      "management": "Remove infected leaves/debris where practical, improve airflow and confirm Alternaria against other leaf spots.",
      "prevention": "Prune for canopy drying and avoid excessive nitrogen that creates dense susceptible growth.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "apple Alternaria leaf blotch apple leaf",
      "aliases": [
        "alternaria_apple",
        "Alternaria Apple"
      ],
      "sources": [
        "applePSU",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Apple Powdery Mildew",
      "ur": "ایپل پاؤڈری ملڈیو",
      "vision": true,
      "icon": "✦",
      "symptoms": "White powdery growth appears on young leaves and shoots; infected leaves may narrow, curl or remain small.",
      "urduSymptoms": "نئے پتوں اور کونپلوں پر سفید سفوف جیسی تہہ بنتی ہے اور پتے سکڑ یا مڑ سکتے ہیں۔",
      "management": "Prune visibly infected shoots where practical and improve canopy airflow.",
      "prevention": "Use resistant cultivars where available and avoid excessive nitrogen.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "apple powdery mildew white shoots leaves",
      "aliases": [
        "apple_powdery_mildew",
        "powdery mildew"
      ],
      "sources": [
        "applePSU",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Apple Scab",
      "ur": "ایپل اسکیب",
      "vision": true,
      "icon": "✦",
      "symptoms": "Olive-green velvety leaf spots become darker; fruit lesions can turn corky, cracked or deformed.",
      "urduSymptoms": "پتوں پر زیتونی سبز مخملی دھبے بعد میں گہرے ہو سکتے ہیں اور پھل کھردرا یا پھٹا ہو سکتا ہے۔",
      "management": "Remove/shred infected leaf litter and prune for rapid drying; protect new growth according to local disease risk.",
      "prevention": "Use resistant cultivars where available and maintain balanced orchard fertility.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "apple scab Venturia inaequalis leaf fruit",
      "aliases": [
        "apple_scab",
        "Apple Apple Scab"
      ],
      "sources": [
        "applePSU",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Black Rot",
      "ur": "بلیک روٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Purple flecks on leaves can enlarge into “frog-eye” spots; fruit develops firm expanding rot and limbs can develop cankers.",
      "urduSymptoms": "پتوں پر جامنی نقطے بڑھ کر فراگ آئی دھبے بن سکتے ہیں، پھل سخت سڑ سکتا ہے اور شاخوں پر کینکر بن سکتے ہیں۔",
      "management": "Remove mummified fruit and dead/cankered wood and sanitize pruning cuts/tools.",
      "prevention": "Maintain tree vigor without excessive nitrogen and manage fire-blight/dead wood that can provide infection sites.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "apple black rot Botryosphaeria obtusa frog eye fruit",
      "aliases": [
        "black_rot"
      ],
      "sources": [
        "applePSU",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Cedar Apple Rust",
      "ur": "سیڈر ایپل رسٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Bright yellow-orange leaf spots develop dark dots; fruit or young shoots may also be affected.",
      "urduSymptoms": "پتوں پر چمکدار زرد نارنجی دھبے اور بعد میں گہرے نقطے بنتے ہیں؛ پھل یا نئی شاخیں بھی متاثر ہو سکتی ہیں۔",
      "management": "Confirm nearby juniper/cedar alternate hosts and remove galls where feasible.",
      "prevention": "Use resistant cultivars and reduce local alternate-host inoculum when practical.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cedar apple rust Gymnosporangium apple leaf orange spots",
      "aliases": [
        "cedar_apple_rust"
      ],
      "sources": [
        "applePSU",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    }
  ],
  "rice": [
    {
      "en": "Bacterial Leaf Blight",
      "ur": "بیکٹیریل لیف بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Water-soaked streaks begin near leaf tips/margins and expand into yellow-white blighted areas; severe plants may wilt.",
      "urduSymptoms": "پتوں کے سروں یا کناروں سے پانی جیسی دھاریاں شروع ہو کر زرد سفید سوکھے حصوں میں بدل سکتی ہیں۔",
      "management": "Use disease-free seed, avoid excessive nitrogen and prevent unnecessary leaf injury/splash.",
      "prevention": "Use resistant varieties, sanitation and balanced crop nutrition.",
      "nutritionNote": "Avoid excessive nitrogen; maintain balanced fertility and correct deficiencies from soil/plant testing rather than increasing nitrogen after symptoms appear.",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "kasugamycin",
        "copper oxychloride",
        "kasugamycin + copper oxychloride"
      ],
      "chemicalNote": "Punjab rice advisories and PPRI list kasugamycin and copper-based options for bacterial leaf blight. Confirm the current DPP rice/BLB label before use and do not infer rate or PHI from this card.",
      "threshold": "Punjab rice diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "rice bacterial leaf blight Xanthomonas oryzae",
      "aliases": [
        "bacterial_leaf_blight"
      ],
      "sources": [
        "riceIRRI",
        "rice2025",
        "ppri",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Brown Spot",
      "ur": "براؤن اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Oval brown lesions often have gray/tan centers and darker margins; spotting can occur on leaves and grain.",
      "urduSymptoms": "پتوں پر بیضوی بھورے دھبے بنتے ہیں جن کا مرکز ہلکا اور کنارے گہرے ہو سکتے ہیں۔",
      "management": "Use healthy seed, manage residue and avoid drought/nutrient stress.",
      "prevention": "Maintain balanced fertility and correct confirmed soil deficiencies.",
      "nutritionNote": "Brown spot is often worse in nutritionally stressed soils. Use soil testing and maintain balanced potassium and overall fertility rather than applying a “disease fertilizer.”",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "tebuconazole",
        "azoxystrobin + difenoconazole",
        "epoxiconazole + pyraclostrobin"
      ],
      "chemicalNote": "Punjab PPRI reports these active ingredients as brown-spot management examples in rice. Use only a currently registered rice/brown-spot product and follow its resistance-management and label directions.",
      "threshold": "Punjab rice diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "rice brown spot Bipolaris oryzae leaf",
      "aliases": [
        "brown_spot"
      ],
      "sources": [
        "riceIRRI",
        "rice2025",
        "ppri",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Leaf Scald",
      "ur": "لیف اسکیلڈ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Lesions often start near leaf tips or margins as zoned/striped brown areas and can expand into large scorched regions.",
      "urduSymptoms": "پتے کے سرے یا کنارے سے حلقہ دار بھورے دھبے شروع ہو کر بڑے جلے ہوئے حصوں میں بدل سکتے ہیں۔",
      "management": "Use clean seed, reduce infected residue and avoid excessive nitrogen.",
      "prevention": "Use resistant varieties where available and balanced fertility.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "Punjab rice diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "rice leaf scald Microdochium oryzae leaf",
      "aliases": [
        "leaf_scald"
      ],
      "sources": [
        "riceIRRI",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Narrow Brown Leaf Spot",
      "ur": "نیرو براؤن لیف اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Many narrow, short brown linear lesions develop parallel to leaf veins and can occur on sheaths or panicles.",
      "urduSymptoms": "رگوں کے متوازی بہت سے باریک چھوٹے بھورے دھبے بنتے ہیں اور غلاف یا بالیوں پر بھی آ سکتے ہیں۔",
      "management": "Confirm against nutrient-related striping and other spots; manage residue and crop stress.",
      "prevention": "Use resistant varieties where available and balanced fertility.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "Punjab rice diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "rice narrow brown leaf spot Cercospora janseana",
      "aliases": [
        "narrow_brown_leaf_spot"
      ],
      "sources": [
        "riceIRRI",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Rice Blast",
      "ur": "رائس بلاسٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Diamond/spindle-shaped leaf lesions with gray centers and brown margins may occur; neck infection can cause panicle blanking or breakage.",
      "urduSymptoms": "پتوں پر ہیرے یا تکلے جیسے دھبے بن سکتے ہیں جن کا مرکز سرمئی اور کنارے بھورے ہوں؛ گردن بلاسٹ بالی کو شدید نقصان دے سکتا ہے۔",
      "management": "Maintain proper flooding/water management where appropriate and remove severe volunteer/grass hosts.",
      "prevention": "Use resistant varieties and avoid excessive or late nitrogen.",
      "nutritionNote": "Avoid excessive or late nitrogen because lush, susceptible growth can increase blast risk. Correct other nutrient deficiencies only from soil/plant testing.",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "azoxystrobin + difenoconazole",
        "pyraclostrobin",
        "isoprothiolane"
      ],
      "chemicalNote": "Punjab PPRI and rice advisories report these active ingredients for rice blast. Apply only under a current DPP rice/blast label; late or excessive nitrogen should also be avoided.",
      "threshold": "Punjab rice diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "rice blast Magnaporthe oryzae leaf neck blast",
      "aliases": [
        "rice_blast",
        "leaf_blast",
        "blast"
      ],
      "sources": [
        "riceIRRI",
        "rice2025",
        "ppri",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Rice Hispa",
      "ur": "رائس ہسپا",
      "vision": true,
      "icon": "✦",
      "symptoms": "Adults scrape green tissue leaving white parallel streaks; larvae mine inside leaves, producing pale blister-like mines.",
      "urduSymptoms": "بالغ کیڑا پتے کو کھرچ کر سفید متوازی لکیریں بناتا ہے اور لاروا پتے کے اندر مائن بناتا ہے۔",
      "management": "Scout plants and remove heavily infested nursery leaves in small plantings; conserve natural enemies.",
      "prevention": "Use clean nursery management and avoid unnecessary insecticide use below threshold.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Use an insecticide only if the Punjab threshold is reached and the product is currently DPP-registered for rice hispa.",
      "threshold": "Punjab rice Hispa threshold: 1 insect per plant.",
      "thresholdUr": "پنجاب میں رائس ہسپا کی حد: فی پودا 1 کیڑا.",
      "imageQuery": "rice hispa Dicladispa armigera leaf damage",
      "aliases": [
        "rice_hispa",
        "hispa"
      ],
      "sources": [
        "riceIRRI",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Rice Leaffolder",
      "ur": "رائس لیف فولڈر",
      "vision": true,
      "icon": "✦",
      "symptoms": "Larvae fold or roll leaves and scrape green tissue inside, leaving whitish transparent feeding patches.",
      "urduSymptoms": "لاروا پتے کو لپیٹ کر اندر سبز بافت کھاتا ہے جس سے سفید شفاف نشان بنتے ہیں۔",
      "management": "Count rolled leaves, open folds to confirm larvae and conserve parasitoids/predators.",
      "prevention": "Avoid excessive nitrogen and use threshold-based IPM.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Use an insecticide only after threshold confirmation and a current DPP rice/leaffolder label.",
      "threshold": "Punjab rice leaf-folder threshold: 2 rolled leaves/plant (July–August), 3 rolled leaves/plant (September–October).",
      "thresholdUr": "",
      "imageQuery": "rice leaf folder Cnaphalocrocis medinalis rolled leaf",
      "aliases": [
        "rice_leaffolder",
        "leaf_folder",
        "leaffolder"
      ],
      "sources": [
        "riceIRRI",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Rice Stripes",
      "ur": "رائس اسٹرائپس",
      "vision": true,
      "icon": "✦",
      "symptoms": "Longitudinal yellow, pale or necrotic striping can run along leaves. Several viral, nutritional and abiotic causes can look similar.",
      "urduSymptoms": "پتوں کے ساتھ لمبی زرد، ہلکی یا سوکھی دھاریاں بن سکتی ہیں اور مختلف وجوہات ایک جیسی لگ سکتی ہیں۔",
      "management": "Treat this model output as a visual syndrome: check field pattern, vectors, nutrient status and laboratory confirmation before disease-specific treatment.",
      "prevention": "Use clean seed/planting material and balanced fertility; manage vectors only after they are identified.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "No single pesticide is appropriate until the cause of the striping is confirmed.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "rice stripe disease striped leaves rice",
      "aliases": [
        "rice_stripes",
        "rice stripe"
      ],
      "sources": [
        "riceIRRI",
        "punjabSoil",
        "dppRegistered",
        "dppBanned"
      ],
      "classNote": "Model/dataset visual class; exact etiology should be confirmed before chemistry."
    },
    {
      "en": "Rice Tungro",
      "ur": "رائس ٹنگرو",
      "vision": true,
      "icon": "✦",
      "symptoms": "Plants become yellow-orange, stunted and produce fewer tillers; leaves may show mottling and panicles can be poorly filled.",
      "urduSymptoms": "پودے زرد نارنجی، چھوٹے اور کم شاخوں والے ہو سکتے ہیں، پتے چتکبرے اور بالیاں کم بھری ہو سکتی ہیں۔",
      "management": "Remove strongly infected plants where feasible and reduce ratoons/volunteer rice that maintain infection.",
      "prevention": "Use resistant varieties and integrated management of green leafhopper vectors.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "No pesticide cures rice tungro. Insecticides can only suppress confirmed leafhopper vectors and must follow thresholds/current label.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "rice tungro virus yellow orange stunted",
      "aliases": [
        "rice_tungro",
        "tungro"
      ],
      "sources": [
        "riceIRRI",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Sheath Blight",
      "ur": "شیتھ بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Oval green-gray lesions with brown margins develop on leaf sheaths near the waterline and can spread upward into the canopy.",
      "urduSymptoms": "پانی کی سطح کے قریب پتوں کے غلاف پر بیضوی سرمئی سبز دھبے بھورے کناروں کے ساتھ بنتے اور اوپر پھیل سکتے ہیں۔",
      "management": "Avoid dense overly nitrogenous canopies, manage infected residue and maintain appropriate plant spacing.",
      "prevention": "Use balanced nitrogen, resistant/tolerant varieties where available and crop sanitation.",
      "nutritionNote": "Avoid excessive nitrogen and overly dense crop growth where practical; balanced fertility is part of risk reduction, not a cure.",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "Punjab rice diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "rice sheath blight Rhizoctonia solani sheath lesion",
      "aliases": [
        "sheath_blight"
      ],
      "sources": [
        "riceIRRI",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    }
  ],
  "mango": [
    {
      "en": "Anthracnose",
      "ur": "انتھراکنوز",
      "vision": true,
      "icon": "✦",
      "symptoms": "Dark irregular leaf spots, blossom blight and black sunken fruit lesions can develop, especially in humid weather.",
      "urduSymptoms": "پتوں پر گہرے بے قاعدہ دھبے، پھولوں کا جھلساؤ اور پھل پر دھنسے سیاہ زخم بن سکتے ہیں۔",
      "management": "Prune infected/dead twigs, remove mummified fruit and improve canopy airflow.",
      "prevention": "Avoid prolonged canopy wetness and maintain balanced orchard nutrition.",
      "nutritionNote": "",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "Bordeaux mixture",
        "copper-based fungicides"
      ],
      "chemicalNote": "Punjab orchard advisories list Bordeaux/copper-based fungicides for anthracnose/wither-tip management. Verify the current DPP mango/anthracnose label.",
      "threshold": "Punjab mango diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "mango anthracnose Colletotrichum fruit leaf",
      "aliases": [
        "Mango / Anthracnose",
        "anthracnose"
      ],
      "sources": [
        "mangoPunjab",
        "orchard2025",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Bacterial Canker",
      "ur": "بیکٹیریل کینکر",
      "vision": true,
      "icon": "✦",
      "symptoms": "Water-soaked leaf/fruit lesions can become dark, cracked or corky; twigs may develop cankers and dieback depending on the causal bacterium.",
      "urduSymptoms": "پتوں یا پھل پر پانی جیسے دھبے گہرے، پھٹے یا کھردرے ہو سکتے ہیں اور شاخوں پر کینکر بن سکتا ہے۔",
      "management": "Prune clearly cankered twigs in dry weather and sanitize tools; avoid wounding and splash spread.",
      "prevention": "Use clean planting material and good canopy aeration.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Do not assume a fungicide is appropriate for a bacterial canker. A bactericide requires a confirmed diagnosis and current Pakistan mango/canker label.",
      "threshold": "Punjab mango diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "mango bacterial canker leaf fruit canker",
      "aliases": [
        "Mango / Bacterial Canker",
        "bacterial_canker"
      ],
      "sources": [
        "mangoPunjab",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Cutting Weevil",
      "ur": "کٹنگ ویول",
      "vision": true,
      "icon": "✦",
      "symptoms": "Notches, cut tissue, holes or internal feeding may be associated with weevil injury depending on life stage and plant part.",
      "urduSymptoms": "ویول کے حملے میں کٹے ہوئے کنارے، سوراخ یا اندرونی کھانے کے نشان ہو سکتے ہیں۔",
      "management": "Inspect fruit, shoots and fallen material for adults/larvae before treatment; remove and destroy heavily infested plant material where locally advised.",
      "prevention": "Maintain orchard sanitation and monitor pest emergence.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "The model class name does not identify a specific weevil species with certainty. Confirm the pest before selecting any insecticide.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "mango weevil damage mango leaf fruit weevil",
      "aliases": [
        "Mango / Cutting Weevil",
        "cutting_weevil"
      ],
      "sources": [
        "mangoPunjab",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": "Pest-damage model class; species confirmation is required for chemical choice."
    },
    {
      "en": "Die Back",
      "ur": "ڈائی بیک",
      "vision": true,
      "icon": "✦",
      "symptoms": "Shoot tips and twigs dry progressively backward; bark may darken or crack and associated gummosis/cankers may be present in some cases.",
      "urduSymptoms": "شاخوں کے سرے سے سوکھاؤ پیچھے کی طرف بڑھ سکتا ہے، چھال گہری یا پھٹی اور بعض اوقات گوند خارج ہو سکتی ہے۔",
      "management": "Prune back to healthy wood, disinfect tools, protect wounds and correct drainage/water-contact problems.",
      "prevention": "Avoid trunk injury/direct irrigation against trunks and maintain balanced orchard vigor.",
      "nutritionNote": "",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "metalaxyl + mancozeb (only where local diagnosis links dieback to wound/gummosis disease)"
      ],
      "chemicalNote": "A recent Punjab orchard advisory mentions metalaxyl+mancozeb paste in quick-decline/dieback/gummosis management. This is not a universal cure for every dieback cause; diagnosis and current label are essential.",
      "threshold": "Punjab mango diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "mango dieback Lasiodiplodia twig die back",
      "aliases": [
        "Mango / Die Back",
        "die_back",
        "dieback"
      ],
      "sources": [
        "mangoPunjab",
        "orchard2025",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Gall Midge",
      "ur": "گال مِج",
      "vision": true,
      "icon": "✦",
      "symptoms": "Small raised galls, blistering or abnormal swellings may form on leaves or young tissues; heavy attack can reduce functional leaf area.",
      "urduSymptoms": "پتوں یا نئی بافت پر چھوٹے ابھرے گال، چھالے یا غیر معمولی سوجن بن سکتی ہے۔",
      "management": "Count galls and confirm larvae/midge injury before treatment; prune or remove heavily affected material where practical.",
      "prevention": "Monitor new flushes and conserve natural enemies.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Use an insecticide only after pest confirmation, threshold assessment and current Pakistan mango/gall-midge label.",
      "threshold": "Punjab mango gall-forming insect threshold: 10 galls per leaf.",
      "thresholdUr": "",
      "imageQuery": "mango gall midge leaf gall damage",
      "aliases": [
        "Mango / Gall Midge",
        "gall_midge"
      ],
      "sources": [
        "mangoPunjab",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Powdery Mildew",
      "ur": "پاؤڈری ملڈیو",
      "vision": true,
      "icon": "✦",
      "symptoms": "White powdery fungal growth occurs on panicles, flowers, young leaves or fruitlets; infected flowers may dry and fruit set can fall.",
      "urduSymptoms": "پھولوں، خوشوں، نئے پتوں یا ننھے پھل پر سفید سفوف جیسی تہہ بن سکتی ہے اور پھول سوکھ سکتے ہیں۔",
      "management": "Remove severely affected panicles/shoots where practical and open the canopy.",
      "prevention": "Avoid excessive nitrogen and maintain airflow around flowering tissue.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "Punjab mango diseases: action on appearance after diagnosis.",
      "thresholdUr": "",
      "imageQuery": "mango powdery mildew Oidium mangiferae inflorescence",
      "aliases": [
        "Mango / Powdery Mildew",
        "powdery_mildew"
      ],
      "sources": [
        "mangoPunjab",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Sooty Mould",
      "ur": "سوٹی مولڈ",
      "vision": true,
      "icon": "✦",
      "symptoms": "A black soot-like coating develops on leaves, twigs or fruit, usually growing on honeydew excreted by sucking insects.",
      "urduSymptoms": "پتوں، شاخوں یا پھل پر سیاہ کالک جیسی تہہ بنتی ہے جو عموماً رس چوسنے والے کیڑوں کے ہنی ڈیو پر اگتی ہے۔",
      "management": "Identify and manage the honeydew-producing pest rather than treating the black coating as the primary disease.",
      "prevention": "Improve canopy airflow and wash/remediate heavy surface deposits where practical after pest control.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "A fungicide is usually not the primary solution. If an insecticide is needed, it must target the confirmed honeydew pest at a justified threshold and carry a current Pakistan mango label.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "mango sooty mould black coating honeydew",
      "aliases": [
        "Mango / Sooty Mould",
        "sooty_mould",
        "sooty mold"
      ],
      "sources": [
        "mangoPunjab",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Senescence / Drying",
      "ur": "سینیسنس / سوکھاؤ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Leaves or tissues show generalized aging, yellowing, browning and drying without a single distinctive infectious lesion pattern.",
      "urduSymptoms": "پتے یا بافت عمر رسیدگی کے ساتھ زرد، بھورے اور خشک ہو سکتے ہیں اور کوئی ایک مخصوص بیماری والا دھبہ نہیں ہوتا۔",
      "management": "Treat this as a condition class: inspect irrigation, root health, salinity, nutrient status, heat/cold injury and natural leaf aging before disease treatment.",
      "prevention": "Correct confirmed agronomic stress and monitor for new progressive lesions.",
      "nutritionNote": "Soil/plant testing is especially important. Correct only measured nutrient or salinity problems; fertilizer does not reverse natural senescence or dead tissue.",
      "chemStatus": "none",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "mango leaf senescence dry leaves abiotic stress",
      "aliases": [
        "Mango / senescence or dry",
        "senescence or dry",
        "senescence",
        "drying"
      ],
      "sources": [
        "mangoPunjab",
        "punjabSoil",
        "dppRegistered",
        "dppBanned"
      ],
      "classNote": "Non-specific physiological/condition model class; not a single pathogen."
    }
  ],
  "grape": [
    {
      "en": "Bacterial Leaf Spot",
      "ur": "بیکٹیریل لیف اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Small water-soaked or angular spots may darken and become necrotic, sometimes with yellow halos.",
      "urduSymptoms": "چھوٹے پانی جیسے یا زاویہ دار دھبے گہرے اور مردہ ہو سکتے ہیں اور کبھی زرد ہالہ بن سکتا ہے۔",
      "management": "Avoid working wet vines, prune for airflow and sanitize tools; confirm bacterial etiology before a chemical decision.",
      "prevention": "Use clean planting material and minimize splash spread.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Because this is bacterial, do not default to a fungicide. Use only a current Pakistan grape/bacterial-disease label after confirmation.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "grape bacterial leaf spot Xanthomonas leaf",
      "aliases": [
        "bacterial_leaf_spot"
      ],
      "sources": [
        "grapePHDEC",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Black Rot",
      "ur": "بلیک روٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Reddish-brown leaf spots develop dark margins and black fruiting dots; berries turn brown, then shrivel into hard black mummies.",
      "urduSymptoms": "پتوں پر سرخی مائل بھورے دھبے اور سیاہ نقطے بنتے ہیں، جبکہ بیر بھورے ہو کر سیاہ خشک ممی بن سکتے ہیں۔",
      "management": "Remove mummified berries and infected clusters/canes and prune for rapid drying.",
      "prevention": "Maintain open canopy, sanitation and timely vineyard scouting.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "grape black rot Guignardia bidwellii black mummies leaf",
      "aliases": [
        "black_rot"
      ],
      "sources": [
        "grapePSU",
        "grapePHDEC",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Downy Mildew",
      "ur": "ڈاؤنی ملڈیو",
      "vision": true,
      "icon": "✦",
      "symptoms": "Yellow oil-like spots form on upper leaf surfaces; white downy growth appears beneath in humid conditions, and berries/young shoots can be blighted.",
      "urduSymptoms": "پتوں کے اوپر تیل جیسے زرد دھبے اور نمی میں نیچے سفید روئیں دار تہہ بن سکتی ہے۔",
      "management": "Improve airflow and avoid prolonged leaf wetness; remove severely infected tissue where practical.",
      "prevention": "Use canopy management, drainage and preventive scouting.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "grape downy mildew Plasmopara viticola oil spots white underside",
      "aliases": [
        "downy_mildew"
      ],
      "sources": [
        "grapePSU",
        "grapePHDEC",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Esca Black Measles",
      "ur": "ایسکا بلیک میزلز",
      "vision": true,
      "icon": "✦",
      "symptoms": "Leaves can develop interveinal “tiger-stripe” necrosis; berries may show small dark spots (“measles”), and wood discoloration can occur.",
      "urduSymptoms": "پتوں میں رگوں کے درمیان ٹائیگر اسٹرائپ جیسا سوکھاؤ اور بیری پر چھوٹے سیاہ دھبے بن سکتے ہیں۔",
      "management": "Mark affected vines, prune/remove severely diseased wood carefully and disinfect tools; confirm trunk-disease symptoms.",
      "prevention": "Use clean planting material and minimize pruning wounds/stress.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "There is no reliable curative foliar pesticide for established Esca/trunk infection; management focuses on sanitation, pruning decisions and vine replacement when necessary.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "grape esca black measles tiger stripe leaves berries",
      "aliases": [
        "esca_black_measles",
        "black measles"
      ],
      "sources": [
        "grapePSU",
        "grapePHDEC",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Leaf Blight / Isariopsis Leaf Spot",
      "ur": "لیف بلائٹ / اساریوپسس لیف اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Irregular brown to dark leaf lesions enlarge, may coalesce and can cause premature leaf drop.",
      "urduSymptoms": "بے قاعدہ بھورے یا گہرے دھبے بڑھ کر آپس میں مل سکتے ہیں اور پتے جلد گرا سکتے ہیں۔",
      "management": "Remove infected debris, improve canopy airflow and confirm the leaf-spot pathogen.",
      "prevention": "Prune/manage canopy for sunlight and drying and keep vineyard sanitation.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "grape Isariopsis leaf spot Pseudocercospora vitis",
      "aliases": [
        "leaf_blight_isariopsis_leaf_spot",
        "isariopsis_leaf_spot",
        "leaf blight"
      ],
      "sources": [
        "grapePSU",
        "grapePHDEC",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Yellow Leaf Spot",
      "ur": "یلو لیف اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Yellow spots or blotches develop on foliage and may progress to necrosis; nutritional or abiotic yellowing can look similar.",
      "urduSymptoms": "پتوں پر زرد دھبے یا چتکبرے حصے بن سکتے ہیں جو بعد میں سوکھ سکتے ہیں؛ غذائی زردی بھی ملتی جلتی ہو سکتی ہے۔",
      "management": "Confirm lesion boundaries, underside signs and field distribution before treatment.",
      "prevention": "Maintain balanced nutrition, drainage and canopy airflow.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "No single pesticide is asserted for a non-specific yellow-leaf-spot model label; confirm the causal disease first.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "grape yellow leaf spot grape leaf disease",
      "aliases": [
        "yellow_leaf_spot"
      ],
      "sources": [
        "grapePHDEC",
        "punjabSoil",
        "dppRegistered",
        "dppBanned"
      ],
      "classNote": "Model class; field/lab confirmation is useful because yellow spotting has multiple causes."
    }
  ],
  "eggplant": [
    {
      "en": "General Pest Damage",
      "ur": "جنرل پیسٹ ڈیمیج",
      "vision": true,
      "icon": "✦",
      "symptoms": "Chewed holes, skeletonizing, stippling, mining, frass or fruit/shoot injury may be present depending on the pest.",
      "urduSymptoms": "کیڑے کے مطابق چبائے ہوئے سوراخ، جالی نما پتے، نقطے، مائنز، فضلہ یا پھل/شاخ کا نقصان ہو سکتا ہے۔",
      "management": "Identify the pest and affected plant part before treatment; inspect leaf undersides, shoots and fruit.",
      "prevention": "Use sanitation, traps, natural enemies and threshold-based IPM.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "No single insecticide is valid for generic pest damage. Confirm the pest and apply the Punjab vegetable threshold/current DPP brinjal label.",
      "threshold": "Relevant Punjab vegetable examples: fruit borer 10% on brinjal; jassid 2/leaf; mites 10/leaf; leaf miner 10% affected leaves.",
      "thresholdUr": "",
      "imageQuery": "eggplant brinjal insect pest damage leaf fruit",
      "aliases": [
        "general_pest_damage",
        "pest damage"
      ],
      "sources": [
        "punjabThresholds",
        "eggplantCornell",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Leaf Spot",
      "ur": "لیف اسپاٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Brown to dark circular or irregular leaf lesions may enlarge or merge; several fungal/bacterial agents can produce a similar pattern.",
      "urduSymptoms": "پتوں پر بھورے یا گہرے گول یا بے قاعدہ دھبے بن سکتے ہیں جو بڑھ کر آپس میں مل سکتے ہیں۔",
      "management": "Remove badly affected leaves/debris, avoid splash and confirm the causal agent before a pesticide.",
      "prevention": "Rotate crops, use clean seed/transplants and improve airflow.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "“Leaf spot” is not one guaranteed pathogen; use only a crop-labelled product after diagnosis.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "eggplant leaf spot disease brown lesions",
      "aliases": [
        "leaf_spot"
      ],
      "sources": [
        "eggplantCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": "Model class groups a visual leaf-spot pattern; etiology should be confirmed for chemistry."
    },
    {
      "en": "Mosaic Virus",
      "ur": "موزیک وائرس",
      "vision": true,
      "icon": "✦",
      "symptoms": "Mottled light/dark green leaves, distortion, puckering and stunting can occur; fruit may be misshapen.",
      "urduSymptoms": "پتوں میں ہلکے گہرے سبز چتکبرے نقش، بگاڑ، شکنیں اور کم بڑھوتری ہو سکتی ہے۔",
      "management": "Remove strongly infected plants where feasible, sanitize tools and control weed/alternate hosts.",
      "prevention": "Use clean transplants/seed and resistant varieties where available; manage confirmed vectors using IPM.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "No pesticide cures a plant virus. Insecticide is only relevant to a confirmed vector and must follow threshold/current label.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "eggplant mosaic virus mottled distorted leaves",
      "aliases": [
        "mosaic_virus"
      ],
      "sources": [
        "eggplantCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Phomopsis Blight",
      "ur": "فوموپسس بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Round leaf spots, elongated stem lesions/cankers and sunken soft fruit rot can occur.",
      "urduSymptoms": "پتوں پر گول دھبے، تنے پر لمبے زخم/کینکر اور پھل پر دھنسے سڑن والے حصے بن سکتے ہیں۔",
      "management": "Remove infected fruit and debris, avoid saving seed from diseased fruit and minimize splash.",
      "prevention": "Use clean seed/transplants and rotate away from eggplant/related hosts.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "eggplant Phomopsis blight fruit rot leaf stem",
      "aliases": [
        "phomopsis_blight"
      ],
      "sources": [
        "eggplantCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "White Mold",
      "ur": "وائٹ مولڈ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Water-soaked soft lesions become covered by white cottony fungal growth; hard black sclerotia may form on or inside stems/fruit.",
      "urduSymptoms": "پانی جیسے نرم زخموں پر سفید روئی جیسی پھپھوندی بنتی ہے اور سیاہ سخت اسکلروٹیا بن سکتے ہیں۔",
      "management": "Remove infected plants/tissue before sclerotia spread and avoid moving infested soil/debris.",
      "prevention": "Use wider spacing, irrigation timing and long rotation with non-hosts where feasible.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Fungicides for white mold are preventive/timing-sensitive; no spray reverses advanced stem infection. Use only a current Pakistan brinjal/white-mold label.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "eggplant white mold Sclerotinia sclerotiorum cottony sclerotia",
      "aliases": [
        "white_mold"
      ],
      "sources": [
        "whiteMoldCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    }
  ],
  "cucumber": [
    {
      "en": "Bacterial Wilt",
      "ur": "بیکٹیریل ولٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "A leaf or vine suddenly wilts, then collapse can spread rapidly through the plant; leaf margins may yellow/necrose.",
      "urduSymptoms": "پتہ یا بیل اچانک مرجھا سکتی ہے اور تیزی سے پورا پودا گر سکتا ہے؛ کناروں پر زردی یا سوکھاؤ ہو سکتا ہے۔",
      "management": "Remove collapsed plants and investigate insect vectors and root/crown problems before treatment.",
      "prevention": "Use clean planting material, vector exclusion/IPM and sanitation.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "There is no pesticide cure once a plant has bacterial wilt. Insecticides only target confirmed beetle/vector pressure where locally relevant and label-supported.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cucumber bacterial wilt Erwinia tracheiphila wilt vine",
      "aliases": [
        "bacterial_wilt"
      ],
      "sources": [
        "cucumberCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Belly Rot",
      "ur": "بیلی روٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Tan-brown, water-soaked or sunken rot develops mainly on the underside of fruit touching wet soil and can enlarge.",
      "urduSymptoms": "گیلی مٹی سے لگنے والے پھل کے نچلے حصے پر پانی جیسی، بھوری یا دھنسے سڑن بن سکتی ہے۔",
      "management": "Remove affected fruit, improve drainage and lift fruit away from wet soil.",
      "prevention": "Use mulch/trellising, well-drained beds and irrigation management.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Cultural prevention is primary. A fungicide should be used only if the diagnosis and current Pakistan cucumber/belly-rot label support it.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cucumber belly rot Rhizoctonia solani fruit underside",
      "aliases": [
        "belly_rot"
      ],
      "sources": [
        "cucumberFruitCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Downy Mildew",
      "ur": "ڈاؤنی ملڈیو",
      "vision": true,
      "icon": "✦",
      "symptoms": "Angular pale-yellow to brown lesions are bounded by small veins; gray-purple downy sporulation can form on leaf undersides.",
      "urduSymptoms": "پتوں پر رگوں سے محدود زاویہ دار زرد یا بھورے دھبے بنتے ہیں اور نیچے سرمئی جامنی روئیں دار تہہ بن سکتی ہے۔",
      "management": "Improve ventilation and keep foliage dry; remove severely blighted leaves where practical.",
      "prevention": "Use resistant varieties where available and preventive scouting.",
      "nutritionNote": "",
      "chemStatus": "pakistan_advisory",
      "chemExamples": [
        "metalaxyl-M + mancozeb"
      ],
      "chemicalNote": "Punjab Plant Pathology Research Institute lists metalaxyl-M + mancozeb for downy mildew of cucurbits. Because resistance can develop quickly, use only when the current DPP crop/target label permits it and rotate modes of action according to that label.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cucumber downy mildew Pseudoperonospora cubensis angular yellow underside",
      "aliases": [
        "downy_mildew"
      ],
      "sources": [
        "cucumberCornell",
        "ppri",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Gummy Stem Blight",
      "ur": "گمی اسٹیم بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Tan-brown leaf lesions, stem cankers and gummy exudate can occur; fruit may develop black rot with dark fruiting bodies.",
      "urduSymptoms": "پتوں پر بھورے دھبے، تنے پر کینکر اور گوند جیسا اخراج ہو سکتا ہے، جبکہ پھل بلیک روٹ کا شکار ہو سکتا ہے۔",
      "management": "Remove infected vines/debris, avoid working wet plants and disinfect tools.",
      "prevention": "Use clean seed, rotation and canopy/irrigation management to reduce leaf wetness.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Use only a fungicide currently labelled in Pakistan for cucumber/gummy stem blight and rotate FRAC groups because resistance can be common.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cucumber gummy stem blight Didymella bryoniae stem gummy exudate",
      "aliases": [
        "gummy_stem_blight"
      ],
      "sources": [
        "cucumberCornell",
        "cucumberFruitCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Pythium Fruit Rot",
      "ur": "پائتھیم فروٹ روٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Fruit in contact with wet soil develops soft/watery rot; small raised whitish lesions or cottony growth may occur depending on stage.",
      "urduSymptoms": "گیلی مٹی سے لگنے والے پھل میں نرم پانی جیسی سڑن بنتی ہے اور بعض اوقات سفید ابھرے دھبے یا روئیں دار تہہ بن سکتی ہے۔",
      "management": "Improve drainage immediately, remove rotting fruit and keep fruit off wet soil.",
      "prevention": "Use mulch/trellising and avoid waterlogging.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "Drainage and fruit-soil separation are fundamental. Oomycete-active products should be used only where a current Pakistan cucumber/Pythium label exists.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "cucumber Pythium fruit rot watery rot fruit",
      "aliases": [
        "pythium_fruit_rot"
      ],
      "sources": [
        "cucumberFruitCornell",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    }
  ],
  "peas": [
    {
      "en": "Ascochyta Blight",
      "ur": "ایسکوکائٹا بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Tan to brown leaf/pod spots often have darker borders and may contain tiny black fruiting dots; stems can develop purplish lesions.",
      "urduSymptoms": "پتوں اور پھلیوں پر ہلکے بھورے دھبے گہرے کناروں کے ساتھ بن سکتے ہیں اور چھوٹے سیاہ نقطے دکھائی دے سکتے ہیں۔",
      "management": "Use clean seed, avoid working wet plants and remove heavily infected residue.",
      "prevention": "Rotate away from peas/legumes according to local guidance and use resistant varieties where available.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "pea Ascochyta blight leaf pod black pycnidia",
      "aliases": [
        "ascochyta_blight"
      ],
      "sources": [
        "peasUMN",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Botrytis Blight",
      "ur": "بوٹریٹس بلائٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Soft brown lesions develop gray fuzzy mold under humid conditions, especially on flowers, pods or senescing tissue.",
      "urduSymptoms": "نمی میں نرم بھورے زخموں پر سرمئی روئیں دار پھپھوندی بن سکتی ہے، خاص طور پر پھول یا پھلی پر۔",
      "management": "Remove infected tissue, reduce canopy humidity and avoid overhead watering late in the day.",
      "prevention": "Use wider spacing/airflow, sanitation and avoid excessive nitrogen.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "pea Botrytis blight gray mold pods flowers",
      "aliases": [
        "botrytis_blight",
        "gray mold peas"
      ],
      "sources": [
        "peasUMN",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Fusarium Wilt",
      "ur": "فیوزیریم ولٹ",
      "vision": true,
      "icon": "✦",
      "symptoms": "Lower leaves yellow and plants wilt progressively; vascular tissue may brown while soil moisture remains adequate.",
      "urduSymptoms": "نچلے پتے زرد اور پودا بتدریج مرجھا سکتا ہے اور مناسب نمی کے باوجود اندرونی نالیاں بھوری ہو سکتی ہیں۔",
      "management": "Confirm vascular wilt, remove severely affected plants and avoid moving infested soil.",
      "prevention": "Use resistant varieties, clean seed and long rotation where feasible; improve drainage.",
      "nutritionNote": "",
      "chemStatus": "no_curative",
      "chemExamples": [],
      "chemicalNote": "There is no reliable foliar pesticide cure for established Fusarium wilt; management is preventive.",
      "threshold": "",
      "thresholdUr": "",
      "imageQuery": "pea Fusarium wilt vascular browning pea",
      "aliases": [
        "fusarium_wilt"
      ],
      "sources": [
        "peasUMN",
        "punjabThresholds",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    },
    {
      "en": "Pod Borer Damage",
      "ur": "پھلی بورر کا نقصان",
      "vision": true,
      "icon": "✦",
      "symptoms": "Entry holes, feeding scars, frass and damaged seeds/pods occur; larvae may be present inside or near pods.",
      "urduSymptoms": "پھلی میں داخلے کے سوراخ، کھانے کے نشان، فضلہ اور خراب بیج/پھلی نظر آ سکتے ہیں اور لاروا اندر ہو سکتا ہے۔",
      "management": "Scout plants/pods, hand-remove infested material in small plots and conserve biological control agents.",
      "prevention": "Use pheromone/light monitoring where appropriate and threshold-based IPM.",
      "nutritionNote": "",
      "chemStatus": "verify_only",
      "chemExamples": [],
      "chemicalNote": "If the threshold is reached, use only an insecticide currently DPP-registered for peas/pod borer; do not transfer a chickpea label to peas.",
      "threshold": "Punjab pulses pod-borer threshold: 5 larvae per m².",
      "thresholdUr": "پنجاب میں دالوں کے پوڈ بورر کی حد: 5 لاروا فی مربع میٹر.",
      "imageQuery": "pea pod borer Helicoverpa damaged pod larva",
      "aliases": [
        "pod_borer_damage",
        "pod borer"
      ],
      "sources": [
        "punjabThresholds",
        "peasUMN",
        "dppRegistered",
        "dppBanned",
        "punjabSoil"
      ],
      "classNote": ""
    }
  ]
  // --- lemon & soybean hidden for now (re-enable later) ---
  // "lemon": [
  //   {
  //     "en": "Citrus Canker",
  //     "ur": "سِٹرس کینکر",
  //     "vision": true,
  //     "icon": "✦",
  //     "symptoms": "Raised corky lesions with yellow halos develop on leaves, twigs or fruit; older lesions may crack and appear crater-like.",
  //     "urduSymptoms": "پتوں، شاخوں یا پھل پر زرد ہالے کے ساتھ ابھرے کھردرے دھبے بنتے ہیں اور پرانے زخم پھٹ سکتے ہیں۔",
  //     "management": "Use disease-free budwood, prune and destroy infected shoots where permitted, disinfect tools and reduce wind-driven splash.",
  //     "prevention": "Maintain orchard hygiene, wind protection where practical and balanced nutrition without excessive soft growth.",
  //     "nutritionNote": "",
  //     "chemStatus": "pakistan_advisory",
  //     "chemExamples": [
  //       "copper-based products",
  //       "kasugamycin"
  //     ],
  //     "chemicalNote": "Punjab orchard guidance lists copper-based products and kasugamycin for citrus canker. PPRI also reports antibacterial treatment work in citrus. Verify the current DPP citrus/canker product label before use.",
  //     "threshold": "Punjab citrus diseases: action on appearance after diagnosis.",
  //     "thresholdUr": "",
  //     "imageQuery": "citrus canker lemon Xanthomonas citri corky yellow halo",
  //     "aliases": [
  //       "citrus_canker",
  //       "Lemon / Citrus Canker"
  //     ],
  //     "sources": [
  //       "orchard2025",
  //       "phdecCitrus",
  //       "punjabThresholds",
  //       "dppRegistered",
  //       "dppBanned",
  //       "punjabSoil"
  //     ],
  //     "classNote": ""
  //   },
  //   {
  //     "en": "Sooty Mould",
  //     "ur": "سوٹی مولڈ",
  //     "vision": true,
  //     "icon": "✦",
  //     "symptoms": "A superficial black soot-like coating forms on leaves, twigs or fruit, usually on sticky honeydew from whiteflies, scales, aphids or other sucking pests.",
  //     "urduSymptoms": "پتوں، شاخوں یا پھل پر سیاہ کالک جیسی سطحی تہہ بنتی ہے جو عموماً رس چوسنے والے کیڑوں کے چپچپے ہنی ڈیو پر اگتی ہے۔",
  //     "management": "Identify and manage the honeydew-producing insect, then wash/allow weathering of the superficial mould where practical.",
  //     "prevention": "Improve canopy airflow and scout for scales, whiteflies, psyllids and aphids.",
  //     "nutritionNote": "",
  //     "chemStatus": "verify_only",
  //     "chemExamples": [],
  //     "chemicalNote": "The mould itself is usually secondary; insecticide use should target a confirmed honeydew pest at its relevant threshold and current citrus label, not the black coating alone.",
  //     "threshold": "",
  //     "thresholdUr": "",
  //     "imageQuery": "lemon citrus sooty mold black leaves honeydew",
  //     "aliases": [
  //       "sooty_mould",
  //       "sooty mold"
  //     ],
  //     "sources": [
  //       "phdecCitrus",
  //       "punjabThresholds",
  //       "dppRegistered",
  //       "dppBanned",
  //       "punjabSoil"
  //     ],
  //     "classNote": ""
  //   }
  // ],
  // "soybean": [
  //   {
  //     "en": "Bacterial Blight",
  //     "ur": "بیکٹیریل بلائٹ",
  //     "vision": true,
  //     "icon": "✦",
  //     "symptoms": "Small angular water-soaked spots turn yellow then brown, often with yellow-green halos; dead centers may fall out and give a ragged look.",
  //     "urduSymptoms": "چھوٹے زاویہ دار پانی جیسے دھبے زرد پھر بھورے ہو جاتے ہیں، عموماً زرد سبز ہالے کے ساتھ، اور مردہ حصہ گر سکتا ہے۔",
  //     "management": "Use pathogen-free seed, avoid cultivation/handling when foliage is wet and rotate with non-host crops.",
  //     "prevention": "Manage infected residue and use resistant varieties where locally available.",
  //     "nutritionNote": "",
  //     "chemStatus": "verify_only",
  //     "chemExamples": [],
  //     "chemicalNote": "Bacterial blight often stops progressing in hot dry weather. Do not apply a fungicide as a default; any bactericide requires a current Pakistan soybean/bacterial-blight label.",
  //     "threshold": "",
  //     "thresholdUr": "",
  //     "imageQuery": "soybean bacterial blight Pseudomonas syringae glycinea halo leaf",
  //     "aliases": [
  //       "bacterial_blight",
  //       "Soybean / bacterial_blight"
  //     ],
  //     "sources": [
  //       "soyBacterial",
  //       "dppRegistered",
  //       "dppBanned",
  //       "punjabSoil"
  //     ],
  //     "classNote": ""
  //   },
  //   {
  //     "en": "Frogeye Leaf Spot",
  //     "ur": "فراگ آئی لیف اسپاٹ",
  //     "vision": true,
  //     "icon": "✦",
  //     "symptoms": "Round leaf lesions have light gray/tan centers with dark reddish-brown or purple margins; black specks or shot-hole centers may appear.",
  //     "urduSymptoms": "پتوں پر ہلکے سرمئی یا بھورے مرکز اور گہرے سرخی مائل یا جامنی کناروں والے گول دھبے بنتے ہیں۔",
  //     "management": "Use resistant varieties and pathogen-free seed, rotate with non-bean crops and manage infected residue.",
  //     "prevention": "Scout warm humid canopies, especially after flowering.",
  //     "nutritionNote": "",
  //     "chemStatus": "verify_only",
  //     "chemExamples": [],
  //     "chemicalNote": "Foliar fungicides can be useful in some systems, but this website does not assert a Pakistan soybean/frogeye product without a current DPP crop/target label.",
  //     "threshold": "",
  //     "thresholdUr": "",
  //     "imageQuery": "soybean frogeye leaf spot Cercospora sojina gray center purple margin",
  //     "aliases": [
  //       "frogeye_leaf_spot",
  //       "Soybean / frogeye_leaf_spot"
  //     ],
  //     "sources": [
  //       "soyFrogeye",
  //       "dppRegistered",
  //       "dppBanned",
  //       "punjabSoil"
  //     ],
  //     "classNote": ""
  //   }
  // ]
};



// -----------------------------------------------------------------------------
// Deep disease descriptors reviewed against crop-specific extension / research
// sources. These add disease-specific cause and risk context without pretending
// that a photo alone proves etiology for broad syndrome classes.
// -----------------------------------------------------------------------------
const DEEP_DISEASE_DETAILS = {
  "corn": {
    "Bacterial Leaf Streak": [
      "bacterial",
      "Xanthomonas vasicola pv. vasculorum",
      "Warm, humid weather, rain splash and infected crop residue favor lesion development and spread."
    ],
    "Common Rust": [
      "fungal",
      "Puccinia sorghi",
      "Cool to moderate temperatures, high humidity and long dew periods favor infection; spores arrive by wind."
    ],
    "Gray Leaf Spot": [
      "fungal",
      "Cercospora zeae-maydis / Cercospora zeina",
      "Warm, humid weather, prolonged leaf wetness and infected maize residue increase risk."
    ],
    "Maize Lethal Necrosis": [
      "viral",
      "Coinfection involving maize chlorotic mottle virus plus a potyvirus such as sugarcane mosaic virus",
      "Infected seed or plants and insect-vector activity increase risk; mixed virus infection drives severe symptoms."
    ],
    "Maize Streak Virus": [
      "viral",
      "Maize streak virus; transmitted mainly by Cicadulina leafhoppers",
      "Early infection and high leafhopper pressure increase stunting and yield loss."
    ],
    "Northern Leaf Blight": [
      "fungal",
      "Exserohilum turcicum",
      "Moderate temperatures, frequent dew/rain and infected residue favor disease development."
    ]
  },
  "cotton": {
    "Alternaria Leaf Spot": [
      "fungal",
      "Alternaria spp., commonly A. macrospora / A. alternata complexes",
      "Leaf wetness, humidity, crop stress and infected residue favor spotting."
    ],
    "Bacterial Blight": [
      "bacterial",
      "Xanthomonas citri pv. malvacearum",
      "Rain splash, storms, wounds, contaminated seed and susceptible varieties increase spread."
    ],
    "Herbicide Growth Damage": [
      "abiotic",
      "Herbicide exposure or carryover injury; not an infectious disease",
      "Recent spraying, drift, tank contamination, overlap, weather stress or soil carryover can produce patterned injury."
    ],
    "Leaf Curl": [
      "viral",
      "Cotton leaf curl begomovirus complex; transmitted by whitefly (Bemisia tabaci)",
      "High whitefly pressure and nearby infected hosts increase risk, especially in young crops."
    ],
    "Leaf Hopper Jassids": [
      "pest",
      "Cotton jassid/leafhopper feeding, commonly Amrasca biguttula biguttula",
      "Warm weather and increasing jassid populations favor hopper-burn symptoms."
    ],
    "Leaf Reddening": [
      "abiotic",
      "Multifactorial physiological syndrome; may involve boll load, nutrient imbalance, root/water stress or temperature stress",
      "Heavy boll load, root stress, moisture imbalance and nutrient imbalance can intensify reddening."
    ],
    "Leaf Variegation": [
      "syndrome",
      "Visual variegation/chlorosis model class; multiple nutritional, genetic, viral or injury causes are possible",
      "Field pattern, new versus old leaves, spray history and nutrient status are needed to identify the true cause."
    ],
    "Verticillium Wilt": [
      "fungal",
      "Verticillium dahliae, a soilborne vascular fungus",
      "Infested soil, susceptible varieties and root-zone stress favor wilt; microsclerotia can persist for years."
    ]
  },
  "tomato": {
    "Bacterial Spot": [
      "bacterial",
      "Xanthomonas species complex",
      "Warm, wet weather, splash, contaminated seed/transplants and handling wet plants favor spread."
    ],
    "Cercospora Leaf Mold": [
      "fungal",
      "Cercospora fuligena (black leaf mold) or a closely related Cercospora leaf-mold complex",
      "Warm, humid conditions and prolonged leaf wetness favor infection."
    ],
    "Early Blight": [
      "fungal",
      "Alternaria solani / Alternaria linariae complex",
      "Warm weather, dew/rain, lower-leaf aging and crop stress favor disease."
    ],
    "General Pest Damage": [
      "syndrome",
      "Non-specific insect/arthropod feeding damage; exact pest must be confirmed",
      "Risk depends on the pest; inspect both leaf surfaces, growing points, stems and fruit for insects, mines, webbing or frass."
    ],
    "Late Blight": [
      "oomycete",
      "Phytophthora infestans",
      "Cool to mild, very humid weather and prolonged leaf wetness can drive rapid epidemics."
    ],
    "Leaf Miner": [
      "pest",
      "Leaf-mining insect damage; species may include Liriomyza spp. or other local miners",
      "Warm weather and untreated host plants allow overlapping generations; mines often increase from lower leaves upward."
    ],
    "Leaf Mold": [
      "fungal",
      "Passalora fulva (syn. Cladosporium fulvum)",
      "High relative humidity, dense canopies and protected cultivation strongly favor disease."
    ],
    "Septoria Leaf Spot": [
      "fungal",
      "Septoria lycopersici",
      "Splashing rain, leaf wetness and infected debris favor lower-leaf infection and upward spread."
    ],
    "Shot Hole Disease": [
      "syndrome",
      "Shot-hole type lesion model class; more than one pathogen or injury can cause tissue to drop out",
      "Wet spotting diseases, spray injury or mechanical damage can produce holes; confirm lesion margins and field pattern."
    ],
    "Spider Mites": [
      "pest",
      "Tetranychus spider mites",
      "Hot, dry, dusty conditions and disruption of natural enemies favor rapid mite increase."
    ],
    "Target Spot": [
      "fungal",
      "Corynespora cassiicola",
      "Warm, humid weather, long leaf wetness and dense foliage favor disease."
    ],
    "Tomato Leaf Curl Virus": [
      "viral",
      "Leaf-curl begomovirus complex, usually whitefly-transmitted",
      "High whitefly pressure and infected alternate hosts/transplants increase risk."
    ],
    "Tomato Mosaic Virus": [
      "viral",
      "Tomato mosaic virus (ToMV)",
      "Mechanical sap transmission, contaminated hands/tools, infected seed and plant debris can spread the virus."
    ],
    "Tomato Yellow Leaf Curl Virus": [
      "viral",
      "Tomato yellow leaf curl virus (TYLCV), transmitted by Bemisia tabaci whiteflies",
      "Whitefly pressure, infected seedlings and nearby host plants increase risk; early infection is most damaging."
    ]
  },
  "apple": {
    "Alternaria Apple": [
      "fungal",
      "Alternaria mali / Alternaria blotch complex",
      "Warm, humid weather and repeated leaf wetness favor blotch development on susceptible cultivars."
    ],
    "Apple Powdery Mildew": [
      "fungal",
      "Podosphaera leucotricha",
      "Mild temperatures and high humidity favor infection; unlike many fungi, free water is not required for spore germination."
    ],
    "Apple Scab": [
      "fungal",
      "Venturia inaequalis",
      "Cool to mild wet periods during green-tip through early fruit development drive primary infections."
    ],
    "Black Rot": [
      "fungal",
      "Botryosphaeria obtusa / Diplodia seriata complex",
      "Dead wood, mummified fruit, fire-blight strikes and wounds provide inoculum and infection courts."
    ],
    "Cedar Apple Rust": [
      "fungal",
      "Gymnosporangium juniperi-virginianae rust fungus",
      "Nearby infected juniper/red cedar plus spring rains and leaf wetness create high infection risk."
    ]
  },
  "rice": {
    "Bacterial Leaf Blight": [
      "bacterial",
      "Xanthomonas oryzae pv. oryzae",
      "Wind-driven rain, wounds, high nitrogen, storms and infected residues can increase disease."
    ],
    "Brown Spot": [
      "fungal",
      "Bipolaris oryzae",
      "Nutrient-stressed plants, drought or other stress, infected seed and humid leaf-wetness periods favor disease."
    ],
    "Leaf Scald": [
      "fungal",
      "Microdochium oryzae (leaf scald pathogen complex)",
      "High humidity, frequent rain and infected seed/residue favor symptom development."
    ],
    "Narrow Brown Leaf Spot": [
      "fungal",
      "Cercospora janseana / narrow brown leaf spot pathogen complex",
      "Humid weather and crop stress favor lesions, often later in the season."
    ],
    "Rice Blast": [
      "fungal",
      "Magnaporthe oryzae (Pyricularia oryzae)",
      "High humidity, dew, cool nights, susceptible varieties and excessive/late nitrogen increase risk."
    ],
    "Rice Hispa": [
      "pest",
      "Rice hispa beetle, Dicladispa armigera",
      "Lush rice growth and favorable warm-humid conditions can increase beetle feeding and larval mining."
    ],
    "Rice Leaffolder": [
      "pest",
      "Rice leaffolder moth, commonly Cnaphalocrocis medinalis",
      "Lush nitrogen-rich canopies and humid conditions can favor populations; larvae fold leaves and feed inside."
    ],
    "Rice Stripes": [
      "syndrome",
      "Stripe-type model class; viral, nutritional or other causes can produce longitudinal striping",
      "Confirm field distribution, vector presence and nutrient status before assigning a causal disease."
    ],
    "Rice Tungro": [
      "viral",
      "Rice tungro virus complex; transmitted by green leafhoppers",
      "Infected volunteer rice and high green-leafhopper activity increase risk, especially in staggered plantings."
    ],
    "Sheath Blight": [
      "fungal",
      "Rhizoctonia solani",
      "Dense canopies, high humidity, standing water contact and high nitrogen favor upward spread from lower sheaths."
    ]
  },
  "mango": {
    "Anthracnose": [
      "fungal",
      "Colletotrichum species complex, commonly C. gloeosporioides sensu lato",
      "Rain, high humidity and wet flowers/young fruit favor infection; latent infections may appear during ripening."
    ],
    "Bacterial Canker": [
      "bacterial",
      "Xanthomonas citri pv. mangiferaeindicae / mango bacterial canker complex",
      "Wind-driven rain, wounds and wet conditions favor spread and infection."
    ],
    "Cutting Weevil": [
      "pest",
      "Weevil feeding/cutting damage; exact local species should be confirmed from the insect or characteristic injury",
      "Tender flush and unmanaged orchard pest reservoirs can increase damage; verify adults/larvae before treatment."
    ],
    "Die Back": [
      "fungal",
      "Lasiodiplodia theobromae / Botryodiplodia-type dieback complex; other causes can mimic it",
      "Wounds, drought/heat stress, poor tree vigor and infected pruning material can contribute."
    ],
    "Gall Midge": [
      "pest",
      "Mango gall-midge complex (Procontarinia and related midges)",
      "Tender flush and flowering stages are most vulnerable; repeated generations can build when infested tissue remains."
    ],
    "Powdery Mildew": [
      "fungal",
      "Oidium mangiferae",
      "Cool to mild, humid weather around flowering strongly favors powdery mildew; rain can reduce exposed spores but prolonged favorable weather drives outbreaks."
    ],
    "Sooty Mould": [
      "fungal",
      "Surface-growing sooty-mould fungi colonizing honeydew; the primary problem is usually a sap-sucking insect",
      "Scale, mealybug, hopper or whitefly honeydew supports black fungal growth."
    ],
    "Senescence / Drying": [
      "abiotic",
      "Non-infectious visual condition class; may reflect natural senescence, water/root stress, salinity, heat/cold or other injury",
      "Irrigation problems, root damage, salinity, nutrient imbalance and weather extremes should be checked before pesticide use."
    ]
  },
  "grape": {
    "Bacterial Leaf Spot": [
      "bacterial",
      "Bacterial leaf-spot complex; Xanthomonas-type pathogens can cause similar symptoms",
      "Warm wet weather, wounds and rain splash favor bacterial spread; exact pathogen should be confirmed locally."
    ],
    "Black Rot": [
      "fungal",
      "Phyllosticta ampelicida (Guignardia bidwellii)",
      "Warm wet periods, mummified berries and infected cane/leaf debris provide inoculum."
    ],
    "Downy Mildew": [
      "oomycete",
      "Plasmopara viticola",
      "Warm, wet nights, high humidity and prolonged leaf wetness strongly favor epidemics."
    ],
    "Esca Black Measles": [
      "fungal",
      "Grapevine trunk-disease complex involving Phaeomoniella, Phaeoacremonium and other wood-colonizing fungi",
      "Pruning wounds, infected propagation material and vine age/stress contribute; foliar symptoms can be intermittent."
    ],
    "Leaf Blight / Isariopsis Leaf Spot": [
      "fungal",
      "Pseudocercospora vitis (formerly Isariopsis leaf spot complex)",
      "Warm humid weather and infected leaves/canes favor repeated spotting."
    ],
    "Yellow Leaf Spot": [
      "syndrome",
      "Non-specific yellow leaf-spot model class; nutritional, viral, fungal or abiotic causes are possible",
      "Confirm lesion pattern, vine distribution, nutrient status and vector/pest signs before choosing treatment."
    ]
  },
  "eggplant": {
    "General Pest Damage": [
      "syndrome",
      "Non-specific insect/arthropod damage model class",
      "Inspect leaf undersides, shoots, stems and fruit for the actual pest before any insecticide decision."
    ],
    "Leaf Spot": [
      "syndrome",
      "Leaf-spot model class; Alternaria, Cercospora and other pathogens can produce similar lesions",
      "Warm humid weather and splash favor many fungal leaf spots, but the causal agent should be confirmed."
    ],
    "Mosaic Virus": [
      "viral",
      "Mosaic-virus syndrome; cucumber mosaic virus, tobamoviruses and other viruses can infect eggplant",
      "Infected seedlings, weeds, aphid vectors or mechanical transmission may be involved depending on the virus."
    ],
    "Phomopsis Blight": [
      "fungal",
      "Diaporthe vexans (syn. Phomopsis vexans)",
      "Warm humid weather, infected seed/debris and splash favor leaf, stem and fruit infection."
    ],
    "White Mold": [
      "fungal",
      "Sclerotinia sclerotiorum",
      "Cool to mild humid conditions, dense canopies and long soil survival of sclerotia favor outbreaks."
    ]
  },
  "cucumber": {
    "Bacterial Wilt": [
      "bacterial",
      "Vascular bacterial-wilt syndrome; pathogen identity can vary by production region, so field confirmation is important",
      "Vector feeding or contaminated soil/water pathways depend on the causal bacterium; confirm vascular signs before treatment."
    ],
    "Belly Rot": [
      "fungal",
      "Rhizoctonia solani",
      "Fruit contact with warm wet soil, poor drainage and dense foliage favor lesions on the underside of fruit."
    ],
    "Downy Mildew": [
      "oomycete",
      "Pseudoperonospora cubensis",
      "High humidity, leaf wetness and moderate temperatures favor rapid foliar spread."
    ],
    "Gummy Stem Blight": [
      "fungal",
      "Stagonosporopsis cucurbitacearum / gummy stem blight complex",
      "Warm wet weather, infected seed/debris and wounds favor leaf, stem and fruit infection."
    ],
    "Pythium Fruit Rot": [
      "oomycete",
      "Pythium species",
      "Waterlogged soil, fruit-soil contact, poor drainage and warm wet conditions favor watery fruit rot."
    ]
  },
  "peas": {
    "Ascochyta Blight": [
      "fungal",
      "Ascochyta/Didymella blight complex of pea",
      "Cool wet weather, infected seed and crop residue favor splash-dispersed lesions."
    ],
    "Botrytis Blight": [
      "fungal",
      "Botrytis cinerea",
      "Cool humid weather, dense canopies, senescing flowers and prolonged tissue wetness favor gray mold."
    ],
    "Fusarium Wilt": [
      "fungal",
      "Fusarium oxysporum f. sp. pisi",
      "Infested soil, susceptible cultivars and warm root-zone conditions favor vascular wilt."
    ],
    "Pod Borer Damage": [
      "pest",
      "Pod-boring caterpillar damage, commonly Helicoverpa armigera in South Asian pulses",
      "Flowering/podding crops are vulnerable; inspect larvae and fresh feeding holes before threshold-based treatment."
    ]
  }
  // --- lemon & soybean hidden for now (re-enable later) ---
  // "lemon": {
  //   "Citrus Canker": [
  //     "bacterial",
  //     "Xanthomonas citri subsp. citri",
  //     "Wind-driven rain, leaf-miner injury, wounds and young flush favor spread; lesions can occur on leaves, twigs and fruit."
  //   ],
  //   "Sooty Mould": [
  //     "fungal",
  //     "Superficial sooty fungi growing on honeydew; usually secondary to scale, aphids, mealybugs or whiteflies",
  //     "Honeydew-producing insects and dense canopies favor black surface growth; the fungi do not usually invade healthy tissue."
  //   ]
  // },
  // "soybean": {
  //   "Bacterial Blight": [
  //     "bacterial",
  //     "Pseudomonas savastanoi pv. glycinea",
  //     "Cool wet weather, rain splash, hail/wounds and infected residue or seed can favor disease."
  //   ],
  //   "Frogeye Leaf Spot": [
  //     "fungal",
  //     "Cercospora sojina",
  //     "Warm humid weather, frequent dew/rain and infected residue favor leaf infection and repeated cycles."
  //   ]
  // }
};
const DEFAULT_NUTRITION_EN = 'Fertilizer does not cure an infectious disease. Use soil/plant testing to identify a real deficiency, then follow a site-specific fertilizer recommendation. Avoid unnecessary or excessive nitrogen where lush growth can increase pest or foliar-disease pressure.';
const DEFAULT_NUTRITION_UR = 'کھاد کسی متعدی بیماری کا علاج نہیں ہے۔ حقیقی غذائی کمی کی شناخت کے لیے مٹی/پودے کا ٹیسٹ کروائیں اور پھر مقام کے مطابق کھاد کی سفارش پر عمل کریں۔ غیر ضروری یا ضرورت سے زیادہ نائٹروجن سے بچیں۔';


const KIND_LABELS = {
  en: {
    fungal:'Fungal disease', oomycete:'Oomycete disease', bacterial:'Bacterial disease',
    viral:'Viral disease', pest:'Insect / mite damage', abiotic:'Non-infectious disorder',
    syndrome:'Visual syndrome / broad model class'
  },
  ur: {
    fungal:'فنگس کی بیماری', oomycete:'فنگس نما جراثیم کی بیماری', bacterial:'بیکٹیریا کی بیماری',
    viral:'وائرس کی بیماری', pest:'کیڑے / مائٹ کا نقصان', abiotic:'غیر متعدی حالت',
    syndrome:'بصری سنڈروم / وسیع ماڈل کلاس'
  }
};

const KIND_RISK_UR = {
  fungal:'زیادہ نمی، پتوں کی طویل نمی، بارش یا گھنی چھتری بیماری کے خطرے کو بڑھا سکتی ہے۔',
  oomycete:'زیادہ نمی، آزاد پانی اور پتوں کی طویل نمی تیز پھیلاؤ کا باعث بن سکتی ہے۔',
  bacterial:'بارش کے چھینٹے، زخم، آلودہ مواد اور زیادہ نمی بیکٹیریا کے پھیلاؤ میں مدد دے سکتے ہیں۔',
  viral:'متاثرہ پودا، ویکٹر کیڑا یا آلودہ پوداتی مواد اہم ذرائع ہو سکتے ہیں؛ وائرس کو فنگس کش دوا ختم نہیں کرتی۔',
  pest:'میزبان فصل کی موجودگی اور بڑھتی ہوئی کیڑوں کی آبادی نقصان بڑھا سکتی ہے؛ علاج سے پہلے کیڑے کی تصدیق کریں۔',
  abiotic:'پانی، نمکیات، غذائیت، جڑی بوٹی مار دوا یا موسمی دباؤ جیسی غیر متعدی وجوہات پہلے چیک کریں۔',
  syndrome:'یہ ایک بصری ماڈل کلاس ہے؛ ایک سے زیادہ وجوہات ممکن ہیں، اس لیے کھیت کی تصدیق ضروری ہے۔'
};

function diseaseDeepDetail(cropId,e){
  const d=DEEP_DISEASE_DETAILS?.[cropId]?.[e?.en];
  if(!d) return {kind:'syndrome',agent:'Cause not uniquely established for this model class.',risk:'Confirm the field pattern and causal agent before disease-specific treatment.'};
  return {kind:d[0],agent:d[1],risk:d[2]};
}
function diseaseKindLabel(d){ return (KIND_LABELS[state.lang]||KIND_LABELS.en)[d.kind] || d.kind; }
function diseaseCauseText(d){
  if(state.lang==='ur') return `${diseaseKindLabel(d)} — ${d.agent}`;
  return `${diseaseKindLabel(d)} — ${d.agent}`;
}
function diseaseRiskText(d){
  if(state.lang==='ur') return KIND_RISK_UR[d.kind] || KIND_RISK_UR.syndrome;
  return d.risk;
}

function chemicalGuidance(e){
  const status=e.chemStatus||'verify_only';
  const examples=(e.chemExamples||[]).join(', ');
  const note=(e.chemicalNote||'').trim();

  if(state.lang==='ur'){
    if(status==='pakistan_advisory'){
      return `پاکستانی/پنجاب سرکاری یا صوبائی تکنیکی ماخذ میں درج مثال: ${examples || 'بیماری مخصوص کیمیائی آپشن'}۔ ${note || ''}`.trim();
    }
    if(status==='no_curative'){
      return `${note || 'اس بیماری کے قائم شدہ انفیکشن کو کوئی زرعی زہر ختم نہیں کرتا۔'} کیمیائی فیصلہ صرف کسی الگ ثابت شدہ ویکٹر/ثانوی مسئلے اور موجودہ پاکستانی لیبل کے مطابق کریں۔`;
    }
    if(status==='none'){
      return note || 'اس غیر متعدی حالت کے لیے زرعی زہر خود بخود درکار نہیں۔ اصل غیر متعدی وجہ کو درست کریں۔';
    }
    return note
      ? `${note} اس مخصوص فصل/ہدف کے لیے موجودہ DPP لیبل کی تصدیق کے بغیر کوئی پروڈکٹ استعمال نہ کریں۔`
      : 'اس ماڈل کلاس کے لیے ہمارے موجودہ پاکستان ماخذ میں کوئی عین فصل/ہدف کیمیائی سفارش تصدیق نہیں ہوئی۔ IPM کو ترجیح دیں اور ضرورت پر موجودہ DPP لیبل چیک کریں۔';
  }

  if(status==='pakistan_advisory'){
    return `Pakistan/Punjab evidence example: ${examples || 'disease-specific chemical option'}. ${note}`.trim();
  }
  if(status==='no_curative'){
    return `${note || 'No pesticide eliminates the established infection.'} Chemical action, if any, should target only a separately confirmed vector or secondary problem under a current Pakistan crop/target label.`;
  }
  if(status==='none'){
    return note || 'No pesticide is automatically indicated for this non-infectious condition. Correct the underlying non-infectious cause instead.';
  }
  return note
    ? `${note} No product should be used unless a current DPP crop/target label confirms that use.`
    : 'No exact Pakistan crop/target chemical recommendation was verified for this model class in the current evidence set. Use IPM first and verify a current DPP label before any pesticide decision.';
}

function nutritionGuidance(e){
  const note=(e.nutritionNote||'').trim();
  if(state.lang==='ur'){
    if(note) return `کھاد بیماری کا براہِ راست علاج نہیں۔ ${note}`;
    return 'اس بیماری کے لیے کوئی مخصوص کھاد بطور علاج تصدیق شدہ نہیں۔ مٹی/پودے کے ٹیسٹ کے بعد صرف حقیقی کمی درست کریں اور متوازن غذائیت برقرار رکھیں۔';
  }
  if(note) return `Fertilizer is not a direct cure. ${note}`;
  return 'No disease-specific fertilizer treatment is verified. Maintain balanced fertility and correct only a measured deficiency using soil/plant testing.';
}

function normalizeDiseaseKey(value){
  return String(value||'').toLowerCase().replace(/^[^/]+\/\s*/, '').replace(/[_\-]+/g,' ').replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
}

const i18n = {
  en:{brandTagline:'Crop Health Assistant',navHome:'Home',navDiagnose:'Diagnose Crop',navDiseases:'Disease Library',navHistory:'Recent Checks',languageLabel:'Language',farmerMode:'Farmer-first mode',farmerModeDesc:'Large controls, simple guidance, mobile ready.',systemReady:'AI system ready',breadcrumbHome:'Home',help:'Help',heroBadge:'AI crop health support for Pakistan',heroTitle:'Check your crop’s health in seconds.',heroText:'Choose a crop, take a clear photo, and get an easy-to-understand health assessment with guidance you can act on.',startDiagnosis:'Start a diagnosis',exploreDiseases:'Explore crop diseases',trust1:'12 project crops',trust2:'English + Urdu',trust3:'Farmer-friendly guidance',sampleScan:'Sample health scan',visualCheck:'Visual check',healthyPlant:'Healthy plant',cropModels:'crop models',languages:'languages',chooseCropEyebrow:'YOUR FIELD, YOUR CROP',chooseCropTitle:'Choose the crop you want to check',chooseCropText:'Tap a crop card to make it active for diagnosis and disease guidance.',simpleProcess:'SIMPLE PROCESS',howTitle:'From field photo to useful guidance',step1Title:'Select your crop',step1Text:'Choose the crop growing in your field.',step2Title:'Take or upload a photo',step2Text:'Use the camera or upload an existing crop image.',step3Title:'Review the result',step3Text:'See disease, confidence and severity when applicable.',step4Title:'Ask the AI assistant',step4Text:'Get crop-specific guidance in your selected language.',diagnoseEyebrow:'FIELD DIAGNOSIS',diagnoseTitle:'Check a crop photo',diagnoseSubtitle:'Select your crop, then upload an image or use your camera.',chooseCrop:'Choose crop',chooseCropSmall:'Tell us which crop is in the image.',notSelected:'Not selected',addPhoto:'Add crop photo',photoAdvice:'Use a clear image with the affected leaf or plant visible.',dropPhoto:'Drop your crop photo here',orChoose:'or choose an option below',uploadPhoto:'Upload Photo',openCamera:'Open Camera',formatHelp:'Images such as JPG, PNG, WEBP, HEIC/HEIF, BMP and TIFF can be sent to the backend.',previewUnavailable:'Preview unavailable, but this file can still be submitted.',remove:'Remove',betterPhoto:'For a better result',tip1:'Use natural light',tip2:'Keep the affected area in focus',tip3:'Avoid extreme zoom or blur',analyzePlant:'Analyze plant',currentCheck:'CURRENT CHECK',crop:'Crop',chooseCropPrompt:'Choose a crop',photo:'Photo',notAdded:'Not added',safeTitle:'Designed to fail safely',safeText:'If the image is unclear or confidence is weak, the app should ask for another photo instead of overstating the result.',analyzing:'Checking your crop…',analyzingText:'Looking at visual signs and preparing an easy-to-understand result.',resultEyebrow:'AI HEALTH ASSESSMENT',resultTitle:'Your crop result',newCheck:'New check',detected:'Disease detected',likelyCondition:'Likely condition',confidence:'confidence',severity:'Severity',severityConfidence:'Severity confidence',uncertainAdvice:'This result is uncertain. Please take another clear photo before acting on it.',whatNext:'What should I do next?',defaultGuidance:'Review crop-specific guidance and ask the assistant if you need help understanding the result.',viewGuidance:'View guidance',askAssistant:'Ask assistant',libraryEyebrow:'CROP KNOWLEDGE',libraryTitle:'Crop disease library',librarySubtitle:'Learn symptoms, prevention and management for the selected crop.',selectCropLabel:'Select crop',searchDiseases:'Search diseases or symptoms',visionAvailable:'AI detection available',infoOnly:'Information only',historyEyebrow:'YOUR ACTIVITY',historyTitle:'Recent crop checks',historySubtitle:'Recent completed checks are stored only in your browser.',clearHistory:'Clear history',assistantName:'CDCNSA Assistant',assistantOnline:'Ready to help',chatPlaceholder:'Ask about your crop…',cameraTitle:'Take crop photo',cameraInstruction:'Place the affected leaf clearly inside the frame.',cameraGuide:'Keep the affected area inside this frame',ready:'Selected',photoAdded:'Added',viewDetails:'View details',symptoms:'Typical signs',management:'Management approach',important:'Important',safetyNote:'Use cultural and integrated management first. Verify current Pakistan registration and the product label before any pesticide decision.',libraryCount:'knowledge entries',noDisease:'No matching disease information found.',emptyHistoryTitle:'No crop checks yet',emptyHistoryText:'Your completed checks will appear here.',healthy:'Healthy',severityNA:'N/A',uncertain:'Uncertain',highConfidence:'High confidence',moderateConfidence:'Moderate confidence',lowConfidence:'Low confidence',demoWelcome:'Assalam-o-Alaikum! I can explain crop symptoms, your diagnosis result, severity and next steps in simple language.',quick1:'What does this result mean?',quick2:'What should I do next?',quick3:'How do I take a better photo?',demoReply:'Sorry, I am currently unable to answer that. Please try again.',demoNoticeText:'Demo preview — connect /api/diagnose for real model inference.',needCrop:'Please select a crop first.',needPhoto:'Please add a crop photo first.',cameraError:'Camera could not be opened. You can still upload a photo.',cameraUnsupported:'Camera access is not supported in this browser.',historyCleared:'Recent checks cleared.',languageChanged:'Language changed to English.',helpToast:'Choose a crop, add a clear photo, then tap Analyze plant.'},
  ur:{brandTagline:'پودوں کی صحت کا معاون',navHome:'ہوم',navDiagnose:'فصل کی جانچ',navDiseases:'بیماریوں کی معلومات',navHistory:'حالیہ جانچ',languageLabel:'زبان',farmerMode:'کسان دوست موڈ',farmerModeDesc:'بڑے بٹن، آسان رہنمائی اور موبائل کے لیے موزوں۔',systemReady:'اے آئی نظام تیار ہے',breadcrumbHome:'ہوم',help:'مدد',heroBadge:'پاکستان کے لیے اے آئی فصل صحت معاون',heroTitle:'اپنی فصل کی صحت چند سیکنڈ میں جانچیں۔',heroText:'فصل منتخب کریں، صاف تصویر لیں اور آسان زبان میں صحت کی جانچ اور قابلِ عمل رہنمائی حاصل کریں۔',startDiagnosis:'فصل کی جانچ شروع کریں',exploreDiseases:'فصل کی بیماریاں دیکھیں',trust1:'12 پروجیکٹ فصلیں',trust2:'انگریزی + اردو',trust3:'کسان دوست رہنمائی',sampleScan:'نمونہ صحت اسکین',visualCheck:'بصری جانچ',healthyPlant:'صحت مند پودا',cropModels:'فصل ماڈلز',languages:'زبانیں',chooseCropEyebrow:'آپ کا کھیت، آپ کی فصل',chooseCropTitle:'وہ فصل منتخب کریں جس کی جانچ کرنی ہے',chooseCropText:'تشخیص اور بیماریوں کی رہنمائی کے لیے فصل کے کارڈ پر ٹیپ کریں۔',simpleProcess:'آسان طریقہ',howTitle:'کھیت کی تصویر سے مفید رہنمائی تک',step1Title:'فصل منتخب کریں',step1Text:'اپنے کھیت میں موجود فصل منتخب کریں۔',step2Title:'تصویر لیں یا اپ لوڈ کریں',step2Text:'کیمرہ استعمال کریں یا موجودہ تصویر اپ لوڈ کریں۔',step3Title:'نتیجہ دیکھیں',step3Text:'بیماری، اعتماد اور جہاں مناسب ہو شدت دیکھیں۔',step4Title:'اے آئی معاون سے پوچھیں',step4Text:'اپنی زبان میں فصل سے متعلق رہنمائی حاصل کریں۔',diagnoseEyebrow:'فصل کی تشخیص',diagnoseTitle:'فصل کی تصویر جانچیں',diagnoseSubtitle:'فصل منتخب کریں، پھر تصویر اپ لوڈ کریں یا کیمرہ استعمال کریں۔',chooseCrop:'فصل منتخب کریں',chooseCropSmall:'بتائیں تصویر میں کون سی فصل ہے۔',notSelected:'منتخب نہیں',addPhoto:'فصل کی تصویر شامل کریں',photoAdvice:'صاف تصویر استعمال کریں جس میں متاثرہ پتہ یا پودا واضح ہو۔',dropPhoto:'فصل کی تصویر یہاں ڈالیں',orChoose:'یا نیچے سے ایک طریقہ منتخب کریں',uploadPhoto:'تصویر اپ لوڈ کریں',openCamera:'کیمرہ کھولیں',formatHelp:'JPG، PNG، WEBP، HEIC/HEIF، BMP اور TIFF جیسی تصاویر بیک اینڈ کو بھیجی جا سکتی ہیں۔',previewUnavailable:'پیش نظارہ دستیاب نہیں، لیکن فائل پھر بھی بھیجی جا سکتی ہے۔',remove:'ہٹائیں',betterPhoto:'بہتر نتیجے کے لیے',tip1:'قدرتی روشنی استعمال کریں',tip2:'متاثرہ حصہ واضح رکھیں',tip3:'زیادہ زوم یا دھندلی تصویر سے بچیں',analyzePlant:'پودے کا معائنہ کریں',currentCheck:'موجودہ جانچ',crop:'فصل',chooseCropPrompt:'فصل منتخب کریں',photo:'تصویر',notAdded:'شامل نہیں',safeTitle:'محفوظ انداز میں بنایا گیا',safeText:'اگر تصویر واضح نہ ہو یا اعتماد کم ہو تو ایپ غلط یقین ظاہر کرنے کے بجائے دوسری تصویر مانگے گی۔',analyzing:'آپ کی فصل کی جانچ ہو رہی ہے…',analyzingText:'بصری علامات دیکھ کر آسان نتیجہ تیار کیا جا رہا ہے۔',resultEyebrow:'اے آئی صحت کی جانچ',resultTitle:'آپ کی فصل کا نتیجہ',newCheck:'نئی جانچ',detected:'بیماری کی شناخت',likelyCondition:'ممکنہ حالت',confidence:'اعتماد',severity:'شدت',severityConfidence:'شدت کا اعتماد',uncertainAdvice:'یہ نتیجہ غیر یقینی ہے۔ کسی اقدام سے پہلے ایک اور صاف تصویر لیں۔',whatNext:'اب مجھے کیا کرنا چاہیے؟',defaultGuidance:'فصل سے متعلق رہنمائی دیکھیں اور نتیجہ سمجھنے کے لیے معاون سے پوچھیں۔',viewGuidance:'رہنمائی دیکھیں',askAssistant:'معاون سے پوچھیں',libraryEyebrow:'فصل کی معلومات',libraryTitle:'فصل کی بیماریوں کی لائبریری',librarySubtitle:'منتخب فصل کی علامات، بچاؤ اور انتظام جانیں۔',selectCropLabel:'فصل منتخب کریں',searchDiseases:'بیماری یا علامت تلاش کریں',visionAvailable:'اے آئی شناخت دستیاب',infoOnly:'صرف معلومات',historyEyebrow:'آپ کی سرگرمی',historyTitle:'حالیہ فصل جانچ',historySubtitle:'حالیہ مکمل جانچ صرف آپ کے براؤزر میں محفوظ ہوتی ہے۔',clearHistory:'تاریخ صاف کریں',assistantName:'سی ڈی سی این ایس اے معاون',assistantOnline:'مدد کے لیے تیار',chatPlaceholder:'اپنی فصل کے بارے میں پوچھیں…',cameraTitle:'فصل کی تصویر لیں',cameraInstruction:'متاثرہ پتے کو واضح طور پر فریم کے اندر رکھیں۔',cameraGuide:'متاثرہ حصہ اس فریم کے اندر رکھیں',ready:'منتخب',photoAdded:'شامل',viewDetails:'تفصیل دیکھیں',symptoms:'عام علامات',management:'انتظام کا طریقہ',important:'اہم',safetyNote:'پہلے ثقافتی اور مربوط انتظام کو ترجیح دیں۔ کسی بھی زرعی دوا کے فیصلے سے پہلے پاکستان میں موجودہ رجسٹریشن اور پروڈکٹ لیبل کی تصدیق کریں۔',libraryCount:'معلوماتی اندراجات',noDisease:'متعلقہ بیماری کی معلومات نہیں ملیں۔',emptyHistoryTitle:'ابھی کوئی جانچ نہیں',emptyHistoryText:'مکمل شدہ جانچ یہاں نظر آئے گی۔',healthy:'صحت مند',severityNA:'لاگو نہیں',uncertain:'غیر یقینی',highConfidence:'زیادہ اعتماد',moderateConfidence:'درمیانہ اعتماد',lowConfidence:'کم اعتماد',demoWelcome:'السلام علیکم! میں فصل کی علامات، تشخیص، شدت اور اگلے اقدامات آسان زبان میں سمجھا سکتا ہوں۔',quick1:'اس نتیجے کا کیا مطلب ہے؟',quick2:'اب مجھے کیا کرنا چاہیے؟',quick3:'بہتر تصویر کیسے لوں؟',demoReply:'معذرت، فی الحال میں اس کا جواب نہیں دے سکتا۔ براہ کرم دوبارہ کوشش کریں۔',demoNoticeText:'یہ ڈیمو پیش نظارہ ہے — حقیقی ماڈل کے لیے /api/diagnose جوڑیں۔',needCrop:'پہلے فصل منتخب کریں۔',needPhoto:'پہلے فصل کی تصویر شامل کریں۔',cameraError:'کیمرہ نہیں کھل سکا۔ آپ تصویر اپ لوڈ کر سکتے ہیں۔',cameraUnsupported:'اس براؤزر میں کیمرہ دستیاب نہیں۔',historyCleared:'حالیہ جانچ صاف کر دی گئی۔',languageChanged:'زبان اردو کر دی گئی۔',helpToast:'فصل منتخب کریں، صاف تصویر شامل کریں اور پھر پودے کا معائنہ کریں۔'}
};

const state = {
  lang: localStorage.getItem('ksa_lang') || 'en',
  selectedCrop: localStorage.getItem('ksa_crop') || null,
  imageFile: null,
  imageDataUrl: null,
  latestDiagnosis: null,
  page: 'home',
  stream: null,
  facingMode: 'environment',
  history: JSON.parse(localStorage.getItem('ksa_history') || '[]')
};

function t(key){ return i18n[state.lang || 'en'][key] || i18n.en[key] || key; }
function cropById(id){ return crops.find(c=>c.id===id); }
function activeCrop(){ return cropById(state.selectedCrop); }
function formatBytes(n){ if(!n && n!==0)return''; const u=['B','KB','MB','GB']; let i=0,v=n; while(v>=1024&&i<u.length-1){v/=1024;i++} return `${v.toFixed(v>=10||i===0?0:1)} ${u[i]}`; }
function escapeHTML(s=''){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#039;','"':'&quot;'}[c]))}

function init(){
  renderCropGrid(); renderDiagnoseCropStrip(); renderLibrarySelect(); renderHistory(); bindEvents();
  applyLanguage(state.lang,false);
  updateSelectedCropUI(); renderDiseaseLibrary(); renderChatContext(); seedChat(); initProfessionalShell(); initNeuralTree();
}

function bindEvents(){
  $$('[data-set-lang]').forEach(b=>b.addEventListener('click',()=>applyLanguage(b.dataset.setLang,true)));
  $('#quickLang').addEventListener('click',()=>applyLanguage(state.lang==='en'?'ur':'en',true));
  $$('[data-nav]').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.nav)));
  $('#menuBtn').addEventListener('click',openSidebar); $('#sidebarClose').addEventListener('click',closeSidebar); $('#sidebarBackdrop').addEventListener('click',closeSidebar); $('#sidebarCollapse')?.addEventListener('click',toggleSidebarCollapse);
  $('#helpBtn').addEventListener('click',()=>toast(t('helpToast')));
  $('#browseBtn').addEventListener('click',e=>{e.stopPropagation();$('#fileInput').click()});
  $('#uploadZone').addEventListener('click',e=>{if(e.target.closest('button'))return;if(!state.imageFile)$('#fileInput').click()});
  $('#uploadZone').addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&!state.imageFile)$('#fileInput').click()});
  $('#fileInput').addEventListener('change',e=>e.target.files[0]&&handleFile(e.target.files[0]));
  ['dragenter','dragover'].forEach(ev=>$('#uploadZone').addEventListener(ev,e=>{e.preventDefault();$('#uploadZone').classList.add('dragover')}));
  ['dragleave','drop'].forEach(ev=>$('#uploadZone').addEventListener(ev,e=>{e.preventDefault();$('#uploadZone').classList.remove('dragover')}));
  $('#uploadZone').addEventListener('drop',e=>e.dataTransfer.files[0]&&handleFile(e.dataTransfer.files[0]));
  $('#removePhoto').addEventListener('click',e=>{e.stopPropagation();clearPhoto()});
  $('#cameraBtn').addEventListener('click',e=>{e.stopPropagation();openCamera()});
  $('#cameraClose').addEventListener('click',closeCamera); $('#capturePhoto').addEventListener('click',capturePhoto); $('#switchCamera').addEventListener('click',switchCamera);
  $('#analyzeBtn').addEventListener('click',analyzePlant); $('#newCheckBtn').addEventListener('click',newCheck);
  $('#viewDiseaseBtn').addEventListener('click',()=>{navigate('diseases'); if(state.latestDiagnosis) setTimeout(()=>openDiseaseByName(state.latestDiagnosis.disease),150)});
  $('#askAssistantBtn').addEventListener('click',()=>openChat(true));
  $('#libraryCropSelect').addEventListener('change',e=>{selectCrop(e.target.value,false);renderDiseaseLibrary()});
  $('#diseaseSearch').addEventListener('input',renderDiseaseLibrary);
  $('#diseaseGrid').addEventListener('click',ev=>{const card=ev.target.closest('.disease-card');if(!card)return;openDiseaseByStableKey(card.dataset.cropId,card.dataset.diseaseKey);});
  $('#diseaseGrid').addEventListener('keydown',ev=>{if(ev.key!=='Enter'&&ev.key!==' ')return;const card=ev.target.closest('.disease-card');if(!card)return;ev.preventDefault();openDiseaseByStableKey(card.dataset.cropId,card.dataset.diseaseKey);});
  $('#clearHistory').addEventListener('click',()=>{state.history=[];localStorage.setItem('ksa_history','[]');renderHistory();toast(t('historyCleared'))});
  $('#chatFab').addEventListener('click',()=>openChat()); $('#closeChat').addEventListener('click',()=>$('#chatPanel').classList.remove('open')); $('#expandChat').addEventListener('click',()=>$('#chatPanel').classList.toggle('expanded'));
  $('#chatForm').addEventListener('submit',sendChat); $('#chatInput').addEventListener('input',e=>{autoGrow(e);_lastInputWasVoice=false});
  $('#chatInput').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('#chatForm').requestSubmit()}});
  if($('#chatMic'))$('#chatMic').addEventListener('click',toggleMic);
  $('#closeDiseaseDrawer').addEventListener('click',closeDiseaseDrawer); $('#diseaseDrawerBackdrop').addEventListener('click',closeDiseaseDrawer); $('#diseaseDrawer').addEventListener('click',e=>e.stopPropagation());
  window.addEventListener('keydown',e=>{if(e.key==='Escape'){closeDiseaseDrawer();closeCamera();closeSidebar();}});
}

function applyLanguage(lang,notify=false){
  state.lang=lang; localStorage.setItem('ksa_lang',lang); document.documentElement.lang=lang; document.documentElement.dir=lang==='ur'?'rtl':'ltr';
  $$('[data-i18n]').forEach(el=>{const key=el.dataset.i18n; if(i18n[lang][key])el.textContent=i18n[lang][key]});
  $$('[data-i18n-placeholder]').forEach(el=>{const key=el.dataset.i18nPlaceholder; if(i18n[lang][key])el.placeholder=i18n[lang][key]});
  $$('.lang-pill').forEach(b=>b.classList.toggle('active',b.dataset.setLang===lang)); const ql=$('#quickLangLabel'); if(ql) ql.textContent=lang==='en'?'اردو':'EN';
  renderCropGrid();renderDiagnoseCropStrip();renderLibrarySelect();updateSelectedCropUI();renderDiseaseLibrary();renderHistory();renderChatContext();renderQuickPrompts();refreshChatLanguage();
  if(state.openDiseaseRef){const ref={...state.openDiseaseRef};const entry=findDiseaseForCrop(ref.cropId,encodeURIComponent(ref.key));if(entry)openDisease(entry,ref.cropId);}
  if(notify)toast(t('languageChanged'));
}

function navigate(page){
  state.page=page; $$('.page').forEach(p=>p.classList.remove('active-page')); $(`#${page}Page`).classList.add('active-page');
  $$('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.nav===page));
  const labels={home:'navHome',diagnose:'navDiagnose',diseases:'navDiseases',history:'navHistory'}; $('#breadcrumb').textContent=t(labels[page]); closeSidebar(); window.scrollTo({top:0,behavior:'smooth'});
  if(page==='diseases')renderDiseaseLibrary(); if(page==='history')renderHistory();
}

function renderCropGrid(){
  $('#cropGrid').innerHTML=crops.map(c=>`<button class="crop-card ${state.selectedCrop===c.id?'selected':''}" data-crop="${c.id}" style="--crop-accent:${c.accent};--crop-soft:${c.soft}">
    <div class="crop-photo-wrap"><img class="crop-photo" src="${c.image}" alt="${state.lang==='ur'?c.ur:c.en}" loading="lazy" referrerpolicy="no-referrer"><span class="crop-photo-overlay"></span></div>
    <div class="crop-card-body"><div><h3>${state.lang==='ur'?c.ur:c.en}</h3><span class="urdu-name">${state.lang==='ur'?c.en:c.ur}</span></div><span class="crop-action"><span>${t('ready')}</span><span>${document.documentElement.dir==='rtl'?'←':'→'}</span></span></div>
  </button>`).join('');
  $$('.crop-card').forEach(b=>b.addEventListener('click',()=>{selectCrop(b.dataset.crop,true);navigate('diagnose')}));
}
function renderDiagnoseCropStrip(){
  $('#diagnoseCropStrip').innerHTML=crops.map(c=>`<button class="crop-chip ${state.selectedCrop===c.id?'selected':''}" data-dcrop="${c.id}" style="--accent:${c.accent};--soft:${c.soft}"><img class="crop-chip-photo" src="${c.image}" alt="" loading="lazy" referrerpolicy="no-referrer"><span>${state.lang==='ur'?c.ur:c.en}</span></button>`).join('');
  $$('.crop-chip').forEach(b=>b.addEventListener('click',()=>selectCrop(b.dataset.dcrop,false)));
}
function renderLibrarySelect(){
  const sel=$('#libraryCropSelect');
  sel.innerHTML=crops.map(c=>`<option value="${c.id}">${state.lang==='ur'?c.ur:c.en}</option>`).join('');
  sel.value=state.selectedCrop || 'corn';
}
function selectCrop(id,fromHome=false){state.selectedCrop=id;localStorage.setItem('ksa_crop',id);renderCropGrid();renderDiagnoseCropStrip();renderLibrarySelect();updateSelectedCropUI();renderDiseaseLibrary();renderChatContext();checkAnalyzeReady(); if(!fromHome)toast(`${state.lang==='ur'?cropById(id).ur:cropById(id).en}`)}
function updateSelectedCropUI(){
  const c=activeCrop(); const badge=$('#selectedCropBadge');
  if(c){
    const name=state.lang==='ur'?c.ur:c.en;
    badge.classList.remove('hidden'); badge.innerHTML=`<img src="${c.image}" alt="" referrerpolicy="no-referrer"><span><small>${state.lang==='ur'?'منتخب فصل':'Selected crop'}</small>${name}</span>`;
    $('#diagnoseCropChip').innerHTML=`<div class="selected-crop-badge"><img src="${c.image}" alt="" referrerpolicy="no-referrer"><span>${name}</span></div>`;
    $('#cropStatus').textContent=t('ready'); $('#cropStatus').classList.add('ready');
    $('#currentCropVisual').innerHTML=`<span class="current-crop-photo"><img src="${c.image}" alt="" referrerpolicy="no-referrer"></span><div><small>${t('crop')}</small><strong>${name}</strong></div>`;
  } else {
    badge.classList.add('hidden'); $('#diagnoseCropChip').innerHTML=''; $('#cropStatus').textContent=t('notSelected'); $('#cropStatus').classList.remove('ready');
    $('#currentCropVisual').innerHTML=`<span class="current-crop-placeholder"></span><div><small>${t('crop')}</small><strong>${t('chooseCropPrompt')}</strong></div>`;
  }
  $('#langSummary').textContent=state.lang==='ur'?'اردو':'English';
}

function handleFile(file){
  if(!file.type.startsWith('image/')&&!/\.(heic|heif|tif|tiff|bmp|webp)$/i.test(file.name)){toast('Please choose an image file.');return}
  state.imageFile=file; $('#uploadEmpty').classList.add('hidden'); $('#previewState').classList.remove('hidden'); $('#previewName').textContent=file.name; $('#previewMeta').textContent=`${file.type||'image'} • ${formatBytes(file.size)}`; $('#photoSummary').textContent=t('photoAdded');
  const img=$('#imagePreview'), fallback=$('#formatFallback'); const url=URL.createObjectURL(file); img.classList.remove('hidden');fallback.classList.add('hidden');img.src=url; img.onload=()=>URL.revokeObjectURL(url); img.onerror=()=>{URL.revokeObjectURL(url);img.classList.add('hidden');fallback.classList.remove('hidden')}; checkAnalyzeReady();
}
function clearPhoto(){state.imageFile=null;state.imageDataUrl=null;$('#fileInput').value='';$('#previewState').classList.add('hidden');$('#uploadEmpty').classList.remove('hidden');$('#photoSummary').textContent=t('notAdded');checkAnalyzeReady()}
function checkAnalyzeReady(){$('#analyzeBtn').disabled=!(state.selectedCrop&&state.imageFile)}

async function openCamera(){
  if(!navigator.mediaDevices?.getUserMedia){toast(t('cameraUnsupported'));return}
  $('#cameraModal').classList.remove('hidden');
  try{await startCamera()}catch(e){console.error(e);closeCamera();toast(t('cameraError'))}
}
async function startCamera(){
  if(state.stream)state.stream.getTracks().forEach(t=>t.stop()); state.stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:state.facingMode}},audio:false}); $('#cameraVideo').srcObject=state.stream;
}
function closeCamera(){if(!$('#cameraModal').classList.contains('hidden'))$('#cameraModal').classList.add('hidden'); if(state.stream){state.stream.getTracks().forEach(t=>t.stop());state.stream=null}}
async function switchCamera(){state.facingMode=state.facingMode==='environment'?'user':'environment';try{await startCamera()}catch(e){toast(t('cameraError'))}}
function capturePhoto(){
  const video=$('#cameraVideo'),canvas=$('#cameraCanvas');canvas.width=video.videoWidth||1280;canvas.height=video.videoHeight||960;canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);canvas.toBlob(blob=>{const file=new File([blob],`crop-photo-${Date.now()}.jpg`,{type:'image/jpeg'});handleFile(file);closeCamera()},'image/jpeg',.92);
}

async function analyzePlant(){
  if(!state.selectedCrop){toast(t('needCrop'));return} if(!state.imageFile){toast(t('needPhoto'));return}
  $('#analysisOverlay').classList.remove('hidden'); let p=0; const timer=setInterval(()=>{p=Math.min(92,p+Math.random()*17);$('#analysisProgress').style.width=`${p}%`},240);
  let result;
  try{
    const fd=new FormData();fd.append('crop',state.selectedCrop);fd.append('language',state.lang);fd.append('image',state.imageFile);
    const r=await fetch('/api/diagnose',{method:'POST',body:fd});
    if(!r.ok){
      let message='Model inference is unavailable for this crop.';
      try{const body=await r.json();message=body?.detail?.message||body?.message||message}catch(_){ }
      const err=new Error(message);err.status=r.status;throw err;
    }
    result=await r.json();
  }catch(e){
    clearInterval(timer);$('#analysisOverlay').classList.add('hidden');$('#analysisProgress').style.width='0%';
    console.error(e);
    toast(state.lang==='ur'?`ماڈل نتیجہ دستیاب نہیں: ${e.message||''}`:`Model result unavailable: ${e.message||''}`);
    return;
  }
  clearInterval(timer);$('#analysisProgress').style.width='100%';await new Promise(r=>setTimeout(r,300));$('#analysisOverlay').classList.add('hidden');$('#analysisProgress').style.width='0%';
  state.latestDiagnosis=normalizeDiagnosis(result);showResult(state.latestDiagnosis,false);saveHistory(state.latestDiagnosis);renderChatContext();
}
function normalizeDiagnosis(r){
  const rawDisease=String(r.disease||r.prediction||'Uncertain').trim();
  const confidence=Number(r.confidence??r.disease_confidence??0);
  const uncertain=Boolean(r.uncertain)||confidence<.55;
  const disease=uncertain?'Uncertain':rawDisease;
  const healthy=!uncertain&&(Boolean(r.healthy)||disease.toLowerCase()==='healthy');
  const rawSeverityConfidence=r.severity_confidence??r.severityConfidence;
  return{
    crop:r.crop||state.selectedCrop,
    disease,
    candidateDisease:r.candidate_disease||(!uncertain?null:rawDisease),
    confidence,
    severity:(healthy||uncertain)?'N/A':(r.severity||'N/A'),
    severityConfidence:(healthy||uncertain)?null:(rawSeverityConfidence==null?null:Number(rawSeverityConfidence)),
    uncertain,
    healthy
  };
}
function showResult(r,demo){
  $('#resultSection').classList.remove('hidden');$('#resultDisease').textContent=r.uncertain?t('uncertain'):displayDisease(r.disease);$('#resultConfidence').textContent=`${Math.round(r.confidence*100)}%`;$('#confidenceFill').style.width=`${Math.round(r.confidence*100)}%`;$('#resultCrop').textContent=state.lang==='ur'?activeCrop().ur:activeCrop().en;$('#resultSeverity').textContent=(r.healthy||r.uncertain)?t('severityNA'):translateSeverity(r.severity);$('#severityConfidence').textContent=(r.healthy||r.uncertain)?t('severityNA'):(r.severityConfidence?`${Math.round(r.severityConfidence*100)}%`:'—');
  const status=$('.result-status');status.classList.remove('healthy','uncertain'); if(r.uncertain){status.classList.add('uncertain');$('#resultStatusLabel').textContent=t('uncertain');$('#resultStatusIcon').textContent='!'}else if(r.healthy){status.classList.add('healthy');$('#resultStatusLabel').textContent=t('healthy');$('#resultStatusIcon').textContent='✓'}else{$('#resultStatusLabel').textContent=t('detected');$('#resultStatusIcon').textContent='✦'}
  $('#uncertaintyNote').classList.toggle('hidden',!r.uncertain); const entry=r.uncertain?null:findDisease(r.disease); $('#resultGuidance').textContent=entry?(state.lang==='ur'?entry.urduSymptoms:entry.management):t('defaultGuidance');$('#demoNotice').textContent=t('demoNoticeText');$('#demoNotice').classList.toggle('hidden',!demo);$('#resultSection').scrollIntoView({behavior:'smooth',block:'start'});
}
function translateSeverity(s){const x=String(s).toUpperCase();if(state.lang==='en')return x;return({MILD:'ہلکی',MODERATE:'درمیانی',SEVERE:'شدید','N/A':t('severityNA')})[x]||s}
function displayDisease(name){const entry=findDisease(name);return entry?(state.lang==='ur'?entry.ur:entry.en):name}
function findDisease(name,cropId=state.selectedCrop){const key=normalizeDiseaseKey(name);return(diseaseKnowledge[cropId]||[]).find(x=>[x.en,...(x.aliases||[])].some(v=>normalizeDiseaseKey(v)===key))}
function newCheck(){state.latestDiagnosis=null;clearPhoto();$('#resultSection').classList.add('hidden');navigate('diagnose');renderChatContext()}
function saveHistory(r){
  const c=activeCrop();
  const healthy=Boolean(r.healthy)||String(r.disease||'').toLowerCase()==='healthy';
  const item={id:Date.now(),crop:c.id,disease:r.disease,confidence:r.confidence,healthy,uncertain:Boolean(r.uncertain),severity:(healthy||r.uncertain)?'N/A':(r.severity||'N/A'),severityConfidence:(healthy||r.uncertain)?null:(r.severityConfidence??null),time:new Date().toISOString()};
  state.history=[item,...state.history].slice(0,12);
  localStorage.setItem('ksa_history',JSON.stringify(state.history));
  renderHistory();
}

function renderDiseaseLibrary(){
  const libraryCropId=$('#libraryCropSelect')?.value || state.selectedCrop || 'corn';
  const c=cropById(libraryCropId)||crops[0];
  $('#libraryCropSelect').value=c.id;
  const entries=diseaseKnowledge[c.id]||[];
  const q=$('#diseaseSearch').value?.toLowerCase().trim()||'';
  const filtered=entries.filter(e=>`${e.en} ${e.ur} ${e.symptoms} ${e.urduSymptoms} ${e.management} ${e.prevention} ${e.chemicalNote} ${(e.chemExamples||[]).join(' ')}`.toLowerCase().includes(q));
  $('#libraryHero').style.setProperty('--hero-soft',c.soft);
  $('#libraryHero').style.setProperty('--hero-accent',c.accent);
  $('#libraryHero').innerHTML=`<div><p class="eyebrow">${t('libraryEyebrow')}</p><h2>${state.lang==='ur'?c.ur:c.en}</h2><p>${state.lang==='ur'?'اس فصل کے تربیت یافتہ ماڈل کی بیماری/حالت کلاسیں۔ ہر کارڈ میں وجہ، ظاہری علامات، فیلڈ ایکشن، غذائیت، پاکستان کیمیکل سیفٹی اور حوالہ تصویر شامل ہے۔':'Trained disease/condition classes for this crop. Each card includes cause, appearance, field action, nutrition, Pakistan chemical safety and a reference image.'}</p><span class="library-count">${entries.length} ${state.lang==='ur'?'ماڈل کلاسیں':'model classes'}</span></div><div class="library-photo"><img src="${c.image}" alt="${state.lang==='ur'?c.ur:c.en}" loading="lazy" referrerpolicy="no-referrer"></div>`;

  $('#diseaseGrid').innerHTML=filtered.length?filtered.map((e,i)=>{
    const d=diseaseDeepDetail(c.id,e);
    return `<article class="disease-card" role="button" tabindex="0" data-crop-id="${escapeHTML(c.id)}" data-disease-key="${encodeURIComponent(e.en)}" aria-label="${escapeHTML((state.lang==='ur'?e.ur:e.en)+' — '+t('viewDetails'))}">
      <div class="disease-card-top"><div class="disease-index">${String(i+1).padStart(2,'0')}</div></div>
      <h3>${state.lang==='ur'?e.ur:e.en}</h3>
      <span class="urdu-disease">${state.lang==='ur'?e.en:e.ur}</span>
      <p>${state.lang==='ur'?e.urduSymptoms:e.symptoms}</p>
      <div class="disease-mini-fact"><span>${state.lang==='ur'?'نوع':'Type'}</span><strong>${escapeHTML(diseaseKindLabel(d))}</strong></div>
      <div class="disease-card-footer"><span>${t('viewDetails')}</span><span>${document.documentElement.dir==='rtl'?'←':'→'}</span></div>
    </article>`;
  }).join(''):`<div class="history-empty"><div class="empty-icon">⌕</div><h3>${t('noDisease')}</h3></div>`;
}
function findDiseaseForCrop(cropId,key){
  const entries=diseaseKnowledge[cropId]||[];
  const wanted=normalizeDiseaseKey(decodeURIComponent(key||''));
  return entries.find(e=>normalizeDiseaseKey(e.en)===wanted || (e.aliases||[]).some(a=>normalizeDiseaseKey(a)===wanted));
}
function openDiseaseByStableKey(cropId,key){
  const e=findDiseaseForCrop(cropId,key);
  if(e) openDisease(e,cropId);
}
function openDiseaseByName(name){const e=findDisease(name);if(e)openDisease(e,state.selectedCrop||'corn')}

function sourceLinksHTML(e){
  const regulatory=new Set(['dppRegistered','dppBanned','punjabSoil']);
  const primary=(e.sources||[]).filter(key=>!regulatory.has(key)).map(key=>VERIFIED_SOURCES[key]).filter(Boolean).slice(0,3);
  if(!primary.length) return `<li><span>${state.lang==='ur'?'اس کارڈ کے لیے اضافی بیماری مخصوص ماخذ دستیاب نہیں؛ پاکستان ریگولیٹری لنکس نیچے موجود ہیں۔':'No additional disease-specific source is attached to this card; Pakistan regulatory checks are listed below.'}</span></li>`;
  return primary.map(s=>`<li><a href="${escapeHTML(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(s.label)}</a></li>`).join('');
}
function pakistanVerificationLinksHTML(){
  const keys=['dppRegistered','dppBanned','punjabSoil'];
  return keys.map(key=>VERIFIED_SOURCES[key]).filter(Boolean).map(s=>`<a class="verification-link" href="${escapeHTML(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(s.label)}</a>`).join('');
}
function stripHTMLText(value){const div=document.createElement('div');div.innerHTML=String(value||'');return(div.textContent||div.innerText||'').trim()}
const diseaseImageCache=new Map();
function imageSearchPage(query){return `https://commons.wikimedia.org/wiki/Special:MediaSearch?type=image&search=${encodeURIComponent(query||'plant disease')}`}
function setDrawerImageFallback(e, query=''){
  const img=$('#drawerDiseaseImage'); const meta=$('#drawerImageMeta');
  if(!img||!meta)return;
  img.removeAttribute('src');
  img.alt=state.lang==='ur'?`${e.ur} — بیماری کی حوالہ تصویر دستیاب نہیں`:`${e.en} — disease reference image unavailable`;
  const shell=img.closest('.drawer-image-shell');
  if(shell) shell.classList.add('image-unavailable');
  const q=query||e.imageQuery||e.en;
  meta.innerHTML=state.lang==='ur'
    ? `اس بیماری کی قابلِ اعتماد مخصوص تصویر خودکار طور پر لوڈ نہیں ہو سکی۔ <a href="${escapeHTML(imageSearchPage(q))}" target="_blank" rel="noopener noreferrer">وکی میڈیا پر بیماری کی تصاویر دیکھیں</a>`
    : `A reliable disease-specific image could not be loaded automatically. <a href="${escapeHTML(imageSearchPage(q))}" target="_blank" rel="noopener noreferrer">Open the disease image search on Wikimedia Commons</a>`;
}
function referenceMetaHTML({label='Reference image',author='',license='',page='',verified=true}={}){
  const badge=verified
    ? (state.lang==='ur'?'تصدیق شدہ بیماری حوالہ تصویر':'Verified disease reference image')
    : (state.lang==='ur'?'بیماری مخصوص وکی میڈیا حوالہ':'Disease-specific Wikimedia reference');
  return `<span class="reference-image-badge">${badge}</span>${author?`<span> · ${escapeHTML(author)}</span>`:''}${license?`<span> · ${escapeHTML(license)}</span>`:''}${page?`<a href="${escapeHTML(page)}" target="_blank" rel="noopener noreferrer">${state.lang==='ur'?'ماخذ / لائسنس':'Source / license'}</a>`:''}<span class="reference-image-warning">${state.lang==='ur'?' · صرف ظاہری موازنہ؛ تشخیص کا ثبوت نہیں':' · visual reference only; not proof of diagnosis'}</span>`;
}
function normalizeImageTerms(value){
  const generic=new Set(['plant','plants','disease','diseases','symptom','symptoms','leaf','leaves','fruit','fruits','damage','general','crop','condition','spot','blight']);
  return normalizeDiseaseKey(value||'').split(' ').filter(t=>t.length>3&&!generic.has(t));
}
function scoreCommonsCandidate(p,e,crop,query){
  const ii=p.imageinfo?.[0]||{};
  const hay=normalizeDiseaseKey(`${p.title||''} ${stripHTMLText(ii.extmetadata?.ImageDescription?.value||'')} ${stripHTMLText(ii.extmetadata?.ObjectName?.value||'')} ${stripHTMLText(ii.extmetadata?.Categories?.value||'')}`);
  const diseaseTerms=normalizeImageTerms(e.en);
  const queryTerms=normalizeImageTerms(query);
  const cropTerms=normalizeImageTerms(crop?.en||'');
  let score=0;
  for(const t of diseaseTerms) if(hay.includes(t)) score+=5;
  for(const t of queryTerms) if(hay.includes(t)) score+=3;
  for(const t of cropTerms) if(hay.includes(t)) score+=2;
  // Scientific-name tokens in imageQuery are highly discriminative and receive extra weight.
  const raw=(query||'').split(/\s+/).map(x=>x.replace(/[^A-Za-z-]/g,'')).filter(Boolean);
  const latin=raw.filter(x=>/^[A-Z][a-z]{3,}$/.test(x)||/^[a-z]{5,}$/.test(x)).map(x=>x.toLowerCase());
  for(const t of latin) if(t.length>5 && hay.includes(t)) score+=2;
  return {score,hay};
}
async function commonsSearch(query,e,crop){
  const api=new URL('https://commons.wikimedia.org/w/api.php');
  api.searchParams.set('action','query'); api.searchParams.set('generator','search');
  api.searchParams.set('gsrsearch',query); api.searchParams.set('gsrnamespace','6'); api.searchParams.set('gsrlimit','20');
  api.searchParams.set('prop','imageinfo'); api.searchParams.set('iiprop','url|mime|extmetadata'); api.searchParams.set('iiurlwidth','1200');
  api.searchParams.set('format','json'); api.searchParams.set('origin','*');
  const r=await fetch(api.toString()); if(!r.ok) throw new Error('Commons request failed');
  const data=await r.json();
  const pages=Object.values(data.query?.pages||{}).filter(p=>{const ii=p.imageinfo?.[0];return ii&&String(ii.mime||'').startsWith('image/')&&!/svg|gif/i.test(ii.mime||'')});
  const scored=pages.map(p=>({p,...scoreCommonsCandidate(p,e,crop,query)})).sort((a,b)=>b.score-a.score);
  return scored;
}
async function loadDiseaseReferenceImage(e){
  const img=$('#drawerDiseaseImage'), meta=$('#drawerImageMeta'); if(!img||!meta)return;
  const crop=activeCrop(); const cropId=crop?.id||state.selectedCrop||''; const key=`${cropId}|${normalizeDiseaseKey(e.en)}`;
  const query=e.imageQuery||`${crop?.en||''} ${e.en} plant disease`;
  img.removeAttribute('src'); img.alt=''; img.closest('.drawer-image-shell')?.classList.remove('image-unavailable');

  // 1) Use a manually verified image when available. Priority: direct URL (PlantVillage/extensions) > Wikimedia file.
  const curated=CURATED_DISEASE_IMAGES[key];
  if(curated){
    const src=curated.url||commonsFileImage(curated.file);
    const page=curated.url?'':commonsFilePage(curated.file);
    img.src=src; img.alt=state.lang==='ur'?`${e.ur} — حوالہ تصویر`:`${e.en} — reference image`;
    meta.innerHTML=referenceMetaHTML({author:curated.author,license:curated.license,page,verified:true});
    img.onerror=()=>{img.onerror=null; resolveCommonsFallback();};
    return;
  }

  // 2) All other cards use a disease/pathogen-specific Commons search. Unlike the previous
  //    version, matching uses the FULL imageQuery (including pathogen/scientific-name terms),
  //    not only the short UI disease name. This fixes many false 'no image' outcomes.
  await resolveCommonsFallback();

  async function resolveCommonsFallback(){
    img.removeAttribute('src');
    meta.textContent=state.lang==='ur'?'بیماری کی حوالہ تصویر تصدیق کی جا رہی ہے…':'Verifying a disease-specific reference image…';
    const cacheKey=`${cropId}:${e.en}`;
    if(diseaseImageCache.has(cacheKey)){
      const x=diseaseImageCache.get(cacheKey); img.src=x.src; img.alt=state.lang==='ur'?e.ur:e.en; meta.innerHTML=referenceMetaHTML(x.meta); return;
    }
    try{
      let scored=await commonsSearch(query,e,crop);
      if(!scored.length || scored[0].score<4) scored=await commonsSearch(`${crop?.en||''} ${e.en}`,e,crop);
      if(!scored.length || scored[0].score<3) scored=await commonsSearch(e.en,e,crop);
      const best=scored[0]; if(!best) throw new Error('No image result');
      if(best.score<2){
        if(best.score<1) throw new Error('No sufficiently matched disease image');
      }
      const p=best.p, ii=p.imageinfo[0], src=ii.thumburl||ii.url, page=ii.descriptionurl||ii.descriptionshorturl||ii.url;
      const author=stripHTMLText(ii.extmetadata?.Artist?.value||'');
      const license=stripHTMLText(ii.extmetadata?.LicenseShortName?.value||ii.extmetadata?.UsageTerms?.value||'');
      const metaObj={author,license,page,verified:false};
      diseaseImageCache.set(cacheKey,{src,meta:metaObj});
      img.src=src; img.alt=state.lang==='ur'?`${e.ur} — حوالہ تصویر`:`${e.en} — reference image`; meta.innerHTML=referenceMetaHTML(metaObj);
      img.onerror=()=>{img.onerror=null;setDrawerImageFallback(e,query)};
    }catch(err){setDrawerImageFallback(e,query)}
  }
}
function openDisease(e,cropId=(state.selectedCrop||'corn')){
  if(!e) return;
  const crop=cropById(cropId)||activeCrop()||crops[0];
  state.openDiseaseRef={cropId:crop.id,key:e.en};
  const d=diseaseDeepDetail(crop.id,e);
  const threshold=e.threshold?`<section class="drawer-section drawer-threshold"><h3>${state.lang==='ur'?'اقتصادی حد / ایکشن پوائنٹ':'Economic threshold / action point'}</h3><p>${state.lang==='ur'?(e.thresholdUr||e.threshold):e.threshold}</p></section>`:'';
  const classNote=e.classNote?`<div class="drawer-class-note"><strong>${state.lang==='ur'?'ماڈل نوٹ':'Model-class note'}:</strong> ${escapeHTML(e.classNote)}</div>`:'';
  const chemStatus=(e.chemStatus||'verify_only');
  const chemBadge=chemStatus==='pakistan_advisory'
    ? (state.lang==='ur'?'پاکستانی/پنجاب تکنیکی ماخذ میں کیمیائی مثال موجود':'Pakistan/Punjab chemical evidence found')
    : chemStatus==='no_curative'
      ? (state.lang==='ur'?'قائم شدہ انفیکشن کے لیے علاجی زرعی زہر نہیں':'No curative pesticide for established infection')
      : chemStatus==='none'
        ? (state.lang==='ur'?'کیمیائی زرعی زہر بنیادی علاج نہیں':'Pesticide is not the primary treatment')
        : (state.lang==='ur'?'عین پاکستان فصل/ہدف کیمیائی لیبل تصدیق درکار':'Exact Pakistan crop/target label not verified');

  $('#diseaseDrawerContent').innerHTML=`
    <div class="drawer-mark">${state.lang==='ur'?'تصدیق شدہ ماڈل کلاس':'VERIFIED MODEL CLASS'}</div>
    <h2>${state.lang==='ur'?e.ur:e.en}</h2><div class="drawer-urdu">${state.lang==='ur'?e.en:e.ur}</div>
    ${classNote}

    <figure class="drawer-disease-figure"><div class="drawer-image-shell"><div class="drawer-image-loader"></div><img id="drawerDiseaseImage" alt="" referrerpolicy="no-referrer"></div><figcaption id="drawerImageMeta"></figcaption></figure>

    <section class="drawer-section drawer-cause">
      <h3>${state.lang==='ur'?'یہ کیا ہے / بنیادی وجہ':'What it is / likely cause'}</h3>
      <p>${escapeHTML(diseaseCauseText(d))}</p>
      <div class="cause-type-badge">${escapeHTML(diseaseKindLabel(d))}</div>
    </section>

    <section class="drawer-section">
      <h3>${state.lang==='ur'?'خطرہ کب بڑھتا ہے؟':'When risk is higher'}</h3>
      <p>${escapeHTML(diseaseRiskText(d))}</p>
    </section>

    <section class="drawer-section"><h3>${state.lang==='ur'?'یہ کیسا نظر آتا ہے؟':'Appearance / typical signs'}</h3><p>${state.lang==='ur'?e.urduSymptoms:e.symptoms}</p></section>

    <section class="drawer-section">
      <h3>${state.lang==='ur'?'فوری فیلڈ ایکشن / علاج':'Immediate field action / treatment'}</h3>
      <p>${escapeHTML(e.management)}</p>
    </section>

    <section class="drawer-section"><h3>${state.lang==='ur'?'بچاؤ اور IPM':'Prevention / IPM'}</h3><p>${escapeHTML(e.prevention)}</p></section>

    <section class="drawer-section drawer-nutrition"><h3>${state.lang==='ur'?'کھاد اور غذائیت':'Fertilizer & nutrition'}</h3><p>${escapeHTML(nutritionGuidance(e))}</p><div class="drawer-verification-badge">${state.lang==='ur'?'صرف حقیقی کمی کو ٹیسٹ کے بعد درست کریں':'Correct measured deficiency only'}</div></section>

    <section class="drawer-section drawer-chemical">
      <h3>${state.lang==='ur'?'پاکستان میں پیسٹی سائیڈ / کیمیکل رہنمائی':'Pakistan pesticide / chemical guidance'}</h3>
      <div class="chemical-status ${chemStatus}">${chemBadge}</div>
      <p>${escapeHTML(chemicalGuidance(e))}</p>
      <div class="pakistan-verification-links">${pakistanVerificationLinksHTML()}</div>
    </section>

    ${threshold}

    <details class="drawer-section drawer-sources">
      <summary>${state.lang==='ur'?'بیماری مخصوص ماخذ دیکھیں':'View disease-specific sources'}</summary>
      <ul class="drawer-source-list">${sourceLinksHTML(e)}</ul>
    </details>

    <section class="drawer-section"><div class="drawer-caution"><strong>${t('important')}:</strong> ${state.lang==='ur'?'یہ تعلیمی فیصلہ سازی کی مدد ہے، پیسٹی سائیڈ لیبل نہیں۔ خوراک، محلول کی طاقت، ٹینک مکس، PHI/REI، وقفہ اور زیادہ سے زیادہ اسپرے صرف موجودہ پاکستانی پروڈکٹ لیبل سے لیں۔ ممنوعہ دوا استعمال نہ کریں۔':'Educational decision support only. Dose, concentration, tank mix, PHI/REI, interval and maximum applications must come from the current Pakistan product label. Never use a banned pesticide.'}</div></section>`;
  $('#diseaseDrawerBackdrop').classList.remove('hidden');
  const diseaseDrawer=$('#diseaseDrawer');
  diseaseDrawer.setAttribute('aria-hidden','false');
  // Add the open state synchronously so RTL/LTR re-rendering cannot lose the click.
  // The CSS transition still animates the transform from the drawer's current state.
  diseaseDrawer.classList.add('open');
  loadDiseaseReferenceImage(e);
}
function closeDiseaseDrawer(){
  state.openDiseaseRef=null;
  $('#diseaseDrawer').classList.remove('open');
  $('#diseaseDrawer').setAttribute('aria-hidden','true');
  setTimeout(()=>$('#diseaseDrawerBackdrop').classList.add('hidden'),280);
}

function renderHistory(){
  const list=$('#historyList'); if(!state.history.length){list.innerHTML=`<div class="history-empty"><div class="empty-icon">—</div><h3>${t('emptyHistoryTitle')}</h3><p>${t('emptyHistoryText')}</p></div>`;return}
  list.innerHTML=state.history.map(h=>{const c=cropById(h.crop)||crops[0],e=findDisease(h.disease,h.crop);return`<article class="history-item"><div class="history-crop"><img src="${c.image}" alt="" referrerpolicy="no-referrer"></div><div><h3>${state.lang==='ur'?(e?.ur||h.disease):(e?.en||h.disease)}</h3><p>${state.lang==='ur'?c.ur:c.en} · ${new Date(h.time).toLocaleString(state.lang==='ur'?'ur-PK':'en-PK',{dateStyle:'medium',timeStyle:'short'})}</p></div><div class="history-score">${Math.round(h.confidence*100)}%</div></article>`}).join('');
}

function seedChat(){if($('#chatMessages').children.length)return;addMessage('assistant',t('demoWelcome'));renderQuickPrompts()}
function refreshChatLanguage(){const msgs=$$('#chatMessages .message');if(msgs.length===1&&msgs[0].dataset.seed==='true')msgs[0].firstChild.textContent=t('demoWelcome');renderQuickPrompts()}
function renderMarkdown(text){
  text=text.replace(/(<\/strong>)([\u2022\-\*]\s)/g,'$1\n$2');
  text=text.replace(/([^\n])\s{2,}([\u2022\-\*])/g,'$1\n$2');
  const lines=text.split('\n');
  let html='';
  let inParagraph=false;
  for(let i=0;i<lines.length;i++){
    let line=lines[i].trim();
    if(!line){
      if(inParagraph){html+='</p>';inParagraph=false}
      continue;
    }
    const isHeadingLine=/^\*\*(.+?)\*\*$/.test(line)&&line.replace(/\*\*/g,'').trim().length<60;
    if(/^[\u2022\-\*]\s/.test(line)){
      if(inParagraph){html+='</p>';inParagraph=false}
      line=line.replace(/^[\u2022\-\*]\s*/,'');
      line=line.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
      line=line.replace(/\*(.+?)\*/g,'<em>$1</em>');
      html+='<div class="chat-bullet">\u2022 '+line+'</div>';
    }else if(isHeadingLine){
      if(inParagraph){html+='</p>';inParagraph=false}
      const headingText=line.replace(/^\*\*(.+?)\*\*$/,'$1');
      html+='<div class="chat-heading"><strong>'+headingText+'</strong></div>';
    }else{
      line=line.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
      line=line.replace(/\*(.+?)\*/g,'<em>$1</em>');
      if(!inParagraph){html+='<p>';inParagraph=true}
      else{html+='<br>'}
      html+=line;
    }
  }
  if(inParagraph)html+='</p>';
  return html;
}
function addMessage(role,text,seed=false){const div=document.createElement('div');div.className=`message ${role}`;div.dataset.seed=seed?'true':'false';const contentSpan=document.createElement('span');contentSpan.className='msg-content';contentSpan.innerHTML=renderMarkdown(text);div.appendChild(contentSpan);const time=document.createElement('small');time.textContent=new Date().toLocaleTimeString(state.lang==='ur'?'ur-PK':'en-PK',{hour:'2-digit',minute:'2-digit'});div.appendChild(time);if(role==='assistant'){const listenBtn=document.createElement('button');listenBtn.className='msg-listen-btn';listenBtn.innerHTML='<svg viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';listenBtn.title='Listen';listenBtn.addEventListener('click',()=>speakText(text,listenBtn));div.appendChild(listenBtn)}$('#chatMessages').appendChild(div);$('#chatMessages').scrollTop=$('#chatMessages').scrollHeight}
function renderQuickPrompts(){$('#quickPrompts').innerHTML=[t('quick1'),t('quick2'),t('quick3')].map(q=>`<button class="quick-prompt">${q}</button>`).join('');$$('.quick-prompt').forEach(b=>b.addEventListener('click',()=>{ $('#chatInput').value=b.textContent; $('#chatForm').requestSubmit()}))}
function renderChatContext(){
  const c=activeCrop();let chips=[];
  if(c)chips.push(`${state.lang==='ur'?c.ur:c.en}`);
  if(state.latestDiagnosis){
    const healthy=Boolean(state.latestDiagnosis.healthy)||String(state.latestDiagnosis.disease||'').toLowerCase()==='healthy';
    chips.push(`${t('detected')}: ${displayDisease(state.latestDiagnosis.disease)}`);
    chips.push(`${t('severity')}: ${healthy?t('severityNA'):translateSeverity(state.latestDiagnosis.severity)}`);
  }
  $('#chatContext').innerHTML=chips.length?chips.map(x=>`<span class="context-chip">${escapeHTML(x)}</span>`).join(''):`<span class="context-chip">${t('chooseCropPrompt')}</span>`;
}
function openChat(force=false){$('#chatPanel').classList.add('open');if(force)$('#chatInput').focus()}
async function sendChat(e){e.preventDefault();const input=$('#chatInput'),text=input.value.trim();if(!text)return;const wasVoiceInput=_lastInputWasVoice;_lastInputWasVoice=false;addMessage('user',text);input.value='';autoGrow({target:input});
  const assistantDiv=document.createElement('div');assistantDiv.className='message assistant';const contentSpan=document.createElement('span');contentSpan.className='msg-content';contentSpan.innerHTML='';assistantDiv.appendChild(contentSpan);const time=document.createElement('small');time.textContent=new Date().toLocaleTimeString(state.lang==='ur'?'ur-PK':'en-PK',{hour:'2-digit',minute:'2-digit'});assistantDiv.appendChild(time);const listenBtn=document.createElement('button');listenBtn.className='msg-listen-btn';listenBtn.innerHTML='<svg viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';listenBtn.title='Listen';assistantDiv.appendChild(listenBtn);$('#chatMessages').appendChild(assistantDiv);$('#chatMessages').scrollTop=$('#chatMessages').scrollHeight;
  let fullReply='';
  try{const history=$$('#chatMessages .message').map(m=>({role:m.classList.contains('user')?'user':'assistant',content:m.childNodes[0].textContent}));const healthy=Boolean(state.latestDiagnosis?.healthy)||String(state.latestDiagnosis?.disease||'').toLowerCase()==='healthy';const context={crop:state.selectedCrop,disease:state.latestDiagnosis?.disease||null,severity:healthy?'N/A':(state.latestDiagnosis?.severity||null),disease_confidence:state.latestDiagnosis?.confidence||null,severity_confidence:healthy?null:(state.latestDiagnosis?.severityConfidence??null),uncertainty:state.latestDiagnosis?.uncertain||false,healthy,language:state.lang};const r=await fetch('/api/chat/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,context,history})});if(!r.ok){let message='The assistant is unavailable right now.';try{const body=await r.json();message=body?.detail?.message||body?.detail||body?.message||message}catch(_){ }throw new Error(message)}const reader=r.body.getReader();const decoder=new TextDecoder();let buffer='';while(true){const{done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});const lines=buffer.split('\n');buffer=lines.pop();for(const line of lines){if(line.startsWith('data: ')){const raw=line.slice(6);if(raw==='[DONE]')break;try{fullReply+=JSON.parse(raw)}catch(e){fullReply+=raw}contentSpan.innerHTML=renderMarkdown(fullReply);$('#chatMessages').scrollTop=$('#chatMessages').scrollHeight}}}if(buffer.trim()){const blines=buffer.split('\n');for(const line of blines){if(line.startsWith('data: ')){const raw=line.slice(6);if(raw!=='[DONE]'){try{fullReply+=JSON.parse(raw)}catch(e){fullReply+=raw}contentSpan.innerHTML=renderMarkdown(fullReply);$('#chatMessages').scrollTop=$('#chatMessages').scrollHeight}}}}if(!fullReply)throw new Error('The assistant returned an empty response.')}catch(err){fullReply=state.lang==='ur'?'معاون اس وقت دستیاب نہیں ہے۔ براہ کرم دوبارہ کوشش کریں۔':`Assistant unavailable: ${err.message||'Please try again.'}`;contentSpan.innerHTML=renderMarkdown(fullReply)}
  listenBtn.addEventListener('click',()=>speakText(fullReply,listenBtn));
  if(wasVoiceInput){speakText(fullReply,listenBtn)}}
function autoGrow(e){const el=e.target;el.style.height='auto';el.style.height=`${Math.min(el.scrollHeight,100)}px`}

let _currentSpeakingBtn=null;
async function speakText(text,btn){
  if(!text)return;
  const audio=$('#chatAudio');
  if(_currentSpeakingBtn===btn&&audio.src){
    audio.pause();
    audio.currentTime=0;
    if(btn){btn.classList.remove('speaking');btn.disabled=false}
    _currentSpeakingBtn=null;
    return;
  }
  if(_currentSpeakingBtn){
    audio.pause();
    audio.currentTime=0;
    if(_currentSpeakingBtn){_currentSpeakingBtn.classList.remove('speaking');_currentSpeakingBtn.disabled=false}
  }
  _currentSpeakingBtn=btn;
  const isUrdu=/[\u0600-\u06FF]/.test(text);
  const language=isUrdu?'urdu':'english';
  if(btn){btn.classList.add('speaking');btn.disabled=false}
  try{
    const r=await fetch('/api/tts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,language})});
    if(!r.ok)throw new Error('TTS failed');
    const blob=await r.blob();
    const url=URL.createObjectURL(blob);
    audio.src=url;
    audio.onended=()=>{if(btn){btn.classList.remove('speaking');btn.disabled=false}_currentSpeakingBtn=null;URL.revokeObjectURL(url)};
    audio.onerror=()=>{if(btn){btn.classList.remove('speaking');btn.disabled=false}_currentSpeakingBtn=null;URL.revokeObjectURL(url)};
    await audio.play();
  }catch(err){
    console.warn('TTS error:',err);
    if(btn){btn.classList.remove('speaking');btn.disabled=false}
    _currentSpeakingBtn=null;
  }
}

let _recognition=null;
let _listening=false;
let _lastInputWasVoice=false;
let _voiceLang=localStorage.getItem('ksa_voice_lang')||'ur-PK';
function toggleMicLang(){
  _voiceLang=_voiceLang==='ur-PK'?'en-US':'ur-PK';
  localStorage.setItem('ksa_voice_lang',_voiceLang);
  const micLangBtn=$('#chatMicLang');
  if(micLangBtn)micLangBtn.textContent=_voiceLang==='ur-PK'?'اُردو':'EN';
  toast(_voiceLang==='ur-PK'?'آواز: اردو':'Voice: English');
}
async function toggleMic(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){toast('Speech recognition not supported. Use Chrome or Edge.');return}
  if(_recognition){try{_recognition.stop()}catch(e){};_recognition=null;_listening=false;$('#chatMic').classList.remove('listening');return}
  if(navigator.permissions&&navigator.permissions.query){
    try{
      const perm=await navigator.permissions.query({name:'microphone'});
      if(perm.state==='denied'){toast('Microphone access blocked. Click the lock icon in the address bar to allow it.');return}
    }catch(e){}
  }
  _recognition=new SR();
  _recognition.lang=_voiceLang;
  _recognition.interimResults=false;
  _recognition.maxAlternatives=1;
  let _startedAt=0;
  _recognition.onstart=()=>{_listening=true;_startedAt=Date.now();$('#chatMic').classList.add('listening');toast(_voiceLang==='ur-PK'?'سن رہا ہے… بولیں':'Listening… speak now')};
  _recognition.onresult=(e)=>{
    const transcript=e.results[0][0].transcript;
    const input=$('#chatInput');
    const existing=input.value.trim();
    input.value=existing?existing+' '+transcript:transcript;
    autoGrow({target:input});
    _lastInputWasVoice=true;
  };
  _recognition.onend=()=>{
    const duration=Date.now()-_startedAt;
    _listening=false;_recognition=null;$('#chatMic').classList.remove('listening');
    if(duration<500&&_startedAt>0){toast('Microphone did not detect speech. Check permissions and try again.')}
  };
  _recognition.onerror=(e)=>{
    _listening=false;_recognition=null;$('#chatMic').classList.remove('listening');
    if(e.error==='not-allowed'){toast('Microphone access denied. Allow it in browser settings.')}
    else if(e.error==='no-speech'){toast('No speech detected. Try again and speak clearly.')}
    else if(e.error==='network'){toast('Voice recognition needs internet. Check connection.')}
    else if(e.error!=='aborted'){toast('Voice error: '+e.error)}
  };
  try{_recognition.start()}catch(e){toast('Could not start microphone. '+e.message);_recognition=null}
}

function openSidebar(){$('#sidebar').classList.add('mobile-open');$('#sidebarBackdrop').classList.add('show')}function closeSidebar(){$('#sidebar').classList.remove('mobile-open');$('#sidebarBackdrop').classList.remove('show')}
function toast(msg){const el=$('#toast');el.textContent=msg;el.classList.add('show');clearTimeout(toast._t);toast._t=setTimeout(()=>el.classList.remove('show'),2600)}


// --- Professional presentation shell -------------------------------------------------------------

function initProfessionalShell(){
  const collapsed = localStorage.getItem('pha_sidebar_collapsed') === '1';
  document.body.classList.toggle('sidebar-collapsed', collapsed);
  syncSidebarCollapseA11y();
}

function toggleSidebarCollapse(){
  if(window.innerWidth <= 960) return;
  const next = !document.body.classList.contains('sidebar-collapsed');
  document.body.classList.toggle('sidebar-collapsed', next);
  localStorage.setItem('pha_sidebar_collapsed', next ? '1' : '0');
  syncSidebarCollapseA11y();
}

function syncSidebarCollapseA11y(){
  const btn = document.querySelector('#sidebarCollapse');
  if(!btn) return;
  const collapsed = document.body.classList.contains('sidebar-collapsed');
  btn.setAttribute('aria-label', collapsed ? 'Expand sidebar' : 'Collapse sidebar');
  btn.title = collapsed ? 'Expand sidebar' : 'Collapse sidebar';
}

function initNeuralTree(){
  const wrap=document.getElementById('neuralTreeWrap');
  if(!wrap) return;

  const STEPS=[
    {step:'01',title:'Select Crop',desc:'Choose from 12 supported crops',icon:'<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><path d="M2 12h20M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10A15 15 0 0 1 12 2z"/>',angle:-60},
    {step:'02',title:'Upload Photo',desc:'Take a clear picture of the leaf',icon:'<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',angle:-20},
    {step:'03',title:'Get Diagnosis',desc:'AI identifies disease and severity',icon:'<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',angle:20},
    {step:'04',title:'AI Assistant',desc:'Get treatment advice instantly',icon:'<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',angle:60},
  ];

  const cx=500,baseY=460,topY=220;
  const branches=[
    {angle:-58,length:240,subs:[{angle:-30,length:80},{angle:15,length:65},{angle:-50,length:50}]},
    {angle:-20,length:200,subs:[{angle:-25,length:70},{angle:20,length:85}]},
    {angle:20,length:200,subs:[{angle:25,length:70},{angle:-20,length:85}]},
    {angle:58,length:240,subs:[{angle:30,length:80},{angle:-15,length:65},{angle:50,length:50}]},
  ];
  const branchOrigins=[topY+20,topY+55,topY+55,topY+20];

  const seededRandom=s=>{const x=Math.sin(s*9301+49297)*49297;return x-Math.floor(x)};

  const endpoints=branches.map((b,i)=>{
    const rad=(b.angle*Math.PI)/180;
    const originY=branchOrigins[i];
    return{
      x:cx+Math.sin(rad)*b.length,
      y:originY-Math.cos(rad)*b.length*0.3+(i<2?(1-i)*40:(i-1)*40),
      originY,angle:b.angle,subs:b.subs
    };
  });

  let activeNode=0;
  let svgNS='http://www.w3.org/2000/svg';

  // Build ambient glow div
  const ambient=document.createElement('div');
  ambient.className='nt-ambient';
  wrap.appendChild(ambient);

  // Build SVG
  const svg=document.createElementNS(svgNS,'svg');
  svg.setAttribute('viewBox','0 0 1000 560');

  // Defs
  const defs=document.createElementNS(svgNS,'defs');
  const gradDefs=[
    {id:'nodeGlowBig',type:'radial',stops:[{o:'0%',c:'#22C55E',a:'0.9'},{o:'40%',c:'#22C55E',a:'0.3'},{o:'100%',c:'#22C55E',a:'0'}]},
    {id:'goldGlow',type:'radial',stops:[{o:'0%',c:'#FDE047',a:'0.9'},{o:'40%',c:'#EAB308',a:'0.4'},{o:'100%',c:'#EAB308',a:'0'}]},
    {id:'canopyGlow',type:'radial',stops:[{o:'0%',c:'#86EFAC',a:'0.12'},{o:'50%',c:'#22C55E',a:'0.04'},{o:'100%',c:'transparent',a:'0'}]},
    {id:'trunkGrad',type:'linear',x1:'0%',y1:'100%',x2:'0%',y2:'0%',stops:[{o:'0%',c:'#16A34A',a:'0.2'},{o:'30%',c:'#22C55E',a:'0.6'},{o:'70%',c:'#4ADE80',a:'0.9'},{o:'100%',c:'#86EFAC',a:'1'}]},
    {id:'trunkGradOuter',type:'linear',x1:'0%',y1:'100%',x2:'0%',y2:'0%',stops:[{o:'0%',c:'#16A34A',a:'0.05'},{o:'50%',c:'#22C55E',a:'0.15'},{o:'100%',c:'#86EFAC',a:'0.25'}]},
    {id:'rootGrad',type:'linear',x1:'0%',y1:'0%',x2:'0%',y2:'100%',stops:[{o:'0%',c:'#22C55E',a:'0.5'},{o:'100%',c:'#16A34A',a:'0.05'}]},
  ];
  gradDefs.forEach(g=>{
    const el=document.createElementNS(svgNS,g.type==='radial'?'radialGradient':'linearGradient');
    el.setAttribute('id',g.id);
    if(g.type==='linear'){el.setAttribute('x1',g.x1);el.setAttribute('y1',g.y1);el.setAttribute('x2',g.x2);el.setAttribute('y2',g.y2)}
    g.stops.forEach(s=>{
      const st=document.createElementNS(svgNS,'stop');
      st.setAttribute('offset',s.o);st.setAttribute('stop-color',s.c);st.setAttribute('stop-opacity',s.a);
      el.appendChild(st);
    });
    defs.appendChild(el);
  });

  // Filters
  [{id:'glow',sd:'3'},{id:'glowMed',sd:'6'},{id:'glowStrong',sd:'10'},{id:'glowUltra',sd:'16'}].forEach(f=>{
    const filter=document.createElementNS(svgNS,'filter');filter.setAttribute('id',f.id);
    const blur=document.createElementNS(svgNS,'feGaussianBlur');blur.setAttribute('stdDeviation',f.sd);blur.setAttribute('result','b');
    const merge=document.createElementNS(svgNS,'feMerge');
    const mn1=document.createElementNS(svgNS,'feMergeNode');mn1.setAttribute('in','b');
    const mn2=document.createElementNS(svgNS,'feMergeNode');mn2.setAttribute('in','SourceGraphic');
    merge.appendChild(mn1);merge.appendChild(mn2);
    filter.appendChild(blur);filter.appendChild(merge);
    defs.appendChild(filter);
  });
  svg.appendChild(defs);

  // Helper to create SVG element
  function el(tag,attrs){
    const e=document.createElementNS(svgNS,tag);
    for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);
    return e;
  }

  // Canopy
  const canopy1=el('ellipse',{cx,cy:topY-10,rx:400,ry:200,fill:'url(#canopyGlow)',opacity:'0.9'});
  canopy1.appendChild(el('animate',{attributeName:'rx',values:'400;440;380;420;400',dur:'5s',repeatCount:'indefinite'}));
  canopy1.appendChild(el('animate',{attributeName:'ry',values:'200;220;190;210;200',dur:'5s',repeatCount:'indefinite'}));
  svg.appendChild(canopy1);

  // Canopy rings
  [{rx:300,ry:120,stroke:'rgba(234,179,8,0.15)',sw:50,dash:'80 40 20 40',dur:'4s',rdur:'30s',dir:'0 500 220'},
   {rx:260,ry:100,stroke:'rgba(34,197,94,0.12)',sw:35,dash:'60 30 30 30',dur:'5s',rdur:'25s',dir:'360 500 225'},
   {rx:180,ry:80,stroke:'rgba(253,224,71,0.12)',sw:25,dash:'',dur:'3s',rdur:'',dir:''}
  ].forEach(r=>{
    const e=el('ellipse',{cx,cy:topY+5,rx:r.rx,ry:r.ry,fill:'none',stroke:r.stroke,'stroke-width':r.sw});
    if(r.dash)e.setAttribute('stroke-dasharray',r.dash);
    e.appendChild(el('animate',{attributeName:'rx',values:`${r.rx};${r.rx+30};${r.rx-20};${r.rx+10};${r.rx}`,dur:r.dur,repeatCount:'indefinite'}));
    e.appendChild(el('animate',{attributeName:'ry',values:`${r.ry};${r.ry+20};${r.ry-10};${r.ry+10};${r.ry}`,dur:r.dur,repeatCount:'indefinite'}));
    if(r.rdur){
      e.appendChild(el('animateTransform',{attributeName:'transform',type:'rotate',from:r.dir,to:r.dir.split(' ').map((v,i)=>i===0?(parseInt(v)===0?360:0):v).join(' '),dur:r.rdur,repeatCount:'indefinite'}));
    }
    svg.appendChild(e);
  });

  // Canopy particles
  for(let i=0;i<28;i++){
    const angle=(i/28)*Math.PI*2;
    const radius=60+seededRandom(i*31)*250;
    const px=cx+Math.cos(angle)*radius;
    const py=topY-10+Math.sin(angle)*radius*0.45;
    const size=1.5+seededRandom(i*41)*4;
    const isGold=i%3===0;
    const c=el('circle',{cx:px,cy:py,r:size,fill:isGold?'#EAB308':'#4ADE80',opacity:(0.2+seededRandom(i*61)*0.35).toFixed(2)});
    if(size>3.5)c.setAttribute('filter','url(#glow)');
    c.style.animation=`floatParticle ${(2.5+seededRandom(i*51)*4).toFixed(1)}s ease-in-out infinite`;
    c.style.animationDelay=`${(seededRandom(i*71)*4).toFixed(1)}s`;
    c.appendChild(el('animate',{attributeName:'opacity',values:`${(0.1+seededRandom(i*81)*0.15).toFixed(2)};${(0.5+seededRandom(i*91)*0.4).toFixed(2)};${(0.1+seededRandom(i*81)*0.15).toFixed(2)}`,dur:`${(1.5+seededRandom(i*101)*2.5).toFixed(1)}s`,repeatCount:'indefinite'}));
    svg.appendChild(c);
  }

  // Background particles
  for(let i=0;i<55;i++){
    const px=80+seededRandom(i*7)*840;
    const py=20+seededRandom(i*13)*500;
    const pr=0.8+seededRandom(i*3)*2.5;
    const isGold=i%5===0;
    const c=el('circle',{cx:px,cy:py,r:pr,fill:isGold?'#EAB308':'#22C55E',opacity:(0.08+seededRandom(i*23)*0.25).toFixed(2)});
    c.style.animation=`floatParticle ${(4+seededRandom(i*11)*6).toFixed(1)}s ease-in-out infinite`;
    c.style.animationDelay=`${(seededRandom(i*17)*8).toFixed(1)}s`;
    svg.appendChild(c);
  }

  // Roots
  [{dx:-80,dy:60,curve:-40},{dx:-40,dy:70,curve:-15},{dx:0,dy:75,curve:0},{dx:40,dy:70,curve:15},{dx:80,dy:60,curve:40}].forEach((root,i)=>{
    const p=el('path',{d:`M ${cx} ${baseY} Q ${cx+root.curve} ${baseY+root.dy*0.5} ${cx+root.dx} ${baseY+root.dy}`,stroke:'url(#rootGrad)','stroke-width':(3-i*0.3).toFixed(1),fill:'none',filter:'url(#glow)'});
    p.classList.add('nt-path');
    p.style.animationDelay=`${i*0.15}s`;
    svg.appendChild(p);
  });

  // Root base glow
  svg.appendChild(el('circle',{cx,cy:baseY,r:30,fill:'url(#nodeGlowBig)',opacity:'0.4'}));
  svg.appendChild(el('circle',{cx,cy:baseY,r:8,fill:'#22C55E',opacity:'0.7',filter:'url(#glowMed)'}));

  // Trunk
  const trunkPath=`M ${cx} ${baseY} C ${cx-6} ${baseY-80} ${cx+4} ${topY+60} ${cx} ${topY}`;
  const trunkOuter=el('path',{d:trunkPath,stroke:'url(#trunkGradOuter)','stroke-width':'14',fill:'none',filter:'url(#glow)'});
  trunkOuter.classList.add('nt-path');
  svg.appendChild(trunkOuter);
  const trunkInner=el('path',{d:trunkPath,stroke:'url(#trunkGrad)','stroke-width':'5',fill:'none',filter:'url(#glowMed)'});
  trunkInner.classList.add('nt-path');
  trunkInner.style.animationDelay='0.2s';
  svg.appendChild(trunkInner);
  const trunkHighlight=el('path',{d:`M ${cx-1} ${baseY} C ${cx-7} ${baseY-80} ${cx+3} ${topY+60} ${cx-1} ${topY}`,stroke:'rgba(134,239,172,0.3)','stroke-width':'1.5',fill:'none'});
  trunkHighlight.classList.add('nt-path');
  trunkHighlight.style.animationDelay='0.4s';
  svg.appendChild(trunkHighlight);

  // Neural connection lines between endpoints
  endpoints.forEach((ep,i)=>{
    if(i>=endpoints.length-1)return;
    const next=endpoints[i+1];
    const midX=(ep.x+next.x)/2;
    const midY=Math.min(ep.y,next.y)-30;
    const p=el('path',{d:`M ${ep.x} ${ep.y} Q ${midX} ${midY} ${next.x} ${next.y}`,stroke:'rgba(34,197,94,0.08)','stroke-width':'1','stroke-dasharray':'4 6',fill:'none'});
    p.appendChild(el('animate',{attributeName:'stroke-dashoffset',from:'0',to:'-20',dur:'3s',repeatCount:'indefinite'}));
    svg.appendChild(p);
  });

  // Branch groups (will be updated on active change)
  const branchGroups=[];
  endpoints.forEach((ep,i)=>{
    const g=document.createElementNS(svgNS,'g');
    const originY=ep.originY;
    const rad=(ep.angle*Math.PI)/180;
    const midX=cx+(ep.x-cx)*0.35;
    const midY=originY+(ep.y-originY)*0.3-20;
    const branchPath=`M ${cx} ${originY} Q ${midX} ${midY} ${ep.x} ${ep.y}`;

    // Outer glow branch
    const bOuter=el('path',{d:branchPath,stroke:'rgba(34,197,94,0.05)','stroke-width':'6',fill:'none',filter:'url(#glowMed)'});
    bOuter.classList.add('nt-path');
    bOuter.style.animationDelay=`${0.6+i*0.25}s`;
    g.appendChild(bOuter);

    // Inner branch
    const bInner=el('path',{d:branchPath,stroke:'rgba(34,197,94,0.35)','stroke-width':'2',fill:'none',filter:'url(#glow)'});
    bInner.classList.add('nt-path');
    bInner.style.animationDelay=`${0.6+i*0.25}s`;
    g.appendChild(bInner);

    // Sub-branches
    ep.subs.forEach((sub,si)=>{
      const subRad=((ep.angle+sub.angle)*Math.PI)/180;
      const subX=ep.x+Math.sin(subRad)*sub.length;
      const subY=ep.y-Math.cos(subRad)*sub.length*0.5;
      const subMidX=ep.x+(subX-ep.x)*0.5;
      const subMidY=ep.y+(subY-ep.y)*0.5-10;
      const sp=el('path',{d:`M ${ep.x} ${ep.y} Q ${subMidX} ${subMidY} ${subX} ${subY}`,stroke:'rgba(34,197,94,0.12)','stroke-width':'1',fill:'none',filter:'url(#glow)'});
      sp.classList.add('nt-path');
      sp.style.animationDelay=`${0.9+i*0.25+si*0.1}s`;
      g.appendChild(sp);
      const sc=el('circle',{cx:subX,cy:subY,r:2.5,fill:'rgba(34,197,94,0.15)',filter:'url(#glow)'});
      g.appendChild(sc);
    });

    // Node circles
    const nodeGlow=el('circle',{cx:ep.x,cy:ep.y,r:18,fill:'rgba(34,197,94,0.05)'});
    nodeGlow.style.transition='all 0.6s ease';
    g.appendChild(nodeGlow);
    const nodeMid=el('circle',{cx:ep.x,cy:ep.y,r:10,fill:'rgba(34,197,94,0.1)',stroke:'rgba(34,197,94,0.2)','stroke-width':'1.5',filter:'url(#glow)'});
    nodeMid.style.transition='all 0.5s ease';
    g.appendChild(nodeMid);
    const nodeCore=el('circle',{cx:ep.x,cy:ep.y,r:5,fill:'rgba(74,222,128,0.4)'});
    nodeCore.style.transition='all 0.4s ease';
    g.appendChild(nodeCore);

    branchGroups.push({g,bOuter,bInner,nodeGlow,nodeMid,nodeCore,branchPath,ep});
    svg.appendChild(g);

    // Pulse rings (visible when active)
    const pulseRings=[];
    [{r:18,to:50,dur:'2s',stroke:'#4ADE80',sw:'1.5',op:'0.6',delay:'0s'},
     {r:18,to:65,dur:'2s',stroke:'#86EFAC',sw:'1',op:'0.4',delay:'0.5s'},
     {r:18,to:80,dur:'2s',stroke:'#22C55E',sw:'0.5',op:'0.3',delay:'1s'}
    ].forEach(pr=>{
      const ring=el('circle',{cx:ep.x,cy:ep.y,r:pr.r,fill:'none',stroke:pr.stroke,'stroke-width':pr.sw,opacity:'0'});
      ring.appendChild(el('animate',{attributeName:'r',from:String(pr.r),to:String(pr.to),dur:pr.dur,repeatCount:'indefinite',begin:pr.delay}));
      ring.appendChild(el('animate',{attributeName:'opacity',from:pr.op,to:'0',dur:pr.dur,repeatCount:'indefinite',begin:pr.delay}));
      ring.style.display='none';
      g.appendChild(ring);
      pulseRings.push(ring);
    });

    // Sparkle particles along branch (visible when active)
    const sparkles=[];
    [{r:5,fill:'#FDE047',filter:'url(#glowStrong)',op:'0.9',delay:'0s'},
     {r:3,fill:'#86EFAC',filter:'url(#glowMed)',op:'0.7',delay:'0.6s'},
     {r:2,fill:'#FDE047',filter:'url(#glow)',op:'0.5',delay:'1.2s'}
    ].forEach(sp=>{
      const c=el('circle',{r:sp.r,fill:sp.fill,filter:sp.filter,opacity:'0'});
      c.appendChild(el('animateMotion',{dur:'1.8s',repeatCount:'indefinite',begin:sp.delay,path:branchPath}));
      c.style.display='none';
      g.appendChild(c);
      sparkles.push(c);
    });

    branchGroups[branchGroups.length-1].pulseRings=pulseRings;
    branchGroups[branchGroups.length-1].sparkles=sparkles;
  });

  // Trunk sparkles
  [0,1.2,2.4,3.6].forEach(delay=>{
    const c=el('circle',{r:2.5,fill:'#86EFAC',filter:'url(#glow)',opacity:'0.6'});
    const am=el('animateMotion',{dur:'4s',repeatCount:'indefinite',begin:`${delay}s`,path:trunkPath});
    c.appendChild(am);
    c.appendChild(el('animate',{attributeName:'opacity',values:'0;0.7;0.7;0',dur:'4s',repeatCount:'indefinite',begin:`${delay}s`}));
    svg.appendChild(c);
  });
  [0.6,1.8,3.0].forEach(delay=>{
    const c=el('circle',{r:2,fill:'#FDE047',filter:'url(#glowMed)',opacity:'0.5'});
    c.appendChild(el('animateMotion',{dur:'4.5s',repeatCount:'indefinite',begin:`${delay}s`,path:trunkPath}));
    c.appendChild(el('animate',{attributeName:'opacity',values:'0;0.6;0.6;0',dur:'4.5s',repeatCount:'indefinite',begin:`${delay}s`}));
    svg.appendChild(c);
  });

  wrap.appendChild(svg);

  // Step labels
  const labelsDiv=document.createElement('div');
  labelsDiv.className='nt-step-labels';
  const labelEls=[];
  endpoints.forEach((ep,i)=>{
    const isRight=ep.x>cx;
    const lbl=document.createElement('div');
    lbl.className='nt-step-label';
    lbl.style.left=`${(ep.x/1000)*100}%`;
    lbl.style.top=`${(ep.y/560)*100}%`;
    lbl.style.transform=isRight?'translate(24px,-50%)':'translate(calc(-100% - 24px),-50%)';
    lbl.innerHTML=`<div class="nt-step-label-inner">
      <div class="nt-step-icon"><svg viewBox="0 0 24 24">${STEPS[i].icon}</svg></div>
      <div><span class="nt-step-num">${STEPS[i].step}</span><p class="nt-step-title">${STEPS[i].title}</p></div>
    </div>`;
    labelsDiv.appendChild(lbl);
    labelEls.push(lbl);
  });
  wrap.appendChild(labelsDiv);

  // Animation: cycle active node
  function updateActive(){
    branchGroups.forEach((bg,i)=>{
      const isActive=i===activeNode;
      bg.bOuter.setAttribute('stroke',isActive?'rgba(34,197,94,0.15)':'rgba(34,197,94,0.05)');
      bg.bOuter.setAttribute('stroke-width',isActive?'10':'6');
      bg.bInner.setAttribute('stroke',isActive?'#4ADE80':'rgba(34,197,94,0.35)');
      bg.bInner.setAttribute('stroke-width',isActive?'3':'2');
      bg.bInner.setAttribute('filter',isActive?'url(#glowStrong)':'url(#glow)');
      bg.nodeGlow.setAttribute('r',isActive?'35':'18');
      bg.nodeGlow.setAttribute('fill',isActive?'url(#nodeGlowBig)':'rgba(34,197,94,0.05)');
      bg.nodeMid.setAttribute('r',isActive?'18':'10');
      bg.nodeMid.setAttribute('fill',isActive?'rgba(34,197,94,0.3)':'rgba(34,197,94,0.1)');
      bg.nodeMid.setAttribute('stroke',isActive?'#4ADE80':'rgba(34,197,94,0.2)');
      bg.nodeMid.setAttribute('filter',isActive?'url(#glowStrong)':'url(#glow)');
      bg.nodeCore.setAttribute('r',isActive?'8':'5');
      bg.nodeCore.setAttribute('fill',isActive?'#86EFAC':'rgba(74,222,128,0.4)');
      bg.nodeCore.setAttribute('filter',isActive?'url(#glowMed)':'none');
      labelEls[i].classList.toggle('active',isActive);
      if(bg.pulseRings)bg.pulseRings.forEach(r=>{r.style.display=isActive?'':'none'});
      if(bg.sparkles)bg.sparkles.forEach(s=>{s.style.display=isActive?'':'none'});
    });
  }
  updateActive();
  setInterval(()=>{activeNode=(activeNode+1)%4;updateActive()},2500);
}

// Initialize only after all presentation-shell lexical state has been declared.
init();
