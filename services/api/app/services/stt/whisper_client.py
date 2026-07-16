"""
Local Whisper v3 Turbo — fallback STT when Deepgram is unavailable.
Buffers the full utterance then transcribes offline.
"""
import io
import numpy as np
import torch
import torchaudio
from transformers import pipeline as hf_pipeline


class WhisperSTT:
    def __init__(self):
        self._pipe = None
        self._buffer: list[bytes] = []
        self._queue = None

    def _load(self):
        if self._pipe is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._pipe = hf_pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-large-v3-turbo",
                device=device,
            )

    async def connect(self):
        import asyncio
        self._queue = asyncio.Queue()
        # Load model in background thread so we don't block startup
        import concurrent.futures
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load)

    async def send_audio(self, pcm_bytes: bytes):
        self._buffer.append(pcm_bytes)

    async def get_transcript(self) -> dict | None:
        if not self._buffer:
            return None
        audio = np.frombuffer(b"".join(self._buffer), dtype=np.int16).astype(np.float32)
        audio = audio / 32768.0
        result = self._pipe(audio, return_timestamps=False)
        self._buffer.clear()
        return {"text": result["text"].strip(), "is_final": True}

    async def close(self):
        self._buffer.clear()
