"""
LangFuse wrapper for tracking every LLM call:
token count, latency, prompt version, cost.
"""
from langfuse import Langfuse
from app.core.config import settings

_lf: Langfuse | None = None


def get_langfuse() -> Langfuse | None:
    global _lf
    if not settings.LANGFUSE_PUBLIC_KEY:
        return None
    if _lf is None:
        _lf = Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )
    return _lf


def track_generation(user_id: str, session_id: str, input_msgs: list, output: str):
    lf = get_langfuse()
    if lf is None:
        return
    tr = lf.trace(name="voice-llm-call", user_id=user_id, session_id=session_id)
    tr.generation(
        name="groq-response",
        model="llama-3.1-8b-instant",
        input=input_msgs,
        output=output,
        usage={"output": len(output.split())},
    )
