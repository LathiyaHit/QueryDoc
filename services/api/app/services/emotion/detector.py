"""
Voice emotion detector using librosa prosodic features.
Analyses pitch, energy, and zero-crossing rate to infer user mood.
"""
import numpy as np
import librosa
from dataclasses import dataclass


@dataclass
class EmotionResult:
    valence: float    # -1.0 (negative) → +1.0 (positive)
    energy: float     #  0.0 (calm)     →  1.0 (energetic)
    label: str        # "calm" | "happy" | "excited" | "frustrated" | "stressed"


class VoiceEmotionDetector:
    SAMPLE_RATE = 16_000

    def analyze(self, pcm_bytes: bytes) -> EmotionResult:
        audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
        audio = audio / 32_768.0

        if len(audio) < self.SAMPLE_RATE * 0.1:
            return EmotionResult(valence=0.0, energy=0.5, label="calm")

        # Feature extraction
        rms = float(np.sqrt(np.mean(audio ** 2)))
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(audio)))

        pitches, magnitudes = librosa.piptrack(y=audio, sr=self.SAMPLE_RATE)
        voiced = pitches[magnitudes > np.max(magnitudes) * 0.1]
        pitch_mean = float(np.mean(voiced)) if voiced.size > 0 else 0.0
        pitch_var  = float(np.var(voiced))  if voiced.size > 0 else 0.0

        # Heuristic scoring (replace with a trained model in production)
        energy  = min(rms * 12.0, 1.0)
        valence = 0.0
        valence += 0.3 if pitch_mean > 180 else -0.2
        valence += 0.2 if pitch_var  > 3000 else 0.0
        valence += 0.1 if zcr        > 0.08  else 0.0
        valence = max(-1.0, min(1.0, valence))

        label = (
            "excited"    if energy > 0.65 and valence >  0.3 else
            "happy"      if energy > 0.35 and valence >  0.3 else
            "frustrated" if energy > 0.55 and valence < -0.1 else
            "stressed"   if energy > 0.45 and valence < -0.2 else
            "calm"
        )
        return EmotionResult(valence=valence, energy=energy, label=label)
