import pyaudio
import wave
import os
import audioop
from pydub import AudioSegment
from typing import Optional, Callable

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

current_directory = os.path.dirname(os.path.abspath(__file__))
FILENAME = "voice.wav"
SAVE_PATH = os.path.join(current_directory, "resource", "voice_in", FILENAME)

def get_speak_input() -> bool:
    """Get speak input state without direct import"""
    from utils.hotkeys import get_speak_input
    return get_speak_input()

def record():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    while get_speak_input():
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(SAVE_PATH, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return SAVE_PATH
