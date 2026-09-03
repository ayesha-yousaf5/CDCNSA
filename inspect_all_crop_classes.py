from pathlib import Path
import json
import re

try:
    import torch
except ImportError:
    torch = None


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(".").resolve()

CROPS = {
    "apple": ["apple"],
    "corn": ["corn", "maize"],
    "cotton": ["cotton"],
    "tomato": ["tomato"],
    "rice": ["rice"],
    "mango": ["mango"],
    "grape": ["grape"],
    "eggplant": ["eggplant", "brinjal"],
    "cucumber": ["cucumber"],
    "peas": ["peas", "pea"],
    "lemon": ["lemon"],
    "soybean": ["soybean", "soy"],
}


KEYS_TO_FIND = {
    "class_to_idx",
    "idx_to_class",
    "classes",
    "class_names",
    "labels",
    "disease_classes",
    "severity_classes",
    "disease_labels",
    "severity_labels",
    "label_map",
    "class_map",
}


# ============================================================
# HELPERS
# ============================================================

def detect_crop(path):
    text = str(path).lower().replace("\\", "/")

    for crop, aliases in CROPS.items():
        for alias in aliases:
            pattern = rf"(^|[/_.\-]){re.escape(alias)}([/_.\-]|$)"
            if re.search(pattern, text):
                return crop

    return None


def normalize_mapping(value):
    """
    Convert common class mapping formats into a readable list.
    """

    if isinstance(value, list):
        return [str(x) for x in value]

    if isinstance(value, tuple):
        return [str(x) for x in value]

    if isinstance(value, dict):

        # class -> index
        if value and all(
            isinstance(v, int) for v in value.values()
        ):
            try:
                return [
                    k for k, v in
                    sorted(value.items(), key=lambda x: x[1])
                ]
            except Exception:
                return value

        # index -> class
        try:
            numeric_keys = all(
                str(k).isdigit() for k in value.keys()
            )

            if numeric_keys:
                return [
                    str(v) for k, v in
                    sorted(
                        value.items(),
                        key=lambda x: int(x[0])
                    )
                ]
        except Exception:
            pass

        return value

    return value


def search_object(obj, source, crop, found, prefix=""):
    """
    Recursively search dictionaries/checkpoints for class mappings.
    """

    if isinstance(obj, dict):

        for key, value in obj.items():

            key_str = str(key)
            key_lower = key_str.lower()

            full_key = (
                f"{prefix}.{key_str}"
                if prefix
                else key_str
            )

            if key_lower in KEYS_TO_FIND:

                cleaned = normalize_mapping(value)

                found.append({
                    "crop": crop,
                    "source": str(source),
                    "key": full_key,
                    "value": cleaned
                })

            if isinstance(value, (dict, list, tuple)):
                search_object(
                    value,
                    source,
                    crop,
                    found,
                    full_key
                )

    elif isinstance(obj, (list, tuple)):

        for i, value in enumerate(obj):

            if isinstance(value, (dict, list, tuple)):
                search_object(
                    value,
                    source,
                    crop,
                    found,
                    f"{prefix}[{i}]"
                )


# ============================================================
# JSON SEARCH
# ============================================================

def inspect_json(path, crop, found):

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        search_object(
            data,
            path,
            crop,
            found
        )

    except Exception:
        pass


# ============================================================
# PYTHON / TEXT SEARCH
# ============================================================

TEXT_PATTERNS = [
    r"class_to_idx\s*=\s*(\{.*?\})",
    r"classes\s*=\s*(\[.*?\])",
    r"class_names\s*=\s*(\[.*?\])",
    r"disease_classes\s*=\s*(\[.*?\])",
    r"severity_classes\s*=\s*(\[.*?\])",
]


def inspect_text(path, crop, found):

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        for pattern in TEXT_PATTERNS:

            matches = re.findall(
                pattern,
                text,
                flags=re.DOTALL | re.IGNORECASE
            )

            for match in matches:

                # Don't dump enormous blocks
                if len(match) > 3000:
                    continue

                found.append({
                    "crop": crop,
                    "source": str(path),
                    "key": "text_match",
                    "value": match.strip()
                })

    except Exception:
        pass


# ============================================================
# PYTORCH CHECKPOINT SEARCH
# ============================================================

def inspect_checkpoint(path, crop, found):

    if torch is None:
        return

    try:

        # Safe mode first
        try:
            checkpoint = torch.load(
                path,
                map_location="cpu",
                weights_only=True
            )

        except Exception:
            # Use only because these should be YOUR trusted model files
            checkpoint = torch.load(
                path,
                map_location="cpu",
                weights_only=False
            )

        search_object(
            checkpoint,
            path,
            crop,
            found
        )

    except Exception as e:

        print(
            f"[checkpoint skipped] "
            f"{path.name}: {str(e)[:100]}"
        )


# ============================================================
# SCAN PROJECT
# ============================================================

found = []

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
}


print("=" * 90)
print("CCNSA — EXACT MODEL CLASS AUDIT")
print("=" * 90)
print("Project root:", ROOT)


files = []

for path in ROOT.rglob("*"):

    if not path.is_file():
        continue

    if any(part.lower() in IGNORE_DIRS for part in path.parts):
        continue

    files.append(path)


print("Files scanned:", len(files))


for path in files:

    crop = detect_crop(path)

    suffix = path.suffix.lower()

    if suffix == ".json":
        inspect_json(
            path,
            crop,
            found
        )

    elif suffix in {
        ".py",
        ".txt",
        ".yaml",
        ".yml",
        ".md"
    }:
        inspect_text(
            path,
            crop,
            found
        )

    elif suffix in {
        ".pth",
        ".pt",
        ".ckpt"
    }:
        inspect_checkpoint(
            path,
            crop,
            found
        )


# ============================================================
# PRINT REPORT
# ============================================================

print("\n")
print("=" * 90)
print("DISCOVERED CLASS INFORMATION")
print("=" * 90)


for crop_name in CROPS:

    crop_results = [
        x for x in found
        if x["crop"] == crop_name
    ]

    print("\n" + "=" * 90)
    print(crop_name.upper())
    print("=" * 90)

    if not crop_results:

        print("No explicit class mapping discovered.")
        continue

    seen = set()

    for result in crop_results:

        fingerprint = repr(result["value"])

        if fingerprint in seen:
            continue

        seen.add(fingerprint)

        print("\nSOURCE:")
        print(result["source"])

        print("KEY:")
        print(result["key"])

        print("VALUE:")

        value = result["value"]

        if isinstance(value, list):

            for i, class_name in enumerate(value):
                print(
                    f"  [{i}] {class_name}"
                )

        else:
            print(value)


# Anything that had labels but crop could not be inferred
unknown = [
    x for x in found
    if x["crop"] is None
]

if unknown:

    print("\n")
    print("=" * 90)
    print("UNASSIGNED / GLOBAL CLASS DEFINITIONS")
    print("=" * 90)

    seen = set()

    for result in unknown:

        fingerprint = (
            result["source"],
            repr(result["value"])
        )

        if fingerprint in seen:
            continue

        seen.add(fingerprint)

        print("\nSOURCE:")
        print(result["source"])

        print("KEY:")
        print(result["key"])

        print("VALUE:")
        print(result["value"])


# ============================================================
# SAVE MACHINE-READABLE REPORT
# ============================================================

output_file = ROOT / "all_crop_class_audit.json"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        found,
        f,
        indent=2,
        ensure_ascii=False,
        default=str
    )


print("\n" + "=" * 90)
print("DONE")
print("=" * 90)

print(
    "Full audit saved to:",
    output_file
)