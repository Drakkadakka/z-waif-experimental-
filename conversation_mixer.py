from typing import List, Dict, Any
import asyncio
from dataclasses import dataclass
import numpy as np

@dataclass
class ModelResponse:
    text: str
    confidence: float
    emotion: str
    context_relevance: float

class ConversationMixer:
    def __init__(self, model_weights: Dict[str, float] = None):
        self.model_weights = model_weights or {}
        self.context_history: List[Dict[str, Any]] = []
        
    async def mix_responses(self, responses: Dict[str, ModelResponse]) -> str:
        weighted_responses = []
        
        for model_name, response in responses.items():
            weight = self.model_weights.get(model_name, 1.0)
            score = self._calculate_response_score(response)
            weighted_responses.append((response.text, weight * score))
            
        # Select best response based on weighted scores
        best_response = max(weighted_responses, key=lambda x: x[1])[0]
        return best_response
        
    def _calculate_response_score(self, response: ModelResponse) -> float:
        return (
            response.confidence * 0.4 +
            response.context_relevance * 0.4 +
            (1.0 if response.emotion != "neutral" else 0.8) * 0.2
        ) 