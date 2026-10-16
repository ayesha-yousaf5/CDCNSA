"""Download the trained model files at deploy time (Render build step / Streamlit start-up).

The model files are too large for GitHub. Every file is listed in model_registry.json with a
"download" block:   {"gdrive_id": "<Google Drive file id or share link>", "bytes": <exact size>}
for every crop's final disease model and for the severity model ("severity_segmentation").

Sources, tried in this order for each file:
  1. Hugging Face model repo  - set CDCNSA_HF_REPO (e.g. "ayesha-yousaf5/cdcnsa-models") or
     "model_source": {"hf_repo": "..."} in model_registry.json. The repo holds the 11 files flat,
     with the same file names as in models_final/ (e.g. apple_disease_dinov2_srcsplit.ts).
     HF_TOKEN is only needed if that repo is private.
  2. Google Drive               - the gdrive_id of each file.

Run:  python download_models.py
- files that already exist with the right size are skipped (fast re-deploys);
- a file is written to "<name>.part" first and only moved into place when its size is right,
  so a failed download never deletes or damages a model that is already there;
- a missing source or a failed download only WARNS: the app still runs (Qwen photo check and
  the other models keep working).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _file_id(value: str) -> str:
    """Accept a bare id or any Google Drive share link."""
    value = (value or "").strip()
    m = re.search(r"/d/([A-Za-z0-9_-]{10,})", value) or re.search(r"[?&]id=([A-Za-z0-9_-]{10,})", value)
    return m.group(1) if m else value


def _registry() -> dict:
    return json.loads((ROOT / "model_registry.json").read_text(encoding="utf-8"))


def hf_repo(reg: dict | None = None) -> str:
    value = os.getenv("CDCNSA_HF_REPO") or ((reg or _registry()).get("model_source") or {}).get("hf_repo") or ""
    value = value.strip().rstrip("/")
    # accept a full link such as https://huggingface.co/user/repo
    m = re.search(r"huggingface\.co/([^/]+/[^/?#]+)", value)
    return m.group(1) if m else value


def wanted_files(root: Path = ROOT) -> list[dict]:
    reg = _registry()
    out = []
    for crop, tasks in reg["crops"].items():
        spec = tasks.get("disease") or {}
        if spec.get("enabled") and spec.get("download"):
            out.append({"name": f"{crop} disease", "path": root / spec["checkpoint"], **spec["download"]})
    seg = reg.get("severity_segmentation") or {}
    if seg.get("enabled") and seg.get("download"):
        out.append({"name": "severity (all crops)", "path": root / seg["checkpoint"], **seg["download"]})
    return out


def _from_hf(repo: str, filename: str, dest: Path) -> None:
    url = f"https://huggingface.co/{repo}/resolve/main/{filename}"
    req = urllib.request.Request(url, headers={"User-Agent": "CDCNSA/1.0"})
    token = os.getenv("HF_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as fh:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            fh.write(chunk)


def _from_gdrive(file_id: str, dest: Path) -> None:
    try:
        import gdown
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown", "-q"])
        import gdown
    if not gdown.download(id=file_id, output=str(dest), quiet=True):
        raise RuntimeError("gdown returned nothing")


def ensure_models(root: Path = ROOT, log=print) -> tuple[list[str], list[str]]:
    """Make sure every model file is present. Returns (ready, missing) lists of names."""
    repo = hf_repo()
    ok, missing = [], []
    for f in wanted_files(root):
        path, size = f["path"], int(f.get("bytes") or 0)
        if path.is_file() and (not size or path.stat().st_size == size):
            log(f"[models] present   {f['name']}")
            ok.append(f["name"])
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_name(path.name + ".part")
        sources = []
        if repo:
            sources.append(("Hugging Face", lambda p=part, n=path.name: _from_hf(repo, n, p)))
        gid = _file_id(f.get("gdrive_id", ""))
        if gid:
            sources.append(("Google Drive", lambda p=part, g=gid: _from_gdrive(g, p)))
        if not sources:
            log(f"[models] WARNING   {f['name']}: no Hugging Face repo and no gdrive_id -> not downloaded")
            missing.append(f["name"])
            continue
        done = False
        for label, fetch in sources:
            log(f"[models] download  {f['name']} from {label}")
            try:
                fetch()
                got = part.stat().st_size if part.is_file() else 0
                if size and got != size:
                    raise RuntimeError(f"wrong size ({got} of {size} bytes)")
                os.replace(part, path)
                done = True
                break
            except Exception as exc:  # network / permission / quota / wrong file
                log(f"[models] WARNING   {f['name']} from {label}: {str(exc)[:200]}")
            finally:
                if part.is_file():
                    part.unlink()
        if done:
            ok.append(f["name"])
        else:
            log(f"[models] WARNING   {f['name']}: not downloaded. Is the file shared publicly "
                "(Hugging Face repo public / Drive 'Anyone with the link')?")
            missing.append(f["name"])
    log(f"[models] ready: {len(ok)}  missing: {len(missing)} {missing if missing else ''}")
    return ok, missing


def main() -> None:
    ensure_models()


if __name__ == "__main__":
    main()
