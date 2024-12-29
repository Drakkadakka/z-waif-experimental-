from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import json

@dataclass
class HotkeyConfig:
    send_message: str = "enter"
    interrupt: str = "esc" 
    reroll: str = "ctrl+r"
    toggle_stream: str = "ctrl+s"

@dataclass
class UIConfig:
    primary_color: str = "blue"
    stopping_strings: List[str] = field(default_factory=lambda: ["User:", "Human:", "Assistant:"])
    enable_send_button: bool = True
    enable_streaming: bool = True
    rp_suppression: bool = True
    newline_cut: bool = True
    rp_suppression_threshold: int = 3  # Lowered threshold as per changelog
    
@dataclass
class Config:
    hotkeys: HotkeyConfig = field(default_factory=HotkeyConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    stopping_strings: Dict[str, List[str]] = field(default_factory=lambda: {
        "system": ["[System:", "[Assistant:", "[Human:"],
        "chat": ["User:", "Human:", "Assistant:"],
        "rp": ["*", "[", "]"]
    })
    max_tokens: int = 2000
    min_tokens: int = 10  # Added for message length warnings
    temperature: float = 0.7
    model_name: str = "default_model"
    enable_streaming: bool = True
    
    def load(self):
        try:
            with open('config.json', 'r') as f:
                config_data = json.load(f)
                self.hotkeys = HotkeyConfig(**config_data.get('hotkeys', {}))
                self.ui = UIConfig(**config_data.get('ui', {}))
        except FileNotFoundError:
            self.save()
            
    def save(self):
        with open('config.json', 'w') as f:
            json.dump({
                'hotkeys': asdict(self.hotkeys),
                'ui': asdict(self.ui)
            }, f, indent=2) 