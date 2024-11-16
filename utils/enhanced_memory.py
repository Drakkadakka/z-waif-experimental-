from chat.learner import ChatLearner
from memory.manager import MemoryManager
from datetime import datetime

class EnhancedMemorySystem:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.chat_learner = ChatLearner()
        
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
        
        return context 