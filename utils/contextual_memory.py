import json
import os
from datetime import datetime, timedelta
from chat.learner import ChatLearner
from memory.manager import MemoryManager

class ContextualMemory:
    def __init__(self, memory_file="user_context_memory.json"):
        self.memory_file = memory_file
        self.context_memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.context_memory, f, indent=2)

    def update_context(self, user_id, context_data):
        if user_id not in self.context_memory:
            self.context_memory[user_id] = {
                "last_updated": datetime.now().isoformat(),
                "context": []
            }
        self.context_memory[user_id]["context"].append(context_data)
        self.context_memory[user_id]["last_updated"] = datetime.now().isoformat()
        self.save_memory()

    def get_context(self, user_id):
        return self.context_memory.get(user_id, {"context": [], "last_updated": None})

    def clear_context(self, user_id):
        if user_id in self.context_memory:
            del self.context_memory[user_id]
            self.save_memory()

    def prune_old_context(self):
        """Remove context data older than 365 days."""
        one_year_ago = datetime.now() - timedelta(days=365)
        for user_id in list(self.context_memory.keys()):
            last_updated = datetime.fromisoformat(self.context_memory[user_id]["last_updated"])
            if last_updated < one_year_ago:
                self.clear_context(user_id)
class EnhancedMemorySystem:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.chat_learner = ChatLearner()
        self.contextual_memory = ContextualMemory()

    async def process_interaction(self, message_data, platform):
        """Process and store interaction data with enhanced context"""
        # Learn from message
        self.chat_learner.learn_from_message(message_data)
        
        # Extract context
        context = {
            "mood": self.analyze_mood(message_data["content"]),
            "topics": self.extract_topics(message_data["content"]),
            "interaction_style": self.analyze_interaction_style(message_data),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store memory
        self.memory_manager.add_memory(
            message_data["author"],
            context,
            platform
        )
        
        # Update contextual memory
        self.contextual_memory.update_context(message_data["author"], context)
        
        return context

    def prune_old_context(self):
        """Automatically prune old context data."""
        self.contextual_memory.prune_old_context()

# Example usage of the EnhancedMemorySystem
if __name__ == "__main__":
    memory_system = EnhancedMemorySystem()
    # You can call memory_system.prune_old_context() periodically to clean up old context data

