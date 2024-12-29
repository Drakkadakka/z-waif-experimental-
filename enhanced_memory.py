from chat.learner import ChatLearner
from memory.manager import MemoryManager
from datetime import datetime
from utils.contextual_memory import ContextualMemory
from utils.character_relationships import CharacterRelationshipManager
from utils.chat_history import update_chat_history
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnhancedMemorySystem:
    def __init__(self):
        logging.info("Initializing EnhancedMemorySystem.")
        self.memory_manager = MemoryManager()
        self.chat_learner = ChatLearner()
        self.contextual_memory = ContextualMemory()
        self.relationship_manager = CharacterRelationshipManager()  # Initialize relationship manager

    async def process_interaction(self, message_data, platform):
        logging.info(f"Processing interaction for platform: {platform}.")
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

        # Update chat history
        await update_chat_history(message_data["author"], platform, message_data["content"], "AI response here")  # Replace with actual AI response

        # Update relationships based on interaction
        self.relationship_manager.update_relationship(message_data["author"], message_data["recipient"], message_data["interaction_type"])

        return context

    def prune_old_context(self):
        """Automatically prune old context data."""
        self.contextual_memory.prune_old_context()
        self.relationship_manager.prune_old_relationships()  # Prune old relationships