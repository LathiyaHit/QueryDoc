"""
ElevenLabs Turbo v2 — streaming TTS.
Yields MP3 chunks as they arrive (audio plays before the full sentence is synthesised).
"""
import httpx
from typing import AsyncGenerator
from app.core.config import settings

BASE_URL = "https://api.elevenlabs.io/v1"
DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"   # Rachel


class ElevenLabsTTS:
    def __init__(self, voice_id: str = DEFAULT_VOICE):
        self.voice_id = voice_id
        self._headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }

    async def stream_audio(self, text: str) -> AsyncGenerator[bytes, None]:
        """Yield MP3 audio bytes for the given text."""
        url = f"{BASE_URL}/text-to-speech/{self.voice_id}/stream"
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
            "optimize_streaming_latency": 4,   # maximum latency optimisation
        }
        async with httpx.AsyncClient(timeout=30) as client:
            async with client.stream(
                "POST", url, json=payload, headers=self._headers
            ) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes(chunk_size=4096):
                    if chunk:
                        yield chunk
