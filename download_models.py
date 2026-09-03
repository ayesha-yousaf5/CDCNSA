"""Download model checkpoints from Google Drive for Render deployment.

Run during build:  python download_models.py
Uses gdown to fetch the full models/ folder from a shared Google Drive link.
"""
import subprocess
import sys
import os
from pathlib import Path

FOLDER_ID = "1FxI1eeinaTsRDAqmRa6doQrX7IrnEKgy"
FOLDER_URL = f"https://drive.google.com/drive/folders/{FOLDER_ID}"

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"


def main():
    if MODELS_DIR.exists() and any(MODELS_DIR.rglob("*.pt")):
        print("[download_models] models/ already populated, skipping download")
        return

    print(f"[download_models] Downloading models from Google Drive folder {FOLDER_ID}...")

    try:
        import gdown
    except ImportError:
        print("[download_models] gdown not installed, installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown", "-q"])
        import gdown

    os.makedirs(MODELS_DIR, exist_ok=True)

    gdown.download_folder(
        FOLDER_URL,
        output=str(MODELS_DIR),
        quiet=False,
        use_cookies=False,
    )

    # Handle case where Google Drive folder contained a nested "models" subfolder
    nested_models = MODELS_DIR / "models"
    if nested_models.exists() and nested_models.is_dir():
        print("[download_models] Found nested models/ folder, flattening...")
        import shutil
        for item in nested_models.iterdir():
            dest = MODELS_DIR / item.name
            if dest.exists():
                shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
            shutil.move(str(item), str(dest))
        nested_models.rmdir()

    pt_files = list(MODELS_DIR.rglob("*.pt"))
    print(f"[download_models] Download complete. Found {len(pt_files)} .pt files:")
    for f in pt_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.relative_to(ROOT)} ({size_mb:.1f} MB)")

    if not pt_files:
        print("[download_models] WARNING: No .pt files found! Check Google Drive share settings.")
        sys.exit(1)


if __name__ == "__main__":
    main()
