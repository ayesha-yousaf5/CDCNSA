"""Lesion-segmentation severity (one model for every crop).

Model: U-Net / ResNet34 trained on PlantSeg (Zenodo 13958858), exported as TorchScript.
Severity % = lesion pixels / leaf pixels, where
    lesion = model probability > lesion_threshold   (threshold chosen on PlantSeg val)
    leaf   = excess-green leaf mask  UNION  lesion
Bands: MILD < mild_max_pct <= MODERATE < moderate_max_pct <= SEVERE.

The preprocessing, leaf mask and band rule below are copied 1:1 from the training notebook
(training/severity_template.py) so the app gives exactly the numbers that were evaluated there.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from scipy import ndimage as ndi


def letterbox(im: Image.Image, size: int, resample) -> Image.Image:
    w, h = im.size; s = size / max(w, h)
    im = im.resize((max(1, round(w * s)), max(1, round(h * s))), resample)
    canvas = Image.new(im.mode, (size, size), 0)
    canvas.paste(im, ((size - im.size[0]) // 2, (size - im.size[1]) // 2))
    return canvas


def leaf_mask(rgb: np.ndarray) -> np.ndarray:
    a = ndi.gaussian_filter(rgb.astype(np.float32) / 255.0, sigma=(2, 2, 0))
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = ndi.binary_opening((2 * g - r - b) > 0.06, iterations=2)
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=4))
    lab, n = ndi.label(m)
    if n > 1:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.flatnonzero(sizes >= 0.02 * m.size))
    return m


class LesionSeverityModel:
    def __init__(self, model_path: Path, config_path: Path, device: torch.device):
        self.cfg = json.loads(Path(config_path).read_text(encoding='utf-8'))
        self.size = int(self.cfg.get('input_size', 384))
        self.mean = torch.tensor(self.cfg.get('mean', [0.485, 0.456, 0.406]))[:, None, None]
        self.std = torch.tensor(self.cfg.get('std', [0.229, 0.224, 0.225]))[:, None, None]
        self.threshold = float(self.cfg.get('lesion_threshold', 0.5))
        self.mild_max = float(self.cfg.get('mild_max_pct', 10.0))
        self.moderate_max = float(self.cfg.get('moderate_max_pct', 30.0))
        self.device = device
        self.model = torch.jit.load(str(model_path), map_location='cpu').eval().to(device)

    def band(self, pct: float) -> str:
        return 'MILD' if pct < self.mild_max else ('MODERATE' if pct < self.moderate_max else 'SEVERE')

    @torch.inference_mode()
    def measure(self, image: Image.Image) -> dict:
        lb = letterbox(image.convert('RGB'), self.size, Image.BILINEAR)
        rgb = np.asarray(lb)
        x = torch.from_numpy(rgb.astype(np.float32) / 255.0).permute(2, 0, 1)
        x = ((x - self.mean) / self.std)[None].to(self.device)
        out = self.model(x)
        if isinstance(out, (tuple, list)): out = out[0]
        prob = out.float().sigmoid()[0, 0].cpu().numpy()
        lesion = prob > self.threshold
        leaf = leaf_mask(rgb) | lesion
        # letterbox padding is black, never counted as leaf by the excess-green rule
        leaf_px = int(leaf.sum()); lesion_px = int(lesion.sum())
        content_px = int(round(image.size[0] * image.size[1] * (self.size / max(image.size)) ** 2))
        pct = 100.0 * lesion_px / max(leaf_px, 1)
        return {'percent': round(pct, 1), 'band': self.band(pct),
                'leaf_fraction': round(leaf_px / max(content_px, 1), 4)}
