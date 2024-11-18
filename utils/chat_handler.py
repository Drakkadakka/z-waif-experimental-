import gc  # for garbage collection
import torch  # add this import
from utils.voice_tone_mapping import analyze_audio_tone, record_audio
from utils.dynamic_expression_mapping import DynamicExpressionMapper  # Import the new mapper
from utils.character_relationships import CharacterRelationshipManager  # Import the relationship manager

class ChatHandler:
    def __init__(self):
        self.message_cache = []
        self.max_cache_size = 50  # Adjust based on your needs
        self.model = self.initialize_model()  # Add model initialization
        self.expression_mapper = DynamicExpressionMapper()  # Initialize the expression mapper
        self.relationship_manager = CharacterRelationshipManager()  # Initialize the relationship manager
        
    def initialize_model(self):
        # Initialize your model here
        pass

    def chat_response(self, message):
        try:
            response = self.model.generate(...)  # Use self.model instead of model
            cleanup_resources()
            return response
        except Exception as e:
            cleanup_resources()
            raise e

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

def cleanup_resources():
    # Clear CUDA cache if GPU is available
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Force garbage collection
    gc.collect()