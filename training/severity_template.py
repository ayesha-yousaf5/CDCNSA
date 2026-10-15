# %% [markdown]
# # CDCNSA — Severity model (lesion segmentation → Mild / Moderate / Severe)
#
# **Before Run All**: Kaggle → **GPU T4 x2**, **Internet On** (or Colab → Runtime → **T4 GPU**). Fresh session. Expected time: 60–100 min.
#
# Instead of a separate weak severity classifier per crop, this trains ONE model that marks the diseased pixels
# (trained on **PlantSeg**: ~11k in-the-wild photos with pixel masks, 115 diseases, 34 plants; CC BY-NC-ND 4.0 → research/hackathon use).
# Severity is then *measured*: **lesion area ÷ leaf area** → Mild < 10 %, Moderate 10–30 %, Severe > 30 %.
#
# Outputs (Output panel → `cdcnsa_severity_export.zip`):
# * `lesion_seg_unet_r34.ts` — TorchScript model (the app needs no extra library to run it)
# * `severity_config.json` — input size, normalisation, thresholds
# * validation report (lesion IoU, Dice, severity agreement on a labelled cotton set if it downloads)
#
# **At the end, copy the printed FINAL REPORT block and send it back.**

# %%
IMG_SIZE = 384
EPOCHS = 18
BATCH = 16
SEED = 42
MILD_MAX, MODERATE_MAX = 10.0, 30.0       # % of leaf area
PLANTSEG_ZENODO = "13958858"               # PlantSeg v2 record (plantsegv2.zip, ~1.7 GB)
COTTON_SEVERITY_MENDELEY = ("74jsdxtmx2", 2)  # optional external check (mild/moderate/severe/critical)

# %%
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "segmentation-models-pytorch"], check=False)
import os, re, json, time, random, shutil, zipfile, urllib.request
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image, ImageOps, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import torch, torch.nn as nn, torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import segmentation_models_pytorch as smp

random.seed(SEED); np.random.seed(SEED)
try:
    torch.manual_seed(SEED)
except Exception as _e:   # a GPU error from an EARLIER crash stays until the session is restarted
    raise SystemExit("STOP: the GPU is broken from an earlier error in this session. Kaggle: stop the session and start "
                     "it again. Colab: Runtime > Disconnect and delete runtime. Then run all again.")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("Device:", DEVICE)
IN_COLAB = Path("/content").exists() and not Path("/kaggle").exists()
WORK = Path(os.environ.get("CDCNSA_WORK", "/kaggle/working" if Path("/kaggle").exists() else ("/content/working" if IN_COLAB else "working")))
def _scratch():
    best, free = str(WORK), -1
    for c in ("/kaggle/temp", "/tmp", str(WORK)):
        try:
            Path(c).mkdir(parents=True, exist_ok=True); f = shutil.disk_usage(c).free
            if f > free: best, free = c, f
        except Exception: pass
    return Path(best)
RAW = (WORK / "raw_sev") if os.environ.get("CDCNSA_WORK") else (_scratch() / "raw_sev"); EXPORT = WORK / "export" / "severity"
RAW.mkdir(parents=True, exist_ok=True); EXPORT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (CDCNSA research notebook)"}
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]

def http_get(url, dest=None, timeout=3600, attempts=3):
    for k in range(attempts):
        try:
            return _http_get_once(url, dest, timeout)
        except Exception as e:
            if k == attempts - 1: raise
            print(f"  download problem ({e}); retrying in {10 * (k + 1)}s", flush=True); time.sleep(10 * (k + 1))

def _http_get_once(url, dest=None, timeout=3600):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        if dest is None: return r.read()
        with open(str(dest) + ".part", "wb") as f: shutil.copyfileobj(r, f, length=1 << 20)
    os.replace(str(dest) + ".part", dest); return dest

# %% [markdown]
# ## 1. Download PlantSeg

