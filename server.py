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
from dotenv import load_dotenv
load_dotenv()

from chatbot import chat_service
from chatbot import voice_service

ROOT=Path(__file__).resolve().parent
MODEL_ROOT=Path(os.getenv("CDCNSA_MODEL_ROOT", str(ROOT))).expanduser().resolve()
app=FastAPI(title='CDCNSA')
runtime=ModelRuntime(MODEL_ROOT)

@app.get('/api/health')
def health()->dict[str,Any]:
    return {'status':'ok','device':str(runtime.device),'model_root':str(MODEL_ROOT),'diagnosis_mode':'real_model_runtime','demo_fallback':False}

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

@app.post('/api/chat')
async def chat(req:ChatRequest)->dict[str,str]:
    try:
        reply=chat_service.ask(message=req.message, context=req.context)
        return {'reply':reply}
    except Exception as exc:
        return {'reply':f'Assistant error: {exc}'}

@app.post('/api/chat/stream')
async def chat_stream(req:ChatRequest):
    try:
        async def generate():
            async for chunk in chat_service.ask_stream(message=req.message, context=req.context):
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
    if req.language=='english':
        audio=voice_service.text_to_speech_english(req.text)
    else:
        audio=voice_service.text_to_speech_urdu(req.text)
    if audio is None:
        raise HTTPException(status_code=500,detail='TTS synthesis failed')
    return Response(content=audio,media_type='audio/mpeg')

@app.post('/api/chat/reset')
async def chat_reset()->dict[str,str]:
    chat_service.reset_context()
    return {'status':'reset'}

# Mount static frontend last so /api routes remain reachable.
app.mount('/',StaticFiles(directory=ROOT,html=True),name='frontend')

if __name__=='__main__':
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app,host='0.0.0.0',port=port)
