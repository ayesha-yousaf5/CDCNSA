# %% [markdown]
# # CDCNSA — __CROP_TITLE__ disease classifier (overfit-safe training)
#
# **Before you press Run All** (right-hand panel → *Session options*):
# 1. **Accelerator → GPU T4 x2** (or P100)
# 2. **Internet → On** (needs a phone-verified Kaggle account)
# 3. Then **Run All**. Expected time: 30–90 min (downloads + 3 backbones).
#
# What this notebook does:
# 1. Downloads every source dataset for __CROP_TITLE__ (Mendeley / Dataverse / Figshare / Hugging Face / GitHub).
# 2. Uses **original images only** (skips any `augmented` folders), resizes them, removes **near-duplicates** (incl. flipped/rotated copies).
# 3. Splits **by source**: training sources vs. a **held-out source** the model never sees. The held-out source is cut into
#    `ood_val` (model selection, early stopping, calibration) and `ood_test` (the number you report).
# 4. Trains **ResNet50, DenseNet121, EfficientNet-B0** (torchvision, ImageNet-pretrained) — the same three backbones as the slides.
# 5. Picks the best by held-out-source macro-F1, calibrates confidence (temperature baked into the final layer), picks the
#    uncertainty threshold, and exports a checkpoint that drops straight into the CDCNSA app (`model_registry.json`).
#
# **At the end, copy the printed "FINAL REPORT" block and send it back.**
#
# __KAGGLE_HINT__

# %%
# ============================== CONFIG (edit only if told to) ==============================
CROP = "__CROP__"
CLASSES = __CLASSES__          # canonical names = names used by the website
# Ordered alias rules: first match wins. Target None = drop images in that folder.
ALIASES = __ALIASES__
# Sources. role: "train" or "heldout". kind: mendeley | dataverse | figshare | zenodo | hf | plantdoc | plantvillage | kaggle_input
SOURCES = __SOURCES__
CAP_PER_CLASS_PER_SOURCE = 1500   # max original images per class per source (keeps lab sets from dominating)
IMG_SIDE = 320                    # stored shorter side; training crops 224
EPOCHS_HEAD, EPOCHS_FULL = 3, 14
BATCH = 48
SEED = 42
TARGET_PRECISION = 0.85           # uncertainty gate: accepted predictions should be >=85% correct on ood_val
PRETRAINED = True                 # ImageNet weights (needs Internet on)
AUTO_KAGGLE_INPUTS = True         # every dataset you attach with "+ Add Input" becomes an extra TRAIN source
ARCHS = ["efficientnet_b0", "resnet50", "densenet121", "dinov2_vits14"]  # slides' 3 backbones + DINOv2 (robust to new photo styles)
MIN_TRAIN_IMAGES = __MIN_TRAIN__     # a class needs at least this many distinct training photos, else it is dropped
MIN_TRAIN_SOURCES = __MIN_SOURCES__      # ...and photos from at least this many different datasets (1 source = shortcut risk)
EXTRA_TEST_DIR = None             # optional: path to your own labelled test photos, e.g. "/kaggle/input/cdcnsa-test-photos/__CROP__"

# %%
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "imagehash", "rarfile"], check=False)
import os, re, io, json, glob, math, time, random, shutil, zipfile, tarfile, hashlib, urllib.request, urllib.parse, urllib.error
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageFile, ImageFilter
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None
import imagehash
import torch, torch.nn as nn, torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms, models
from sklearn.metrics import f1_score, classification_report, confusion_matrix

import warnings
warnings.filterwarnings("ignore", message=".*lr_scheduler.step.*")
warnings.filterwarnings("ignore", category=torch.jit.TracerWarning) if hasattr(torch.jit, "TracerWarning") else None
warnings.filterwarnings("ignore", message=".*unauthenticated requests to the HF Hub.*")
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("Device:", DEVICE, torch.cuda.get_device_name(0) if DEVICE == "cuda" else "")
if DEVICE != "cuda":
    print("WARNING: no GPU. Turn on Accelerator -> GPU in Session options, then restart.")
WORK = Path(os.environ.get("CDCNSA_WORK", "/kaggle/working"))
PROC = WORK / "proc" / CROP; EXPORT = WORK / "export" / CROP
for p in (PROC, EXPORT): p.mkdir(parents=True, exist_ok=True)
# clean leftovers from the first (disk-filling) version of this notebook
shutil.rmtree(WORK / "raw", ignore_errors=True)
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff", ".jfif"}
UA = {"User-Agent": "Mozilla/5.0 (CDCNSA research notebook)"}

# %% [markdown]
# ## 1. Download helpers

# %%
def http_get(url, dest=None, timeout=300, attempts=3):
    """Download with retries (network hiccups / timeouts). A clear refusal (HTTP 4xx) fails fast."""
    for k in range(attempts):
        try:
            return _http_get_once(url, dest, timeout)
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 and e.code != 429: raise
            err = e
        except Exception as e:
            err = e
        wait = 10 * (k + 1)
        print(f"    download problem ({err}); retry {k + 1}/{attempts - 1} in {wait}s" if k < attempts - 1 else f"    giving up: {err}", flush=True)
        if k < attempts - 1: time.sleep(wait)
    raise err

