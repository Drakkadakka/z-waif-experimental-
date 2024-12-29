from typing import Dict, Any, List
import json
from dataclasses import dataclass, asdict, field

@dataclass
class UIConfig:
    primary_color: str = "#0b9ed9"
    stopping_strings: List[str] = field(default_factory=lambda: [
        "Human:", "Assistant:", "User:"
    ])
    
class UIConfigManager:
    def __init__(self):
        self.config = UIConfig()
        
    def load_config(self, config_path: str = "config/ui_config.json"):
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
                self.config = UIConfig(**config_dict)
        except FileNotFoundError:
            self.save_config(config_path)
            
    def save_config(self, config_path: str = "config/ui_config.json"):
        with open(config_path, 'w') as f:
            json.dump(asdict(self.config), f, indent=2)
            
    def get_gradio_theme(self) -> Dict[str, Any]:
        return {
            "primary_hue": self.config.primary_color,
            "button_primary_background_fill": self.config.primary_color,
            "button_primary_background_fill_dark": self.config.primary_color
        } 