"""
Maps detected emotion to a modifier string consumed by prompt_builder.
"""
from app.services.emotion.detector import VoiceEmotionDetector, EmotionResult


_detector = VoiceEmotionDetector()


def detect_emotion_label(pcm_bytes: bytes) -> str:
    """Analyse the audio buffer and return an emotion label."""
    if not pcm_bytes:
        return "calm"
    result: EmotionResult = _detector.analyze(pcm_bytes)
    return result.label
