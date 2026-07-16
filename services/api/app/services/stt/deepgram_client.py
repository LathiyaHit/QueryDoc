"""
Deepgram Nova-2 — streaming STT via WebSocket.
Sends PCM chunks and receives partial + final transcripts.
"""
import asyncio
import json
import websockets
from app.core.config import settings


class DeepgramSTT:
    WS_URL = (
        "wss://api.deepgram.com/v1/listen"
        "?model=nova-2"
        "&language=en-US"
        "&encoding=linear16"
        "&sample_rate=16000"
        "&channels=1"
        "&interim_results=true"
        "&endpointing=300"
        "&utterance_end_ms=1000"
    )

    def __init__(self):
        self._ws = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._recv_task = None
        self._keepalive_task = None

    async def connect(self):
        headers = {"Authorization": f"Token {settings.DEEPGRAM_API_KEY}"}
        self._ws = await websockets.connect(self.WS_URL, extra_headers=headers)
        self._recv_task = asyncio.create_task(self._receive_loop())
        self._keepalive_task = asyncio.create_task(self._keepalive_loop())

    async def _keepalive_loop(self):
        try:
            while True:
                await asyncio.sleep(5)
                if self._ws:
                    await self._ws.send(json.dumps({"type": "KeepAlive"}))
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    async def _receive_loop(self):
        try:
            async for raw in self._ws:
                data = json.loads(raw)
                if data.get("type") == "Results":
                    alts = data["channel"]["alternatives"]
                    if alts:
                        transcript = alts[0].get("transcript", "")
                        is_final = data.get("is_final", False)
                        if transcript:
                            await self._queue.put(
                                {"text": transcript, "is_final": is_final}
                            )
        except Exception:
            pass

    async def send_audio(self, pcm_bytes: bytes):
        if self._ws:
            await self._ws.send(pcm_bytes)

    async def get_transcript(self) -> dict | None:
        try:
            return self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def close(self):
        if hasattr(self, '_keepalive_task') and self._keepalive_task:
            self._keepalive_task.cancel()
        if self._recv_task:
            self._recv_task.cancel()
        if self._ws:
            await self._ws.close()
