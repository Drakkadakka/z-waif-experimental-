from typing import Dict, Any
import json
import logging

class ConfigManager:
    def __init__(self):
        self.default_config = {
            "stopping_strings": ["[END]", "[STOP]", "[DONE]"],
            "primary_color": "blue",
            "hotkeys": {
                "send_message": "enter",
                "interrupt": "esc",
                "reroll": "ctrl+r",
                "clear": "ctrl+l"
            },
            "ui_theme": {
                "border_color": "#2e2e2e",
                "button_color": "#2e2e2e",
                "checkbox_color": "#2e2e2e"
            }
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        try:
            with open('config.json', 'r') as f:
                user_config = json.load(f)
                return {**self.default_config, **user_config}
        except FileNotFoundError:
            logging.info("No config file found, using defaults")
            return self.default_config.copy()

    def save_config(self) -> None:
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_setting(self, key: str) -> Any:
        return self.config.get(key, self.default_config.get(key)) 