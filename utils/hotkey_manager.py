from typing import Dict, Callable, Optional
import keyboard
import logging
from utils.config import Config
from utils.error_boundary import ErrorBoundary

class HotkeyManager:
    def __init__(self):
        self.active_hotkeys = set()
        self.config = Config()
        self.config.load()
        self.bound_hotkeys = {}

    @ErrorBoundary.component()
    def setup_hotkeys(self):
        hotkey_mappings = {
            self.config.hotkeys.send_message: self._handle_send,
            self.config.hotkeys.interrupt: self._handle_interrupt,
            self.config.hotkeys.reroll: self._handle_reroll,
            self.config.hotkeys.toggle_stream: self._handle_toggle_stream
        }
        
        for hotkey, handler in hotkey_mappings.items():
            try:
                keyboard.add_hotkey(hotkey, handler, suppress=True)
                self.bound_hotkeys[hotkey] = handler
            except Exception as e:
                logging.warning(f"Failed to bind hotkey {hotkey}: {e}")
                continue  # Skip failed hotkey but continue with others

    def cleanup(self):
        for hotkey in self.bound_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except:
                pass

    def _handle_send(self):
        if "send" not in self.active_hotkeys:
            self.active_hotkeys.add("send")
            # Handle send action
            self.active_hotkeys.remove("send") 