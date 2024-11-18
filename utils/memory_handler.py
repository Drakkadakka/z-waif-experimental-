import json
import os
from datetime import datetime, timedelta

class MemoryHandler:
    def __init__(self, platform, memory_file="user_memories.json"):
        self.platform = platform
        self.memory_file = memory_file
        self.memories = self._load_memories()
        self._clean_old_memories()
        
    def _load_memories(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {}
        
    def save_memories(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
            
    def _clean_old_memories(self):
        current_time = datetime.now()
        one_year_ago = current_time - timedelta(days=365)
        
        for user_id in list(self.memories.keys()):
            # Filter interactions older than one year
            self.memories[user_id]["interactions"] = [
                interaction for interaction in self.memories[user_id]["interactions"]
                if datetime.fromisoformat(interaction["timestamp"]) > one_year_ago
            ]
            
            # Clean conversation history based on timestamps in interactions
            if self.memories[user_id]["interactions"]:
                recent_interactions = self.memories[user_id]["interactions"][-50:]  # Keep last 50 for context
                self.memories[user_id]["conversation_history"] = [
                    f"User: {interaction['content']}" 
                    for interaction in recent_interactions
                ]
        
        self.save_memories()
    
    def update_user_memory(self, user_id, interaction_data):
        current_time = datetime.now()
        
        if user_id not in self.memories:
            self.memories[user_id] = {
                "first_seen": current_time.isoformat(),
                "interactions": [],
                "preferences": {},
                "conversation_history": []
            }
        
        # Add new interaction
        self.memories[user_id]["interactions"].append({
            "timestamp": current_time.isoformat(),
            "content": interaction_data["content"],
            "context": interaction_data.get("context", ""),
            "emotion": interaction_data.get("emotion", "")
        })
        
        # Clean old memories for this user
        self._clean_old_memories()
        
    def get_user_context(self, user_id):
        if user_id not in self.memories:
            return "This is a new user."
            
        memory = self.memories[user_id]
        recent_interactions = memory["conversation_history"]
        return "\n".join([
            f"User history context:",
            f"First seen: {memory['first_seen']}",
            f"Recent conversation:",
            "\n".join(recent_interactions)
        ]) 