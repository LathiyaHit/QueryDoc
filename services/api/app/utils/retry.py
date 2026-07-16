"""
Async retry decorator with exponential back-off.
Usage:
    @retry(max_attempts=3, base_delay=0.5)
    async def call_external_api():
        ...
"""
import asyncio
import functools
from typing import Callable


def retry(max_attempts: int = 3, base_delay: float = 0.5):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
            raise last_exc
        return wrapper
    return decorator
