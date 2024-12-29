from twitchio.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import main
from utils import settings
import logging
from utils.logging import log_info, log_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

class Bot(commands.Bot):
    def __init__(self):
        log_info("Initializing Twitch Bot...")
        # Get credentials
        token = os.environ.get('TWITCH_TOKEN')
        channel = os.environ.get('TWITCH_CHANNEL', 'youtubbi')
        client_id = os.environ.get('TWITCH_CLIENT_ID')
        
        if not token.startswith('oauth:'):
            token = f'oauth:{token}'
            
        print(f"\n=== Initializing Twitch Bot ===")
        print(f"Channel: {channel}")
        print(f"Token Status: {'Valid' if token else 'Missing'}")
        print(f"Client ID Status: {'Valid' if client_id else 'Missing'}")
        
        super().__init__(
            token=token,
            client_id=client_id,
            nick=channel,
            prefix='!',
            initial_channels=[channel]
        )
        logging.info("Twitch Bot initialized.")
        
    async def event_ready(self):
        print(f"\n=== Twitch Bot Ready! ===")
        print(f"Connected as: {self.nick}")
        print(f"User ID: {self.user_id}")

    async def event_message(self, message):
        log_info(f"Received message: {message.content}")
        # Ignore bot's own messages
        if message.echo:
            return

        print(f"\nTwitch Chat > {message.channel.name} | {message.author.name}: {message.content}")
        
        try:
            # Process non-command messages
            if not message.content.startswith('!'):
                # Format message for AI processing
                chat_message = {
                    "platform": "twitch",
                    "author": message.author.name,
                    "content": message.content,
                    "channel": message.channel.name
                }
                
                # Get AI response
                response = await main.main_twitch_chat(chat_message)
                
                # Send response if valid
                if response and isinstance(response, str):
                    # Trim response to Twitch's character limit
                    trimmed_response = response[:500]
                    await message.channel.send(trimmed_response)
                    print(f"Bot Response > {trimmed_response}")
                    
        except Exception as e:
            print(f"Error processing Twitch message: {e}")
            import traceback
            traceback.print_exc()

async def run_twitch_bot():
    logging.info("Starting Twitch bot...")
    if not settings.TWITCH_ENABLED:
        logging.warning("Twitch bot is disabled in settings.")
        return
    try:
        bot = Bot()
        await bot.start()
        logging.info("Twitch bot started successfully.")
    except Exception as e:
        logging.error(f"Failed to start Twitch bot: {e}")

def start_twitch_bot():
    logging.info("Entry point for starting the Twitch bot.")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_twitch_bot())
    except Exception as e:
        logging.error(f"Failed to start Twitch bot: {e}")
