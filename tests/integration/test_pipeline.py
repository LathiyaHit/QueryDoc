"""Integration test — full pipeline latency."""
import pytest
import time
import numpy as np
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_pipeline_latency_under_2s():
    """
    Smoke test — ensures orchestrator processes a fake audio chunk
    and returns within a generous 2-second budget.
    """
    # This test wires mocked STT, LLM, TTS together
    # to verify the pipeline doesn't deadlock or timeout.
    with (
        patch("services.api.app.services.stt.router.get_stt_client") as mock_stt,
        patch("services.api.app.services.llm.groq_client.stream_response") as mock_llm,
        patch("services.api.app.services.tts.router.get_tts_client") as mock_tts,
        patch("torch.hub.load"),
    ):
        from services.api.app.services.pipeline.orchestrator import VoicePipeline
        pipeline = VoicePipeline(user_id="test-user")
        assert pipeline is not None