def _http_get_once(url, dest=None, timeout=300):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        if dest is None:
            return r.read()
        tmp = str(dest) + ".part"
        total = int(r.headers.get("Content-Length") or 0); done = 0; next_report = 100 << 20; t0 = time.time()
        with open(tmp, "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk: break
                f.write(chunk); done += len(chunk)
                if done >= next_report:
                    tot = f" of {total/1e6:.0f} MB" if total else ""
                    print(f"    ... {Path(str(dest)).name}: {done/1e6:.0f} MB{tot} ({done/1e6/max(1e-6, time.time()-t0):.1f} MB/s)", flush=True)
                    next_report += 100 << 20
        os.replace(tmp, dest)
        return dest

def http_json(url):
    return json.loads(http_get(url).decode("utf-8"))

def extract_all(folder):
    """Extract every archive under folder (repeatedly, for nested archives)."""
    for _ in range(4):
        found = False
        for p in list(Path(folder).rglob("*")):
            if not p.is_file():
                continue
            name = p.name.lower()
            out = p.with_name(p.name + "_x")
            try:
                if name.endswith(".zip"):
                    with zipfile.ZipFile(p) as z: z.extractall(out)
                elif name.endswith((".tar", ".tar.gz", ".tgz")):
                    with tarfile.open(p) as t: t.extractall(out)
                elif name.endswith((".rar", ".7z")):
                    r = subprocess.run(["7z", "x", "-y", f"-o{out}", str(p)], capture_output=True)
                    if r.returncode != 0:
                        print("  could not extract", p.name, "(install p7zip?)"); continue
                else:
                    continue
                p.unlink(); found = True
            except Exception as e:
                print("  extract failed:", p.name, e)
        if not found:
            break

def dl_mendeley(spec, dest):
    ds, ver = spec["id"], spec.get("version", 1)
    only = re.compile(spec["only_files"], re.I) if spec.get("only_files") else None
    if not only and not spec.get("download_folders"):   # the bulk zip contains every file, so it is skipped when only some files are wanted
        zip_url = f"https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/{ds}-{ver}.zip"
        try:
            print("  trying Mendeley bulk zip ...")
            http_get(zip_url, dest / f"{ds}-{ver}.zip", timeout=600)
            return True
        except Exception as e:
            print("  bulk zip failed:", e)
    # fallback: public API. Files are saved under their FULL folder path (class folders like
    # "Field Background/Rice Blast/" carry the labels - flattening them loses every label).
    try:
        base = f"https://data.mendeley.com/public-api/datasets/{ds}"
        folders = http_json(f"{base}/folders/{ver}")
        folders = folders if isinstance(folders, list) else []
        by_id = {fo["id"]: fo for fo in folders}
        def folder_path(fid):
            parts = []
            while fid in by_id:
                parts.append(re.sub(r'[\\/:*?"<>|]+', "_", by_id[fid]["name"].strip())); fid = by_id[fid].get("parent_id")
            return Path(*reversed(parts)) if parts else Path()
        todo = [(Path(), f) for f in http_json(f"{base}/files?folder_id=root&version={ver}")]
        for fo in folders:
            try:
                todo += [(folder_path(fo["id"]), f) for f in http_json(f"{base}/files?folder_id={fo['id']}&version={ver}")]
            except Exception:
                pass
        print(f"  Mendeley API: {len(todo)} files in {len(folders)} folders")
        jobs = []
        for sub, f in todo:
            url = (f.get("content_details") or {}).get("download_url")
            if not url: continue
            if only and not only.search(f["filename"]): continue
            if spec.get("download_folders") and not re.search(spec["download_folders"], str(sub), re.I): continue
            out = dest / sub / f["filename"]; out.parent.mkdir(parents=True, exist_ok=True)
            if not (out.exists() and out.stat().st_size > 0): jobs.append((url, out))
        # many small files -> 16 parallel downloads (one-by-one took ~1 s per photo)
        from concurrent.futures import ThreadPoolExecutor
        done = [0]
        def _one(job):
            try:
                http_get(job[0], job[1], timeout=600)
            except Exception as e:
                print("    failed:", job[1].name, e)
            done[0] += 1
            if done[0] % 300 == 0: print(f"    ... {done[0]}/{len(jobs)} files", flush=True)
        with ThreadPoolExecutor(16 if len(jobs) > 20 else 2) as ex:
            list(ex.map(_one, jobs))
        n = sum(1 for _, f in todo if (dest / _ / f["filename"]).exists())
        print(f"  downloaded {n} files via Mendeley API")
        return n > 0
    except Exception as e:
        print("  Mendeley API failed:", e)
    return False

def dl_dataverse(spec, dest, cap_files=None):
    doi = spec["doi"]
    meta = http_json(f"https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId={urllib.parse.quote(doi)}")
    files = meta["data"]["latestVersion"]["files"]
    total = sum(f["dataFile"].get("filesize", 0) for f in files)
    print(f"  Dataverse: {len(files)} files, {total/1e9:.2f} GB")
    per_dir = Counter()
    for f in files:
        df = f["dataFile"]; d = f.get("directoryLabel", "")
        name = df.get("filename") or df.get("label")
        is_img = Path(name).suffix.lower() in IMG_EXT
        if is_img and per_dir[d] >= CAP_PER_CLASS_PER_SOURCE:  # sample instead of downloading thousands of photos
            continue
        sub = dest / d; sub.mkdir(parents=True, exist_ok=True)
        try:
            http_get(f"https://dataverse.harvard.edu/api/access/datafile/{df['id']}", sub / name, timeout=900)
            per_dir[d] += 1
        except Exception as e:
            print("   failed", name, e)
    return True

def dl_figshare(spec, dest):
    art = http_json(f"https://api.figshare.com/v2/articles/{spec['id']}")
    for f in art.get("files", []):
        print(f"  figshare file {f['name']} {f.get('size',0)/1e6:.0f} MB")
        http_get(f["download_url"], dest / f["name"], timeout=1800)
    return True

def dl_zenodo(spec, dest):
    rec = http_json(f"https://zenodo.org/api/records/{spec['id']}")
    for f in rec["files"]:
        name = f.get("key") or f.get("filename")
        http_get(f["links"]["self"], dest / name, timeout=3600)
    return True

def dl_osf(spec, dest):
    """OSF project: try the whole-storage zip, else walk the API and download every file."""
    node = spec["id"]
    only = re.compile(spec["osf_folders"], re.I) if spec.get("osf_folders") else None
    if not only:   # the whole-storage zip holds every folder, so it is skipped when only some folders are wanted
        try:
            print("  trying OSF storage zip ...")
            http_get(f"https://files.osf.io/v1/resources/{node}/providers/osfstorage/?zip=", dest / f"{node}.zip", timeout=3600)
            return True
        except Exception as e:
            print("  OSF zip failed:", e)
    if spec.get("osf_zip_folder"):   # zip of ONE folder (much smaller than the whole project)
        try:
            print("  trying OSF folder zip ...")
            http_get(f"https://files.osf.io/v1/resources/{node}/providers/osfstorage/{spec['osf_zip_folder']}/?zip=",
                     dest / "Dataset_Original.zip", timeout=3600)   # zip name becomes the path prefix
            return True
        except Exception as e:
            print("  OSF folder zip failed:", e)
    n = 0
    def walk(url, sub):
        nonlocal n
        while url:
            page = http_json(url)
            for item in page.get("data", []):
                a = item["attributes"]
                if a.get("kind") == "folder":
                    nxt = sub / a["name"]
                    if only and len(nxt.parts) <= 2 and not only.search(str(nxt)): continue   # filter top levels only
                    walk(item["relationships"]["files"]["links"]["related"]["href"], nxt)
                else:
                    (dest / sub).mkdir(parents=True, exist_ok=True)
                    http_get(item["links"]["download"], dest / sub / a["name"], timeout=3600); n += 1
            url = (page.get("links") or {}).get("next")
    walk(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", Path("."))
    print(f"  downloaded {n} files via OSF API")
    return n > 0

def dl_plantdoc(spec, dest):
    if not (dest / "PlantDoc-Dataset").exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/pratikkayal/PlantDoc-Dataset", str(dest / "PlantDoc-Dataset")], check=True)
    return True

def dl_plantvillage(spec, dest):
    repo = dest / "PlantVillage-Dataset"
    if not repo.exists():
        subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                        "https://github.com/spMohanty/PlantVillage-Dataset", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "sparse-checkout", "set"] + [f"raw/color/{d}" for d in spec["folders"]], check=True)
    return True

def dl_git(spec, dest):
    """Git repo, checking out only the listed folders (no history, blobs fetched only for those folders)."""
    repo = dest / "repo"
    if not repo.exists():
        subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", spec["repo"], str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "sparse-checkout", "set", "--no-cone"] + [p.rstrip("/") + "/" for p in spec["paths"]], check=True)
    shutil.rmtree(repo / ".git", ignore_errors=True)
    return True

