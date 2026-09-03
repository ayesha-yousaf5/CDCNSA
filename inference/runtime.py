from __future__ import annotations
import threading
from pathlib import Path
import torch
from torch.nn import functional as F
from .architectures import build_classifier
from .errors import ModelContractError, ModelUnavailable
from .preprocess import decode_rgb, transform_for
from .registry import ModelRegistry

ALIASES={'maize':'corn','corn / maize':'corn','brinjal':'eggplant','eggplant / brinjal':'eggplant'}  # lemon/citrus aliases hidden for now

def canonical_crop(value:str)->str:
    x=' '.join(str(value or '').strip().lower().split())
    return ALIASES.get(x,x)

def display_label(label:str)->str:
    # Member-2 checkpoints retain 'Crop / class' prefixes; the UI ontology does not need them.
    if ' / ' in label: label=label.split(' / ',1)[1]
    return label.replace('_',' ').strip().title() if '_' in label else label.strip()

def is_healthy(label:str)->bool:
    x=display_label(label).strip().lower().replace('_',' ')
    return x=='healthy'

class ModelRuntime:
    def __init__(self,root:Path):
        self.root=Path(root)
        self.registry=ModelRegistry(self.root)
        self.device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._models={}; self._locks={}; self._errors={}
    def _lock(self,key):
        self._locks.setdefault(key,threading.Lock()); return self._locks[key]
    def _extract(self,obj):
        if not isinstance(obj,dict): raise ModelContractError('Checkpoint must deserialize to a dict/state_dict.')
        for key in ('model_state_dict','state_dict','model'):
            if key in obj and isinstance(obj[key],dict): return obj[key],obj
        if obj and all(torch.is_tensor(v) for v in obj.values()): return obj,{}
        raise ModelContractError('No model_state_dict/state_dict found in checkpoint.')
    @staticmethod
    def _strip_module(sd):
        return {k[7:] if k.startswith('module.') else k:v for k,v in sd.items()}
    def load(self,crop:str,task:str):
        crop=canonical_crop(crop); key=(crop,task)
        if key in self._models:return self._models[key]
        spec=self.registry.task(crop,task)
        if not spec.get('enabled'): raise ModelUnavailable(f'{crop} {task} model is not enabled in this build.')
        if spec.get('runtime_kind')!='classification': raise ModelUnavailable(f'{crop} {task} uses {spec.get("runtime_kind")}; its dedicated runtime is not attached yet.')
        p=self.registry.checkpoint_path(spec)
        if not p.is_file(): raise ModelUnavailable(f'{crop} {task} checkpoint is missing: {spec.get("checkpoint")}')
        with self._lock(key):
            if key in self._models:return self._models[key]
            if spec.get('expected_sha256'):
                actual=self.registry.sha256(p)
                if actual!=spec['expected_sha256']: raise ModelContractError(f'{crop} {task} checkpoint SHA256 mismatch.')
            obj=torch.load(p,map_location='cpu',weights_only=False)
            sd,meta=self._extract(obj); sd=self._strip_module(sd)
            class_to_idx=(meta.get('class_to_idx') or meta.get('class_mapping')
                          or meta.get('severity_to_idx') or spec.get('class_to_idx'))
            if not class_to_idx:
                for list_key in ('class_order','severity_classes','classes'):
                    if meta.get(list_key):
                        class_to_idx={c:i for i,c in enumerate(meta[list_key])}
                        break
            if not class_to_idx: raise ModelContractError(f'{crop} {task} has no exact class mapping.')
            ordered=[c for c,_ in sorted(class_to_idx.items(),key=lambda kv:kv[1])]
            if sorted(class_to_idx.values())!=list(range(len(ordered))): raise ModelContractError(f'{crop} {task} class indices are not contiguous from zero.')
            arch=(meta.get('backbone') or meta.get('architecture') or meta.get('model_name') or spec.get('architecture') or '').lower().replace('-','_')
            aliases={'efficientnet_b0':'efficientnet_b0','efficientnet_b0_':'efficientnet_b0','densenet121':'densenet121','resnet50':'resnet50','resnet18':'resnet18','mobilenetv3_large':'mobilenet_v3_large','mobilenet_v3_large':'mobilenet_v3_large','mobilenet_v3':'mobilenet_v3_large','mobilenetv3':'mobilenet_v3_large'}
            arch=aliases.get(arch,arch)
            model=build_classifier(arch,len(ordered))
            try: model.load_state_dict(sd,strict=True)
            except RuntimeError as exc: raise ModelContractError(f'{crop} {task} state_dict does not match {arch}/{len(ordered)} classes: {exc}') from exc
            model.eval().to(self.device)
            loaded={'model':model,'classes':ordered,'spec':spec,'architecture':arch,'meta':meta}
            self._models[key]=loaded
            return loaded
    @torch.inference_mode()
    def predict_task(self,crop:str,task:str,image):
        loaded=self.load(crop,task); spec=loaded['spec']
        x=transform_for(spec)(image).unsqueeze(0).to(self.device)
        logits=loaded['model'](x)
        if logits.ndim!=2 or logits.shape[1]!=len(loaded['classes']): raise ModelContractError('Unexpected model output shape.')
        probs=F.softmax(logits,dim=1)[0]; conf,idx=torch.max(probs,dim=0)
        idx=int(idx.item()); return loaded['classes'][idx],float(conf.item())
    @staticmethod
    def _confidence_to_severity(conf: float) -> str:
        if conf >= 0.85:
            return 'SEVERE'
        if conf >= 0.65:
            return 'MODERATE'
        return 'MILD'
    def diagnose(self,crop:str,payload:bytes,language:str='en')->dict:
        crop=canonical_crop(crop); image=decode_rgb(payload)
        label,conf=self.predict_task(crop,'disease',image)
        disease=display_label(label); healthy=is_healthy(label)
        threshold=float(self.registry.data.get('disease_confidence_threshold',0.55))
        uncertain=conf<threshold
        out={'crop':crop,'disease':disease,'confidence':round(conf,6),'healthy':healthy,'uncertain':uncertain,'severity':'N/A','severity_confidence':None,'severity_unavailable':False,'severity_abstained':False,'language':language,'runtime_device':str(self.device),'demo':False}
        if healthy:
            out['reason']='healthy_skips_severity'; return out
        if uncertain:
            out['reason']='disease_uncertain_skips_severity'; return out
        sev_spec=self.registry.task(crop,'severity')
        if not sev_spec.get('enabled') or not self.registry.checkpoint_path(sev_spec).is_file():
            use_heuristic = self.registry.data.get('rules', {}).get('confidence_heverity_fallback', False)
            if use_heuristic:
                out['severity'] = self._confidence_to_severity(conf)
                out['severity_confidence'] = round(conf, 6)
                out['severity_source'] = 'confidence_heuristic'
                out['reason'] = 'severity_heuristic_fallback'
                return out
            out['severity_unavailable']=True; out['reason']='severity_model_unavailable'; return out
        try:
            sev_label,sev_conf=self.predict_task(crop,'severity',image)
        except ModelUnavailable:
            use_heuristic = self.registry.data.get('rules', {}).get('confidence_heverity_fallback', False)
            if use_heuristic:
                out['severity'] = self._confidence_to_severity(conf)
                out['severity_confidence'] = round(conf, 6)
                out['severity_source'] = 'confidence_heuristic'
                out['reason'] = 'severity_heuristic_fallback'
                return out
            out['severity_unavailable']=True; out['reason']='severity_runtime_unavailable'; return out
        out['severity_confidence']=round(sev_conf,6)
        sev_threshold=float(self.registry.data.get('severity_abstain_threshold',0.40))
        if sev_conf<sev_threshold:
            out['severity']='N/A'; out['severity_abstained']=True; out['reason']='severity_low_confidence_abstention'
        else:
            out['severity']=display_label(sev_label).upper(); out['reason']='ok'
        return out
    def status(self,deep:bool=False)->dict:
        result={'device':str(self.device),'crops':{}}
        for crop,tasks in self.registry.crops.items():
            result['crops'][crop]={}
            for task,spec in tasks.items():
                st=self.registry.file_status(spec); st['loadable']=None; st['load_error']=None
                if deep and st['enabled'] and st['present']:
                    try: self.load(crop,task); st['loadable']=True
                    except Exception as exc: st['loadable']=False; st['load_error']=str(exc)
                result['crops'][crop][task]=st
        return result
