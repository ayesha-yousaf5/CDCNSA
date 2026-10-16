"""Download the trained model files from Google Drive at deploy time (Render build step).

The model files are too large for GitHub. Each one is listed in model_registry.json with a
"download" block:   {"gdrive_id": "<Google Drive file id or share link>", "bytes": <exact size>}
for every crop's final disease model and for the severity model ("severity_segmentation").

Run:  python download_models.py
- files that already exist with the right size are skipped (fast re-deploys);
- a missing id or a failed download only WARNS: the app still runs, using the Qwen photo check
  and the other models (it never crashes on a missing model).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _file_id(value: str) -> str:
    """Accept a bare id or any Google Drive share link."""
    value = (value or "").strip()
    m = re.search(r"/d/([A-Za-z0-9_-]{10,})", value) or re.search(r"[?&]id=([A-Za-z0-9_-]{10,})", value)
    return m.group(1) if m else value


def wanted_files() -> list[dict]:
    reg = json.loads((ROOT / "model_registry.json").read_text(encoding="utf-8"))
    out = []
    for crop, tasks in reg["crops"].items():
        spec = tasks.get("disease") or {}
        if spec.get("enabled") and spec.get("download"):
            out.append({"name": f"{crop} disease", "path": ROOT / spec["checkpoint"], **spec["download"]})
    seg = reg.get("severity_segmentation") or {}
    if seg.get("enabled") and seg.get("download"):
        out.append({"name": "severity (all crops)", "path": ROOT / seg["checkpoint"], **seg["download"]})
    return out


def main() -> None:
    try:
        import gdown
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown", "-q"])
        import gdown

    ok, missing = [], []
    for f in wanted_files():
        path, size = f["path"], int(f.get("bytes") or 0)
        if path.is_file() and (not size or path.stat().st_size == size):
            print(f"[models] present   {f['name']}: {path.relative_to(ROOT)}")
            ok.append(f["name"])
            continue
        gid = _file_id(f.get("gdrive_id", ""))
        if not gid:
            print(f"[models] WARNING   {f['name']}: no gdrive_id in model_registry.json -> not downloaded")
            missing.append(f["name"])
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[models] download  {f['name']} -> {path.relative_to(ROOT)}")
        try:
            got = gdown.download(id=gid, output=str(path), quiet=True)
        except Exception as exc:  # network / permission / quota
            got = None
            print(f"[models] WARNING   {f['name']}: {exc}")
        if not got or not path.is_file() or (size and path.stat().st_size != size):
            have = path.stat().st_size if path.is_file() else 0
            print(f"[models] WARNING   {f['name']}: download failed or wrong size ({have} of {size} bytes). "
                  "Is the Drive file shared as 'Anyone with the link'?")
            if path.is_file():
                path.unlink()
            missing.append(f["name"])
            continue
        ok.append(f["name"])

    print(f"[models] ready: {len(ok)}  missing: {len(missing)} {missing if missing else ''}")


if __name__ == "__main__":
    main()
