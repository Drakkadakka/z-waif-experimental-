from minecraft_handler import MinecraftHandler
from discord_handler import DiscordHandler
from twitch_handler import TwitchHandler

class PlatformManager:
    def __init__(self):
        self.handlers = {
            "twitch": TwitchHandler(),
            "discord": DiscordHandler(),
            "minecraft": MinecraftHandler()
        }
    
    async def handle_message(self, message_data):
        """Route messages to appropriate platform handlers"""
        platform = message_data.get("platform")
        if platform in self.handlers:
            return await self.handlers[platform].process(message_data) 