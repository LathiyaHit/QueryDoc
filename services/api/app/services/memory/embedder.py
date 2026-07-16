"""
Sentence-transformers MiniLM embedder.
Produces 384-dim vectors for semantic similarity search in Qdrant.
"""
from sentence_transformers import SentenceTransformer
import asyncio

_model: SentenceTransformer | None = None
EMBEDDING_DIM = 384


def _load_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")


async def embed(text: str) -> list[float]:
    """Return embedding vector for text (runs in thread pool)."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _load_model)
    vector = await loop.run_in_executor(None, lambda: _model.encode(text).tolist())
    return vector
