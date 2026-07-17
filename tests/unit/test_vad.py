"""Unit tests for SileroVAD wrapper."""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock


def make_pcm(duration_ms: int = 30, is_speech: bool = False) -> bytes:
    samples = int(16_000 * duration_ms / 1000)
    if is_speech:
        audio = np.random.randn(samples).astype(np.float32) * 0.5
    else:
        audio = np.zeros(samples, dtype=np.float32)
    return (audio * 32_767).astype(np.int16).tobytes()


@patch("torch.hub.load")
def test_silent_chunk_not_speech(mock_hub):
    mock_model = MagicMock()
    mock_model.return_value = MagicMock()
    mock_model.return_value.item.return_value = 0.1   # below threshold
    mock_hub.return_value = (mock_model, None)

    from services.api.app.services.pipeline.vad import SileroVAD
    vad = SileroVAD()
    is_speech, end_of_utt = vad.process_chunk(make_pcm(is_speech=False))
    assert is_speech is False
    assert end_of_utt is False


@patch("torch.hub.load")
def test_speech_chunk_detected(mock_hub):
    mock_model = MagicMock()
    mock_model.return_value = MagicMock()
    mock_model.return_value.item.return_value = 0.9   # above threshold
    mock_hub.return_value = (mock_model, None)

    from services.api.app.services.pipeline.vad import SileroVAD
    vad = SileroVAD()
    is_speech, _ = vad.process_chunk(make_pcm(is_speech=True))
    assert is_speech is True
