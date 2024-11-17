from pathlib import Path
import asyncio
import tempfile
import time
from gtts import gTTS
import os
from . import settings
import discord
from discord import FFmpegPCMAudio
import yt_dlp
import utils.api as API  # Adjust the import based on your project structure


class DiscordVoiceHandler:
    def __init__(self, client):
        self.client = client
        self.voice_clients = {}
        self.audio_queue = {}
        self.temp_dir = Path(tempfile.gettempdir()) / "z_waif_voice"
        self.temp_dir.mkdir(exist_ok=True)
        
        # YouTube DL options for streaming
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'extract_audio': True
        }
        
    async def join_voice_channel(self, channel):
        """Join a voice channel"""
        if channel.guild.id in self.voice_clients:
            if self.voice_clients[channel.guild.id].is_playing():
                self.voice_clients[channel.guild.id].stop()
            await self.voice_clients[channel.guild.id].disconnect()
            
        voice_client = await channel.connect()
        self.voice_clients[channel.guild.id] = voice_client
        return voice_client
        
    async def leave_voice_channel(self, guild_id):
        """Leave a voice channel"""
        if guild_id in self.voice_clients:
            if self.voice_clients[guild_id].is_playing():
                self.voice_clients[guild_id].stop()
            await self.voice_clients[guild_id].disconnect()
            del self.voice_clients[guild_id]

    async def play_audio(self, url, voice_client, after_callback=None):
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
                    'force_generic_extractor': False,
                    'noplaylist': True
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
                        voice_client.play(audio_source, after=lambda e: asyncio.create_task(self.check_for_new_messages()))
                        print("Playback started successfully")
                        
                except Exception as e:
                    print(f"Error in YouTube processing: {e}")
                    raise
                    
            else:
                print("Non-YouTube URL detected")
                audio_source = FFmpegPCMAudio(url)
                voice_client.play(audio_source, after=lambda e: asyncio.create_task(self.check_for_new_messages()))
                print("Direct URL playback started")
                
        except Exception as e:
            print(f"Error in play_audio: {e}")
            raise
            
    async def text_to_speech(self, text, voice_client):
        """Convert text to speech and play in voice channel"""
        try:
            # Generate TTS file
            temp_file = await self.generate_tts(text)
            
            # Play audio
            source = FFmpegPCMAudio(str(temp_file))
            if voice_client.is_playing():
                voice_client.stop()
                
            voice_client.play(source)
            
            # Wait briefly to ensure playback starts
            await asyncio.sleep(0.5)
            
            # Cleanup will happen in background
            asyncio.create_task(self.cleanup_old_files())
            
        except Exception as e:
            print(f"TTS Error: {e}")
            raise
            
    async def generate_tts(self, text: str) -> Path:
        """Generate TTS audio file from text"""
        tts = gTTS(text=text, lang=settings.DISCORD_TTS_LANGUAGE)
        
        # Save to temp file
        temp_file = self.temp_dir / f"tts_{hash(text)}.mp3"
        tts.save(str(temp_file))
        
        return temp_file
        
    async def cleanup_old_files(self):
        """Clean up old temporary files"""
        for file in self.temp_dir.glob("*.mp3"):
            if file.stat().st_mtime < (time.time() - 3600):  # Older than 1 hour
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Error cleaning up file {file}: {e}")
        
    async def check_for_new_messages(self, channel_id):
        """Check for new messages after audio playback."""
        print("Checking for new messages...")
        
        # Call the Oogabooga API to get the latest message
        reply_message = API.Oogabooga_Api_Support.receive_via_oogabooga()
        
        if reply_message:
            # Print the reply message to the command line
            print(f"Reply from Oogabooga: {reply_message}")
            
            # Send the reply message to the Discord channel
            channel = self.client.get_channel(channel_id)  # Use the passed channel ID
            await channel.send(reply_message)
            
            # Play the audio response using TTS
            await self.text_to_speech(reply_message, self.voice_clients[channel.guild.id])
        else:
            print("No new messages from Oogabooga.")