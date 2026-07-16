"""
TTS router — ElevenLabs (primary) or Kokoro (local fallback).
"""
from app.core.config import settings


def get_tts_client():
    if settings.ELEVENLABS_API_KEY:
        from app.services.tts.elevenlabs_client import ElevenLabsTTS
        return ElevenLabsTTS()
    from app.services.tts.kokoro_client import KokoroTTS
    return KokoroTTS()
