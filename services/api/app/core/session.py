"""
WebSocket session manager backed by Redis.
Tracks active voice sessions per user.
"""
import json
import redis.asyncio as aioredis
from redis.exceptions import RedisError
from app.core.config import settings


class SessionManager:
    PREFIX = "session:"
    TTL = 3600  # 1 hour

    def __init__(self):
        self._redis = None

    async def _conn(self):
        if self._redis is None:
            self._redis = await aioredis.from_url(settings.REDIS_URL)
        return self._redis

    async def create(self, user_id: str, session_id: str) -> None:
        try:
            r = await self._conn()
            await r.setex(
                f"{self.PREFIX}{user_id}:{session_id}",
                self.TTL,
                json.dumps({"user_id": user_id, "session_id": session_id, "active": True}),
            )
        except RedisError:
            self._redis = None

    async def get(self, user_id: str, session_id: str) -> dict | None:
        try:
            r = await self._conn()
            data = await r.get(f"{self.PREFIX}{user_id}:{session_id}")
            return json.loads(data) if data else None
        except RedisError:
            self._redis = None
            return None

    async def delete(self, user_id: str, session_id: str) -> None:
        try:
            r = await self._conn()
            await r.delete(f"{self.PREFIX}{user_id}:{session_id}")
        except RedisError:
            self._redis = None
