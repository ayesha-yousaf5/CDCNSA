"""Audit CDCNSA checkpoint contracts, OOD behavior, and endpoint parity.

Examples
--------
Run checkpoint metadata and synthetic out-of-distribution probes::

    python tools/runtime_parity_auditor.py --crops apple corn cotton tomato peas

Compare labeled images with both the local runtime and a running website::

    python tools/runtime_parity_auditor.py \
        --samples-csv parity_samples.csv \
        --endpoint http://127.0.0.1:8000 \
        --json-out parity_report.json

The sample CSV requires ``crop,image,expected_disease`` columns. Optional
columns are ``expected_severity`` and ``source``. Image paths are resolved
relative to the CSV file.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import mimetypes
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inference.preprocess import transform_for  # noqa: E402
from inference.runtime import ModelRuntime, canonical_crop, display_label  # noqa: E402


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".heif"}


def normalize_architecture(value: Any) -> str:
    value = str(value or "").lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "mobilenetv3": "mobilenet_v3_large",
        "mobilenet_v3": "mobilenet_v3_large",
        "mobilenetv3_large": "mobilenet_v3_large",
        "mobilenetv3_large_": "mobilenet_v3_large",
    }
    return aliases.get(value, value)


def checkpoint_mapping(meta: dict[str, Any]) -> dict[str, int] | None:
    for key in ("class_to_idx", "class_mapping", "severity_to_idx"):
        value = meta.get(key)
        if isinstance(value, dict):
            return {str(label): int(index) for label, index in value.items()}
    for key in ("class_order", "severity_classes", "classes"):
        value = meta.get(key)
        if isinstance(value, (list, tuple)):
            return {str(label): index for index, label in enumerate(value)}
    return None


def first_meta(meta: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in meta:
            return meta[key]
    return None


def nearly_equal_list(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return True
    try:
        return len(left) == len(right) and all(math.isclose(float(a), float(b), abs_tol=1e-9) for a, b in zip(left, right))
    except (TypeError, ValueError):
        return False


def contract_audit(runtime: ModelRuntime, crop: str, task: str) -> dict[str, Any]:
    spec = runtime.registry.task(crop, task)
    path = runtime.registry.checkpoint_path(spec)
    result: dict[str, Any] = {
        "crop": crop,
        "task": task,
        "enabled": bool(spec.get("enabled")),
        "checkpoint": str(path.relative_to(ROOT)),
        "present": path.is_file(),
        "issues": [],
    }
    if not result["enabled"] or spec.get("runtime_kind") != "classification":
        result["skipped"] = True
        return result
    if not path.is_file():
        result["issues"].append("checkpoint_missing")
        return result

    try:
        loaded = runtime.load(crop, task)
    except Exception as exc:  # a diagnostic tool should report every crop
        result["issues"].append(f"load_failed: {exc}")
        return result

    meta = loaded["meta"]
    result.update(
        {
            "loadable": True,
            "actual_sha256": runtime.registry.sha256(path),
            "architecture": loaded["architecture"],
            "classes": loaded["classes"],
        }
    )
    if not spec.get("expected_sha256"):
        result["issues"].append("checkpoint_hash_unprotected")

    meta_arch = first_meta(meta, "backbone", "architecture", "model_name")
    if meta_arch and normalize_architecture(meta_arch) != normalize_architecture(spec.get("architecture")):
        result["issues"].append(
            f"architecture_mismatch: registry={spec.get('architecture')} checkpoint={meta_arch}"
        )

    meta_mapping = checkpoint_mapping(meta)
    registry_mapping = {str(k): int(v) for k, v in (spec.get("class_to_idx") or {}).items()}
    if meta_mapping and meta_mapping != registry_mapping:
        result["issues"].append("class_mapping_mismatch")

    meta_size = first_meta(meta, "image_size", "input_size")
    if meta_size is not None and int(meta_size) != int(spec["image_size"]):
        result["issues"].append(
            f"image_size_mismatch: registry={spec['image_size']} checkpoint={meta_size}"
        )

    meta_mean = first_meta(meta, "imagenet_mean", "normalization_mean")
    meta_std = first_meta(meta, "imagenet_std", "normalization_std")
    if not nearly_equal_list(meta_mean, spec.get("normalization_mean")):
        result["issues"].append("normalization_mean_mismatch")
    if not nearly_equal_list(meta_std, spec.get("normalization_std")):
        result["issues"].append("normalization_std_mismatch")

    size = int(spec["image_size"])
    with torch.inference_mode():
        logits = loaded["model"](torch.zeros(1, 3, size, size, device=runtime.device))
    result["dummy_output_shape"] = list(logits.shape)
    if tuple(logits.shape) != (1, len(loaded["classes"])):
        result["issues"].append("unexpected_output_shape")
    return result


def ood_images() -> dict[str, Image.Image]:
    rng = np.random.default_rng(42)
    return {
        "flat_white": Image.new("RGB", (640, 480), "white"),
        "flat_gray": Image.new("RGB", (640, 480), (127, 127, 127)),
        "flat_black": Image.new("RGB", (640, 480), "black"),
        "flat_green": Image.new("RGB", (640, 480), (30, 130, 40)),
        "random_noise": Image.fromarray(rng.integers(0, 256, (480, 640, 3), dtype=np.uint8)),
    }


def local_prediction(runtime: ModelRuntime, crop: str, image: Image.Image, task: str = "disease") -> dict[str, Any]:
    loaded = runtime.load(crop, task)
    tensor = transform_for(loaded["spec"])(image).unsqueeze(0).to(runtime.device)
    with torch.inference_mode():
        probabilities = torch.softmax(loaded["model"](tensor), dim=1)[0]
    values, indices = torch.topk(probabilities, min(3, len(probabilities)))
    top = [
        {"label": display_label(loaded["classes"][int(index)]), "confidence": round(float(value), 6)}
        for value, index in zip(values, indices)
    ]
    return {"label": top[0]["label"], "confidence": top[0]["confidence"], "top3": top}


def ood_audit(runtime: ModelRuntime, crop: str) -> list[dict[str, Any]]:
    threshold = float(runtime.registry.data.get("disease_confidence_threshold", 0.55))
    rows = []
    for probe, image in ood_images().items():
        prediction = local_prediction(runtime, crop, image)
        runtime_decision = runtime.diagnose(crop, image_to_jpeg(image))
        rows.append(
            {
                "crop": crop,
                "probe": probe,
                **prediction,
                "threshold": threshold,
                "classifier_threshold_accepts": prediction["confidence"] >= threshold,
                "runtime_decision": runtime_decision,
                "incorrectly_accepted": not bool(runtime_decision.get("uncertain")),
            }
        )
    return rows


def image_to_jpeg(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def endpoint_diagnose(endpoint: str, crop: str, payload: bytes, filename: str, mime: str) -> dict[str, Any]:
    boundary = f"----CDCNSAAudit{uuid.uuid4().hex}"
    chunks = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"crop\"\r\n\r\n{crop}\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\nen\r\n".encode(),
        (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
            f"filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n"
        ).encode(),
        payload,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    request = Request(
        f"{endpoint.rstrip('/')}/api/diagnose",
        data=b"".join(chunks),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"endpoint HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc
    except URLError as exc:
        raise RuntimeError(f"endpoint unavailable: {exc.reason}") from exc


def normalized_label(value: Any) -> str:
    value = str(value or "").split(" / ", 1)[-1]
    return " ".join(value.lower().replace("_", " ").replace("-", " ").split())


def load_samples(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    required = {"crop", "image", "expected_disease"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Sample CSV must contain crop,image,expected_disease columns")
    return rows


def sample_audit(runtime: ModelRuntime, csv_path: Path, endpoint: str | None) -> list[dict[str, Any]]:
    results = []
    for row_number, row in enumerate(load_samples(csv_path), start=2):
        crop = canonical_crop(row["crop"])
        image_path = (csv_path.parent / row["image"]).resolve()
        result: dict[str, Any] = {
            "row": row_number,
            "crop": crop,
            "image": str(image_path),
            "source": row.get("source", ""),
            "expected_disease": row["expected_disease"],
        }
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS or not image_path.is_file():
            result["error"] = "image_missing_or_unsupported"
            results.append(result)
            continue

        payload = image_path.read_bytes()
        with Image.open(io.BytesIO(payload)) as opened:
            image = opened.convert("RGB").copy()
        local = local_prediction(runtime, crop, image)
        result["local"] = local
        result["local_disease_correct"] = normalized_label(local["label"]) == normalized_label(row["expected_disease"])

        local_diagnosis = runtime.diagnose(crop, payload)
        result["local_diagnosis"] = local_diagnosis
        expected_severity = row.get("expected_severity", "").strip()
        if expected_severity:
            result["expected_severity"] = expected_severity
            result["local_severity_correct"] = normalized_label(local_diagnosis.get("severity")) == normalized_label(expected_severity)

        if endpoint:
            mime = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
            try:
                remote = endpoint_diagnose(endpoint, crop, payload, image_path.name, mime)
                result["endpoint"] = remote
                result["runtime_endpoint_disease_parity"] = (
                    normalized_label(remote.get("disease")) == normalized_label(local_diagnosis.get("disease"))
                    and math.isclose(float(remote.get("confidence", -1)), float(local_diagnosis.get("confidence", -2)), abs_tol=1e-5)
                )
                result["runtime_endpoint_severity_parity"] = (
                    normalized_label(remote.get("severity")) == normalized_label(local_diagnosis.get("severity"))
                )
            except Exception as exc:
                result["endpoint_error"] = str(exc)
        results.append(result)
    return results


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    contracts = report["contracts"]
    ood = report["ood_probes"]
    samples = report["samples"]
    return {
        "contract_issue_count": sum(len(item.get("issues", [])) for item in contracts),
        "missing_checkpoint_count": sum("checkpoint_missing" in item.get("issues", []) for item in contracts),
        "ood_incorrectly_accepted": sum(bool(item.get("incorrectly_accepted")) for item in ood),
        "ood_classifier_threshold_accepts": sum(bool(item.get("classifier_threshold_accepts")) for item in ood),
        "labeled_samples": len(samples),
        "local_disease_correct": sum(bool(item.get("local_disease_correct")) for item in samples),
        "endpoint_parity_failures": sum(
            item.get("runtime_endpoint_disease_parity") is False
            or item.get("runtime_endpoint_severity_parity") is False
            for item in samples
        ),
        "sample_errors": sum("error" in item or "endpoint_error" in item for item in samples),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crops", nargs="*", help="Crop IDs to audit; defaults to every registered crop")
    parser.add_argument("--samples-csv", type=Path, help="Labeled parity sample manifest")
    parser.add_argument("--endpoint", help="Optional website base URL for local-vs-deployed parity")
    parser.add_argument("--json-out", type=Path, help="Optional path for the complete JSON report")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when critical failures are found")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime = ModelRuntime(ROOT)
    crops = [canonical_crop(crop) for crop in (args.crops or runtime.registry.crops.keys())]
    unknown = [crop for crop in crops if crop not in runtime.registry.crops]
    if unknown:
        raise SystemExit(f"Unknown crop(s): {', '.join(unknown)}")

    contracts = []
    ood = []
    for crop in crops:
        for task in ("disease", "severity"):
            contracts.append(contract_audit(runtime, crop, task))
        disease_spec = runtime.registry.task(crop, "disease")
        if disease_spec.get("enabled") and runtime.registry.checkpoint_path(disease_spec).is_file():
            try:
                ood.extend(ood_audit(runtime, crop))
            except Exception as exc:
                ood.append({"crop": crop, "error": str(exc)})

    samples = sample_audit(runtime, args.samples_csv.resolve(), args.endpoint) if args.samples_csv else []
    report = {
        "device": str(runtime.device),
        "endpoint": args.endpoint,
        "contracts": contracts,
        "ood_probes": ood,
        "samples": samples,
    }
    report["summary"] = summarize(report)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    critical = (
        report["summary"]["missing_checkpoint_count"]
        + report["summary"]["ood_incorrectly_accepted"]
        + report["summary"]["endpoint_parity_failures"]
        + report["summary"]["sample_errors"]
    )
    return 1 if args.strict and critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
