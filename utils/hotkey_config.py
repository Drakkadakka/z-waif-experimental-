from typing import Dict, Optional
import json
import logging
import keyboard
from dataclasses import dataclass, asdict

@dataclass
class HotkeyConfig:
    next_message: str = "RIGHT_ARROW"
    redo_message: str = "UP_ARROW"
    lock_system: str = "GRAVE" 
    lock_confirm: str = "BACKSLASH"
    toggle_speak: str = "RIGHT_CTRL"
    toggle_auto: str = "A"
    change_sensitivity: str = "S"
    soft_reset: str = "R"
    view_image: str = "C"
    cancel_image: str = "X"
    blank_message: str = "B"

class HotkeyManager:
    def __init__(self):
        self.config = HotkeyConfig()
        self.bound_keys: Dict[str, bool] = {}
        
    def load_config(self, config_path: str = "config/hotkeys.json"):
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
                self.config = HotkeyConfig(**config_dict)
        except FileNotFoundError:
            logging.info("No hotkey config found, using defaults")
            self.save_config(config_path)
            
    def save_config(self, config_path: str = "config/hotkeys.json"):
        with open(config_path, 'w') as f:
            json.dump(asdict(self.config), f, indent=2)
            
    def bind_hotkeys(self):
        try:
            # Clear any existing bindings
            for key in self.bound_keys:
                keyboard.unhook_key(key)
            self.bound_keys.clear()
            
            # Bind new hotkeys
            bindings = {
                self.config.next_message: "next_input",
                self.config.redo_message: "redo_input",
                self.config.lock_system: "lock_inputs",
                self.config.lock_confirm: "input_lock_backslash",
                self.config.toggle_speak: "speak_input_toggle",
                self.config.toggle_auto: "input_toggle_autochat",
                self.config.change_sensitivity: "input_change_listener_sensitivity",
                self.config.soft_reset: "input_soft_reset",
                self.config.view_image: "input_view_image",
                self.config.cancel_image: "input_cancel_image",
                self.config.blank_message: "input_send_blank"
            }
            
            for key, func_name in bindings.items():
                try:
                    keyboard.on_press_key(key, lambda _: getattr(self, func_name)())
                    self.bound_keys[key] = True
                except Exception as e:
                    logging.error(f"Failed to bind key {key}: {e}")
                    
        except Exception as e:
            logging.error(f"Error binding hotkeys: {e}")
            # Continue running even if hotkeys fail 