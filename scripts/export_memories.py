"""
Export all Qdrant memories for a given user.
Run: python scripts/export_memories.py <user_id>
"""
import asyncio
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/api"))


async def export(user_id: str):
    from app.services.memory.vector_store import VectorStore
    from app.services.memory.embedder import embed

    store = VectorStore()
    await store.ensure_collection()
    dummy_vec = await embed("general")
    memories = await store.search(user_id, dummy_vec, top_k=100)
    print(json.dumps(memories, indent=2))


if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "test-user"
    asyncio.run(export(user_id))
