"""
MemoryManager — high-level API for reading and writing user memories.
Used by the orchestrator to build system prompts and store new facts.
"""
from app.services.memory.vector_store import VectorStore
from app.services.memory.embedder import embed
from app.services.memory.extractor import extract_facts
from app.services.llm.prompt_builder import build_system_prompt
from app.utils.logger import log


class MemoryManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._store = VectorStore()
        self._ready = False

    async def _ensure_ready(self):
        if not self._ready:
            await self._store.ensure_collection()
            self._ready = True

    async def build_system_prompt(
        self,
        current_query: str = "",
        emotion_label: str = "calm",
        rag_context: str = "",
        rag_source: str = "none",
    ) -> str:
        memories = []
        try:
            await self._ensure_ready()
            if current_query:
                vec = await embed(current_query)
                memories = await self._store.search(self.user_id, vec, top_k=5)
        except Exception as exc:
            log.warning(
                "memory.unavailable",
                user_id=self.user_id,
                error_type=exc.__class__.__name__,
                error=str(exc),
            )
        return build_system_prompt(memories, emotion_label, rag_context, rag_source)

    async def extract_and_store(self, conversation_turn: str):
        """Extract facts from a conversation turn and store them in Qdrant."""
        try:
            await self._ensure_ready()
            facts = await extract_facts(conversation_turn)
            for fact in facts:
                vec = await embed(fact["text"])
                await self._store.upsert(
                    self.user_id,
                    fact["text"],
                    vec,
                    {"category": fact.get("category", "general")},
                )
                log.debug("memory.stored", user_id=self.user_id, text=fact["text"])
        except Exception as exc:
            log.warning(
                "memory.store_failed",
                user_id=self.user_id,
                error_type=exc.__class__.__name__,
                error=str(exc),
            )
