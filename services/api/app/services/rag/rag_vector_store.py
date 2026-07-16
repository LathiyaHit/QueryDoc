"""
Qdrant client wrapper for the RAG knowledge base.

Every chunk is tagged with:
- session_id: which upload session it belongs to (None for the default PDF)
- is_default: True for the pre-loaded fallback PDF, False for user uploads

Retrieval prefers a session's own uploaded document; falls back to the
default document when the session hasn't uploaded anything.
"""
import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.core.config import settings
from app.services.memory.embedder import EMBEDDING_DIM
from app.services.rag.document_loader import DocChunk


class RagVectorStore:
    def __init__(self):
        self._client = AsyncQdrantClient(url=settings.QDRANT_URL)

    async def ensure_collection(self):
        exists = await self._client.collection_exists(settings.RAG_QDRANT_COLLECTION)
        if not exists:
            await self._client.create_collection(
                collection_name=settings.RAG_QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert_chunks(
        self,
        chunks: list[DocChunk],
        vectors: list[list[float]],
        session_id: str | None,
        is_default: bool = False,
    ) -> list[str]:
        """Bulk upsert chunks + their pre-computed embedding vectors."""
        assert len(chunks) == len(vectors), "chunks and vectors must be same length"

        points = []
        point_ids = []
        for chunk, vector in zip(chunks, vectors):
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "session_id": session_id,
                        "is_default": is_default,
                        "text": chunk.text,
                        **chunk.metadata,
                    },
                )
            )

        if points:
            await self._client.upsert(
                collection_name=settings.RAG_QDRANT_COLLECTION,
                points=points,
            )
        return point_ids

    async def has_session_documents(self, session_id: str) -> bool:
        """Check whether this session has uploaded its own PDF."""
        result = await self._client.count(
            collection_name=settings.RAG_QDRANT_COLLECTION,
            count_filter=Filter(
                must=[
                    FieldCondition(key="session_id", match=MatchValue(value=session_id)),
                    FieldCondition(key="is_default", match=MatchValue(value=False)),
                ]
            ),
            exact=True,
        )
        return result.count > 0

    async def delete_session_documents(self, session_id: str):
        """Remove a session's previously uploaded document (e.g. before a re-upload)."""
        await self._client.delete(
            collection_name=settings.RAG_QDRANT_COLLECTION,
            points_selector=Filter(
                must=[
                    FieldCondition(key="session_id", match=MatchValue(value=session_id)),
                    FieldCondition(key="is_default", match=MatchValue(value=False)),
                ]
            ),
        )
    
    async def delete_default_documents(self):
        """Remove the previously ingested default document (before re-ingesting)."""
        await self._client.delete(
            collection_name=settings.RAG_QDRANT_COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="is_default", match=MatchValue(value=True))]
            ),
        )

    async def search(
        self,
        query_vector: list[float],
        session_id: str | None,
        use_default: bool,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> list[dict]:
        """
        Search either this session's uploaded document (use_default=False)
        or the shared default document (use_default=True).
        """
        top_k = top_k or settings.RAG_TOP_K
        min_score = min_score if min_score is not None else settings.RAG_MIN_SCORE

        if use_default:
            query_filter = Filter(
                must=[FieldCondition(key="is_default", match=MatchValue(value=True))]
            )
        else:
            query_filter = Filter(
                must=[
                    FieldCondition(key="session_id", match=MatchValue(value=session_id)),
                    FieldCondition(key="is_default", match=MatchValue(value=False)),
                ]
            )

        results = await self._client.search(
            collection_name=settings.RAG_QDRANT_COLLECTION,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=min_score,
            with_payload=True,
        )
        return [hit.payload for hit in results]