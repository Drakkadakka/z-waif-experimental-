# Support for playing Minecraft!

import logging
from typing import Optional, List
import json
import time
import os
from utils.logging import log_info, log_error
from utils.settings import minecraft_enabled

# Configure logging
logging.basicConfig(level=logging.INFO)

class MinecraftIntegration:
    def __init__(self):
        self.chat = None
        self.enabled = False
        self.mc_names = []
        self.mc_username = ""
        self.mc_username_follow = ""
        self.last_chat = "None!"
        self.remembered_messages = ["", "Minecraft Chat Loaded!"]
        self.api = None
        self.load_config()
        self._init_api()
        
    def _init_api(self):
        """Initialize API support with fallback"""
        try:
            import API.Oogabooga_Api_Support as api
            self.api = api
            log_info("Oogabooga API loaded successfully")
        except ImportError:
            log_error("Oogabooga API not available - chat features limited")
            self.api = None

    def minecraft_chat(self):
        """Send chat with API fallback"""
        if not self.enabled or not self.chat:
            return False
            
        try:
            if self.api:
                message = self.api.receive_via_oogabooga()
                return self.send_message(message)
            else:
                log_error("Cannot send chat - API not available")
                return False
        except Exception as e:
            log_error(f"Error in minecraft chat: {e}")
            return False

    def load_config(self) -> None:
        """Load Minecraft configuration files"""
        try:
            with open("Configurables/MinecraftNames.json", 'r') as f:
                self.mc_names = json.load(f)
            with open("Configurables/MinecraftUsername.json", 'r') as f:
                self.mc_username = json.load(f)
            with open("Configurables/MinecraftUsernameFollow.json", 'r') as f:
                self.mc_username_follow = json.load(f)
            log_info("Minecraft configuration loaded successfully")
        except Exception as e:
            log_error(f"Failed to load Minecraft configuration: {e}")

    def connect(self) -> bool:
        if not minecraft_enabled:
            return False
            
        try:
            from pythmc import ChatLink
            self.chat = ChatLink()
            self.enabled = True
            log_info("Connected to Minecraft successfully")
            return True
        except Exception as e:
            log_error(f"Failed to connect to Minecraft: {e}")
            self.enabled = False
            return False

    def send_message(self, message: str) -> bool:
        """Send message to Minecraft chat"""
        if not self.enabled or not self.chat:
            return False
        try:
            self.chat.send(message)
            return True
        except Exception as e:
            log_error(f"Failed to send Minecraft message: {e}")
            return False

    def check_for_command(self, message: str) -> None:
        """Process potential Minecraft commands"""
        if not self.enabled:
            return
            
        if "#" in message or "/" in message:
            word_collector = ""
            word_collector_on = False

            for char in message:
                if char in ["#", "/"]:
                    word_collector_on = True
                if word_collector_on:
                    if char == "\"":
                        word_collector_on = False
                    else:
                        word_collector += char

            if "#follow" in word_collector:
                word_collector = f"#follow player {self.mc_username_follow}"
            elif "#drop" in word_collector:
                word_collector = ".drop"

            self.send_message(word_collector)

    def get_chat_history(self) -> List[str]:
        """Get Minecraft chat history safely"""
        if not self.enabled or not self.chat:
            return []
        try:
            messages = self.chat.get_history(limit=10)
            return messages if messages else []
        except Exception as e:
            log_error(f"Failed to get Minecraft chat history: {e}")
            return []

# Create singleton instance
minecraft = MinecraftIntegration()

def initialize():
    """Initialize Minecraft integration if possible"""
    return minecraft.connect()

def send_chat(message: str) -> bool:
    """Send chat message if Minecraft is available"""
    return minecraft.send_message(message)

def check_minecraft_window() -> bool:
    """Check if Minecraft window is open"""
    try:
        import pygetwindow
        return any('minecraft' in win.title.lower() for win in pygetwindow.getAllWindows())
    except:
        return False

