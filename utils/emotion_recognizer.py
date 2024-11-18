import torch
from transformers import pipeline

# Initialize the emotion recognition model
emotion_recognizer = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion")

def recognize_emotion_from_text(text):
    """Recognize emotion from a given text input."""
    predictions = emotion_recognizer(text)
    emotion = max(predictions, key=lambda x: x['score'])
    return emotion['label']

def recognize_emotion_from_audio(audio_file):
    """Transcribe audio and recognize emotion."""
    from utils.transcriber_translate import analyze_audio_emotion
    transcribed_text, emotion = analyze_audio_emotion(audio_file)
    return transcribed_text, emotion
