from chat.learner import ChatLearner
from utils.memory_handler import MemoryHandler

class PersonalizedResponseGenerator:
    def __init__(self):
        self.chat_learner = ChatLearner()
        self.memory_handler = MemoryHandler(platform="default")

    def generate_response(self, user_id, user_message):
        """Generate a personalized response based on user profile and message context."""
        profile = self.chat_learner.get_user_profile(user_id)
        if profile:
            personality = profile[0]
            if personality == 'Friendly':
                return f"{user_message} 😊 How can I assist you further?"
            elif personality == 'Formal':
                return f"{user_message} How may I assist you today?"
            else:
                return f"{user_message} I'm here to help!"
        else:
            return f"{user_message} I'm not sure how to respond to that."

    def get_user_context(self, user_id):
        """Retrieve the user's context for more tailored responses."""
        return self.memory_handler.get_user_context(user_id)
