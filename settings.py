import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

hotkeys_locked = False
speak_shadowchats = False

max_tokens = 110
newline_cut = True

alarm_time = "09:09"
model_preset = "Default"

cam_use_image_feed = False
cam_direct_talk = True
cam_reply_after = False
cam_image_preview = True

# Valid values; "Faces", "Random", "None"
eyes_follow = "None"

minecraft_enabled = False
alarm_enabled = True
vtube_enabled = True
discord_enabled = True
rag_enabled = True
vision_enabled = True

# Feature Toggles
autochat_enabled = True  # Toggle for auto-chat feature
voice_enabled = True       # Toggle for voice feature
memory_enabled = True      # Toggle for memory feature
debug_mode = True        # Toggle for debug mode

# Twitch Settings
TWITCH_ENABLED = True
TWITCH_DEBUG_LOGGING = True

# Rate Limiting Settings
TWITCH_RATE_LIMIT_MESSAGES = 20  # Maximum messages per time window
TWITCH_RATE_LIMIT_SECONDS = 30   # Time window in seconds
TWITCH_MESSAGE_COOLDOWN = 2.0    # Minimum seconds between messages

# Other Twitch Settings
TWITCH_MAX_RESPONSE_LENGTH = 500  # Maximum length of responses

# Discord Voice Settings
DISCORD_VOICE_ENABLED = True
DISCORD_TTS_LANGUAGE = "en"
DISCORD_TTS_SPEED = 1.0
DISCORD_VOICE_TIMEOUT = 300  # 5 minutes
DISCORD_MAX_AUDIO_LENGTH = 300  # 5 minutes
DISCORD_AUDIO_QUALITY = "high"

# Voice Command Settings
DISCORD_COMMAND_PREFIX = "/"
DISCORD_VOICE_COMMANDS = {
    "tts": "Convert text to speech",
    "play": "Play audio from URL",
    "stop": "Stop current audio",
    "help": "Show command list"
}

# Streaming Settings
ENABLE_STREAMING = True  # Can be overridden by .env
STREAM_CHUNK_SIZE = 8
MAX_MESSAGE_LENGTH = 2000
MIN_MESSAGE_LENGTH = 10

# RP Settings
RP_SUPPRESSION_THRESHOLD = 3  # Lowered threshold for RP suppression
RP_SUPPRESSION_ENABLED = False  # Can be toggled independently
NEWLINE_CUT_ENABLED = True     # Can be toggled independently

# Stopping strings configuration 
SYSTEM_STOPPING_STRINGS = ["[System:", "[Assistant:", "[Human:"]
CHAT_STOPPING_STRINGS = ["User:", "Human:", "Assistant:"]
RP_STOPPING_STRINGS = ["*", "[", "]"]

logging.info("Settings loaded.")
