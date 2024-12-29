import os
import whisper
import torch
from dotenv import load_dotenv
from transformers import pipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"
USER_MODEL = os.environ.get("WHISPER_MODEL")

# Initialize emotion recognition model
emotion_recognizer = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion", device=0 if device == "cuda" else -1)

def to_transcribe_original_language(voice):
    logging.info("Transcribing original language.")
    model = whisper.load_model(USER_MODEL, device=device)
    result = model.transcribe(voice, language="en", compression_ratio_threshold=1.9, no_speech_threshold=0.1)
    return " ".join([mem['text'] for mem in result["segments"]])

def analyze_audio_emotion(voice):
    logging.info("Analyzing audio emotion.")
    """Transcribe audio and analyze emotion."""
    transcribed_text = to_transcribe_original_language(voice)
    emotion = emotion_recognizer(transcribed_text)[0]['label']
    return transcribed_text, emotion


