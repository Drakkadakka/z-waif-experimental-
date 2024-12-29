from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import logging

@dataclass
class PersonalityTemplate:
    name: str
    base_traits: Dict[str, float]
    emotional_responses: Dict[str, List[str]]
    voice_parameters: Dict[str, float]
    interaction_style: Dict[str, Any]

class PersonalityTemplateManager:
    def __init__(self):
        self.templates: Dict[str, PersonalityTemplate] = {}
        
    def load_template(self, template_name: str) -> Optional[PersonalityTemplate]:
        try:
            with open(f"templates/{template_name}.json", "r") as f:
                data = json.load(f)
                return PersonalityTemplate(**data)
        except Exception as e:
            logging.error(f"Failed to load template {template_name}: {e}")
            return None
            
    def save_template(self, template: PersonalityTemplate):
        try:
            with open(f"templates/{template.name}.json", "w") as f:
                json.dump(template.__dict__, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save template {template.name}: {e}") 