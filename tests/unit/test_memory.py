"""Unit tests for memory extraction and storage."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_extract_facts_returns_list():
    with patch(
        "services.api.app.services.memory.extractor._client"
    ) as mock_client:
        mock_response = AsyncMock()
        mock_response.content = [
            MagicMock(text='{"facts": [{"text": "Likes Python", "category": "preference"}]}')
        ]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        from unittest.mock import MagicMock
        from services.api.app.services.memory.extractor import extract_facts
        facts = await extract_facts("User: I love Python programming.")
        assert isinstance(facts, list)
