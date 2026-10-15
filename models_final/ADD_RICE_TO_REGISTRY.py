"""Run after you put the rice model + registry_snippet.json into models_final/rice/disease/.
Points the app's model_registry.json at the new rice model (backup is written first)."""
import json, shutil, sys
from pathlib import Path
here = Path(__file__).resolve().parent; root = here.parent
snip = here / "rice" / "disease" / "registry_snippet.json"
if not snip.is_file(): sys.exit(f"not found: {snip}")
sn = json.loads(snip.read_text(encoding="utf-8")); spec = dict(sn["disease"])
spec["checkpoint"] = spec["checkpoint"].replace("models/", "models_final/", 1)
if not (root / spec["checkpoint"]).is_file(): sys.exit(f"rice model file missing: {spec['checkpoint']}")
spec["final"] = True
reg_p = root / "model_registry.json"
shutil.copy(reg_p, root / "model_registry_BACKUP_before_rice.json")
reg = json.loads(reg_p.read_text(encoding="utf-8"))
reg["crops"]["rice"]["disease"] = spec
if "disease_threshold" in sn: reg["disease_thresholds"]["rice"] = sn["disease_threshold"]
reg_p.write_text(json.dumps(reg, indent=1, ensure_ascii=False), encoding="utf-8")
print("rice ->", spec["checkpoint"], "| classes:", list(spec.get("class_to_idx", {})))
