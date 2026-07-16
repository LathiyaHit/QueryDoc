"""
Silero VAD wrapper.
Detects end-of-utterance from raw PCM bytes so STT
is triggered the moment the user stops speaking.
"""
import numpy as np
import torch
from collections import deque


class SileroVAD:
    def __init__(self, threshold: float = 0.5, silence_windows: int = 3):
        self.model, _ = torch.hub.load(
            "snakers4/silero-vad", "silero_vad", trust_repo=True
        )
        self.model.eval()
        self.threshold = threshold
        self.sample_rate = 16_000
        self.silence_windows = silence_windows

        self._history: deque = deque(maxlen=20)
        self._buffer = np.array([], dtype=np.float32)
        self.is_speaking = False

    def process_chunk(self, pcm_bytes: bytes) -> tuple[bool, bool]:
        """
        Returns:
            is_speech (bool)      — chunk contains voice
            end_of_utterance (bool) — was speaking, now silent
        """
        audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        if audio.size == 0:
            return False, False

        self._buffer = np.concatenate((self._buffer, audio))
        window_size = 512
        chunk_has_speech = False
        chunk_end_of_utterance = False

        while self._buffer.size >= window_size:
            window = self._buffer[:window_size]
            self._buffer = self._buffer[window_size:]
            tensor = torch.from_numpy(window)

            with torch.no_grad():
                prob = self.model(tensor, self.sample_rate).item()

            is_speech = prob > self.threshold
            chunk_has_speech = chunk_has_speech or is_speech
            self._history.append(is_speech)

            recent_silence = sum(list(self._history)[-self.silence_windows:]) == 0
            end_of_utterance = self.is_speaking and recent_silence
            chunk_end_of_utterance = chunk_end_of_utterance or end_of_utterance
            self.is_speaking = is_speech or (
                self.is_speaking and not recent_silence
            )

        return chunk_has_speech, chunk_end_of_utterance

    def reset(self):
        self._history.clear()
        self._buffer = np.array([], dtype=np.float32)
        self.is_speaking = False
