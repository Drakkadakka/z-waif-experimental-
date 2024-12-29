import time

import utils.cane_lib
import asyncio,os,threading
import pyvts
import json
from dotenv import load_dotenv
import mediapipe as mp
import cv2
import numpy as np
from scipy.io import wavfile
import librosa  # For audio analysis

VTS = pyvts.vts(
    plugin_info={
        "plugin_name": "Z-Waif",
        "developer": "sugarcanefarmer",
        "authentication_token_path": "./token.txt",
    },
    vts_api_info={
        "version": "1.0",
        "name": "VTubeStudioPublicAPI",
        "port": os.environ.get("VTUBE_STUDIO_API_PORT", 8001)
    }
)


load_dotenv()

global EMOTE_ID
EMOTE_ID = 2

global EMOTE_STRING
EMOTE_STRING = ""

global CUR_LOOK
CUR_LOOK = 0

global LOOK_LEVEL_ID
LOOK_LEVEL_ID = 1

global look_start_id
look_start_id = int(os.environ.get("EYES_START_ID", 0))


# Load in the EmoteLib from configurables
with open("Configurables/EmoteLib.json", 'r') as openfile:
    emote_lib = json.load(openfile)


# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)


# Starter Authentication

def run_vtube_studio_connection():
    asyncio.run(vtube_studio_connection())

async def vtube_studio_connection():
    try:
        await VTS.connect()
        await VTS.request_authenticate_token()
        await VTS.request_authenticate()
        
        # Start motion capture listener
        asyncio.create_task(motion_capture_listener())
    except Exception as e:
        print(f"Error in vtube_studio_connection: {e}")

async def motion_capture_listener():
    """Listens for motion capture data and triggers reactions."""
    cap = cv2.VideoCapture(0)  # Use the default camera
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        # Check if any landmarks are detected
        if results.pose_landmarks:
            # Analyze the landmarks to determine the emotion or action
            emotion = detect_emotion_from_landmarks(results.pose_landmarks)
            await handle_motion_capture_data({'emotion': emotion})

        await asyncio.sleep(0.1)  # Adjust the frequency as needed

    cap.release()

def detect_emotion_from_landmarks(landmarks):
    """Detects emotion based on pose landmarks."""
    # Extract landmark positions
    try:
        shoulder_left = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        shoulder_right = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        hip_left = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        hip_right = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        head = landmarks.landmark[mp_pose.PoseLandmark.NOSE]
        elbow_left = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
        elbow_right = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
        wrist_left = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        wrist_right = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        knee_left = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        knee_right = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
        eye_left = landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE]
        eye_right = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE]
        mouth = landmarks.landmark[mp_pose.PoseLandmark.MOUTH]

        # Calculate positions
        shoulder_y = (shoulder_left.y + shoulder_right.y) / 2
        hip_y = (hip_left.y + hip_right.y) / 2
        head_y = head.y
        eye_distance = np.linalg.norm(np.array([eye_left.x, eye_left.y]) - np.array([eye_right.x, eye_right.y]))
        mouth_open = mouth.y - head_y  # Simple approximation for mouth opening

        # Determine emotion based on positions
        if shoulder_y < hip_y and head_y < shoulder_y and mouth_open > 0.05:
            return 'happy'
        elif shoulder_y > hip_y and head_y > shoulder_y:
            return 'sad'
        elif elbow_left.y < shoulder_left.y or elbow_right.y < shoulder_right.y:
            return 'surprised'
        elif shoulder_y > hip_y and head_y < shoulder_y:
            return 'angry'
        elif wrist_left.y < elbow_left.y and wrist_right.y < elbow_right.y:
            return 'confident'
        elif head_y > shoulder_y:
            return 'defeated'
        elif knee_left.y < hip_left.y and knee_right.y < hip_right.y:
            return 'excited'
        elif eye_distance < 0.05:
            return 'confused'
        else:
            return 'neutral'
    except Exception as e:
        print(f"Error in detect_emotion_from_landmarks: {e}")
        return 'neutral'  # Default to neutral if there's an error

def analyze_voice_tone(audio_file):
    """Analyzes the tone of voice from an audio file."""
    # Load the audio file
    sample_rate, audio_data = wavfile.read(audio_file)
    # Use librosa to analyze the audio
    audio_data = librosa.load(audio_file, sr=sample_rate)[0]
    # Analyze the tone (e.g., pitch, loudness)
    pitch, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
    avg_pitch = np.mean(pitch)
    # Determine emotion based on pitch
    if avg_pitch > 300:  # Example threshold for happy tone
        return 'happy'
    elif avg_pitch < 150:  # Example threshold for sad tone
        return 'sad'
    else:
        return 'neutral'