def _hf_token():
    if os.environ.get("HF_TOKEN"): return os.environ["HF_TOKEN"]
    try:
        from kaggle_secrets import UserSecretsClient
        return UserSecretsClient().get_secret("HF_TOKEN")
    except Exception:
        return None

def dl_hf(spec, dest):
    from datasets import load_dataset
    tok = _hf_token()
    if tok:
        os.environ["HF_TOKEN"] = tok; print("  using HF_TOKEN from Kaggle secrets (faster)")
    ds = load_dataset(spec["repo"], split=spec.get("split", "train"), streaming=True)
    feats = ds.features or {}
    label_col = spec.get("label_col")
    img_col = spec.get("image_col", "image")
    if label_col is None:
        for k, v in feats.items():
            if k != img_col and k.lower() in ("label", "labels", "class", "category"):
                label_col = k; break
    names = None
    try:
        names = feats[label_col].names
    except Exception:
        try: names = feats[label_col].feature.names
        except Exception: pass
    per = Counter(); n = 0; last_new = 0; t_hf = time.time()
    cap = spec.get("cap", CAP_PER_CLASS_PER_SOURCE)
    for row in ds:
        lab = row[label_col]
        if isinstance(lab, list):
            if spec.get("single_label_only", True) and len(lab) != 1: continue
            lab = lab[0]
        if isinstance(lab, str) and " " in lab.strip() and spec.get("space_separated_labels"):
            parts = lab.split()
            if len(parts) != 1: continue
            lab = parts[0]
        lab = names[lab] if (names and isinstance(lab, int)) else str(lab)
        n += 1; per[lab] += 1
        got = per_src[spec["name"]]
        if per[lab] <= cap * 2:                       # decode the image only while this label may still be needed
            img = row[img_col]
            if not isinstance(img, Image.Image):
                img = Image.open(io.BytesIO(img["bytes"]))
            classes_before = len(got)
            add_image(spec, (re.sub(r"[^\w\- ]", "_", lab), f"{n:06d}.jpg"), lambda img=img: img)
            if len(got) > classes_before: last_new = n
        if n % 500 == 0:
            print(f"    ... {n} rows read, kept {dict(got)} ({time.time() - t_hf:.0f}s)", flush=True)
        # stop once every class found so far is full and no new class has shown up for 3000 rows
        if got and all(v >= cap for v in got.values()) and n - last_new > 3000:
            print("    all classes reached the cap -> stopping the download early"); break
        if time.time() - t_hf > 60 * spec.get("max_minutes", 45):
            print(f"    time budget of {spec.get('max_minutes', 45)} min reached -> stopping with what we have"); break
    print("  HF labels seen:", dict(per))
    return True   # images were ingested directly (nothing left on disk)

def dl_kaggle_input(spec, dest):
    src = Path(spec["path"])
    if not src.exists():
        print("  Kaggle input not attached:", src); return False
    return True   # files are read in place from /kaggle/input

DL = {"git": dl_git, "osf": dl_osf, "mendeley": dl_mendeley, "dataverse": dl_dataverse, "figshare": dl_figshare, "zenodo": dl_zenodo,
      "plantdoc": dl_plantdoc, "plantvillage": dl_plantvillage, "hf": dl_hf, "kaggle_input": dl_kaggle_input}

# %% [markdown]
# ## 2. Download → keep originals only → resize → de-duplicate, ONE SOURCE AT A TIME
# Raw downloads go to the biggest scratch disk and are deleted as soon as a source is processed, so the
# 20 GB `/kaggle/working` limit is never hit. Images inside .zip files are read straight from the archive.
# Re-running this cell skips sources that are already finished.

# %%
def pick_scratch():
    best, free = None, -1
    for c in ("/kaggle/temp", "/tmp", str(WORK)):
        try:
            Path(c).mkdir(parents=True, exist_ok=True); f = shutil.disk_usage(c).free
            if f > free: best, free = c, f
        except Exception:
            pass
    print(f"Scratch disk: {best} ({free/1e9:.0f} GB free) | working: {shutil.disk_usage(str(WORK)).free/1e9:.0f} GB free")
    return Path(best) / "cdcnsa_raw" / CROP
SCRATCH = pick_scratch()

DROP_PATH = re.compile(r"augment|augument|augumen|\baug\b|_aug|synthetic|generated|__macosx", re.I)
COMPILED = [(re.compile(p, re.I), t) for p, t in ALIASES]
ARCHIVES = (".zip", ".rar", ".7z", ".tar", ".tar.gz", ".tgz")

def norm_part(s):
    return re.sub(r"[_\-\.\(\)]+", " ", s).strip().lower()

def class_for(rel_parts, require=None, exclude=None, allow_aug=False):
    path_txt = " / ".join(norm_part(p) for p in rel_parts)
    if DROP_PATH.search(path_txt) and not (allow_aug and "macosx" not in path_txt): return "SKIP_AUG"
    if require and not re.search(require, path_txt, re.I): return "OTHER_CROP"
    if exclude and re.search(exclude, path_txt, re.I): return None
    parts_ = [norm_part(p) for p in rel_parts[:-1]] + [norm_part(Path(rel_parts[-1]).stem)]
    for i, part in reversed(list(enumerate(parts_))):
        # dataset-title folders (long, or containing "dataset") must not decide the class;
        # PlantVillage-style "Crop___Disease" folders are class folders and are never skipped for length
        pv_style = i < len(rel_parts) - 1 and "___" in rel_parts[i]       # PlantVillage "Crop___Disease" class folder
        if "dataset" in part or part.endswith(" zip x") or (len(part.split()) > 6 and not pv_style):
            continue
        for rx, target in COMPILED:
            if rx.search(part):
                return target if target is not None else "DROP"
    return None

def to_rgb_resized(im):
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    if min(w, h) < 64: return None
    sc = IMG_SIDE / min(w, h)
    if sc < 1: im = im.resize((max(1, round(w*sc)), max(1, round(h*sc))), Image.BILINEAR)
    return im

def hashes(im):
    small = im.copy(); small.thumbnail((256, 256))
    vs = [small, ImageOps.mirror(small), ImageOps.flip(small), small.rotate(90, expand=True), small.rotate(180), small.rotate(270, expand=True)]
    return [imagehash.phash(v) for v in vs]
def band_keys(h):
    s = str(h); return [(b, s[2*b:2*b+2]) for b in range(8)]

kept, status = [], {}
dup, skipped_aug, unmapped, per_src = Counter(), Counter(), Counter(), defaultdict(Counter)
seen, bands = [], defaultdict(list)   # global de-dup index (across ALL sources of this crop)
_counter = [0]

def remember(hs0):
    seen.append(hs0)
    for k in band_keys(hs0): bands[k].append(len(seen) - 1)

