"""Download model checkpoints from Google Drive for Render deployment.

Run during build:  python download_models.py
Downloads a single models.tar.gz archive and extracts it.
"""
import subprocess
import sys
import os
import tarfile
from pathlib import Path

FILE_ID = "1FxI1eeinaTsRDAqmRa6doQrX7IrnEKgy"

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
ARCHIVE = ROOT / "models.tar.gz"


def main():
    if MODELS_DIR.exists() and any(MODELS_DIR.rglob("*.pt")):
        print("[download_models] models/ already populated, skipping download")
        return

    print(f"[download_models] Downloading models archive from Google Drive (file {FILE_ID})...")

    try:
        import gdown
    except ImportError:
        print("[download_models] gdown not installed, installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown", "-q"])
        import gdown

    url = f"https://drive.google.com/uc?id={FILE_ID}"
    result = gdown.download(url, str(ARCHIVE), quiet=False, use_cookies=False)

    if not result:
        print("[download_models] ERROR: Download failed. Check Google Drive share settings.")
        print("[download_models] The file must be shared as 'Anyone with the link' can view.")
        sys.exit(1)

    size_mb = ARCHIVE.stat().st_size / (1024 * 1024)
    print(f"[download_models] Downloaded {size_mb:.1f} MB. Extracting...")

    with tarfile.open(ARCHIVE, "r:gz") as tar:
        tar.extractall(path=ROOT)

    ARCHIVE.unlink()
    print("[download_models] Archive extracted and removed.")

    pt_files = list(MODELS_DIR.rglob("*.pt"))
    pth_files = list(MODELS_DIR.rglob("*.pth"))
    all_models = pt_files + pth_files
    print(f"[download_models] Found {len(all_models)} model files:")
    for f in all_models:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.relative_to(ROOT)} ({size_mb:.1f} MB)")

    if not all_models:
        print("[download_models] WARNING: No model files found after extraction!")
        sys.exit(1)

    print("[download_models] Models ready.")


if __name__ == "__main__":
    main()
