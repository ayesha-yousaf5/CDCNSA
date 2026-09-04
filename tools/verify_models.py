from __future__ import annotations
import json, os, sys
from pathlib import Path
import torch
ROOT=Path(__file__).resolve().parents[1]
MODEL_ROOT=Path(os.getenv("CDCNSA_MODEL_ROOT", str(ROOT))).expanduser().resolve()
sys.path.insert(0,str(ROOT))
from inference.runtime import ModelRuntime

rt=ModelRuntime(MODEL_ROOT)
print(f'Device: {rt.device}')
status=rt.status(deep=True)
print(json.dumps(status,indent=2,ensure_ascii=False))
failed=[]
for crop,tasks in status['crops'].items():
    for task,s in tasks.items():
        if not s['enabled'] or s['runtime_kind']!='classification': continue
        if not s['present']: failed.append((crop,task,'checkpoint missing'))
        elif s['loadable'] is not True: failed.append((crop,task,s['load_error']))
if failed:
    print('FAILED ENABLED MODELS:')
    for x in failed: print(x)
    raise SystemExit(1)
# Dummy forward checks for enabled classifiers.
for crop,tasks in rt.registry.crops.items():
    for task,spec in tasks.items():
        if not spec.get('enabled') or spec.get('runtime_kind')!='classification': continue
        loaded=rt.load(crop,task); size=int(spec['image_size']); x=torch.zeros(1,3,size,size,device=rt.device)
        with torch.inference_mode(): y=loaded['model'](x)
        assert tuple(y.shape)==(1,len(loaded['classes'])),(crop,task,y.shape)
        print(f'PASS {crop}/{task}: {loaded["architecture"]} -> {tuple(y.shape)}')
print('ALL ATTACHED ENABLED MODEL CONTRACTS: PASS')
