"""
Audio transcription using OpenRouter's Whisper endpoint.
"""
import os
import tempfile
import logging
# pyrefly: ignore [missing-import]
from openai import AsyncOpenAI
from config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

# Shared client - reused across requests for performance
client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


async def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """
    Transcribes audio bytes into text using OpenAI Whisper via OpenRouter.
    Writes bytes to a temp file, uploads, then cleans up.
    """
    _, ext = os.path.splitext(filename)
    if not ext:
        ext = ".mp3"

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                model="openai/whisper-1",
                file=audio_file,
            )

        return response.text

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
