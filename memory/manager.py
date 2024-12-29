from datetime import datetime
import json
import os

class MemoryManager:
    def __init__(self, memory_file="user_memories.json"):
        self.memory_file = memory_file
        self.memories = self._load_memories()
        
    def _load_memories(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {}

    def add_memory(self, user_id, context, platform, emotion=None, interaction_type=None):
        if user_id not in self.memories:
            self.memories[user_id] = {
                'first_interaction': datetime.now().isoformat(),
                'interactions': [],
                'preferences': {},
                'emotional_history': [],
                'topics_of_interest': set()
            }
            
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'platform': platform,
            'emotion': emotion,
            'interaction_type': interaction_type
        }
        
        self.memories[user_id]['interactions'].append(interaction)
        self._save_memories()
        
    def get_user_context(self, user_id):
        if user_id not in self.memories:
            return None
        return self.memories[user_id]
        
    def _save_memories(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=4)