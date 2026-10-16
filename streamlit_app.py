"""CDCNSA - Streamlit deployment (backup for Streamlit Community Cloud).

The screen is the ORIGINAL website: index.html, app.js and styles.css are served unchanged
inside a Streamlit component (built into ./_streamlit_ui_build at start-up). The website's three
server calls - /api/diagnose, /api/chat/stream, /api/tts (and /api/chat/reset) - are caught by
streamlit_ui/st_bridge.js and answered here by the same Python code server.py uses:
inference/runtime.py (crop models + Qwen-VL + lesion severity), chatbot/chat_service.py and
chatbot/voice_service.py.

Run locally:   streamlit run streamlit_app.py
Secrets (Streamlit Cloud -> App settings -> Secrets, TOML):
    GROQ_API_KEY = "..."            # chatbot (+ photo check if no vision key)
    GROQ_VISION_API_KEY = "..."     # optional, separate key for the Qwen photo check
    CDCNSA_HF_REPO = "user/cdcnsa-models"   # optional, Hugging Face repo with the model files
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import shutil
import threading
import traceback
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="CDCNSA - Crop Health Assistant", page_icon="🌱", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------------------------------------------------------- secrets -> environment
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, (str, int, float, bool)):
            os.environ.setdefault(_k, str(_v))
except Exception:  # no secrets file (local run with .env)
    pass
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass
os.environ.setdefault("CDCNSA_DIAGNOSIS_MODE", "hybrid")
os.environ.setdefault("CDCNSA_MAX_CACHED_MODELS", "2")  # disease + severity model in memory (Streamlit has ~2.7 GB)

MODEL_ROOT = Path(os.getenv("CDCNSA_MODEL_ROOT", str(ROOT))).expanduser().resolve()
BUILD = ROOT / "_streamlit_ui_build"


# ---------------------------------------------------------------- the original website as a component
def build_ui() -> Path:
    """Copy the website files and add the bridge script just before app.js."""
    BUILD.mkdir(exist_ok=True)
    for name in ("app.js", "styles.css"):
        shutil.copyfile(ROOT / name, BUILD / name)
    shutil.copyfile(ROOT / "streamlit_ui" / "st_bridge.js", BUILD / "st_bridge.js")
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    marker = '<script src="app.js'
    if marker not in page:
        raise RuntimeError("index.html no longer loads app.js - update build_ui()")
    page = page.replace(marker, '<script src="st_bridge.js"></script>\n  ' + marker, 1)
    (BUILD / "index.html").write_text(page, encoding="utf-8")
    return BUILD


@st.cache_resource(show_spinner=False)
def ui_component():
    return components.declare_component("cdcnsa_ui", path=str(build_ui()))


# ---------------------------------------------------------------- heavy resources (once per server)
class _Models:
    """Downloads the model files and creates the ModelRuntime in the background, so the page opens at once."""

    def __init__(self):
        self.runtime = None
        self.missing: list[str] = []
        self.error: str | None = None
        self.ready = threading.Event()
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        try:
            if os.getenv("CDCNSA_SKIP_DOWNLOAD", "0").lower() not in ("1", "true", "yes"):
                from download_models import ensure_models
                _, self.missing = ensure_models(MODEL_ROOT)
            from inference.runtime import ModelRuntime
            self.runtime = ModelRuntime(MODEL_ROOT)
        except Exception as exc:
            self.error = str(exc)
            traceback.print_exc()
        finally:
            self.ready.set()


@st.cache_resource(show_spinner=False)
def models() -> _Models:
    return _Models()


@st.cache_resource(show_spinner=False)
def chat():
    from chatbot import chat_service
    threading.Thread(target=chat_service.warm_up, daemon=True).start()
    return chat_service


# ---------------------------------------------------------------- the API (same answers as server.py)
def _json(status: int, data) -> dict:
    return {"status": status, "content_type": "application/json", "text": json.dumps(data, default=str)}


def _error(status: int, code: str, message: str, **extra) -> dict:
    return _json(status, {"detail": {"code": code, "message": message, **extra}})


def api_diagnose(form: dict) -> dict:
    from inference.errors import ImageDecodeError, ModelContractError, ModelRuntimeError, ModelUnavailable
    crop = str(form.get("crop") or "")
    language = str(form.get("language") or "en")
    image = form.get("image") or {}
    payload = base64.b64decode(image.get("b64") or "") if isinstance(image, dict) else b""
    if len(payload) > 25 * 1024 * 1024:
        return _error(413, "image_too_large", "Image exceeds the 25 MB upload limit.")
    m = models()
    if not m.ready.wait(timeout=200):
        return _error(503, "models_loading", "The models are still being prepared. Please try again in a minute.", crop=crop)
    if m.runtime is None:
        return _error(503, "model_unavailable", f"Models could not be loaded: {m.error}", crop=crop)
    try:
        return _json(200, m.runtime.diagnose(crop, payload, language))
    except ModelUnavailable as exc:
        return _error(503, "model_unavailable", str(exc), crop=crop)
    except ImageDecodeError as exc:
        return _error(415, "image_decode_error", str(exc))
    except ModelContractError as exc:
        return _error(500, "model_contract_error", str(exc), crop=crop)
    except ModelRuntimeError as exc:
        return _error(500, "model_runtime_error", str(exc), crop=crop)


def api_chat_stream(body: dict) -> dict:
    chat_service = chat()

    async def collect() -> list:
        out = []
        async for chunk in chat_service.ask_stream(message=str(body.get("message") or ""),
                                                   context=body.get("context") or {},
                                                   session_id=str(body.get("session_id") or "default")):
            out.append(chunk)
        return out

    try:
        chunks = asyncio.run(collect())
    except Exception as exc:
        chunks = [f"Assistant error: {exc}"]
    text = "".join(f"data: {json.dumps(c)}\n\n" for c in chunks) + "data: [DONE]\n\n"
    return {"status": 200, "content_type": "text/event-stream", "text": text}


def api_tts(body: dict) -> dict:
    from chatbot import voice_service
    language = "english" if body.get("language") == "english" else "urdu"
    try:
        audio = asyncio.run(voice_service.text_to_speech_async(str(body.get("text") or ""), language))
    except Exception:
        audio = None
    if not audio:
        return _json(500, {"detail": "TTS synthesis failed"})
    return {"status": 200, "content_type": "audio/mpeg", "b64": base64.b64encode(audio).decode("ascii")}


def api_chat_reset(body: dict) -> dict:
    chat().reset_context(str(body.get("session_id") or "default"))
    return _json(200, {"status": "reset"})


def handle(req: dict) -> dict:
    path = req.get("path")
    try:
        body = json.loads(req["json"]) if req.get("json") else {}
    except ValueError:
        body = {}
    try:
        if path == "/api/diagnose":
            return api_diagnose(req.get("form") or {})
        if path == "/api/chat/stream":
            return api_chat_stream(body)
        if path == "/api/chat":
            r = api_chat_stream(body)
            reply = "".join(json.loads(line[6:]) for line in r["text"].split("\n")
                            if line.startswith("data: ") and line[6:] != "[DONE]")
            return _json(200, {"reply": reply})
        if path == "/api/tts":
            return api_tts(body)
        if path == "/api/chat/reset":
            return api_chat_reset(body)
        if path == "/api/health":
            from inference import vlm
            return _json(200, {"status": "ok", "host": "streamlit", "diagnosis_mode": "qwen_vl_hybrid" if vlm.available() else "cnn_only"})
    except Exception as exc:
        traceback.print_exc()
        return _error(500, "server_error", str(exc)[:300])
    return _error(404, "not_found", f"Unknown API path {path}")


# ---------------------------------------------------------------- page
st.markdown(
    """
<style>
  header[data-testid="stHeader"], footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
  [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
  .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { overflow: hidden !important; }
  .block-container, [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
  [data-testid="stVerticalBlock"] { gap: 0 !important; }
  iframe[title="cdcnsa_ui"], iframe[title$=".cdcnsa_ui"] { height: 100vh !important; width: 100% !important; border: 0; display: block; }
</style>
""",
    unsafe_allow_html=True,
)

models()  # start downloading / loading the models in the background straight away
chat()    # warm the chatbot knowledge search

ss = st.session_state
ss.setdefault("api_done", {})  # request id -> response, for the requests the page is still waiting for

incoming = (ss.get("cdcnsa_ui") or {}).get("requests") or []
waiting = {r["id"] for r in incoming if isinstance(r, dict) and r.get("id")}
ss.api_done = {k: v for k, v in ss.api_done.items() if k in waiting}  # forget answers the page already took
for r in incoming:
    if isinstance(r, dict) and r.get("id") and r["id"] not in ss.api_done:
        ss.api_done[r["id"]] = handle(r)  # saved at once, so an interrupted rerun never repeats the work

ui_component()(responses=ss.api_done, key="cdcnsa_ui", default=None)
