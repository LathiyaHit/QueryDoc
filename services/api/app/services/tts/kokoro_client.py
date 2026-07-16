"""
Kokoro — open-source local TTS fallback.
Requires: pip install kokoro-onnx
Falls back when ElevenLabs quota is exhausted or API is down.
"""
from typing import AsyncGenerator
import asyncio


class KokoroTTS:
    def __init__(self):
        self._model = None

    def _load(self):
        try:
            from kokoro_onnx import Kokoro
            self._model = Kokoro("kokoro-v0_19.onnx", "voices.bin")
        except ImportError:
            raise RuntimeError("Install kokoro-onnx: pip install kokoro-onnx")

    async def stream_audio(self, text: str) -> AsyncGenerator[bytes, None]:
        if self._model is None:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load)

        loop = asyncio.get_event_loop()
        samples, sample_rate = await loop.run_in_executor(
            None,
            lambda: self._model.create(text, voice="af_bella", speed=1.0, lang="en-us"),
        )
        # Convert numpy float32 → raw PCM bytes
        import numpy as np
        pcm = (samples * 32767).astype(np.int16).tobytes()
        # Yield in 4 KB chunks to simulate streaming
        chunk_size = 4096
        for i in range(0, len(pcm), chunk_size):
            yield pcm[i : i + chunk_size]
