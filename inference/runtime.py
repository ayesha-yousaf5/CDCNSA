from __future__ import annotations
import gc
import os
import threading
from collections import OrderedDict
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from PIL import ImageStat
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
    _RUNTIME_META_KEYS=(
        'backbone','architecture','model_name','class_to_idx','class_mapping',
        'severity_to_idx','class_order','severity_classes','classes','image_size',
        'input_size','imagenet_mean','imagenet_std','normalization_mean',
        'normalization_std',
    )
    def __init__(self,root:Path):
        self.root=Path(root)
        self.registry=ModelRegistry(self.root)
        self.device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # Render's smaller instances cannot safely retain multiple CNNs. Keep the
        # limit configurable, but default to one model so disease is released
        # before severity is loaded.
        try:
            self.max_cached_models=max(1,int(os.getenv('CDCNSA_MAX_CACHED_MODELS','1')))
        except ValueError:
            self.max_cached_models=1
        self._models=OrderedDict(); self._cache_lock=threading.RLock()
        self._inference_lock=threading.RLock(); self._errors={}
    def _cached(self,key):
        loaded=self._models.get(key)
        if loaded is not None:self._models.move_to_end(key)
        return loaded
    def _make_cache_room(self):
        evicted=False
        while len(self._models)>=self.max_cached_models:
            _,loaded=self._models.popitem(last=False)
            del loaded; evicted=True
        if evicted:
            gc.collect()
            if self.device.type=='cuda':torch.cuda.empty_cache()
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
        with self._cache_lock:
            loaded=self._cached(key)
            if loaded is not None:return loaded
            spec=self.registry.task(crop,task)
            if not spec.get('enabled'): raise ModelUnavailable(f'{crop} {task} model is not enabled in this build.')
            if spec.get('runtime_kind')!='classification': raise ModelUnavailable(f'{crop} {task} uses {spec.get("runtime_kind")}; its dedicated runtime is not attached yet.')
            p=self.registry.checkpoint_path(spec)
            if not p.is_file(): raise ModelUnavailable(f'{crop} {task} checkpoint is missing: {spec.get("checkpoint")}')
            self._make_cache_room()
            if spec.get('expected_sha256'):
                actual=self.registry.sha256(p)
                if actual!=spec['expected_sha256']: raise ModelContractError(f'{crop} {task} checkpoint SHA256 mismatch.')
            obj=torch.load(p,map_location='cpu',weights_only=False)
            sd,meta=self._extract(obj); sd=self._strip_module(sd)
            # Never retain the checkpoint/state_dict as "metadata" alongside the
            # instantiated model. Several checkpoints embed model_state_dict in
            # the top-level dict, which otherwise nearly doubles resident RAM.
            runtime_meta={k:meta[k] for k in self._RUNTIME_META_KEYS if k in meta}
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
            del sd,meta,obj
            gc.collect()
            loaded={'model':model,'classes':ordered,'spec':spec,'architecture':arch,'meta':runtime_meta}
            self._models[key]=loaded
            return loaded
    @torch.inference_mode()
    def predict_task(self,crop:str,task:str,image):
        with self._inference_lock:
            loaded=self.load(crop,task); spec=loaded['spec']
            x=transform_for(spec)(image).unsqueeze(0).to(self.device)
            logits=loaded['model'](x)
            if logits.ndim!=2 or logits.shape[1]!=len(loaded['classes']): raise ModelContractError('Unexpected model output shape.')
            probs=F.softmax(logits,dim=1)[0]
            values,indices=torch.topk(probs,min(2,len(probs)))
            idx=int(indices[0].item())
            confidence=float(values[0].item())
            margin=confidence-float(values[1].item()) if len(values)>1 else confidence
            return loaded['classes'][idx],confidence,margin
    @staticmethod
    def _image_quality_reason(image):
        # This is a conservative content gate, not a substitute for a trained OOD model.
        if min(image.size)<32:return 'image_too_small'
        gray=image.resize((64,64)).convert('L')
        if float(ImageStat.Stat(gray).stddev[0])<2.0:return 'image_too_uniform'
        sample=np.asarray(image.resize((64,64)).convert('RGB'))
        quantized=(sample//32).reshape(-1,3)
        unique_colors=len(np.unique(quantized,axis=0))
        dark_fraction=float(np.mean(np.max(sample,axis=2)<35))
        if dark_fraction>0.58 and unique_colors<90:
            return 'image_not_crop_like'
        return None
    def diagnose(self,crop:str,payload:bytes,language:str='en')->dict:
        with self._inference_lock:
            return self._diagnose(crop,payload,language)
    def _diagnose(self,crop:str,payload:bytes,language:str='en')->dict:
        crop=canonical_crop(crop); image=decode_rgb(payload)
        quality_reason=self._image_quality_reason(image)
        if quality_reason:
            return {'crop':crop,'disease':'Uncertain','candidate_disease':None,'confidence':0.0,'healthy':False,'candidate_healthy':False,'uncertain':True,'severity':'N/A','severity_confidence':None,'severity_unavailable':False,'severity_abstained':False,'language':language,'runtime_device':str(self.device),'demo':False,'reason':quality_reason}
        label,conf,margin=self.predict_task(crop,'disease',image)
        disease=display_label(label); healthy=is_healthy(label)
        thresholds=self.registry.data.get('disease_thresholds',{})
        threshold=float(thresholds.get(crop,self.registry.data.get('disease_confidence_threshold',0.55)))
        margins=self.registry.data.get('disease_margins',{})
        margin_threshold=float(margins.get(crop,self.registry.data.get('disease_margin_threshold',0.08)))
        uncertain=conf<threshold or margin<margin_threshold
        out={'crop':crop,'disease':disease,'candidate_disease':None,'confidence':round(conf,6),'healthy':healthy,'candidate_healthy':healthy,'uncertain':uncertain,'severity':'N/A','severity_confidence':None,'severity_unavailable':False,'severity_abstained':False,'language':language,'runtime_device':str(self.device),'demo':False}
        if uncertain:
            out['candidate_disease']=disease
            out['disease']='Uncertain'
            out['healthy']=False
            out['reason']='disease_uncertain_skips_severity'
            out['margin']=round(margin,6)
            return out
        if healthy:
            out['reason']='healthy_skips_severity'; return out
        sev_spec=self.registry.task(crop,'severity')
        if not sev_spec.get('enabled') or not self.registry.checkpoint_path(sev_spec).is_file():
            out['severity_unavailable']=True; out['reason']='severity_model_unavailable'; return out
        try:
            sev_label,sev_conf,_=self.predict_task(crop,'severity',image)
        except ModelUnavailable:
            out['severity_unavailable']=True; out['reason']='severity_runtime_unavailable'; return out
        out['severity_confidence']=round(sev_conf,6)
        sev_threshold=float(self.registry.data.get('severity_abstain_threshold',0.40))
        if sev_conf<sev_threshold:
            out['severity']='N/A'; out['severity_abstained']=True; out['reason']='severity_low_confidence_abstention'
        else:
            out['severity']=display_label(sev_label).upper(); out['reason']='ok'
        return out
    def status(self,deep:bool=False)->dict:
        result={'device':str(self.device),'max_cached_models':self.max_cached_models,'crops':{}}
        for crop,tasks in self.registry.crops.items():
            result['crops'][crop]={}
            for task,spec in tasks.items():
                st=self.registry.file_status(spec); st['loadable']=None; st['load_error']=None
                if deep and st['enabled'] and st['present']:
                    try: self.load(crop,task); st['loadable']=True
                    except Exception as exc: st['loadable']=False; st['load_error']=str(exc)
                result['crops'][crop][task]=st
        return result