def add_image(spec, rel_parts, opener):
    """Map -> cap -> resize -> de-dup -> save. opener() returns a PIL image."""
    name = spec["name"]
    c = class_for(rel_parts, spec.get("require"), spec.get("exclude"), spec.get("collapse_aug", False))
    if c == "SKIP_AUG": skipped_aug[name] += 1; return
    if c == "OTHER_CROP": return
    if c is None: unmapped[(name, "/".join(rel_parts[-3:-1]))] += 1; return
    if c == "DROP" or (c not in CLASSES and c != "__DISEASED__"): return
    if c == "__DISEASED__" and spec["role"] not in ("external", "split"): return
    if per_src[name][c] >= spec.get("cap", CAP_PER_CLASS_PER_SOURCE): return
    try:
        im = to_rgb_resized(opener())
    except Exception:
        return
    if im is None: return
    hs = hashes(im)
    cand = set()
    for h in hs:
        for k in band_keys(h): cand.update(bands.get(k, ()))
    if any(min(seen[j] - h for h in hs) <= 4 for j in cand):
        dup[name] += 1; return
    remember(hs[0])
    _counter[0] += 1
    out = PROC / name / c.replace("/", "-") / f"{_counter[0]:07d}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True); im.save(out, quality=90)
    per_src[name][c] += 1
    kept.append({"src": name, "role": spec["role"], "cls": c, "path": str(out)})

def ingest_zip(spec, zpath, prefix):
    with zipfile.ZipFile(zpath) as z:
        infos = [i for i in z.infolist() if not i.is_dir()]
        random.shuffle(infos)
        for info in infos:
            parts = prefix + tuple(Path(info.filename).parts)
            low = info.filename.lower()
            if Path(low).suffix in IMG_EXT:
                add_image(spec, parts, lambda info=info: Image.open(io.BytesIO(z.read(info))))
            elif low.endswith(ARCHIVES):
                tmp = SCRATCH / f"_nested_{_counter[0]}_{Path(low).name}"
                with z.open(info) as src_f, open(tmp, "wb") as dst: shutil.copyfileobj(src_f, dst, 1 << 20)
                ingest_path(spec, tmp, parts[:-1] + (Path(info.filename).stem,))
                tmp.unlink(missing_ok=True)

def ingest_path(spec, path, prefix=()):
    path = Path(path)
    if path.is_file():
        low = path.name.lower()
        if low.endswith(".zip"):
            ingest_zip(spec, path, prefix)
        elif low.endswith(ARCHIVES):
            out = path.with_name(path.name + "_x")
            if low.endswith((".rar", ".7z")):
                subprocess.run(["7z", "x", "-y", f"-o{out}", str(path)], capture_output=True)
            else:
                with tarfile.open(path) as t: t.extractall(out)
            ingest_path(spec, out, prefix); shutil.rmtree(out, ignore_errors=True)
        elif Path(low).suffix in IMG_EXT:
            add_image(spec, prefix + (path.name,), lambda: Image.open(path))
        return
    files = [p for p in path.rglob("*") if p.is_file()]
    random.shuffle(files)
    for p in files:
        rel = tuple(p.relative_to(path).parts)
        if p.name.lower().endswith(ARCHIVES):
            ingest_path(spec, p, prefix + rel[:-1] + (p.name.split(".")[0],))
        elif p.suffix.lower() in IMG_EXT:
            add_image(spec, prefix + rel, lambda p=p: Image.open(p))

def ingest_dataverse(spec, dest):
    """Per file: download -> ingest -> delete (the Tanzania set is many GB of 13 MP photos)."""
    meta = http_json(f"https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId={urllib.parse.quote(spec['doi'])}")
    files = meta["data"]["latestVersion"]["files"]; random.shuffle(files)
    print(f"  Dataverse: {len(files)} files, {sum(f['dataFile'].get('filesize', 0) for f in files)/1e9:.2f} GB listed")
    for f in files[:40]:
        print(f"    - {f.get('directoryLabel', '')}/{f['dataFile'].get('filename')} ({f['dataFile'].get('filesize', 0)/1e6:.0f} MB)")
    cap = spec.get("cap", CAP_PER_CLASS_PER_SOURCE)
    for f in files:
        df = f["dataFile"]; dlab = f.get("directoryLabel", "")
        name = df.get("filename") or df.get("label")
        parts = tuple(Path(dlab).parts) + (name,)
        if name.lower().endswith(ARCHIVES) and class_for(parts, spec.get("require"), spec.get("exclude"), spec.get("collapse_aug", False)) in ("DROP", "SKIP_AUG"):
            print(f"    skipping {name} (class not used)"); continue
        if Path(name).suffix.lower() in IMG_EXT:
            c = class_for(parts, spec.get("require"), spec.get("exclude"), spec.get("collapse_aug", False))
            if c in CLASSES and per_src[spec["name"]][c] >= cap: continue   # don't even download
            if c is None or c in ("DROP", "SKIP_AUG", "OTHER_CROP"): continue
        tmp = dest / name
        try:
            before_n = sum(per_src[spec["name"]].values())
            http_get(f"https://dataverse.harvard.edu/api/access/datafile/{df['id']}", tmp, timeout=3600)
            ingest_path(spec, tmp, tuple(Path(dlab).parts))
            if not Path(name).suffix.lower() in IMG_EXT:
                print(f"   file {dlab}/{name} ({df.get('filesize', 0)/1e6:.0f} MB): kept {sum(per_src[spec['name']].values()) - before_n} images")
        except Exception as e:
            print("   failed", name, e)
        finally:
            if tmp.exists(): tmp.unlink()
    return True

CACHE_VERSION = "2026-10-15c"   # bump when download/label logic changes -> old caches are rebuilt
def spec_key(spec):
    return CACHE_VERSION + json.dumps({k: v for k, v in spec.items() if k != "role"}, sort_keys=True) + json.dumps(ALIASES)

def reload_done(spec):
    meta = PROC / spec["name"] / "_records.json"
    if not meta.exists(): return False
    try:
        saved = json.loads(meta.read_text())
    except Exception:
        return False
    # re-process if the cache came from an older notebook / different config, or kept nothing
    if not isinstance(saved, dict) or saved.get("key") != spec_key(spec) or not saved.get("rows"):
        print(f"[{spec['name']}] old or empty cache -> processing again")
        shutil.rmtree(PROC / spec["name"], ignore_errors=True); return False
    rows = saved["rows"]
    for r in rows:
        try:
            im = Image.open(r["path"]); remember(hashes(im)[0])
        except Exception:
            continue
        r["role"] = spec["role"]           # always use the role from the CURRENT config
        kept.append(r); per_src[r["src"]][r["cls"]] += 1
    return True

if AUTO_KAGGLE_INPUTS and Path("/kaggle/input").exists():
    used = {s.get("path") for s in SOURCES}
    for d in sorted(Path("/kaggle/input").iterdir()):
        if d.is_dir() and str(d) not in used:
            SOURCES.append({"name": "kaggle_" + d.name[:20], "kind": "kaggle_input", "role": "train", "path": str(d)})
            print("Attached Kaggle dataset added as training source:", d.name)

