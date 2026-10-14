"""Compare the shared (combined) model against the crop-specific models on labeled images.

Usage (Windows PowerShell, from the project folder):

    python tools\\compare_models.py ^
        --models-root "D:\\hacathon\\website deployment\\CDCNSA" ^
        --combined-dir "D:\\CDCNSA-main\\CDCNSA-main\\combined_models\\models\\combined" ^
        --extra-root "D:\\CDCNSA-main\\CDCNSA-main\\brinjal_cucumber_models" ^
        --images "D:\\hacathon\\website deployment\\CCNSA_Diagnostic_Image_Pack\\CCNSA_Diagnostic_Image_Pack\\CCNSA_Diagnostic_Images"

Image folder layout: <images>/<crop>/<Disease_Name>.jpg  (file name = true label;
"healthy" for healthy leaves). Any extra suffix like "_2" is ignored.

Writes model_comparison.csv and model_comparison_summary.json next to this script
and prints a per-crop accuracy table for each model/preprocessing variant.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import torch
from torch.nn import functional as F
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inference.architectures import build_classifier  # noqa: E402
from inference.preprocess import decode_rgb  # noqa: E402

ARCH_ALIASES = {
    'efficientnetb0': 'efficientnet_b0', 'efficientnet_b0': 'efficientnet_b0',
    'mobilenetv3_large': 'mobilenet_v3_large', 'mobilenet_v3_large': 'mobilenet_v3_large',
    'mobilenet_v3': 'mobilenet_v3_large', 'mobilenetv3': 'mobilenet_v3_large',
    'resnet50': 'resnet50', 'resnet18': 'resnet18', 'densenet121': 'densenet121',
}
IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic'}
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
TRANSFORMS = {
    'squash224': transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(MEAN, STD)]),
    'crop256_224': transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize(MEAN, STD)]),
}


def norm(label: str) -> str:
    label = str(label)
    if '|' in label:
        label = label.split('|', 1)[1]
    if ' / ' in label:
        label = label.split(' / ', 1)[1]
    return re.sub(r'[^a-z0-9]', '', label.lower())


def true_label(path: Path) -> str:
    stem = re.sub(r'[_\- ]\(?\d+\)?$', '', path.stem)  # drop "_2", " (1)" suffixes
    return stem


def load_checkpoint(path: Path, spec: dict | None = None):
    obj = torch.load(path, map_location='cpu', weights_only=False)
    if not isinstance(obj, dict):
        raise RuntimeError(f'{path.name}: not a dict checkpoint')
    meta = obj
    sd = None
    for key in ('model_state_dict', 'state_dict', 'model'):
        if isinstance(obj.get(key), dict):
            sd = obj[key]
            break
    if sd is None and all(torch.is_tensor(v) for v in obj.values()):
        sd, meta = obj, {}
    sd = {k[7:] if k.startswith('module.') else k: v for k, v in sd.items()}
    spec = spec or {}
    c2i = meta.get('class_to_idx') or meta.get('class_mapping') or meta.get('severity_to_idx') or spec.get('class_to_idx')
    if not c2i:
        for k in ('class_order', 'severity_classes', 'classes'):
            if meta.get(k):
                c2i = {c: i for i, c in enumerate(meta[k])}
                break
    classes = [c for c, _ in sorted(c2i.items(), key=lambda kv: kv[1])]
    arch = (meta.get('backbone') or meta.get('architecture') or meta.get('model_name') or spec.get('architecture') or '')
    arch = ARCH_ALIASES.get(arch.lower().replace('-', '_'), arch.lower().replace('-', '_'))
    model = build_classifier(arch, len(classes))
    model.load_state_dict(sd, strict=True)
    model.eval()
    extra = {k: meta.get(k) for k in ('val_acc', 'val_macro_f1', 'best_epoch', 'image_size', 'input_size') if k in meta}
    extra = {k: (float(v) if torch.is_tensor(v) else v) for k, v in extra.items()}
    return model, classes, arch, extra


@torch.inference_mode()
def predict(model, classes, image, tf, keep_prefix: str | None = None):
    probs = F.softmax(model(tf(image).unsqueeze(0)), dim=1)[0]
    idx_list = list(range(len(classes)))
    if keep_prefix is not None:
        idx_list = [i for i, c in enumerate(classes) if c.startswith(keep_prefix)]
        if not idx_list:
            return None, 0.0, 0.0
    sub = probs[idx_list]
    raw_top = float(sub.max())  # probability mass before renormalisation
    sub = sub / sub.sum()
    vals, inds = torch.topk(sub, min(2, len(sub)))
    best = classes[idx_list[int(inds[0])]]
    return best, float(vals[0]), raw_top


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--models-root', required=True, help='Folder that contains models/<crop>/<task>/...')
    ap.add_argument('--combined-dir', required=True, help='Folder with disease_model.pt and severity_model.pt')
    ap.add_argument('--extra-root', default=None, help='Optional second root with models/ (e.g. brinjal_cucumber_models)')
    ap.add_argument('--images', required=True)
    ap.add_argument('--registry', default=str(ROOT / 'model_registry.json'))
    ap.add_argument('--candidate', action='append', default=[],
                    help='Extra checkpoint to test: crop=path (repeatable), e.g. tomato=D:\\x\\tomato_robust.pt')
    args = ap.parse_args()
    candidates = {}
    for item in args.candidate:
        crop_name, _, cpath = item.partition('=')
        candidates.setdefault(crop_name.strip().lower(), []).append(Path(cpath.strip().strip('"')))

    registry = json.loads(Path(args.registry).read_text(encoding='utf-8'))
    roots = [Path(args.models_root)] + ([Path(args.extra_root)] if args.extra_root else [])
    combined_spec = registry.get('combined_models', {}).get('disease', {})
    combined_crops = set(combined_spec.get('crops', []))

    print('Loading combined disease model ...')
    comb_model, comb_classes, comb_arch, comb_meta = load_checkpoint(Path(args.combined_dir) / 'disease_model.pt')
    print(f'  combined: {comb_arch}, {len(comb_classes)} classes, meta={comb_meta}')
    prefixes = sorted({c.split('|', 1)[0] for c in comb_classes if '|' in c})
    print(f'  crop prefixes inside combined model: {prefixes}')
    print('  ALL combined classes:')
    for i, c in enumerate(comb_classes):
        print(f'    {i:3d} {c}')

    rows = []
    images_root = Path(args.images)
    for crop_dir in sorted(p for p in images_root.iterdir() if p.is_dir()):
        crop = crop_dir.name.lower()
        if crop in ('maize',):
            crop = 'corn'
        if crop in ('brinjal',):
            crop = 'eggplant'
        files = sorted(p for p in crop_dir.iterdir() if p.suffix.lower() in IMAGE_EXT)
        if not files:
            continue
        # crop-specific model
        spec = registry['crops'].get(crop, {}).get('disease')
        own = None
        if spec:
            for r in roots:
                p = r / spec['checkpoint']
                if p.is_file():
                    try:
                        own = load_checkpoint(p, spec)
                        print(f'[{crop}] own model {p.name}: {own[2]}, classes={own[1]}, meta={own[3]}')
                    except Exception as exc:  # noqa: BLE001
                        print(f'[{crop}] own model FAILED to load: {exc}')
                    break
            else:
                print(f'[{crop}] own model checkpoint not found: {spec["checkpoint"]}')
        cand_models = []
        for cpath in candidates.get(crop, []):
            try:
                cm = load_checkpoint(cpath, spec)
                cand_models.append((cpath.stem, cm))
                print(f'[{crop}] candidate {cpath.name}: {cm[2]}, classes={cm[1]}, meta={cm[3]}')
            except Exception as exc:  # noqa: BLE001
                print(f'[{crop}] candidate {cpath} FAILED to load: {exc}')
        prefix = {'corn': 'Corn|', 'pepper': 'Pepper Chilli|'}.get(crop, f'{crop.title()}|')
        comb_for_crop = [c for c in comb_classes if c.startswith(prefix)]
        print(f'[{crop}] combined classes kept with prefix {prefix!r}: {comb_for_crop}')
        for f in files:
            try:
                img = decode_rgb(f.read_bytes())
            except Exception as exc:  # noqa: BLE001
                print(f'  skip {f.name}: {exc}')
                continue
            truth = true_label(f)
            row = {'crop': crop, 'image': f.name, 'truth': truth}
            for tname, tf in TRANSFORMS.items():
                if own:
                    lab, conf, _ = predict(own[0], own[1], img, tf)
                    row[f'own_{tname}'] = lab
                    row[f'own_{tname}_conf'] = round(conf, 3)
                    row[f'own_{tname}_ok'] = norm(lab) == norm(truth)
                for cname, cm in cand_models:
                    lab, conf, _ = predict(cm[0], cm[1], img, tf)
                    row[f'cand:{cname}_{tname}'] = lab
                    row[f'cand:{cname}_{tname}_conf'] = round(conf, 3)
                    row[f'cand:{cname}_{tname}_ok'] = norm(lab) == norm(truth)
                if crop in combined_crops and comb_for_crop:
                    lab, conf, raw = predict(comb_model, comb_classes, img, tf, keep_prefix=prefix)
                    row[f'comb_{tname}'] = lab
                    row[f'comb_{tname}_conf'] = round(conf, 3)
                    row[f'comb_{tname}_rawmass'] = round(raw, 3)
                    row[f'comb_{tname}_ok'] = norm(lab) == norm(truth)
                    # what the combined model says without crop filtering
                    lab2, conf2, _ = predict(comb_model, comb_classes, img, tf)
                    row[f'comb_{tname}_unfiltered'] = lab2
            rows.append(row)
            print('  ' + ' | '.join(f'{k}={v}' for k, v in row.items() if not k.endswith('_ok')))

    out = Path(__file__).resolve().parent
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ('crop', 'image', 'truth'), k))
    with (out / 'model_comparison.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    summary = {}
    print('\nAccuracy per crop (correct/total) for each model + preprocessing:')
    for crop in sorted({r['crop'] for r in rows}):
        rs = [r for r in rows if r['crop'] == crop]
        variants = sorted({k[:-3] for r in rs for k in r if k.endswith('_ok')})
        summary[crop] = {}
        print(f'  {crop}:')
        for v in variants:
            vals = [r[f'{v}_ok'] for r in rs if f'{v}_ok' in r]
            summary[crop][v] = f'{sum(vals)}/{len(vals)}'
            print(f'      {v:60s} {summary[crop][v]}')
    summary['_combined_classes'] = comb_classes
    (out / 'model_comparison_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f'\nWrote {out / "model_comparison.csv"} and model_comparison_summary.json')


if __name__ == '__main__':
    main()
