"""Check the severity model on one photo, through the same code the app uses.
   python tools/test_severity.py leaf.jpg tomato "Early Blight"
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import Image
from inference.runtime import ModelRuntime
if len(sys.argv) < 4:
    sys.exit('usage: python tools/test_severity.py <photo> <crop> "<disease name>"')
rt = ModelRuntime(ROOT)
print("severity model present:", rt._seg_available(), "|", rt._seg_paths()[0])
print(rt._segmentation_severity(sys.argv[2].lower(), sys.argv[3], Image.open(sys.argv[1]).convert("RGB")))