for s in SOURCES:
    name = s["name"]
    if reload_done(s):
        status[name] = "cached"; print(f"[{name}] already processed -> reused"); continue
    d = SCRATCH / name; d.mkdir(parents=True, exist_ok=True)
    print(f"[{name}] ({s['kind']}, role={s['role']}) ...")
    t0 = time.time(); before = len(kept)
    try:
        if s["kind"] == "dataverse":
            ok = ingest_dataverse(s, d)
        elif s["kind"] == "hf":
            ok = dl_hf(s, d)
        elif s["kind"] == "kaggle_input":
            ok = dl_kaggle_input(s, d)
            if ok: ingest_path(s, Path(s["path"]))
        else:
            ok = DL[s["kind"]](s, d)
            if ok: ingest_path(s, d)
        status[name] = "ok" if ok else "FAILED"
    except Exception as e:
        status[name] = f"FAILED: {e}"
    finally:
        shutil.rmtree(d, ignore_errors=True)          # free the disk immediately
    mine = [r for r in kept[before:] if r["src"] == name]
    if status[name] == "ok":
        (PROC / name).mkdir(parents=True, exist_ok=True)
        (PROC / name / "_records.json").write_text(json.dumps({"key": spec_key(s), "rows": mine}))
    print(f"   -> {status[name]}: kept {len(mine)} images {dict(per_src[name])} "
          f"({time.time()-t0:.0f}s, working disk free {shutil.disk_usage(str(WORK)).free/1e9:.1f} GB)")

print("\nDOWNLOAD STATUS:", json.dumps(status, indent=1))
print("Skipped augmented-folder images:", dict(skipped_aug))
print("Near-duplicates removed per source:", dict(dup))
print("Top unmapped folders (send these if real disease folders appear here):")
for (src, fol), n in unmapped.most_common(25): print(f"  {src:28s} {fol:60s} {n}")
# If a source FAILED: open its page, click "Download All", copy the link, then in Kaggle use
# "+ Add Input -> Datasets -> New dataset -> Link" and change that source to kind="kaggle_input" with its /kaggle/input path.

table = defaultdict(Counter)
for r in kept: table[r["src"]][r["cls"]] += 1
print("\nORIGINAL, DE-DUPLICATED IMAGES PER SOURCE x CLASS")
print(f"{'class':38s}" + "".join(f"{s['name'][:16]:>18s}" for s in SOURCES))
for c in CLASSES:
    print(f"{c:38s}" + "".join(f"{table[s['name']][c]:>18d}" for s in SOURCES))

# %% [markdown]
# ## 4. Source-based split (the anti-overfitting step)

# %%
# Sources that ship ONLY augmented copies (e.g. the Kashmir apple set: shifted/sheared/zoomed versions of each photo)
# defeat the perceptual hash. For those ("collapse_aug": True) every image is embedded with DINOv2 and copies of the
# same photo are grouped (cosine >= COLLAPSE_SIM, no chaining); only ONE image per group is kept, so the train half
# and test half of a split can never contain two versions of the same leaf.
COLLAPSE_SIM = 0.90
def collapse_augmented(src_name):
    rows = [r for r in kept if r["src"] == src_name]
    if len(rows) < 2: return
    E, how = None, "DINOv2 similarity"
    try:
        try:
            enc = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14")
        except Exception:
            repo = WORK / "dinov2_src"
            if not repo.exists():
                subprocess.run(["git", "clone", "-q", "--depth", "1", "https://github.com/facebookresearch/dinov2", str(repo)], check=True)
            enc = torch.hub.load(str(repo), "dinov2_vits14", source="local")
        enc = enc.to(DEVICE).eval()
        tf = transforms.Compose([transforms.Resize(224), transforms.CenterCrop(224), transforms.ToTensor(),
                                 transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        feats = []
        with torch.no_grad():
            for i in range(0, len(rows), 64):
                x = torch.stack([tf(Image.open(r["path"]).convert("RGB")) for r in rows[i:i + 64]]).to(DEVICE)
                feats.append(F.normalize(enc(x).float(), dim=1).cpu())
        E = torch.cat(feats); del enc
    except Exception as e:   # no DINOv2 weights -> fall back to a looser perceptual-hash match
        print("  DINOv2 not available for grouping (", str(e)[:120], ") -> using perceptual hash")
        how = "perceptual hash <= 14 bits"
        H = np.array([np.asarray(imagehash.phash(Image.open(r["path"]).convert("RGB")).hash).ravel() for r in rows])
    removed = 0; sizes = Counter()
    for cls_ in sorted({r["cls"] for r in rows}):
        idx = [i for i, r in enumerate(rows) if r["cls"] == cls_]
        if E is not None:
            M = ((E[idx] @ E[idx].T) >= COLLAPSE_SIM).numpy()
        else:
            h = H[idx].astype(np.int16); M = (np.abs(h[:, None, :] - h[None, :, :]).sum(-1) <= 14)
        free = np.ones(len(idx), bool)
        for a in range(len(idx)):
            if not free[a]: continue
            grp = np.where(M[a] & free)[0]
            free[grp] = False; sizes[len(grp)] += 1
            for b in grp:
                if b != a: rows[idx[b]]["role"] = "aug_copy"; removed += 1
    if DEVICE == "cuda": torch.cuda.empty_cache()
    left = Counter(r["cls"] for r in rows if r["role"] != "aug_copy")
    print(f"  {src_name} ({how}): removed {removed} augmented copies -> {dict(left)} distinct photos "
          f"(group sizes: {dict(sorted(sizes.items())[:8])})")
for s in SOURCES:
    if s.get("collapse_aug"): collapse_augmented(s["name"])
kept = [r for r in kept if r["role"] != "aug_copy"]

held = [r for r in kept if r["role"] == "heldout"]
external = [r for r in kept if r["role"] == "external"]
split_rows = [r for r in kept if r["role"] == "split" and r["cls"] != "__DISEASED__"]
if split_rows:
    # Half of each 'split' source (e.g. Pakistani photos) is used for TRAINING, the other half stays a never-seen test.
    by = defaultdict(list)
    for r in split_rows: by[(r["src"], r["cls"])].append(r)
    rng_split = random.Random(SEED + 7)
    for (src, cls_), lst in by.items():
        rng_split.shuffle(lst); half = len(lst) // 2
        for r in lst[:half]: r["role"] = "train"
        for r in lst[half:]: r["role"] = "external"
    kept_train_extra = [r for r in split_rows if r["role"] == "train"]
    print(f"'split' sources: {len(kept_train_extra)} photos added to training, "
          f"{len(split_rows) - len(kept_train_extra)} kept as real-world test")
    external += [r for r in split_rows if r["role"] == "external"]
train_pool = [r for r in kept if r["role"] == "train"]
_n_cls = Counter(r["cls"] for r in train_pool)
_src_cls = defaultdict(set)
for r in train_pool: _src_cls[r["cls"]].add(r["src"])
present, too_small = [], []
for c in CLASSES:
    if _n_cls[c] == 0: continue
    if _n_cls[c] < MIN_TRAIN_IMAGES or len(_src_cls[c]) < MIN_TRAIN_SOURCES:
        too_small.append(f"{c} ({_n_cls[c]} photos from {len(_src_cls[c])} dataset(s))")
    else:
        present.append(c)
if too_small:
    print("DROPPED - too few training photos or only one dataset:", too_small)
    print(f"  (rule: >= {MIN_TRAIN_IMAGES} photos from >= {MIN_TRAIN_SOURCES} datasets; the app will leave these to Qwen)")
missing = [c for c in CLASSES if c not in present]
if missing: print("Classes with NO training images (will be excluded):", missing)
if len(present) < 2:
    print("\n" + "!" * 80 + "\nSTOP - not enough training data. Training images per source x class:")
    for s_ in SOURCES:
        print(f"   {s_['name']:28s} role={s_['role']:8s} {dict(per_src[s_['name']])}  status={status.get(s_['name'])}")
    print("Copy everything from 'DOWNLOAD STATUS' down to here and send it back.\n" + "!" * 80)
    raise SystemExit("STOP: fewer than 2 classes have training images. Check DOWNLOAD STATUS and the "
                     "'unmapped folders' list above, then send that output back.")
CLS = present; C2I = {c: i for i, c in enumerate(CLS)}
train_pool = [r for r in train_pool if r["cls"] in C2I]
held = [r for r in held if r["cls"] in C2I]

def stratified_split(rows, frac, seed=SEED):
    by = defaultdict(list)
    for r in rows: by[r["cls"]].append(r)
    a, b = [], []
    rng = random.Random(seed)
    for c, lst in by.items():
        rng.shuffle(lst); k = max(1, int(round(len(lst) * frac))) if len(lst) > 1 else 0
        b += lst[:k]; a += lst[k:]
    return a, b

train, val_id = stratified_split(train_pool, 0.12)       # in-distribution val (sanity only)
if len(held) >= 40:
    ood_val, ood_test = stratified_split(held, 0.5)
    SELECT_ON = "ood_val"
else:
    ood_val, ood_test = [], held
    SELECT_ON = "val_id"
    print("WARNING: held-out source too small/absent -> selecting on in-distribution val. "
          "Scores for this crop are NOT proof of generalisation.")
if EXTRA_TEST_DIR and Path(EXTRA_TEST_DIR).exists():
    extra = []
    for p in Path(EXTRA_TEST_DIR).rglob("*"):
        if p.suffix.lower() in IMG_EXT:
            c = class_for(p.relative_to(EXTRA_TEST_DIR).parts)
            if c in C2I: extra.append({"src": "extra", "role": "extra", "cls": c, "path": str(p)})
    print("Extra test photos:", len(extra))
else:
    extra = []
external = [r for r in external if r["cls"] in C2I or r["cls"] == "__DISEASED__"]
for name, rows in [("train", train), ("val_id", val_id), ("ood_val", ood_val), ("ood_test", ood_test), ("extra", extra), ("external", external)]:
    print(f"{name:9s} {len(rows):6d}  {dict(Counter(r['cls'] for r in rows))}")

# %% [markdown]
# ## 5. Training: ResNet50 · DenseNet121 · EfficientNet-B0 (same constructors as the app)

# %%
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
T_TRAIN = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.35, 1.0), ratio=(0.75, 1.33)),
    transforms.RandomHorizontalFlip(), transforms.RandomVerticalFlip(),
    transforms.RandomApply([transforms.RandomPerspective(0.25, p=1.0)], p=0.3),
    transforms.RandomRotation(25),
    transforms.TrivialAugmentWide(),
    transforms.ColorJitter(0.35, 0.35, 0.3, 0.04),
    transforms.RandomGrayscale(0.05),
    transforms.RandomApply([transforms.GaussianBlur(5, (0.1, 2.0))], p=0.25),
    transforms.ToTensor(), transforms.Normalize(MEAN, STD),
    transforms.RandomErasing(p=0.25, scale=(0.02, 0.12)),
])
T_EVAL = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(MEAN, STD)])  # = app runtime

