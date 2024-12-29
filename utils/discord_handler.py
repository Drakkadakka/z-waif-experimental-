from ai_handler import AIHandler
from utils.performance_metrics import track_performance
import logging
from utils.logging import log_info, log_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DiscordHandler:
    def __init__(self):
        log_info("Initializing DiscordHandler.")
        self.ai = AIHandler()
        self.speak_shadowchats = True
        
    @track_performance
    async def process(self, message_data):
        """Process messages from Discord"""
        log_info(f"Processing message data: {message_data}.")
        try:
            print(f"Message Data: {message_data}")  # Debugging line
            if message_data.get('needs_ai_response', False):
                prompt = self._format_prompt(message_data['content'])
                response = await self.ai.generate_response(prompt)

                # Print formatted output to console
                print(f"------{message_data['author']}------")
                print(f"{message_data['content']}\n")
                print(f"------{self.ai.char_name}------")
                print(f"{response}\n")

                # Display in web UI chat (assuming you have a function to handle this)
                self.display_in_web_ui(message_data['author'], message_data['content'], response)

                if self.speak_shadowchats:
                    # Speak the shadow chat and the AI response
                    await self.speak_message(message_data['content'])  # Speak the shadow chat
                    await self.speak_message(response)  # Speak the AI response

                return response
        except Exception as e:
            print(f"Error processing message: {e}")
        return None
        
    @track_performance
    def _format_prompt(self, content):
        return f"User: {content}\nAssistant: " 

    async def speak_message(self, message):
        print(f"Speaking message: {message}")

    def display_in_web_ui(self, author, content, response):
        """Function to display messages in the web UI chat"""
        # This function should be implemented to send messages to your web UI
        print(f"Web UI Chat > {author}: {content}")  # Display user message in web UI format
        print(f"Web UI Chat > {self.ai.char_name}: {response}")  # Display AI response in web UI format