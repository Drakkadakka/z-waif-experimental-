import numpy as np
import sounddevice as sd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_audio_tone(audio_data):
    """Analyze audio data to determine the tone."""
    logging.info("Analyzing audio tone.")
    volume_norm = np.linalg.norm(audio_data) * 10
    if volume_norm > 40:
        return "happy"
    elif volume_norm > 20:
        return "neutral"
    else:
        return "sad"

def record_audio(duration=5):
    """Record audio for a specified duration."""
    logging.info(f"Recording audio for {duration} seconds.")
    audio_data = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype='float64')
    sd.wait()  # Wait until recording is finished
    return audio_data
