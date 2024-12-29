from chat.learner import ChatLearner
from utils.memory_handler import MemoryHandler
from datetime import datetime
from textblob import TextBlob
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PersonalizedResponseGenerator:
    def __init__(self, memory_manager, chat_learner):
        logging.info("Initializing PersonalizedResponseGenerator.")
        self.memory_manager = memory_manager
        self.chat_learner = chat_learner
        self.memory_handler = memory_manager

    async def generate_response(self, user_id, message, platform):
        logging.info(f"Generating response for user: {user_id}.")
        # Get user context and history
        user_context = self.memory_handler.get_user_context(user_id)
        emotional_history = self.chat_learner.get_emotional_state(user_id)
        
        if not user_context:
            # New user
            response = await self._generate_new_user_response(message)
        else:
            # Existing user
            response = await self._generate_personalized_response(user_id, message, user_context)
            
        # Analyze message sentiment
        sentiment = TextBlob(message).sentiment
        
        # Store interaction
        self.memory_manager.add_memory(
            user_id=user_id,
            context={
                'message': message,
                'response': response,
                'sentiment': sentiment.polarity
            },
            platform=platform,
            emotion=sentiment.polarity,
            interaction_type='chat'
        )
        
        return response
        
    async def _generate_personalized_response(self, user_id, message, user_context):
        # Get recent interactions
        recent_interactions = user_context['interactions'][-5:]
        
        # Build context string
        context = f"""User Profile:
First interaction: {user_context['first_interaction']}
Total interactions: {len(user_context['interactions'])}
Recent context: {recent_interactions}
"""
        
        # Generate response using chat learner with context
        response = await self.chat_learner.generate_response(message, context)
        return response

    async def _generate_new_user_response(self, message):
        return await self.chat_learner.generate_response(message, "New user interaction")
