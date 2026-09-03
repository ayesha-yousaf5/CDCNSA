from __future__ import annotations
import hashlib, json
from pathlib import Path
from .errors import ModelContractError

class ModelRegistry:
    def __init__(self, root: Path, path: str='model_registry.json'):
        self.root=Path(root)
        self.path=self.root/path
        self.data=json.loads(self.path.read_text(encoding='utf-8'))
        self.crops=self.data['crops']
    def crop(self, crop_id: str)->dict:
        if crop_id not in self.crops: raise ModelContractError(f'Unknown crop: {crop_id}')
        return self.crops[crop_id]
    def task(self,crop_id:str,task:str)->dict:
        return self.crop(crop_id)[task]
    def checkpoint_path(self,spec:dict)->Path:
        return self.root/spec['checkpoint']
    @staticmethod
    def sha256(path:Path)->str:
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
        return h.hexdigest()
    def file_status(self,spec:dict)->dict:
        p=self.checkpoint_path(spec)
        present=p.is_file()
        actual=None; hash_ok=None
        if present:
            actual=self.sha256(p)
            expected=spec.get('expected_sha256')
            hash_ok=(actual==expected) if expected else None
        return {'enabled':bool(spec.get('enabled')),'checkpoint':spec.get('checkpoint'),'present':present,'architecture':spec.get('architecture'),'runtime_kind':spec.get('runtime_kind'),'expected_sha256':spec.get('expected_sha256'),'actual_sha256':actual,'hash_ok':hash_ok,'note':spec.get('note','')}
