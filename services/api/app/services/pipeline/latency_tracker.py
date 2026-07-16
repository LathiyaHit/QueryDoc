"""
Measures wall-clock latency for each pipeline stage.
Stores per-session results in a simple list.
"""
import time
from dataclasses import dataclass, field


@dataclass
class LatencySnapshot:
    speech_start_ms: float = 0.0
    stt_done_ms: float = 0.0
    first_token_ms: float = 0.0
    first_audio_ms: float = 0.0

    @property
    def total_ms(self) -> float:
        return self.first_audio_ms - self.speech_start_ms

    def report(self) -> dict:
        return {
            "stt_latency_ms": round(self.stt_done_ms - self.speech_start_ms, 1),
            "llm_first_token_ms": round(self.first_token_ms - self.stt_done_ms, 1),
            "tts_start_ms": round(self.first_audio_ms - self.first_token_ms, 1),
            "total_ms": round(self.total_ms, 1),
        }


class LatencyTracker:
    def __init__(self):
        self.snapshots: list[LatencySnapshot] = []
        self._current: LatencySnapshot | None = None

    def start_turn(self):
        self._current = LatencySnapshot(speech_start_ms=time.time() * 1000)

    def mark(self, stage: str):
        if self._current is None:
            return
        now = time.time() * 1000
        setattr(self._current, stage, now)

    def end_turn(self) -> dict:
        if self._current is None:
            return {}
        report = self._current.report()
        self.snapshots.append(self._current)
        self._current = None
        return report
