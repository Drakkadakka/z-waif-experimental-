import json
from pathlib import Path
from datetime import datetime
import re

class ChatLearner:
    def __init__(self, chat_file="chat_learning.json"):
        self.data_dir = Path("data")
        self.chat_file = self.data_dir / chat_file
        self.chat_data = self._load_chat_data()
        
    def _load_chat_data(self):
        """Load existing chat data or create new structure"""
        self.data_dir.mkdir(exist_ok=True)
        try:
            with open(self.chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "messages": [],
                "patterns": {},
                "user_interactions": {},
                "common_phrases": {},
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_messages": 0
                }
            }

    def _save_chat_data(self):
        """Save chat data to file"""
        self.chat_data["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.chat_file, 'w', encoding='utf-8') as f:
            json.dump(self.chat_data, f, indent=4)

    def learn_from_message(self, message_data):
        """
        Learn from a new chat message
        message_data: dict containing message details
        """
        # Add to messages history
        self.chat_data["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "content": message_data["content"],
            "author": message_data["author"],
            "platform": message_data["platform"]
        })

        # Update user interactions
        user = message_data["author"]
        if user not in self.chat_data["user_interactions"]:
            self.chat_data["user_interactions"][user] = {
                "message_count": 0,
                "common_phrases": {},
                "first_seen": datetime.now().isoformat()
            }
        
        self.chat_data["user_interactions"][user]["message_count"] += 1

        # Learn common phrases
        words = message_data["content"].lower().split()
        for i in range(len(words)-1):
            phrase = f"{words[i]} {words[i+1]}"
            if phrase not in self.chat_data["common_phrases"]:
                self.chat_data["common_phrases"][phrase] = 0
            self.chat_data["common_phrases"][phrase] += 1

        # Update metadata
        self.chat_data["metadata"]["total_messages"] += 1

        # Save updates
        self._save_chat_data()

    def get_chat_insights(self):
        """Return insights about the chat"""
        return {
            "total_messages": self.chat_data["metadata"]["total_messages"],
            "unique_users": len(self.chat_data["user_interactions"]),
            "top_phrases": sorted(
                self.chat_data["common_phrases"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }

    def get_user_stats(self, username):
        """Get statistics for a specific user"""
        if username in self.chat_data["user_interactions"]:
            return self.chat_data["user_interactions"][username]
        return None 