# %%
ps_dir = RAW / "plantseg"
if not (ps_dir / ".done").exists():
    ps_dir.mkdir(exist_ok=True)
    rec = json.loads(http_get(f"https://zenodo.org/api/records/{PLANTSEG_ZENODO}").decode())
    for f in rec["files"]:
        name = f.get("key") or f.get("filename"); print("downloading", name, f.get("size", 0) / 1e9, "GB")
        http_get(f["links"]["self"], ps_dir / name)
        if name.endswith(".zip"):
            with zipfile.ZipFile(ps_dir / name) as z: z.extractall(ps_dir)
            (ps_dir / name).unlink()
    (ps_dir / ".done").write_text("ok")

# %% [markdown]
# ## 2. Pair images with masks (structure-agnostic) and keep PlantSeg's own train/val/test split

# %%
masks = {}
images = {}
for p in ps_dir.rglob("*"):
    if p.suffix.lower() not in IMG_EXT: continue
    parts = [x.lower() for x in p.parts]
    split = next((s for s in ("train", "val", "test") if s in parts), "train")
    if any(k in x for x in parts for k in ("annotation", "mask", "label", "gt")) and p.suffix.lower() == ".png":
        masks[(split, p.stem)] = p
    else:
        images[(split, p.stem)] = p
pairs = {s: [] for s in ("train", "val", "test")}
for key, ip in images.items():
    mp = masks.get(key)
    if mp: pairs[key[0]].append((ip, mp))
print({k: len(v) for k, v in pairs.items()}, "| unpaired images:", len(images) - sum(len(v) for v in pairs.values()))
from collections import Counter as _C
print("Folder layout (top 12):", _C(str(p.parent.relative_to(ps_dir)) for p in list(images.values())[:5000] + list(masks.values())[:5000]).most_common(12))
if not pairs["val"]:
    random.shuffle(pairs["train"]); n = len(pairs["train"]) // 10
    pairs["val"], pairs["train"] = pairs["train"][:n], pairs["train"][n:]
if not pairs["test"]:
    n = len(pairs["val"]) // 2; pairs["test"], pairs["val"] = pairs["val"][:n], pairs["val"][n:]
assert len(pairs["train"]) > int(os.environ.get("CDCNSA_MIN_PAIRS", 100)), "Could not pair PlantSeg images and masks — send this output back."

# %% [markdown]
# ## 3. Data pipeline (lesion = any non-zero mask pixel)

