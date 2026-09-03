from __future__ import annotations
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError
from torchvision import transforms
from .errors import ImageDecodeError

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass

def decode_rgb(payload: bytes) -> Image.Image:
    if not payload:
        raise ImageDecodeError('The uploaded image is empty.')
    try:
        with Image.open(BytesIO(payload)) as im:
            im=ImageOps.exif_transpose(im)
            return im.convert('RGB').copy()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageDecodeError('The uploaded file could not be decoded as an image.') from exc

def transform_for(spec: dict):
    size=int(spec['image_size'])
    mean=spec.get('normalization_mean') or [0.485,0.456,0.406]
    std=spec.get('normalization_std') or [0.229,0.224,0.225]
    return transforms.Compose([
        transforms.Resize((size,size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean,std=std),
    ])
