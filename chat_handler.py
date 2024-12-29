import gc  # for garbage collection
import torch  # add this import
from utils.voice_tone_mapping import analyze_audio_tone, record_audio
from utils.dynamic_expression_mapping import DynamicExpressionMapper  # Import the new mapper
from utils.character_relationships import CharacterRelationshipManager  # Import the relationship manager
from utils.performance_metrics import track_performance
from utils.memory_manager import MemoryManager
from API.Oogabooga_Api_Support import generate_contextual_response
from utils.personalized_response import PersonalizedResponseGenerator
from textblob import TextBlob
import logging
from utils.logging import log_info, log_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatHandler:
    def __init__(self, memory_manager):
        log_info("Initializing ChatHandler.")
        self.memory_manager = memory_manager

    @track_performance
    def initialize_model(self):
        from utils.chat_learner import ChatLearner  # Moved import here
        # Initialize your model here
        self.chat_learner = ChatLearner()
        self.memory_handler = self.memory_manager
        self.response_generator = PersonalizedResponseGenerator(self.chat_learner, self.memory_handler)

    async def handle_message(self, user_id, message):
        log_info(f"Handling message from user: {user_id}.")
        # Check for YouTube URLs
        if "youtube.com" in message or "youtu.be" in message:
            video_context = self.video_processor.process_youtube_video(message)
        else:
            video_context = None
            
        # Get user context
        user_context = self.memory_manager.get_recent_interactions(user_id)
        
        # Generate response
        response = generate_contextual_response(
            message,
            user_context,
            video_context
        )
        
        # Store interaction
        self.memory_manager.store_interaction(
            user_id,
            message,
            response,
            video_context
        )
        
        return response

    def process_audio_input(self):
        """Process audio input to determine tone and generate response."""
        audio_data = record_audio()
        tone = analyze_audio_tone(audio_data)
        # Use the tone to adjust the response
        return tone

    def generate_response_with_expression(self, user_id, message):
        """Generate a response with an expression based on user emotion."""
        emotion = self.analyze_user_emotion(message)  # Assume this method exists
        expression = self.expression_mapper.get_expression(emotion)
        response = self.chat_response(message)
        return f"{response} {expression}"  # Append the expression to the response

    def update_relationship(self, character_a, character_b, interaction_type):
        """Update the relationship based on user interactions."""
        self.relationship_manager.update_relationship(character_a, character_b, interaction_type)

    def handle_user_message(self, user_id, message):
        log_info(f"User {user_id} sent a message: {message}")
        # Process the message...

def cleanup_resources():
    # Clear CUDA cache if GPU is available
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Force garbage collection
    gc.collect()