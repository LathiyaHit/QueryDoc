"""Pydantic schemas for WebSocket messages."""
from pydantic import BaseModel
from enum import Enum


class MessageType(str, Enum):
    audio_chunk = "audio_chunk"
    transcript = "transcript"
    response_text = "response_text"
    response_audio = "response_audio"
    error = "error"
    session_start = "session_start"
    session_end = "session_end"


class WSMessage(BaseModel):
    type: MessageType
    payload: dict = {}


class TranscriptEvent(BaseModel):
    text: str
    is_final: bool
    latency_ms: float | None = None
