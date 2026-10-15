"""
Voice service - Urdu and English TTS using Edge TTS.

Writes text to a temp file and runs edge-tts via a helper script
to avoid Windows subprocess Unicode encoding issues.
"""

import os
import re
import subprocess
import sys
import tempfile


def _strip_markdown(text: str) -> str:
    """Remove markdown formatting so TTS reads clean text."""
    text = re.sub(r'[•●▪◦✓✔✦→←]', ' ', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\n{2,}', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


URDU_VOICE = "ur-PK-UzmaNeural"
URDU_VOICE_FALLBACK = "ur-IN-GulNeural"
ENGLISH_VOICE = "en-US-GuyNeural"

_HELPER_SCRIPT = os.path.join(os.path.dirname(__file__), "_tts_worker.py")


def _synthesize(text: str, voice: str) -> bytes | None:
    """Run edge-tts in a subprocess, passing text via a temp file."""
    text_path = None
    media_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix='.txt', mode='w', encoding='utf-8'
        ) as tf:
            tf.write(text)
            text_path = tf.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as mf:
            media_path = mf.name

        result = subprocess.run(
            [sys.executable, _HELPER_SCRIPT,
             "--voice", voice,
             "--text-file", text_path,
             "--output", media_path],
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            stderr_text = result.stderr.decode("utf-8", errors="replace")[:2000]
            print(f"TTS worker error (voice={voice}): {stderr_text}")
            return None

        if not os.path.exists(media_path) or os.path.getsize(media_path) == 0:
            print(f"TTS worker: no output for voice={voice}")
            return None

        with open(media_path, 'rb') as f:
            return f.read()

    except subprocess.TimeoutExpired:
        print(f"TTS worker timeout for voice={voice}")
        return None
    except Exception as e:
        print(f"TTS worker error: {e}")
        return None
    finally:
        for p in (text_path, media_path):
            if p and os.path.exists(p):
                os.unlink(p)


def text_to_speech_english(text: str) -> bytes | None:
    clean_text = _strip_markdown(text)
    if not clean_text:
        return None
    return _synthesize(clean_text, ENGLISH_VOICE)


def text_to_speech_urdu(text: str) -> bytes | None:
    clean_text = _strip_markdown(text)
    if not clean_text:
        return None
    result = _synthesize(clean_text, URDU_VOICE)
    if result is None:
        print(f"TTS: primary Urdu voice failed, trying fallback {URDU_VOICE_FALLBACK}")
        result = _synthesize(clean_text, URDU_VOICE_FALLBACK)
    return result


# ---------------------------------------------------------------------------------------------
# Fast path: edge-tts in-process (async). Before, every request started a new Python process
# (~1-2 s) and the server waited for the WHOLE answer to be spoken into one file. The website now
# sends short pieces (1-2 sentences), so the first words play after ~1 s.
# ---------------------------------------------------------------------------------------------
from collections import OrderedDict as _OD

_CACHE: "_OD[tuple, bytes]" = _OD()
_CACHE_MAX = 200


async def _synthesize_async(text: str, voice: str) -> bytes | None:
    try:
        import edge_tts
    except ImportError:
        return None
    try:
        buf = bytearray()
        async for chunk in edge_tts.Communicate(text, voice).stream():
            if chunk.get("type") == "audio":
                buf.extend(chunk["data"])
        return bytes(buf) or None
    except Exception as e:
        print(f"TTS (in-process) error for voice={voice}: {e}")
        return None


async def text_to_speech_async(text: str, language: str = "urdu") -> bytes | None:
    clean = _strip_markdown(text)
    if not clean:
        return None
    voices = [ENGLISH_VOICE] if language == "english" else [URDU_VOICE, URDU_VOICE_FALLBACK]
    for voice in voices:
        key = (voice, clean)
        if key in _CACHE:
            _CACHE.move_to_end(key)
            return _CACHE[key]
        audio = await _synthesize_async(clean, voice)
        if audio is None:   # in-process failed -> old subprocess path (runs in a thread, not blocking the server)
            import asyncio
            audio = await asyncio.to_thread(_synthesize, clean, voice)
        if audio:
            _CACHE[key] = audio
            while len(_CACHE) > _CACHE_MAX:
                _CACHE.popitem(last=False)
            return audio
    return None
