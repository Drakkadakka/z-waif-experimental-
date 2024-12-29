from typing import Dict, Any, Optional
import json
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PersonalityTemplate:
    name: str
    traits: Dict[str, float]
    behaviors: Dict[str, Any]
    created_at: datetime
    modified_at: datetime
    
class TemplateManager:
    def __init__(self):
        self.templates: Dict[str, PersonalityTemplate] = {}
        
    def create_template(self, name: str, traits: Dict[str, float], behaviors: Dict[str, Any]) -> PersonalityTemplate:
        template = PersonalityTemplate(
            name=name,
            traits=traits,
            behaviors=behaviors,
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        self.templates[name] = template
        return template
        
    def get_template(self, name: str) -> Optional[PersonalityTemplate]:
        return self.templates.get(name) 