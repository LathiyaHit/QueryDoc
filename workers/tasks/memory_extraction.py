"""
Post-session memory extraction task.
Runs after each voice session to extract and persist facts.
"""
from workers.main import celery_app


@celery_app.task(name="tasks.memory_extraction.extract_session_memories")
def extract_session_memories(user_id: str, conversation_text: str):
    """
    Called by the pipeline after each session ends.
    Runs synchronously inside Celery — uses asyncio.run() for async calls.
    """
    import asyncio
    from app.services.memory.manager import MemoryManager

    manager = MemoryManager(user_id)
    asyncio.run(manager.extract_and_store(conversation_text))