# %%
def letterbox(im, size, resample):
    w, h = im.size; s = size / max(w, h)
    im = im.resize((max(1, round(w * s)), max(1, round(h * s))), resample)
    canvas = Image.new(im.mode, (size, size), 0)
    canvas.paste(im, ((size - im.size[0]) // 2, (size - im.size[1]) // 2)); return canvas

class SegDS(Dataset):
    def __init__(self, rows, train): self.rows, self.train = rows, train
    def __len__(self): return len(self.rows)
    def __getitem__(self, i):
        ip, mp = self.rows[i]
        im = ImageOps.exif_transpose(Image.open(ip)).convert("RGB"); m = Image.open(mp).convert("L")
        if m.size != im.size: m = m.resize(im.size, Image.NEAREST)
        if self.train:
            w, h = im.size; s = random.uniform(0.6, 1.0)
            cw, ch = int(w * s), int(h * s); x0, y0 = random.randint(0, w - cw), random.randint(0, h - ch)
            im, m = im.crop((x0, y0, x0 + cw, y0 + ch)), m.crop((x0, y0, x0 + cw, y0 + ch))
            if random.random() < 0.5: im, m = ImageOps.mirror(im), ImageOps.mirror(m)
            if random.random() < 0.5: im, m = ImageOps.flip(im), ImageOps.flip(m)
            k = random.randint(0, 3)                       # 90-degree rotations (phone photos come in any orientation)
            if k: im, m = im.rotate(90 * k, expand=True), m.rotate(90 * k, expand=True)
            if random.random() < 0.8:                      # colour/lighting variety (sun, shade, phone cameras)
                from PIL import ImageEnhance
                im = ImageEnhance.Color(im).enhance(random.uniform(0.7, 1.3))
                im = ImageEnhance.Contrast(im).enhance(random.uniform(0.75, 1.25))
            if random.random() < 0.2:
                from PIL import ImageFilter
                im = im.filter(ImageFilter.GaussianBlur(random.uniform(0.3, 1.5)))
        im, m = letterbox(im, IMG_SIZE, Image.BILINEAR), letterbox(m, IMG_SIZE, Image.NEAREST)
        x = torch.from_numpy(np.asarray(im, np.float32) / 255.).permute(2, 0, 1)
        if self.train:
            x = (x * random.uniform(0.8, 1.2) + random.uniform(-0.06, 0.06)).clamp(0, 1)
        x = (x - torch.tensor(MEAN)[:, None, None]) / torch.tensor(STD)[:, None, None]
        y = torch.from_numpy((np.asarray(m) > 0).astype(np.float32))[None]
        return x, y

dl = {s: DataLoader(SegDS(pairs[s], s == "train"), batch_size=BATCH, shuffle=s == "train",
                    num_workers=4, pin_memory=True, drop_last=s == "train") for s in pairs}

# %% [markdown]
# ## 4. Train U-Net (ResNet34 encoder) with BCE + Dice

# %%
model = smp.Unet("resnet34", encoder_weights=(None if os.environ.get("CDCNSA_ENC_WEIGHTS") == "None" else "imagenet"), classes=1).to(DEVICE)
dice = smp.losses.DiceLoss("binary"); bce = nn.BCEWithLogitsLoss()
opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-4, total_steps=EPOCHS * len(dl["train"]), pct_start=0.1)
scaler = torch.amp.GradScaler("cuda", enabled=DEVICE == "cuda")

THRESHOLDS = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7]
@torch.no_grad()
def evaluate(loader, thresholds=(0.5,)):
    """Dataset-level lesion IoU / Dice at each threshold. Returns the best threshold's numbers (+ the threshold)."""
    model.eval(); st = {t: [0.0, 0.0, 0.0, 0.0] for t in thresholds}
    for x, y in loader:
        with torch.autocast(device_type="cuda", enabled=DEVICE == "cuda"):
            pr = model(x.to(DEVICE)).float().sigmoid().cpu()
        for t in thresholds:
            p = (pr > t).float(); a = st[t]
            a[0] += (p * y).sum().item(); a[1] += ((p + y) > 0).float().sum().item(); a[2] += p.sum().item(); a[3] += y.sum().item()
    res = {t: {"IoU": a[0] / max(a[1], 1), "Dice": 2 * a[0] / max(a[2] + a[3], 1)} for t, a in st.items()}
    t_best = max(res, key=lambda t: res[t]["IoU"])
    return dict(res[t_best], threshold=t_best)

best, best_state = -1, None
for ep in range(EPOCHS):
    model.train(); tl = 0; t0 = time.time()
    for x, y in dl["train"]:
        x, y = x.to(DEVICE, non_blocking=True), y.to(DEVICE, non_blocking=True)
        opt.zero_grad(set_to_none=True)
        with torch.autocast(device_type="cuda", enabled=DEVICE == "cuda"):
            out = model(x); loss = bce(out, y) + dice(out, y)
        scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); sched.step(); tl += loss.item()
    v = evaluate(dl["val"])
    print(f"ep{ep+1}/{EPOCHS} loss {tl/len(dl['train']):.3f} val IoU {v['IoU']:.3f} Dice {v['Dice']:.3f} ({time.time()-t0:.0f}s)", flush=True)
    if v["IoU"] > best:
        best = v["IoU"]; best_state = {k: t.detach().cpu().clone() for k, t in model.state_dict().items()}
model.load_state_dict(best_state)
# pick the lesion threshold on VALIDATION, then report TEST at that fixed threshold (honest)
vt = evaluate(dl["val"], THRESHOLDS); LESION_T = vt["threshold"]
print(f"Best lesion threshold on val: {LESION_T} (val IoU {vt['IoU']:.3f})")
test_metrics = evaluate(dl["test"], (LESION_T,)); print("TEST (PlantSeg test split, never used for training or threshold):", test_metrics)