async def handle_motion_capture_data(data):
    """Handles motion capture data to trigger dynamic reactions."""
    # Process the motion capture data
    if data['emotion'] == 'happy':
        set_emote_string("*happy*")
    elif data['emotion'] == 'sad':
        set_emote_string("*sad*")
    elif data['emotion'] == 'angry':
        set_emote_string("*angry*")
    elif data['emotion'] == 'surprised':
        set_emote_string("*surprised*")
    elif data['emotion'] == 'confident':
        set_emote_string("*confident*")
    elif data['emotion'] == 'defeated':
        set_emote_string("*defeated*")
    elif data['emotion'] == 'excited':
        set_emote_string("*excited*")
    elif data['emotion'] == 'neutral':
        set_emote_string("*neutral*")
    # Add more conditions as needed


# Emote System

def set_emote_string(emote_string):
    global EMOTE_STRING
    EMOTE_STRING = emote_string

def check_emote_string():

    # Setup our global
    global EMOTE_ID
    EMOTE_ID = -1


    # Cleanup the text to only look at the asterisk'ed words

    clean_emote_text = ''
    asterisk_count = 0

    for char in EMOTE_STRING:
        if char == "*":
            asterisk_count += 1
        elif asterisk_count % 2 == 1:
            clean_emote_text = clean_emote_text + char


    # Run through emotes, using OOP to only run one at a time (last = most prominent)

    for emote_page in emote_lib:
        if utils.cane_lib.keyword_check(clean_emote_text, emote_page[0]):
            EMOTE_ID = emote_page[1]




    # If we got an emote, run it through the system
    if EMOTE_ID != -1:
        run_emote()


def run_emote():
    asyncio.run(emote())

async def emote():
    await VTS.connect()
    await VTS.request_authenticate()
    response_data = await VTS.request(VTS.vts_request.requestHotKeyList())
    hotkey_list = []
    for hotkey in response_data["data"]["availableHotkeys"]:
        hotkey_list.append(hotkey["name"])
    send_hotkey_request = VTS.vts_request.requestTriggerHotKey(hotkey_list[EMOTE_ID])
    await VTS.request(send_hotkey_request)

    await VTS.close()

def change_look_level(value):

    # Inputting value should be from -1 to 1
    # We translate to what the look level should be here

    new_look_ID = -1

    if value < -0.67:
        new_look_ID = 5
    elif value < -0.4:
        new_look_ID = 4
    elif value < -0.2:
        new_look_ID = 3
    elif value > 0.67:
        new_look_ID = 2
    elif value > 0.4:
        new_look_ID = 1
    elif value > 0.2:
        new_look_ID = 0

    global LOOK_LEVEL_ID, CUR_LOOK

    if LOOK_LEVEL_ID != new_look_ID:
        run_clear_look()

        #mini rest between
        time.sleep(0.02)

        LOOK_LEVEL_ID = new_look_ID

        # only change if we are not at center
        if new_look_ID != -1:
            run_set_look()
        else:
            CUR_LOOK = 0




def run_clear_look():
    asyncio.run(clear_look())

def run_set_look():
    asyncio.run(set_look())

async def clear_look():
    await VTS.connect()
    await VTS.request_authenticate()

    # Remove the previous look emote
    if CUR_LOOK != 0:
        response_data = await VTS.request(VTS.vts_request.requestHotKeyList())
        hotkey_list = []
        for hotkey in response_data["data"]["availableHotkeys"]:
            hotkey_list.append(hotkey["name"])
        send_hotkey_request = VTS.vts_request.requestTriggerHotKey(hotkey_list[CUR_LOOK])
        await VTS.request(send_hotkey_request)

        await VTS.close()


async def set_look():
    await VTS.connect()
    await VTS.request_authenticate()


    # Make this configurable. The start of the section of emotes where the looking works
    global look_start_id
    new_look_id = look_start_id + LOOK_LEVEL_ID

    response_data = await VTS.request(VTS.vts_request.requestHotKeyList())
    hotkey_list = []
    for hotkey in response_data["data"]["availableHotkeys"]:
        hotkey_list.append(hotkey["name"])
    send_hotkey_request = VTS.vts_request.requestTriggerHotKey(hotkey_list[new_look_id])
    await VTS.request(send_hotkey_request)

    global CUR_LOOK
    CUR_LOOK = new_look_id

    await VTS.close()
