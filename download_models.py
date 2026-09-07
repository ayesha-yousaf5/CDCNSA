"""Download the model archives from Google Drive for Render deployment."""
import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path

ARCHIVE_IDS = {
    "brinjal_cucumber_models.tar.gz": "1ow6SCPK9o4NRdL8-b21s4xzenJ6l5AzZ",
    "combined_models.tar.gz": "10lXq0GCMxNqTRM7vaTbYP_bi0yELy3UK",
}

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
def required_checkpoints() -> list[tuple[Path, str | None]]:
    registry = json.loads((ROOT / "model_registry.json").read_text(encoding="utf-8"))
    combined_crops = {
        crop
        for spec in registry.get("combined_models", {}).values()
        for crop in spec.get("crops", [])
    }
    required: list[tuple[Path, str | None]] = []
    for crop, tasks in registry["crops"].items():
        for spec in tasks.values():
            if (
                spec.get("enabled")
                and spec.get("runtime_kind") == "classification"
                and crop not in combined_crops
            ):
                required.append((ROOT / spec["checkpoint"], spec.get("expected_sha256")))
    return required


def required_combined_checkpoints() -> list[Path]:
    registry = json.loads((ROOT / "model_registry.json").read_text(encoding="utf-8"))
    return [
        ROOT / spec["checkpoint"]
        for spec in registry.get("combined_models", {}).values()
        if spec.get("enabled")
    ]


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


def combined_checkpoint_issues() -> list[Path]:
    return [path for path in required_combined_checkpoints() if not path.is_file()]


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


def download_archive(gdown, filename: str, file_id: str) -> None:
    archive = ROOT / filename
    if archive.is_file():
        return
    print(f"[download_models] Downloading {filename}...")
    result = gdown.download(
        f"https://drive.google.com/uc?id={file_id}",
        output=str(archive),
        quiet=False,
        use_cookies=False,
        resume=True,
    )
    if not result:
        raise SystemExit(f"[download_models] Archive download failed: {filename}")
    print(f"[download_models] Extracting {filename}...")
    extract_archive_safely(archive)
    archive.unlink()


def main():
    try:
        import gdown
    except ImportError:
        print("[download_models] gdown not installed, installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown", "-q"])
        import gdown
    for filename, file_id in ARCHIVE_IDS.items():
        download_archive(gdown, filename, file_id)

    pt_files = list(MODELS_DIR.rglob("*.pt"))
    pth_files = list(MODELS_DIR.rglob("*.pth"))
    all_models = pt_files + pth_files
    print(f"[download_models] Found {len(all_models)} model files:")
    for f in all_models:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.relative_to(ROOT)} ({size_mb:.1f} MB)")

    issues_after = checkpoint_issues()
    combined_issues = combined_checkpoint_issues()
    if issues_after or combined_issues:
        print("[download_models] ERROR: Download completed but required checkpoints are missing or invalid:")
        for path, reason in issues_after:
            print(f"  {path.relative_to(ROOT)}: {reason}")
        for path in combined_issues:
            print(f"  {path.relative_to(ROOT)}: missing")
        raise SystemExit(1)

    print("[download_models] All enabled classification checkpoints are ready.")


if __name__ == "__main__":
    main()