# ---- domain-gap augmentation: make every source look like every other source ----
from scipy import ndimage as ndi
def plant_mask(arr):
    """Green tissue (excess-green on a smoothed image), speckle-removed, closed and hole-filled so lesions
    INSIDE the leaf count as leaf while brown soil around it stays background."""
    a = ndi.gaussian_filter(arr.astype(np.float32) / 255.0, sigma=(2, 2, 0))
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = ndi.binary_opening((2 * g - r - b) > 0.06, iterations=2)
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=4))
    lab, n = ndi.label(m)
    if n > 1:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.flatnonzero(sizes >= 0.02 * m.size))
    return m

def background_swap(im, rows):
    """Paste the leaf onto the background of a random photo from ANOTHER source (or a plain/noisy one)."""
    arr = np.asarray(im); m = plant_mask(arr)
    if m.mean() < 0.12 or m.mean() > 0.92: return im          # mask unreliable -> leave as is
    k = random.random()
    if k < 0.6:
        other = random.choice(rows)
        bg = Image.open(other["path"]).convert("RGB").resize(im.size)
    elif k < 0.8:
        bg = Image.new("RGB", im.size, tuple(int(x) for x in np.random.randint(40, 230, 3)))
    else:
        bg = Image.fromarray(np.random.randint(0, 255, (im.size[1] // 8 + 1, im.size[0] // 8 + 1, 3), np.uint8)).resize(im.size, Image.BILINEAR)
    mm = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    return Image.composite(im, bg, mm)

def jpeg_degrade(im):
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=random.randint(25, 90)); buf.seek(0)
    return Image.open(buf).convert("RGB")

def random_shadow(im):
    arr = np.asarray(im).astype(np.float32); h, w = arr.shape[:2]
    x0, x1 = sorted(random.sample(range(w), 2)); f = random.uniform(0.45, 0.8)
    arr[:, x0:x1] *= f
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))

P_BG, P_JPEG, P_SHADOW = 0.35, 0.35, 0.2

class DS(Dataset):
    """Augmentation strength adapts to class size: small classes (they are oversampled by the balanced
    sampler, so the same photo is seen many times) get stronger augmentation so the model cannot memorise them."""
    def __init__(self, rows, tf, train=False):
        self.rows, self.tf, self.train = rows, tf, train
        cnt = Counter(r["cls"] for r in rows)
        big = max(cnt.values()) if cnt else 1
        # boost in [1, 2]: 1 for the largest class, up to 2 for classes >= 8x smaller
        self.boost = {c: 1.0 + min(1.0, math.log2(max(1.0, big / n)) / 3.0) for c, n in cnt.items()}
        if train:
            print("Augmentation strength per class:", {c: round(b, 2) for c, b in sorted(self.boost.items(), key=lambda kv: -kv[1])})
    def __len__(self): return len(self.rows)
    def __getitem__(self, i):
        r = self.rows[i]
        im = Image.open(r["path"]).convert("RGB")
        if self.train:
            b = self.boost.get(r["cls"], 1.0)
            if random.random() < min(0.8, P_BG * b): im = background_swap(im, self.rows)
            if random.random() < min(0.6, P_SHADOW * b): im = random_shadow(im)
            if random.random() < min(0.7, P_JPEG * b): im = jpeg_degrade(im)
            if b > 1.3 and random.random() < 0.5:            # extra geometric/colour variety for rare classes
                im = transforms.RandomAffine(20, translate=(0.1, 0.1), scale=(0.8, 1.2), shear=10)(im)
                im = transforms.ColorJitter(0.25, 0.25, 0.25, 0.03)(im)
        return self.tf(im), C2I[r["cls"]]

