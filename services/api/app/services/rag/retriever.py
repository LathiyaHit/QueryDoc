"""
RAG retriever.

Decides, per session, whether to search the session's own uploaded
document or fall back to the shared default document — then embeds
the query, searches Qdrant, and formats the result for the prompt.
"""
from app.services.memory.embedder import embed
from app.services.rag.rag_vector_store import RagVectorStore

_store = RagVectorStore()


def get_rag_store() -> RagVectorStore:
    return _store


async def retrieve_context(session_id: str, query: str) -> dict:
    """
    Returns:
        {
            "chunks": list[dict],           # raw payloads (text + metadata)
            "context_text": str,            # formatted block ready for the prompt
            "source": "upload" | "default" | "none",
        }
    """
    has_upload = await _store.has_session_documents(session_id)
    use_default = not has_upload

    query_vector = await embed(query)
    chunks = await _store.search(
        query_vector=query_vector,
        session_id=session_id,
        use_default=use_default,
    )

    if not chunks:
        return {"chunks": [], "context_text": "", "source": "none"}

    return {
        "chunks": chunks,
        "context_text": _format_context(chunks),
        "source": "default" if use_default else "upload",
    }


def _format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered, cited context block."""
    lines = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk.get("source_file", "document")
        page = chunk.get("page")
        page_info = f", page {page + 1}" if page is not None else ""
        lines.append(f"[{i}] (from {source}{page_info})\n{chunk['text']}")
    return "\n\n".join(lines)