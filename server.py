"""CDCNSA local/production-style server with real crop-model routing.

Run:
    pip install -r requirements.txt
    python server.py

The diagnose endpoint fails closed: there is no fabricated/demo diagnosis fallback.
Models are loaded lazily on first use and validated against model_registry.json.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import os
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
from inference.errors import ImageDecodeError, ModelContractError, ModelRuntimeError, ModelUnavailable
from inference.runtime import ModelRuntime
from inference import vlm
from dotenv import load_dotenv
load_dotenv()

from chatbot import chat_service
from chatbot import voice_service

ROOT=Path(__file__).resolve().parent
MODEL_ROOT=Path(os.getenv("CDCNSA_MODEL_ROOT", str(ROOT))).expanduser().resolve()
app=FastAPI(title='CDCNSA')

@app.on_event('startup')
def _warm_chatbot()->None:
    import threading
    threading.Thread(target=chat_service.warm_up,daemon=True).start()
runtime=ModelRuntime(MODEL_ROOT)

@app.get('/api/health')
def health()->dict[str,Any]:
    return {'status':'ok','device':str(runtime.device),'model_root':str(MODEL_ROOT),'diagnosis_mode':'qwen_vl_hybrid' if vlm.available() else 'cnn_only','vlm_model':vlm.model_name() if vlm.available() else None,'separate_vision_key':bool(os.getenv('GROQ_VISION_API_KEY')),'demo_fallback':False}

@app.get('/api/debug/llm')
def llm_models()->dict[str,Any]:
    """Which Groq models this API key can use (the key itself never leaves the server)."""
    try:
        chat_service._initialize()
        ids=sorted(m.id for m in chat_service.client.models.list().data)
        return {'chat_model':chat_service.GROQ_MODEL,'vision_model':vlm.model_name() if vlm.available() else None,'available':ids}
    except Exception as exc:
        return {'error':str(exc)[:300]}

@app.get('/api/debug/llm-limits')
def llm_limits(models:str='qwen/qwen3.8-27b,openai/gpt-oss-120b,openai/gpt-oss-20b')->dict[str,Any]:
    """Real per-model rate limits for this key (one tiny request each; Groq reports limits in response headers)."""
    chat_service._initialize()
    out={}
    for m in [x.strip() for x in models.split(',') if x.strip()]:
        try:
            raw=chat_service.client.chat.completions.with_raw_response.create(model=m,messages=[{'role':'user','content':'Say OK'}],max_tokens=5)
            h=raw.headers
            out[m]={k:h.get(k) for k in h.keys() if k.lower().startswith('x-ratelimit')}
        except Exception as exc:
            out[m]={'error':str(exc)[:200]}
    return out

@app.get('/api/models/status')
def model_status(deep:bool=Query(False,description='When true, deserialize and contract-check every enabled checkpoint.'))->dict[str,Any]:
    return runtime.status(deep=deep)

@app.post('/api/diagnose')
async def diagnose(crop:str=Form(...),language:str=Form('en'),image:UploadFile=File(...))->dict[str,Any]:
    payload=await image.read()
    if len(payload)>25*1024*1024:
        raise HTTPException(status_code=413,detail={'code':'image_too_large','message':'Image exceeds the 25 MB upload limit.'})
    try:
        return runtime.diagnose(crop,payload,language)
    except ModelUnavailable as exc:
        raise HTTPException(status_code=503,detail={'code':'model_unavailable','crop':crop,'message':str(exc)}) from exc
    except ImageDecodeError as exc:
        raise HTTPException(status_code=415,detail={'code':'image_decode_error','message':str(exc)}) from exc
    except ModelContractError as exc:
        raise HTTPException(status_code=500,detail={'code':'model_contract_error','crop':crop,'message':str(exc)}) from exc
    except ModelRuntimeError as exc:
        raise HTTPException(status_code=500,detail={'code':'model_runtime_error','crop':crop,'message':str(exc)}) from exc

class ChatRequest(BaseModel):
    message:str
    context:dict[str,Any]=Field(default_factory=dict)
    history:list[dict[str,Any]]=Field(default_factory=list)
    session_id:str='default'

# plain 'def' -> FastAPI runs it in a worker thread, so a slow answer never freezes the whole server
@app.post('/api/chat')
def chat(req:ChatRequest)->dict[str,str]:
    try:
        reply=chat_service.ask(message=req.message, context=req.context, session_id=req.session_id)
        return {'reply':reply}
    except Exception as exc:
        return {'reply':f'Assistant error: {exc}'}

@app.post('/api/chat/stream')
async def chat_stream(req:ChatRequest):
    try:
        async def generate():
            async for chunk in chat_service.ask_stream(message=req.message, context=req.context, session_id=req.session_id):
                import json
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(generate(), media_type='text/event-stream')
    except Exception as exc:
        return {'reply':f'Assistant error: {exc}'}

class TTSRequest(BaseModel):
    text:str
    language:str='urdu'

@app.post('/api/tts')
async def tts(req:TTSRequest)->Response:
    audio=await voice_service.text_to_speech_async(req.text,'english' if req.language=='english' else 'urdu')
    if audio is None:
        raise HTTPException(status_code=500,detail='TTS synthesis failed')
    return Response(content=audio,media_type='audio/mpeg')

class ResetRequest(BaseModel):
    session_id:str='default'

@app.post('/api/chat/reset')
async def chat_reset(req:ResetRequest|None=None)->dict[str,str]:
    chat_service.reset_context((req or ResetRequest()).session_id)
    return {'status':'reset'}

# Mount static frontend last so /api routes remain reachable.
app.mount('/',StaticFiles(directory=ROOT,html=True),name='frontend')

if __name__=='__main__':
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app,host='0.0.0.0',port=port)
