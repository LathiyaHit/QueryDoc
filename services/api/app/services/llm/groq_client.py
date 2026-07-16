"""
Groq — async streaming client.
Yields text tokens as they arrive so TTS can start immediately.
"""
from groq import AsyncGroq
from typing import AsyncGenerator
from app.core.config import settings

_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

MODEL = "llama-3.1-8b-instant"


async def stream_response(
    messages: list[dict],
    system_prompt: str,
) -> AsyncGenerator[str, None]:
    """Yield text tokens from Groq as they stream in."""
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    stream = await _client.chat.completions.create(
        model=MODEL,
        messages=full_messages,
        max_tokens=1024,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def get_full_response(
    messages: list[dict],
    system_prompt: str,
    tools: list[dict] | None = None,
) -> dict:
    """
    Non-streaming call — used for tool-use turns where we need
    the full response before deciding the next step.
    """
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    kwargs = dict(
        model=MODEL,
        messages=full_messages,
        max_tokens=1024,
    )
    if tools:
        kwargs["tools"] = tools

    response = await _client.chat.completions.create(**kwargs)
    message = response.choices[0].message
    
    return {
        "content": message.content if message.content else "",
        "tool_calls": message.tool_calls,
        "stop_reason": response.choices[0].finish_reason,
        "usage": response.usage.model_dump() if response.usage else {},
    }
