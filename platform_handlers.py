from minecraft_handler import MinecraftHandler
from discord_handler import DiscordHandler
from twitch_handler import TwitchHandler
from utils.personalized_response import PersonalizedResponseGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PlatformManager:
    def __init__(self, memory_manager, chat_learner):
        logging.info("Initializing PlatformManager.")
        self.response_generator = PersonalizedResponseGenerator(memory_manager, chat_learner)
        self.handlers = {
            "twitch": TwitchHandler(self.response_generator),
            "discord": DiscordHandler(self.response_generator),
            "minecraft": MinecraftHandler(self.response_generator)
        }
    
    async def handle_message(self, message_data):
        logging.info(f"Handling message data: {message_data}.")
        """Route messages to appropriate platform handlers"""
        platform = message_data.get("platform")
        if platform in self.handlers:
            return await self.handlers[platform].process(message_data)
        else:
            logging.error(f"Platform handler for {platform} not found.") 