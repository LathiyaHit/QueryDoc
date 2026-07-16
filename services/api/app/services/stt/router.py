"""
STT router — returns Deepgram (primary) or Whisper (fallback).
"""
from app.core.config import settings


def get_stt_client():
    if settings.DEEPGRAM_API_KEY:
        from app.services.stt.deepgram_client import DeepgramSTT
        return DeepgramSTT()
    from app.services.stt.whisper_client import WhisperSTT
    return WhisperSTT()
