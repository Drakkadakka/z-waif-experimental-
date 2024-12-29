from typing import Dict, Any, List
import logging
from datetime import datetime
from dataclasses import dataclass

@dataclass
class PersonalityTrait:
    name: str
    value: float
    confidence: float
    last_updated: datetime

class PersonalityManager:
    def __init__(self):
        self.traits: Dict[str, PersonalityTrait] = {}
        self.interaction_history: List[Dict[str, Any]] = []
        
    async def update_trait(self, trait_name: str, feedback_value: float, confidence: float = 1.0):
        if trait_name not in self.traits:
            self.traits[trait_name] = PersonalityTrait(
                name=trait_name,
                value=feedback_value,
                confidence=confidence,
                last_updated=datetime.now()
            )
        else:
            current = self.traits[trait_name]
            # Weighted average based on confidence
            new_value = (
                (current.value * current.confidence + feedback_value * confidence) /
                (current.confidence + confidence)
            )
            self.traits[trait_name] = PersonalityTrait(
                name=trait_name,
                value=new_value,
                confidence=min(current.confidence + confidence, 1.0),
                last_updated=datetime.now()
            )
            
    async def record_interaction(self, interaction_data: Dict[str, Any]):
        self.interaction_history.append({
            **interaction_data,
            'timestamp': datetime.now()
        })
        
    async def get_personality_profile(self) -> Dict[str, Any]:
        return {
            'traits': {name: trait.value for name, trait in self.traits.items()},
            'confidence_levels': {name: trait.confidence for name, trait in self.traits.items()}
        }