def loader(rows, train_mode):
    if not rows: return None
    ds = DS(rows, T_TRAIN if train_mode else T_EVAL, train=train_mode)
    if train_mode:
        cnt = Counter(r["cls"] for r in rows)
        w = [1.0 / cnt[r["cls"]] for r in rows]
        return DataLoader(ds, batch_size=BATCH, sampler=WeightedRandomSampler(w, len(rows), replacement=True),
                          num_workers=4, pin_memory=True, drop_last=True)
    return DataLoader(ds, batch_size=BATCH * 2, shuffle=False, num_workers=4, pin_memory=True)

def build(arch, n):
    # identical to inference/architectures.py in the app, so checkpoints load with strict=True
    if arch == "resnet50":
        m = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2 if PRETRAINED else None); m.fc = nn.Linear(m.fc.in_features, n); head = m.fc
    elif arch == "densenet121":
        m = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1 if PRETRAINED else None); m.classifier = nn.Linear(m.classifier.in_features, n); head = m.classifier
    elif arch == "efficientnet_b0":
        m = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1 if PRETRAINED else None); m.classifier[1] = nn.Linear(m.classifier[1].in_features, n); head = m.classifier
    elif arch == "dinov2_vits14":
        m = DinoClassifier(n); head = m.head
    else:
        raise ValueError(arch)
    return m, head

class DinoClassifier(nn.Module):
    """DINOv2 ViT-S/14 (self-supervised on 142M curated images) + linear head. Exported as TorchScript."""
    def __init__(self, n):
        super().__init__()
        try:
            self.backbone = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14", pretrained=PRETRAINED)
        except Exception as e:   # hub API unreachable -> use a plain git clone of the same code
            repo = WORK / "dinov2_src"
            if not repo.exists():
                subprocess.run(["git", "clone", "-q", "--depth", "1", "https://github.com/facebookresearch/dinov2", str(repo)], check=True)
            self.backbone = torch.hub.load(str(repo), "dinov2_vits14", source="local", pretrained=PRETRAINED)
        self.head = nn.Linear(self.backbone.embed_dim, n)
    def forward(self, x):
        return self.head(self.backbone(x))

@torch.no_grad()
def predict(model, dl):
    model.eval(); L, Y = [], []
    for x, y in dl:
        with torch.autocast(device_type="cuda", enabled=DEVICE == "cuda"):
            L.append(model(x.to(DEVICE, non_blocking=True)).float().cpu())
        Y.append(y)
    return torch.cat(L), torch.cat(Y)

def macro_f1(logits, y):
    return f1_score(y.numpy(), logits.argmax(1).numpy(), average="macro", labels=sorted(set(y.numpy().tolist())))

def train_arch(arch):
    model, head = build(arch, len(CLS)); model.to(DEVICE)
    dl_tr = loader(train, True)
    dl_sel = loader(ood_val if SELECT_ON == "ood_val" else val_id, False)
    dl_vid_sel = loader(val_id, False) if SELECT_ON == "ood_val" else None
    crit = nn.CrossEntropyLoss(label_smoothing=0.1)
    scaler = torch.amp.GradScaler("cuda", enabled=DEVICE == "cuda")
    best, best_state, patience = -1, None, 0
    def run(epochs, params, lr):
        nonlocal best, best_state, patience
        opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.05)
        sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=max(1, epochs * len(dl_tr)), pct_start=0.15)
        for ep in range(epochs):
            model.train(); tl = 0
            for x, y in dl_tr:
                x, y = x.to(DEVICE, non_blocking=True), y.to(DEVICE, non_blocking=True)
                opt.zero_grad(set_to_none=True)
                with torch.autocast(device_type="cuda", enabled=DEVICE == "cuda"):
                    loss = crit(model(x), y)
                scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); sched.step(); tl += loss.item()
            lg, yy = predict(model, dl_sel); f_ood = macro_f1(lg, yy)
            if dl_vid_sel is not None:
                # held-out sources often contain only a few classes -> also require all classes to stay good
                lg2, yy2 = predict(model, dl_vid_sel); f_id = macro_f1(lg2, yy2)
                f = 0.5 * f_ood + 0.5 * f_id
                print(f"  {arch} ep{ep+1}/{epochs} loss {tl/len(dl_tr):.3f}  held-out F1 {f_ood:.3f} | all-class F1 {f_id:.3f} | score {f:.3f}")
            else:
                f = f_ood
                print(f"  {arch} ep{ep+1}/{epochs} loss {tl/len(dl_tr):.3f}  {SELECT_ON} macroF1 {f:.3f}")
            if f > best + 1e-4:
                best, patience = f, 0
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            else:
                patience += 1
            if patience >= 4: print("  early stop"); return
    for p in model.parameters(): p.requires_grad = False
    for p in head.parameters(): p.requires_grad = True
    run(EPOCHS_HEAD, list(head.parameters()), 1e-3)
    for p in model.parameters(): p.requires_grad = True
    patience = 0
    run(EPOCHS_FULL, model.parameters(), {"efficientnet_b0": 3e-4, "dinov2_vits14": 2e-5}.get(arch, 1.5e-4))
    model.load_state_dict(best_state)
    return model, best

results = {}
trained = {}
for arch in ARCHS:
    t0 = time.time()
    try:
        m, f = train_arch(arch)
    except Exception as e:
        print(f"{arch} skipped: {e}"); continue
    results[arch] = {"select_macroF1": round(f, 4), "minutes": round((time.time() - t0) / 60, 1)}
    trained[arch] = m.cpu(); torch.cuda.empty_cache()
    print(arch, results[arch])

# %% [markdown]
# ## 6. Pick best backbone, calibrate, set uncertainty threshold, report

# %%
dl_sel = loader(ood_val if SELECT_ON == "ood_val" else val_id, False)
dl_test = loader(ood_test, False); dl_vid = loader(val_id, False); dl_extra = loader(extra, False)
best_arch = max(results, key=lambda a: results[a]["select_macroF1"])
model = trained[best_arch].to(DEVICE)

lg_sel, y_sel = predict(model, dl_sel)
T = torch.ones(1, requires_grad=True)
opt = torch.optim.LBFGS([T], lr=0.05, max_iter=100)
def _closure():
    opt.zero_grad(); l = F.cross_entropy(lg_sel / T.clamp(min=0.05), y_sel); l.backward(); return l
opt.step(_closure)
TEMP = float(T.detach().clamp(min=0.05))
# bake temperature into the final layer so the app needs no code change
lin = {"resnet50": lambda: model.fc, "densenet121": lambda: model.classifier,
       "efficientnet_b0": lambda: model.classifier[1], "dinov2_vits14": lambda: model.head}[best_arch]()
with torch.no_grad():
    lin.weight /= TEMP; lin.bias /= TEMP

