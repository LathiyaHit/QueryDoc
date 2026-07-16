"""
Qdrant client wrapper — upsert and search user memories.
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


class VectorStore:
    def __init__(self):
        self._client = AsyncQdrantClient(url=settings.QDRANT_URL)

    async def ensure_collection(self):
        exists = await self._client.collection_exists(settings.QDRANT_COLLECTION)
        if not exists:
            await self._client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert(
        self,
        user_id: str,
        text: str,
        vector: list[float],
        metadata: dict,
    ) -> str:
        point_id = str(uuid.uuid4())
        await self._client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"user_id": user_id, "text": text, **metadata},
                )
            ],
        )
        return point_id

    async def search(
        self, user_id: str, query_vector: list[float], top_k: int = 5
    ) -> list[dict]:
        results = await self._client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id", match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=top_k,
            with_payload=True,
        )
        return [hit.payload for hit in results]
