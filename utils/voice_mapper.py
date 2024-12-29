from typing import Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class VoiceToneParameters:
    pitch: float
    speed: float
    volume: float
    emotion_intensity: float

class VoiceToneMapper:
    def __init__(self):
        self.tone_profiles: Dict[str, VoiceToneParameters] = {}
        
    def map_emotion_to_voice(self, emotion: str, intensity: float) -> VoiceToneParameters:
        base_profile = self.tone_profiles.get(emotion)
        if not base_profile:
            return self.get_default_profile()
            
        return VoiceToneParameters(
            pitch=base_profile.pitch * intensity,
            speed=base_profile.speed * (1 + (intensity - 0.5) * 0.2),
            volume=base_profile.volume * intensity,
            emotion_intensity=intensity
        ) 