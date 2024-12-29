import os
import importlib.util
import json
import time
import threading
from discord import Client  # Import Discord client
from PIL import Image  # Import Pillow for image processing
import requests  # Ensure requests is imported for downloading
import cv2  # Ensure OpenCV is imported
from textblob import TextBlob  # Import TextBlob for sentiment analysis
import logging
from utils.logging import log_info, log_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MEMORY_CLEANUP_FREQUENCY = 10  # Set your desired frequency in minutes

class Oogabooga_Api_Support:
    loaded_plugins = {}
    enabled_plugins = set()  # Track enabled plugins
    memory_cleanup_thread = None

    @staticmethod
    def send_via_oogabooga(content):
        log_info(f"Sending content to Oogabooga: {content}.")
        # Implement the logic to send content to the Oogabooga API
        print(f"Sending to Oogabooga: {content}")
        # Here you would typically make an API call

    @staticmethod
    def receive_via_oogabooga():
        # Implement the logic to receive a response from the Oogabooga API
        print("Receiving from Oogabooga")
        # Here you would typically return a response from the API
        return "Sample response from Oogabooga"

    @staticmethod
    def load_plugins(plugin_directory):
        print(f"Loading plugins from: {plugin_directory}")
        for filename in os.listdir(plugin_directory):
            if filename.endswith('.py'):
                plugin_name = filename[:-3]
                try:
                    # Load the plugin module
                    spec = importlib.util.spec_from_file_location(plugin_name, os.path.join(plugin_directory, filename))
                    plugin_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(plugin_module)
                    Oogabooga_Api_Support.loaded_plugins[plugin_name] = plugin_module
                    print(f"Loaded plugin: {plugin_name}")
                except Exception as e:
                    print(f"Failed to load plugin {plugin_name}: {e}")

    @staticmethod
    def enable_plugin(plugin_name):
        if plugin_name in Oogabooga_Api_Support.loaded_plugins:
            Oogabooga_Api_Support.enabled_plugins.add(plugin_name)
            print(f"Enabled plugin: {plugin_name}")
        else:
            print(f"Plugin {plugin_name} not found.")

    @staticmethod
    def disable_plugin(plugin_name):
        if plugin_name in Oogabooga_Api_Support.enabled_plugins:
            Oogabooga_Api_Support.enabled_plugins.remove(plugin_name)
            print(f"Disabled plugin: {plugin_name}")
        else:
            print(f"Plugin {plugin_name} is not enabled.")

    @staticmethod
    def execute_plugin(plugin_name, *args, **kwargs):
        if plugin_name in Oogabooga_Api_Support.enabled_plugins:
            plugin = Oogabooga_Api_Support.loaded_plugins[plugin_name]
            try:
                if hasattr(plugin, 'execute'):
                    return plugin.execute(*args, **kwargs)
                else:
                    print(f"Plugin {plugin_name} does not have an execute method.")
            except Exception as e:
                print(f"Error executing plugin {plugin_name}: {e}")
        else:
            print(f"Plugin {plugin_name} not found or not enabled.")

    @staticmethod
    def list_plugins():
        print("Loaded plugins:")
        for plugin_name in Oogabooga_Api_Support.loaded_plugins.keys():
            status = "enabled" if plugin_name in Oogabooga_Api_Support.enabled_plugins else "disabled"
            print(f"- {plugin_name} ({status})")

    @staticmethod
    def soft_reset():
        # Implement the logic for a soft reset
        print("Performing soft reset") 

    @staticmethod
    def cleanup_memory():
        """Cleans up memory for loaded plugins and resets the state."""
        print("Cleaning up memory for loaded plugins.")
        
        # Unload all enabled plugins
        for plugin_name in list(Oogabooga_Api_Support.enabled_plugins):
            Oogabooga_Api_Support.disable_plugin(plugin_name)
        
        # Clear loaded plugins
        Oogabooga_Api_Support.loaded_plugins.clear()
        Oogabooga_Api_Support.enabled_plugins.clear()
        
        print("Memory cleanup complete. All plugins unloaded.")

    @staticmethod
    def save_memory_state(file_path='memory_state.json'):
        """Saves the current state of loaded plugins to a file."""
        state = {
            'loaded_plugins': list(Oogabooga_Api_Support.loaded_plugins.keys()),
            'enabled_plugins': list(Oogabooga_Api_Support.enabled_plugins)
        }
        with open(file_path, 'w') as f:
            json.dump(state, f)
        print(f"Memory state saved to {file_path}.")

    @staticmethod
    def load_memory_state(file_path='memory_state.json'):
        """Loads the state of loaded plugins from a file."""
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                state = json.load(f)
                for plugin_name in state['loaded_plugins']:
                    Oogabooga_Api_Support.load_plugins(plugin_name)  # Assuming load_plugins can handle loading by name
                Oogabooga_Api_Support.enabled_plugins.update(state['enabled_plugins'])
            print(f"Memory state loaded from {file_path}.")
        else:
            print(f"No memory state file found at {file_path}.")

    @staticmethod
    def start_memory_cleanup_scheduler(frequency):
        """Starts a thread to periodically clean up memory."""
        def cleanup_loop():
            while True:
                time.sleep(frequency * 60)  # Convert minutes to seconds
                Oogabooga_Api_Support.cleanup_memory()

        Oogabooga_Api_Support.memory_cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        Oogabooga_Api_Support.memory_cleanup_thread.start()
        print(f"Memory cleanup scheduler started with a frequency of {frequency} minutes.")

    @staticmethod
    def stop_memory_cleanup_scheduler():
        """Stops the memory cleanup scheduler."""
        if Oogabooga_Api_Support.memory_cleanup_thread is not None:
            Oogabooga_Api_Support.memory_cleanup_thread = None
            print("Memory cleanup scheduler stopped.")

    # Call this method to initialize memory management
    @staticmethod
    def initialize_memory_management():
        """Initializes memory management features."""
        Oogabooga_Api_Support.load_memory_state()
        Oogabooga_Api_Support.start_memory_cleanup_scheduler(MEMORY_CLEANUP_FREQUENCY)

    @staticmethod
    def process_gif(gif_url):
        """Processes a GIF from a given URL."""
        print(f"Processing GIF from URL: {gif_url}")
        # Download the GIF
        response = requests.get(gif_url)
        if response.status_code == 200:
            temp_gif_path = 'temp.gif'  # Path for the temporary GIF
            with open(temp_gif_path, 'wb') as f:
                f.write(response.content)
            # Open the GIF using OpenCV
            cap = cv2.VideoCapture(temp_gif_path)
            if not cap.isOpened():
                print("Error: Could not open GIF.")
                return
            
            # Process each frame of the GIF
            while True:
                ret, frame = cap.read()
                if not ret:
                    break  # Exit the loop if there are no more frames
                
                # Perform your analysis or processing here
                # For example, convert to grayscale
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Display the processed frame (optional)
                cv2.imshow('Processed Frame', gray_frame)
                cv2.waitKey(100)  # Display each frame for 100 ms
            
            cap.release()
            cv2.destroyAllWindows()
            print("GIF processed successfully.")
            
            # Cleanup: Remove the temporary GIF file
            os.remove(temp_gif_path)  # Delete the temporary GIF file
            print(f"Temporary GIF file {temp_gif_path} cleaned up.")
        else:
            print(f"Failed to download GIF. Status code: {response.status_code}")

    @staticmethod
    def generate_emotional_response(message_content, previous_messages):
        """Generates a context-aware emotional response based on the message content and previous messages."""
        analysis = TextBlob(message_content)
        sentiment = analysis.sentiment.polarity  # Get sentiment polarity

        # Analyze previous messages for context
        previous_sentiments = [TextBlob(msg).sentiment.polarity for msg in previous_messages]
        average_previous_sentiment = sum(previous_sentiments) / len(previous_sentiments) if previous_sentiments else 0

        # Generate response based on current and previous sentiments
        if sentiment > 0.1 and average_previous_sentiment > 0.1:
            return "I'm really happy to hear that! 😊"
        elif sentiment < -0.1 and average_previous_sentiment < -0.1:
            return "I'm really sorry to hear that. 😢"
        elif sentiment > 0.1:
            return "That's great! But I sense some underlying concerns. 🤔"
        elif sentiment < -0.1:
            return "I understand you're feeling down. Let's talk about it. 😟"
        else:
            return "I see. Let's explore this together. 🤔"

    @staticmethod
    def listen_for_gifs():
        """Listens for GIFs in Discord."""
        client = Client()

        @client.event
        async def on_ready():
            print(f'Logged in as {client.user}')  # Log when the bot is ready

        @client.event
        async def on_message(message):
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.url.endswith('.gif'):
                        Oogabooga_Api_Support.process_gif(attachment.url)
            # Generate and send an emotional response based on the message content
            previous_messages = [msg.content for msg in await message.channel.history(limit=5).flatten() if msg.author == message.author]
            response = Oogabooga_Api_Support.generate_emotional_response(message.content, previous_messages)
            await message.channel.send(response)  # Send the emotional response back to the channel

        # Start the Discord client using the token from the environment variable
        discord_token = os.getenv('DISCORD_TOKEN')  # Get the token from the environment
        if discord_token:
            try:
                client.run(discord_token)  # Use the token from the .env file
            except Exception as e:
                print(f"Failed to connect to Discord: {e}")  # Log any connection errors
        else:
            print("Discord token not found. Please set the DISCORD_TOKEN in your .env file.")

class APIHandler:
    def __init__(self):
        log_info("Initializing APIHandler.")
        # Your existing code...

    async def handle_request(self, request):
        log_info(f"Handling request: {request}.")
        # Your existing code...