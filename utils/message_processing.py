import numpy as np
from utils.emotion_recognizer import recognize_emotion_from_text, recognize_emotion_from_audio
from utils.transcriber_translate import analyze_audio_emotion
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_input(input_data):
    logging.info(f"Processing input data: {input_data}.")
    """Process text or audio input and return recognized emotion."""
    if input_data['type'] == 'text':
        # For text input
        emotion = recognize_emotion_from_text(input_data['content'])
        return input_data['content'], emotion
    elif input_data['type'] == 'audio':
        # For audio input
        transcribed_text, emotion = recognize_emotion_from_audio(input_data['file'])
        return transcribed_text, emotion
    return None, None

def clean_response(response: str) -> str:
    logging.info("Cleaning response.")
    """Clean and format AI response for Twitch chat."""
    response = ' '.join(response.split())
    
    # Truncate if too long (Twitch has a 500 char limit)
    if len(response) > 500:
        response = response[:497] + "..."
        
    # Remove any potential unsafe content
    # TODO: Add more content filtering as needed
    
    return response 