def gate_threshold(lg, y, target=TARGET_PRECISION):
    p = F.softmax(lg / TEMP, 1); conf, pred = p.max(1)
    for t in np.arange(0.50, 0.96, 0.01):   # never below 0.50
        keep = conf >= t
        if keep.sum() >= max(5, 0.2 * len(y)) and (pred[keep] == y[keep]).float().mean() >= target:
            return float(round(t, 2)), float(keep.float().mean())
    return 0.60, float((conf >= 0.60).float().mean())  # target not reachable -> conservative default
THRESH, COVER = gate_threshold(lg_sel, y_sel)

def report(name, dl):
    if dl is None: return None
    lg, y = predict(model, dl)          # temperature already baked in
    p = F.softmax(lg, 1); conf, pred = p.max(1)
    labs = sorted(set(y.numpy().tolist()))
    f1 = f1_score(y.numpy(), pred.numpy(), average="macro", labels=labs)
    acc = float((pred == y).float().mean())
    keep = conf >= THRESH
    acc_kept = float((pred[keep] == y[keep]).float().mean()) if keep.any() else float("nan")
    print(f"\n=== {name}: n={len(y)} acc={acc:.3f} macroF1={f1:.3f} | gate@{THRESH}: answered {keep.float().mean():.0%}, accuracy on answered {acc_kept:.3f}")
    print(classification_report(y.numpy(), pred.numpy(), labels=labs, target_names=[CLS[i] for i in labs], digits=3, zero_division=0))
    return {"n": int(len(y)), "acc": round(acc, 4), "macroF1": round(f1, 4), "answered": round(float(keep.float().mean()), 3), "acc_answered": round(acc_kept, 4)}

final = {"crop": CROP, "best_arch": best_arch, "selected_on": SELECT_ON, "backbones": results,
         "temperature": round(TEMP, 3), "threshold": THRESH, "classes": CLS,
         "counts": {k: dict(v) for k, v in table.items()}, "download_status": status}
final["val_in_distribution"] = report("val (same sources as training — optimistic)", dl_vid)
final["ood_test"] = report("OOD TEST (held-out source — the honest number)", dl_test)
final["extra_test"] = report("EXTRA (your own photos)", dl_extra)

@torch.no_grad()
def external_report():
    """Real-world test sets (e.g. Pakistani field photos). Rows labelled __DISEASED__ only say 'some disease':
    they count as correct when the model does NOT answer healthy."""
    if not external: return None
    model.eval(); out = {}
    by_src = defaultdict(list)
    for r in external: by_src[r["src"]].append(r)
    hi = C2I.get("healthy")
    for src, rows in by_src.items():
        ok = Counter(); tot = Counter(); answered = Counter(); ok_ans = Counter(); confusion = defaultdict(Counter)
        for i in range(0, len(rows), 64):
            chunk = rows[i:i + 64]
            x = torch.stack([T_EVAL(Image.open(r["path"]).convert("RGB")) for r in chunk]).to(DEVICE)
            with torch.autocast(device_type="cuda", enabled=DEVICE == "cuda"):
                p = F.softmax(model(x).float(), 1).cpu()
            conf, pred = p.max(1)
            for r, c, pr in zip(chunk, conf.tolist(), pred.tolist()):
                lab = r["cls"]
                good = (pr != hi) if lab == "__DISEASED__" else (pr == C2I[lab])
                tot[lab] += 1; ok[lab] += int(good); confusion[lab][CLS[pr]] += 1
                if c >= THRESH: answered[lab] += 1; ok_ans[lab] += int(good)
        print(f"\n=== EXTERNAL REAL-WORLD TEST: {src} (never seen in training) ===")
        res = {}
        for lab in tot:
            name = "any disease (not healthy)" if lab == "__DISEASED__" else lab
            acc = ok[lab] / tot[lab]; ans = answered[lab] / tot[lab]
            acc_ans = (ok_ans[lab] / answered[lab]) if answered[lab] else float("nan")
            print(f"  {name:32s} n={tot[lab]:4d}  correct {acc:6.1%} | answered {ans:5.0%}, correct when answered {acc_ans:6.1%}")
            print(f"      predicted as: {dict(confusion[lab].most_common(4))}")
            res[name] = {"n": tot[lab], "acc": round(acc, 4), "answered": round(ans, 3), "acc_answered": round(acc_ans, 4)}
        out[src] = res
    return out
final["external_real_world"] = external_report()

# %% [markdown]
# ## 7. Export for the CDCNSA app

# %%
fname = f"{CROP}_disease_{best_arch}_srcsplit.pt"
ckpt = {"model_state_dict": {k: v.cpu() for k, v in model.state_dict().items()},
        "class_to_idx": C2I, "architecture": best_arch, "image_size": 224,
        "normalization_mean": MEAN, "normalization_std": STD, "temperature_baked": TEMP,
        "threshold": THRESH, "report": final}
if best_arch == "dinov2_vits14":
    fname = f"{CROP}_disease_dinov2_srcsplit.ts"
    model.eval().cpu()
    traced = torch.jit.trace(model, torch.zeros(1, 3, 224, 224), check_trace=False)
    x_chk = torch.randn(2, 3, 224, 224)
    assert torch.allclose(traced(x_chk), model(x_chk), atol=1e-3), "TorchScript export mismatch"
    traced.save(str(EXPORT / fname))
    runtime_kind = "torchscript"
else:
    torch.save(ckpt, EXPORT / fname)
    runtime_kind = "classification"
registry_entry = {"runtime_kind": runtime_kind, "architecture": best_arch,
                  "checkpoint": f"models/{CROP}/disease/{fname}", "image_size": 224,
                  "normalization_mean": MEAN, "normalization_std": STD, "class_to_idx": C2I, "enabled": True,
                  "note": f"source-held-out training {time.strftime('%Y-%m-%d')}; ood_test macroF1="
                          f"{(final['ood_test'] or {}).get('macroF1')}"}
snippet = {"crop": CROP, "disease": registry_entry, "disease_threshold": THRESH}
(EXPORT / "registry_snippet.json").write_text(json.dumps(snippet, indent=2))
ok = (final["ood_test"] or {}).get("macroF1") or 0
if not final["ood_test"]:
    verdict = "NO HONEST TEST - the held-out dataset gave 0 images; the in-distribution score means nothing. Do not ship."
else:
    verdict = "PASS (ship it)" if (SELECT_ON == "ood_val" and ok >= 0.70) else ("WEAK - keep Qwen as primary" if ok >= 0.5 else "FAIL - hide crop or rely on Qwen")
final["verdict"] = verdict
(EXPORT / "final_report.json").write_text(json.dumps(final, indent=2))
shutil.make_archive(str(WORK / f"cdcnsa_{CROP}_export"), "zip", EXPORT)
print("\n" + "=" * 30 + " FINAL REPORT (copy everything below) " + "=" * 30)
print(json.dumps({k: final[k] for k in ("crop", "best_arch", "selected_on", "backbones", "threshold", "classes", "ood_test", "val_in_distribution", "extra_test", "external_real_world")}, indent=1))
print("VERDICT:", verdict)
print("Download from the Output panel:", f"cdcnsa_{CROP}_export.zip")
