"""
VoicePipeline — the core engine.

Flow (fully streaming):
  PCM audio → VAD → Deepgram STT → Groq LLM → streamed text
"""
import asyncio
from typing import AsyncGenerator, TypedDict

from app.services.pipeline.vad import SileroVAD
from app.services.pipeline.latency_tracker import LatencyTracker
from app.services.stt.router import get_stt_client
from app.services.llm.groq_client import stream_response
from app.services.memory.manager import MemoryManager
from app.services.rag.retriever import retrieve_context
from app.utils.logger import log


class PipelineEvent(TypedDict, total=False):
    type: str
    text: str


class VoicePipeline:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.vad = SileroVAD()
        self.stt = get_stt_client()
        self.memory = MemoryManager(user_id)
        self.tracker = LatencyTracker()
        self.conversation: list[dict] = []
        self.audio_buffer: list[bytes] = []

    async def start(self):
        await self.stt.connect()
        log.info("pipeline.started", user_id=self.user_id)

    async def process_audio_chunk(
        self, pcm: bytes
    ) -> AsyncGenerator[PipelineEvent, None]:
        is_speech, end_of_utt = self.vad.process_chunk(pcm)

        if is_speech:
            if not self.audio_buffer:
                self.tracker.start_turn()
            self.audio_buffer.append(pcm)
            await self.stt.send_audio(pcm)

        if end_of_utt and self.audio_buffer:
            transcript = await self._collect_transcript()
            if transcript and transcript.strip():
                yield {"type": "transcript", "text": transcript.strip()}
                async for event in self._generate_response(transcript.strip()):
                    yield event
            self.audio_buffer.clear()
            self.vad.reset()

    async def _collect_transcript(self) -> str:
        """Wait up to 800 ms for the final transcript from STT."""
        deadline = asyncio.get_event_loop().time() + 0.8
        text = ""
        while asyncio.get_event_loop().time() < deadline:
            result = await self.stt.get_transcript()
            if result:
                text = result["text"]
                if result["is_final"]:
                    self.tracker.mark("stt_done_ms")
                    break
            await asyncio.sleep(0.02)
        return text

    async def process_text_input(
        self, text: str
    ) -> AsyncGenerator[PipelineEvent, None]:
        """Handle a typed (non-voice) message — skips VAD/STT entirely."""
        text = text.strip()
        if not text:
            return
        self.tracker.start_turn()
        self.tracker.start_turn()
        async for event in self._generate_response(text):
            yield event

    async def _generate_response(
        self, user_text: str
    ) -> AsyncGenerator[PipelineEvent, None]:
        rag_context, rag_source = "", "none"
        try:
            rag_result = await retrieve_context(self.user_id, user_text)
            rag_context = rag_result["context_text"]
            rag_source = rag_result["source"]
        except Exception as exc:
            log.warning(
                "rag.unavailable",
                user_id=self.user_id,
                error_type=exc.__class__.__name__,
                error=str(exc),
            )

        yield {"type": "rag_source", "text": rag_source}

        system = await self.memory.build_system_prompt(
            user_text, rag_context=rag_context, rag_source=rag_source
        )
        self.conversation.append({"role": "user", "content": user_text})

        full_response = ""
        async for chunk in stream_response(self.conversation, system):
            full_response += chunk
            yield {"type": "response_delta", "text": chunk}
        
        yield {"type": "response_done"}
        self.conversation.append({"role": "assistant", "content": full_response})

    async def cleanup(self):
        await self.stt.close()
        log.info("pipeline.closed", user_id=self.user_id)
