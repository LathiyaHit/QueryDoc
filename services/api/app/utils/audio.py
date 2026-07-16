"""
Audio format helpers — PCM conversion, chunking, silence detection.
"""
import numpy as np


def pcm_to_float32(pcm_bytes: bytes) -> np.ndarray:
    """Convert 16-bit PCM bytes → normalised float32 array."""
    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    return audio / 32_768.0


def float32_to_pcm(audio: np.ndarray) -> bytes:
    """Convert normalised float32 array → 16-bit PCM bytes."""
    return (audio * 32_767).astype(np.int16).tobytes()


def chunk_audio(audio: bytes, chunk_size: int = 4096) -> list[bytes]:
    """Split a large audio buffer into fixed-size chunks."""
    return [audio[i : i + chunk_size] for i in range(0, len(audio), chunk_size)]


def is_silent(pcm_bytes: bytes, threshold: float = 0.01) -> bool:
    """Return True if the chunk is below the silence threshold."""
    if not pcm_bytes:
        return True
    audio = pcm_to_float32(pcm_bytes)
    rms = float(np.sqrt(np.mean(audio ** 2)))
    return rms < threshold
