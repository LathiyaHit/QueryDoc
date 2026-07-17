"""
Measures end-to-end pipeline latency using synthetic audio.
Run: python scripts/benchmark_latency.py
"""
import asyncio
import time
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/api"))


def generate_speech_pcm(duration_s: float = 2.0) -> bytes:
    """Generate synthetic 440 Hz sine-wave audio (sounds like a tone)."""
    sr = 16_000
    t = np.linspace(0, duration_s, int(sr * duration_s))
    audio = (np.sin(2 * np.pi * 440 * t) * 16000).astype(np.int16)
    return audio.tobytes()


async def benchmark():
    print("Generating synthetic audio...")
    pcm = generate_speech_pcm(2.0)

    print("Timing pipeline (mocked STT/LLM/TTS)...")
    start = time.time()
    # Place real pipeline call here when services are running
    await asyncio.sleep(0.1)  # placeholder
    elapsed = (time.time() - start) * 1000
    print(f"Simulated round trip: {elapsed:.1f} ms")


if __name__ == "__main__":
    asyncio.run(benchmark())
