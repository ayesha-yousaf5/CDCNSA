"""Download model checkpoints from Google Drive for Render deployment.

Run during build:  python download_models.py

The configured Google Drive ID is a ``models.tar.gz`` archive containing
``models/<crop>/...``. After extraction, every enabled classification checkpoint
is validated for presence and protected hashes so a partial or corrupt archive
cannot silently pass a build.
"""
import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path

FILE_ID = "1-paulafZwj8obchN2kGiTRTfVQAfkwSl"

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
ARCHIVE = ROOT / "models.tar.gz"


def required_checkpoints() -> list[tuple[Path, str | None]]:
    registry = json.loads((ROOT / "model_registry.json").read_text(encoding="utf-8"))
    required: list[tuple[Path, str | None]] = []
    for tasks in registry["crops"].values():
        for spec in tasks.values():
            if spec.get("enabled") and spec.get("runtime_kind") == "classification":
                required.append((ROOT / spec["checkpoint"], spec.get("expected_sha256")))
    return required


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_issues() -> list[tuple[Path, str]]:
    issues: list[tuple[Path, str]] = []
    for path, expected in required_checkpoints():
        if not path.is_file():
            issues.append((path, "missing"))
        elif expected and sha256(path) != expected:
            issues.append((path, "sha256_mismatch"))
    return issues


def extract_archive_safely(archive_path: Path) -> None:
    root = ROOT.resolve()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            target = (ROOT / member.name).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"Unsafe archive path: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"Archive links are not allowed: {member.name}")
        archive.extractall(path=ROOT)


def main():
    issues_before = checkpoint_issues()
    if not issues_before:
        print("[download_models] All enabled classification checkpoints are present and protected hashes match; skipping download")
        return

    print(
        f"[download_models] {len(issues_before)} enabled checkpoint issue(s); "
        f"downloading Google Drive archive {FILE_ID}..."
    )
    for path, reason in issues_before:
        print(f"  {path.relative_to(ROOT)}: {reason}")

    try:
        import gdown
    except ImportError:
        print("[download_models] gdown not installed, installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown", "-q"])
        import gdown

    url = f"https://drive.google.com/uc?id={FILE_ID}"
    result = gdown.download(
        url,
        output=str(ARCHIVE),
        quiet=False,
        use_cookies=False,
        resume=True,
    )

    if not result:
        print("[download_models] ERROR: Archive download failed.")
        print("[download_models] Share the file as 'Anyone with the link' can view.")
        raise SystemExit(1)

    size_mb = ARCHIVE.stat().st_size / (1024 * 1024)
    print(f"[download_models] Downloaded {size_mb:.1f} MB. Extracting...")
    extract_archive_safely(ARCHIVE)
    ARCHIVE.unlink()

    pt_files = list(MODELS_DIR.rglob("*.pt"))
    pth_files = list(MODELS_DIR.rglob("*.pth"))
    all_models = pt_files + pth_files
    print(f"[download_models] Found {len(all_models)} model files:")
    for f in all_models:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.relative_to(ROOT)} ({size_mb:.1f} MB)")

    issues_after = checkpoint_issues()
    if issues_after:
        print("[download_models] ERROR: Download completed but required checkpoints are missing or invalid:")
        for path, reason in issues_after:
            print(f"  {path.relative_to(ROOT)}: {reason}")
        raise SystemExit(1)

    print("[download_models] All enabled classification checkpoints are ready.")


if __name__ == "__main__":
    main()