# %% [markdown]
# ## 5. Severity = lesion area / leaf area

# %%
from scipy import ndimage as ndi
def leaf_mask(rgb):
    """Leaf = green tissue (excess-green on a smoothed image), speckle-removed, closed + hole-filled so lesions
    inside the leaf count as leaf, while brown soil / background does not (it would dilute the severity %)."""
    a = ndi.gaussian_filter(rgb.astype(np.float32) / 255.0, sigma=(2, 2, 0))
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = ndi.binary_opening((2 * g - r - b) > 0.06, iterations=2)
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=4))
    lab, n = ndi.label(m)
    if n > 1:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.flatnonzero(sizes >= 0.02 * m.size))
    return m

@torch.no_grad()
def lesion_prob(im):
    lb = letterbox(im, IMG_SIZE, Image.BILINEAR)
    x = torch.from_numpy(np.asarray(lb, np.float32) / 255.).permute(2, 0, 1)
    x = ((x - torch.tensor(MEAN)[:, None, None]) / torch.tensor(STD)[:, None, None])[None].to(DEVICE)
    model.eval()
    return model(x).float().sigmoid()[0, 0].cpu().numpy(), np.asarray(lb)

def severity(im):
    prob, rgb = lesion_prob(im)
    les = prob > LESION_T
    leaf = leaf_mask(rgb) | les
    pct = 100.0 * les.sum() / max(leaf.sum(), 1)
    band = "MILD" if pct < MILD_MAX else ("MODERATE" if pct < MODERATE_MAX else "SEVERE")
    return pct, band

# ground-truth-mask severity vs predicted severity on PlantSeg test (same leaf-mask rule for both)
agree = []; errs = []
for ip, mp in pairs["test"][:1000]:
    im = ImageOps.exif_transpose(Image.open(ip)).convert("RGB")
    p_pct, p_band = severity(im)
    m = np.asarray(letterbox(Image.open(mp).convert("L").resize(im.size, Image.NEAREST), IMG_SIZE, Image.NEAREST)) > 0
    rgb = np.asarray(letterbox(im, IMG_SIZE, Image.BILINEAR))
    g_pct = 100.0 * m.sum() / max((leaf_mask(rgb) | m).sum(), 1)
    g_band = "MILD" if g_pct < MILD_MAX else ("MODERATE" if g_pct < MODERATE_MAX else "SEVERE")
    agree.append(p_band == g_band); errs.append(abs(p_pct - g_pct))
# per-crop lesion IoU on the test split for the app's crops
OUR = ["apple", "corn", "cucumber", "eggplant", "grape", "rice", "tomato", "citrus"]
per_crop = {}
for crop in OUR:
    rows_c = [r for r in pairs["test"] if Path(r[0]).stem.lower().startswith(crop)]
    if len(rows_c) >= 5:
        per_crop[crop] = dict(evaluate(DataLoader(SegDS(rows_c, False), batch_size=BATCH, num_workers=2), (LESION_T,)), n=len(rows_c))
print("Per-crop test IoU:", {k: (round(v["IoU"], 3), v["n"]) for k, v in per_crop.items()})
sev_report = {"band_agreement_vs_gt_masks": round(float(np.mean(agree)), 3), "mean_abs_pct_error": round(float(np.mean(errs)), 2), "n": len(agree)}
print("Severity vs ground-truth masks:", sev_report)

# %% [markdown]
# ## 6. Optional external check on a labelled cotton severity set (skipped if it does not download)

