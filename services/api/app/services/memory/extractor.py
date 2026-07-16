"""
Uses Groq (Llama 3) to extract structured facts from conversation turns.
Fast and cheap — runs after each turn off the hot path.
"""
import json
from groq import AsyncGroq
from app.core.config import settings

_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

EXTRACT_SYSTEM = """Extract factual personal information from the conversation turn.
Return ONLY valid JSON in this exact format — no other text:
{"facts": [{"text": "...", "category": "preference|habit|goal|personality|context"}]}
Return {"facts": []} if nothing notable is present."""


async def extract_facts(conversation_turn: str) -> list[dict]:
    """Returns a list of {text, category} dicts."""
    try:
        response = await _client.chat.completions.create(
            model="llama3-8b-8192",
            max_tokens=512,
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM},
                {"role": "user", "content": conversation_turn}
            ],
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)
        return data.get("facts", [])
    except (json.JSONDecodeError, Exception):
        return []
