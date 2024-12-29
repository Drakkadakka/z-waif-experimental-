from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class EmotionIntensity(Enum):
    LOW = 0.33
    MEDIUM = 0.66
    HIGH = 1.0

@dataclass
class ExpressionConfig:
    base_expression: str
    intensity: EmotionIntensity
    modifiers: Dict[str, float]
    blend_duration: float = 0.5

class DynamicExpressionMapper:
    def __init__(self):
        self.expression_configs: Dict[str, ExpressionConfig] = {}
        self.current_expression: Optional[str] = None
        
    async def map_emotion_to_expression(self, emotion: str, intensity: float) -> ExpressionConfig:
        base_config = self.expression_configs.get(emotion)
        if not base_config:
            logging.warning(f"No expression config found for emotion: {emotion}")
            return self.get_default_expression()
            
        # Adjust intensity based on input
        adjusted_intensity = EmotionIntensity.MEDIUM
        if intensity > 0.7:
            adjusted_intensity = EmotionIntensity.HIGH
        elif intensity < 0.3:
            adjusted_intensity = EmotionIntensity.LOW
            
        return ExpressionConfig(
            base_expression=base_config.base_expression,
            intensity=adjusted_intensity,
            modifiers={k: v * intensity for k, v in base_config.modifiers.items()}
        ) 