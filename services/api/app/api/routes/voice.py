"""
WebSocket endpoint — one persistent connection per user session.
Accepts both raw PCM audio bytes (voice input) and JSON text frames
(typed input). Transcript and LLM text events flow back out as JSON.
"""
import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.pipeline.orchestrator import VoicePipeline
from app.core.session import SessionManager
from app.utils.logger import log

router = APIRouter()
session_mgr = SessionManager()


@router.websocket("/ws/{user_id}")
async def voice_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    pipeline = None

    try:
        await session_mgr.create(user_id, session_id)

        pipeline = VoicePipeline(user_id=user_id)
        await pipeline.start()
        await websocket.send_json({"type": "status", "message": "Voice pipeline ready"})

        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            # Voice path — raw PCM audio chunk (16-bit mono, 16 kHz)
            if message.get("bytes") is not None:
                async for event in pipeline.process_audio_chunk(message["bytes"]):
                    await websocket.send_json(event)

            # Text path — JSON: {"type": "text_input", "text": "..."}
            elif message.get("text") is not None:
                try:
                    payload = json.loads(message["text"])
                except json.JSONDecodeError:
                    continue

                if payload.get("type") == "text_input":
                    user_text = payload.get("text", "")
                    async for event in pipeline.process_text_input(user_text):
                        await websocket.send_json(event)

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        log.error(
            "voice.websocket_error",
            user_id=user_id,
            error_type=exc.__class__.__name__,
            error=str(exc),
        )
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": f"{exc.__class__.__name__}: {exc}",
                }
            )
        except Exception:
            pass
    finally:
        if pipeline is not None:
            await pipeline.cleanup()
        await session_mgr.delete(user_id, session_id)