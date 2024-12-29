import asyncio
import os
import discord
from discord.ext import commands
import main
import API.Oogabooga_Api_Support
from discord import FFmpegPCMAudio
from discord.ext import commands
from utils import settings
from .discord_voice_handler import DiscordVoiceHandler
import yt_dlp
import requests  # Make sure to import requests or any other library you use for API calls
import logging
from utils.logging import log_info, log_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DiscordClient(commands.Bot):
    def __init__(self):
        log_info("Initializing Discord Client...")
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='/', intents=intents)
        self.voice_handler = DiscordVoiceHandler(self)
        log_info("Discord Client initialized.")
        
    async def setup_hook(self):
        print("Setting up command tree...")
        
        # Initialize a dictionary to hold playlists for each guild
        playlists = {}

        @self.tree.command(name="play", description="Play audio from URL or add to playlist")
        async def play(interaction: discord.Interaction, url: str):
            print(f"Play command received for URL: {url}")
            
            # Store these before any async operations
            channel = interaction.channel
            guild_id = interaction.guild_id
            voice_state = interaction.user.voice
            
            # Check if user is in voice channel
            if not voice_state:
                print("User not in voice channel")
                await interaction.response.send_message("❌ You must be in a voice channel!")
                return

            voice_channel = voice_state.channel
            print(f"User is in voice channel: {voice_channel.name}")

            # Initialize the playlist for the guild if it doesn't exist
            if guild_id not in playlists:
                playlists[guild_id] = []

            # Add the URL to the playlist
            playlists[guild_id].append(url)
            await interaction.response.send_message(f"🎵 Added to playlist: {url}")

            # If the bot is not already playing, start playing the playlist
            if len(playlists[guild_id]) == 1:  # Only start if this is the first item
                try:
                    # Connect to the voice channel
                    if guild_id in self.voice_handler.voice_clients:
                        print("Already connected, disconnecting...")
                        await self.voice_handler.voice_clients[guild_id].disconnect()
                        del self.voice_handler.voice_clients[guild_id]

                    print("Connecting to voice channel...")
                    voice_client = await voice_channel.connect()
                    self.voice_handler.voice_clients[guild_id] = voice_client
                    await channel.send("✅ Connected to voice channel")
                    
                    # Start playing the playlist
                    await play_next(guild_id, voice_client, channel)
                    
                except Exception as e:
                    print(f"Error during playback: {e}")
                    await channel.send(f"❌ Error: {str(e)}")

        async def play_next(guild_id, voice_client, channel):
            """Play the next audio in the playlist."""
            if guild_id in playlists and playlists[guild_id]:
                url = playlists[guild_id][0]  # Get the first URL in the playlist
                print(f"Playing next URL: {url}")
                
                try:
                    await channel.send(f"🎵 Now playing: {url}")
                    # Pass the callback to play_audio
                    await self.voice_handler.play_audio(url, voice_client, after_callback=lambda e: asyncio.create_task(play_next(guild_id, voice_client, channel)))
                    
                    # Remove the played URL from the playlist
                    playlists[guild_id].pop(0)
                    print(f"Removed played URL. Remaining playlist: {playlists[guild_id]}")

                except Exception as e:
                    print(f"Error playing next URL: {e}")
                    await channel.send(f"❌ Error: {str(e)}")
                    # Cleanup on error
                    if guild_id in self.voice_handler.voice_clients:
                        await voice_client.disconnect()
                        del self.voice_handler.voice_clients[guild_id]
            else:
                print("No more URLs in the playlist.")
                await channel.send("✅ Playlist finished.")
                if guild_id in self.voice_handler.voice_clients:
                    await voice_client.disconnect()
                    del self.voice_handler.voice_clients[guild_id]
                # Allow the bot to respond to new commands
                await channel.send("🤖 I'm back and ready for your commands!")

        @self.tree.command(name="stop", description="Stop audio playback and clear the playlist")
        async def stop(interaction: discord.Interaction):
            print("Stop command received")
            channel = interaction.channel
            guild_id = interaction.guild_id
            
            try:
                await interaction.response.send_message("⏹️ Stopping playback...")
                
                if guild_id in self.voice_handler.voice_clients:
                    voice_client = self.voice_handler.voice_clients[guild_id]
                    if voice_client.is_playing():
                        voice_client.stop()
                    await voice_client.disconnect()
                    del self.voice_handler.voice_clients[guild_id]
                    await channel.send("✅ Stopped and disconnected")
                
                # Clear the playlist
                if guild_id in playlists:
                    playlists[guild_id].clear()
                    print("Cleared the playlist.")
                
                await channel.send("🤖 I'm back and ready for your commands!")
                
            except Exception as e:
                print(f"Error in stop command: {e}")
                await channel.send(f"❌ Error: {str(e)}")

        @self.tree.command(name="tts", description="Convert text to speech")
        async def tts(interaction: discord.Interaction, text: str):
            if not interaction.user.voice:
                await interaction.response.send_message("❌ You must be in a voice channel!")
                return

            # Get channel and guild info before responding
            channel = interaction.channel
            guild_id = interaction.guild_id
            voice_channel = interaction.user.voice.channel

            # Send initial response
            await interaction.response.send_message("🗣️ Processing TTS...")

            try:
                # Join voice channel
                voice_client = await voice_channel.connect()
                self.voice_handler.voice_clients[guild_id] = voice_client
                
                # Play TTS
                await self.voice_handler.text_to_speech(text, voice_client)
                await channel.send("✅ TTS completed")
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                print(f"TTS error: {e}")
                await channel.send(error_msg)
                
                # Cleanup on error
                if guild_id in self.voice_handler.voice_clients:
                    try:
                        voice_client = self.voice_handler.voice_clients[guild_id]
                        if voice_client.is_connected():
                            await voice_client.disconnect()
                        del self.voice_handler.voice_clients[guild_id]
                    except:
                        pass

        # Sync commands
        print("Syncing commands...")
        try:
            await self.tree.sync()
            print("Commands synced successfully!")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def play_audio(self, url, voice_client):
        """Play audio from URL"""
        try:
            print(f"Starting play_audio for URL: {url}")
            
            # Check if it's a YouTube URL
            if 'youtube.com' in url or 'youtu.be' in url:
                print("YouTube URL detected")
                
                # YouTube DL options
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': False,
                    'no_warnings': False,
                    'extract_audio': True,
                    'force_generic_extractor': False
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        print("Extracting video info...")
                        info = await asyncio.get_event_loop().run_in_executor(
                            None, lambda: ydl.extract_info(url, download=False)
                        )
                        print("Info extracted successfully")
                        
                        if 'formats' in info:
                            print("Selecting best audio format...")
                            formats = [f for f in info['formats'] 
                                     if f.get('acodec') != 'none']
                            if not formats:
                                formats = info['formats']
                            
                            stream_url = formats[0]['url']
                            print(f"Audio stream URL selected: {stream_url}")
                        else:
                            stream_url = info['url']
                            print("Using direct URL")
                        
                        print("Setting up FFmpeg options...")
                        ffmpeg_options = {
                            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                            'options': '-vn'
                        }
                        
                        print("Creating audio source...")
                        audio_source = FFmpegPCMAudio(stream_url, **ffmpeg_options)
                        
                        print("Starting playback...")
                        voice_client.play(audio_source)
                        print("Playback started successfully")
                        
                except Exception as e:
                    print(f"Error in YouTube processing: {e}")
                    raise
                
            else:
                print("Non-YouTube URL detected")
                audio_source = FFmpegPCMAudio(url)
                voice_client.play(audio_source)
                print("Direct URL playback started")
                
        except Exception as e:
            print(f"Error in play_audio: {e}")
            raise

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            log_info(f"Received message: {message.content}")
            if message.author == self.user:
                return  # Ignore messages from the bot itself

            # Process the message and generate a response
            response = await self.generate_response(message.content)
            await message.channel.send(response)
        except Exception as e:
            log_error(f"Error processing message: {e}")

    async def generate_response(self, content):
        """Send the content to the Oogabooga API and return the response."""
        try:
            # Use the Oogabooga API to get a response
            API.Oogabooga_Api_Support.send_via_oogabooga(content)  # Send the user input to Oogabooga
            response = API.Oogabooga_Api_Support.receive_via_oogabooga()  # Get the response from Oogabooga

            if response:
                return response
            else:
                return "Sorry, I couldn't process that."

        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I couldn't process that."

def run_z_waif_discord():
    log_info("Starting Discord bot...")
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
    if not DISCORD_TOKEN:
        log_error("Error: DISCORD_TOKEN not found in environment variables")
        return
        
    client = DiscordClient()
    log_info("Running Discord client...")
    client.run(DISCORD_TOKEN)