# %%
ext = None
try:
    # Cotton-Original.zip only (112 MB, verified 2026-10-16): <disease>/{mild,moderate,critical} + healthy (789).
    # Bacterial blight is a spot/lesion disease -> the fair test for an area-based severity. Curl virus / wilt are
    # shape-changing diseases (no clear lesion area), reported separately for information only.
    ds, ver = COTTON_SEVERITY_MENDELEY; cdir = RAW / "cotton_sev"; cdir.mkdir(exist_ok=True)
    z = cdir / "Cotton-Original.zip"
    if not z.exists():
        files = json.loads(http_get(f"https://data.mendeley.com/public-api/datasets/{ds}/files?folder_id=root&version={ver}").decode())
        f = next(x for x in files if x["filename"] == "Cotton-Original.zip")
        http_get(f["content_details"]["download_url"], z)
    with zipfile.ZipFile(z) as zz: zz.extractall(cdir)
    by = {}
    for p in cdir.rglob("*"):
        if p.suffix.lower() not in IMG_EXT: continue
        parts = [x.lower() for x in p.parts]
        lab = next((k for k in ("critical", "moderate", "mild") if k in parts), "healthy" if "healthy" in parts else None)
        dis = next((d for d in ("bacterial blight", "curl virus", "fussarium wilt") if d in parts), "healthy")
        if lab: by.setdefault(dis, []).append((p, {"critical": "SEVERE"}.get(lab, lab.upper())))
    ext = {}
    for dis, rows in by.items():
        random.shuffle(rows); rows = rows[:200]
        res = [severity(ImageOps.exif_transpose(Image.open(p)).convert("RGB")) for p, _ in rows]
        pred = [b for _, b in res]
        if dis == "healthy":
            ext[dis] = {"n": len(rows), "predicted_MILD_share": round(float(np.mean([b == "MILD" for b in pred])), 3),
                        "mean_pct": round(float(np.mean([pc for pc, _ in res])), 2)}
        else:
            order = {"MILD": 0, "MODERATE": 1, "SEVERE": 2}
            ext[dis] = {"n": len(rows), "agreement": round(float(np.mean([a == b for a, (_, b) in zip(pred, rows)])), 3),
                        "within_one_level": round(float(np.mean([abs(order[a] - order[b]) <= 1 for a, (_, b) in zip(pred, rows)])), 3),
                        "label_counts": dict(Counter(b for _, b in rows)), "pred_counts": dict(Counter(pred))}
    print("Cotton severity external check:", json.dumps(ext, indent=1))
except Exception as e:
    print("External cotton check skipped:", e)

# %% [markdown]
# ## 7. Export (TorchScript — the app loads it with plain PyTorch)

# %%
model.eval().cpu()
ts = torch.jit.trace(model, torch.zeros(1, 3, IMG_SIZE, IMG_SIZE))
ts.save(str(EXPORT / "lesion_seg_unet_r34.ts"))
cfg = {"model": "lesion_seg_unet_r34.ts", "input_size": IMG_SIZE, "letterbox": True, "mean": MEAN, "std": STD,
       "lesion_threshold": LESION_T, "mild_max_pct": MILD_MAX, "moderate_max_pct": MODERATE_MAX,
       "leaf_mask": "fill_holes(close(open(exg>0.06))) union lesion",
       "test": test_metrics, "per_crop_test": per_crop, "severity_vs_gt": sev_report, "external_cotton": ext,
       "dataset": "PlantSeg (Zenodo 13958858, CC BY-NC-ND 4.0)"}
(EXPORT / "severity_config.json").write_text(json.dumps(cfg, indent=2))
shutil.make_archive(str(WORK / "cdcnsa_severity_export"), "zip", EXPORT)
print("\n" + "=" * 30 + " FINAL REPORT (copy everything below) " + "=" * 30)
print(json.dumps({"lesion_threshold": LESION_T, "test": test_metrics, "per_crop_test": per_crop, "severity_vs_gt": sev_report, "external_cotton": ext}, indent=1))
print("Download from the Output panel: cdcnsa_severity_export.zip")
if IN_COLAB:
    try:
        from google.colab import files as _cf; _cf.download(str(WORK / "cdcnsa_severity_export.zip"))
    except Exception as _e: print("Colab download did not start:", _e)
