from __future__ import annotations
import torch.nn as nn
from torchvision.models import (
    densenet121, efficientnet_b0, mobilenet_v3_large, resnet18, resnet50,
)

class UnsupportedArchitecture(ValueError): pass

def build_classifier(architecture: str, num_classes: int) -> nn.Module:
    arch=(architecture or '').lower().replace('-', '_')
    if arch=='efficientnet_b0':
        model=efficientnet_b0(weights=None)
        model.classifier[1]=nn.Linear(model.classifier[1].in_features,num_classes)
        return model
    if arch=='resnet18':
        model=resnet18(weights=None); model.fc=nn.Linear(model.fc.in_features,num_classes); return model
    if arch=='resnet50':
        model=resnet50(weights=None); model.fc=nn.Linear(model.fc.in_features,num_classes); return model
    if arch=='densenet121':
        model=densenet121(weights=None); model.classifier=nn.Linear(model.classifier.in_features,num_classes); return model
    if arch=='mobilenet_v3_large':
        model=mobilenet_v3_large(weights=None); model.classifier[3]=nn.Linear(model.classifier[3].in_features,num_classes); return model
    raise UnsupportedArchitecture(f'Unsupported or unresolved architecture: {architecture!r}')
