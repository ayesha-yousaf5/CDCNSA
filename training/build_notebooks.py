import json, re, sys, pprint
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from crops import CROPS
import nbformat as nbf

HERE = Path(__file__).parent
OUT = HERE / "notebooks"; OUT.mkdir(exist_ok=True)

def to_cells(src):
    cells = []
    for chunk in re.split(r"^# %%", src, flags=re.M):
        if not chunk.strip():
            continue
        if chunk.startswith(" [markdown]"):
            body = "\n".join(l[2:] if l.startswith("# ") else l.lstrip("#") for l in chunk.split("\n")[1:]).strip()
            cells.append(nbf.v4.new_markdown_cell(body))
        else:
            cells.append(nbf.v4.new_code_cell(chunk.split("\n", 1)[1].strip("\n")))
    return cells

def write_nb(src, path):
    nb = nbf.v4.new_notebook()
    nb["cells"] = to_cells(src)
    nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                      "language_info": {"name": "python"},
                      "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True, "isGpuEnabled": True}}
    nbf.write(nb, path)

tmpl = (HERE / "disease_template.py").read_text()
order = ["corn", "cotton", "rice", "tomato", "apple", "mango", "grape", "eggplant", "cucumber", "peas"]
for i, crop in enumerate(order, 1):
    c = CROPS[crop]
    src = (tmpl.replace("__KAGGLE_HINT__", ("**Extra data tip:** " + c["kaggle_hint"]) if c.get("kaggle_hint") else "").replace("__CROP_TITLE__", c["title"]).replace("__CROP__", crop).replace("AUTO_KAGGLE_INPUTS = True ", "AUTO_KAGGLE_INPUTS = " + str(c.get("auto_kaggle_inputs", True)) + " ")
               .replace("__MIN_TRAIN__", str(c.get("min_train_images", 1)).ljust(4))
               .replace("__MIN_SOURCES__", str(c.get("min_train_sources", 1)))
               .replace("__CLASSES__", pprint.pformat(c["classes"], width=110))
               .replace("__ALIASES__", pprint.pformat(c["aliases"], width=110))
               .replace("__SOURCES__", pprint.pformat(c["sources"], width=110, sort_dicts=False)))
    compile(src, crop, "exec")
    write_nb(src, OUT / f"{i:02d}_{crop}_disease.ipynb")
    (HERE / "scripts").mkdir(exist_ok=True); (HERE / "scripts" / f"{crop}_disease.py").write_text(src)
sev = HERE / "severity_template.py"
if sev.exists():
    write_nb(sev.read_text(), OUT / "11_severity_lesion_segmentation.ipynb")
print(sorted(p.name for p in OUT.iterdir()))
