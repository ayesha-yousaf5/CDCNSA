"""Cucumber's training run calibrated its confidence to temperature 0.05 (the lower limit) - that makes every
answer ~100% confident, so the app's "uncertain" gate never fires (Kazakhstan test: diseased leaves called healthy
with full confidence). This undoes that scaling (back to the raw model, temperature 1.0). Safe to run twice."""
import sys
from pathlib import Path
import torch
p = Path(__file__).resolve().parent / "cucumber" / "disease" / "cucumber_disease_resnet50_srcsplit.pt"
if not p.exists():
    sys.exit(f"not found: {p}")
ck = torch.load(p, map_location="cpu", weights_only=False)
if ck.get("temperature_fix_applied"):
    print("cucumber: temperature fix already applied"); sys.exit(0)
T = float(ck.get("temperature_baked", 1.0))
sd = ck["model_state_dict"]
sd["fc.weight"] = sd["fc.weight"] * T
sd["fc.bias"] = sd["fc.bias"] * T
ck["temperature_baked"] = 1.0
ck["temperature_fix_applied"] = f"undid baked temperature {T}"
torch.save(ck, p)
print(f"cucumber: undid baked temperature {T} -> 1.0, saved {p.name}")
