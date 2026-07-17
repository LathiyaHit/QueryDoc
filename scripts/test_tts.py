"""
Play TTS output locally to verify audio quality.
Run: python scripts/test_tts.py "Hello, this is a test."
"""
import asyncio
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/api"))


async def test_tts(text: str):
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

    from app.services.tts.elevenlabs_client import ElevenLabsTTS

    tts = ElevenLabsTTS()
    chunks = []
    async for chunk in tts.stream_audio(text):
        chunks.append(chunk)

    audio = b"".join(chunks)
    out_path = "/tmp/tts_test.mp3"
    with open(out_path, "wb") as f:
        f.write(audio)
    print(f"Audio saved to {out_path} ({len(audio)} bytes)")
    print("Play with: mpv /tmp/tts_test.mp3")


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello! I am your voice assistant."
    asyncio.run(test_tts(text))
