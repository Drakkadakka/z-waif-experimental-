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

# Import advanced VTube controller integration
try:
    from utils.vtuber_integration import get_vtuber_integration, apply_ai_emotions, set_vtube_emotion
    from utils.advanced_vtube_controller import get_controller, EmotionType
    ADVANCED_INTEGRATION_AVAILABLE = True
except ImportError:
    ADVANCED_INTEGRATION_AVAILABLE = False
    print("Advanced VTube integration not available, using legacy mode only")

from utils.logging import log_info, log_error, update_debug_log

# Legacy VTS API configuration
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

# Integration mode configuration
USE_ADVANCED_INTEGRATION = ADVANCED_INTEGRATION_AVAILABLE and os.environ.get("USE_ADVANCED_VTUBE", "true").lower() == "true"
MOTION_CAPTURE_ENABLED = os.environ.get("MOTION_CAPTURE_ENABLED", "true").lower() == "true"
VOICE_ANALYSIS_ENABLED = os.environ.get("VOICE_ANALYSIS_ENABLED", "true").lower() == "true"

# Advanced integration instance
_advanced_integration = None

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
    """Enhanced connection supporting both legacy and advanced modes"""
    global _advanced_integration
    
    try:
        # Initialize advanced integration if available
        if USE_ADVANCED_INTEGRATION:
            log_info("Initializing enhanced VTube Studio connection with advanced integration...")
            _advanced_integration = await get_vtuber_integration()
            if _advanced_integration.connected:
                log_info("Advanced VTube integration connected successfully")
                update_debug_log("VTube Studio: Advanced mode active")
            else:
                log_error("Advanced integration failed, falling back to legacy mode")
                USE_ADVANCED_INTEGRATION = False
        
        # Legacy VTS connection as fallback or primary
        if not USE_ADVANCED_INTEGRATION:
            log_info("Connecting to VTube Studio using legacy API...")
            await VTS.connect()
            await VTS.request_authenticate_token()
            await VTS.request_authenticate()
            log_info("Legacy VTube Studio connection established")
        
        # Start motion capture listener if enabled
        if MOTION_CAPTURE_ENABLED:
            asyncio.create_task(motion_capture_listener())
            log_info("Motion capture listener started")
            
    except Exception as e:
        log_error(f"Error in vtube_studio_connection: {e}")
        print(f"Error in vtube_studio_connection: {e}")

async def motion_capture_listener():
    """Enhanced motion capture with advanced emotion processing"""
    cap = cv2.VideoCapture(0)  # Use the default camera
    if not cap.isOpened():
        log_error("Could not open camera for motion capture")
        return

    log_info("Motion capture listener active")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            log_error("Could not read frame from camera")
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
    """Enhanced emotion detection with more nuanced analysis"""
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

        # Calculate positions
        shoulder_y = (shoulder_left.y + shoulder_right.y) / 2
        hip_y = (hip_left.y + hip_right.y) / 2
        head_y = head.y

        # Enhanced emotion detection with more precise calculations
        shoulder_width = abs(shoulder_left.x - shoulder_right.x)
        posture_ratio = (shoulder_y - hip_y) / shoulder_width if shoulder_width > 0 else 0
        arm_raised_left = elbow_left.y < shoulder_left.y
        arm_raised_right = elbow_right.y < shoulder_right.y
        
        # Determine emotion based on pose analysis
        if arm_raised_left and arm_raised_right:
            return 'excited'
        elif posture_ratio > 0.3:  # Slumped posture
            return 'sad'
        elif posture_ratio < -0.2:  # Upright, chest out
            return 'confident'
        elif arm_raised_left or arm_raised_right:
            return 'surprised'
        elif head_y > shoulder_y:
            return 'defeated'
        elif wrist_left.y < elbow_left.y and wrist_right.y < elbow_right.y:
            return 'happy'
        else:
            return 'neutral'
            
    except Exception as e:
        log_error(f"Error in detect_emotion_from_landmarks: {e}")
        return 'neutral'

def analyze_voice_tone(audio_file):
    """Enhanced voice analysis with multiple parameters"""
    if not VOICE_ANALYSIS_ENABLED:
        return 'neutral'
        
    try:
        # Load the audio file
        sample_rate, audio_data = wavfile.read(audio_file)
        audio_data = librosa.load(audio_file, sr=sample_rate)[0]
        
        # Analyze multiple audio features
        pitch, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
        avg_pitch = np.mean(pitch[pitch > 0])  # Only non-zero pitches
        
        # Additional features
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        avg_spectral_centroid = np.mean(spectral_centroid)
        
        # Enhanced emotion classification
        if avg_pitch > 250 and tempo > 120:  # High pitch, fast tempo
            return 'excited'
        elif avg_pitch > 200:  # Higher pitch
            return 'happy'
        elif avg_pitch < 150 and tempo < 80:  # Low pitch, slow tempo
            return 'sad'
        elif avg_spectral_centroid > 3000:  # Sharp, harsh sounds
            return 'angry'
        elif tempo > 140:  # Fast tempo
            return 'surprised'
        else:
            return 'neutral'
            
    except Exception as e:
        log_error(f"Error in analyze_voice_tone: {e}")
        return 'neutral'

async def handle_motion_capture_data(data):
    """Enhanced motion capture handler with advanced integration"""
    emotion = data['emotion']
    
    try:
        if USE_ADVANCED_INTEGRATION and _advanced_integration:
            # Use advanced emotion system
            await _advanced_integration.set_manual_emotion(emotion, intensity=0.7, duration=1.5)
            log_info(f"Applied motion capture emotion via advanced system: {emotion}")
        else:
            # Use legacy emote system
            set_emote_string(f"*{emotion}*")
            log_info(f"Applied motion capture emotion via legacy system: {emotion}")
            
    except Exception as e:
        log_error(f"Error handling motion capture data: {e}")


# Emote System

def set_emote_string(emote_string):
    """Enhanced emote string setter with advanced processing"""
    global EMOTE_STRING
    EMOTE_STRING = emote_string
    
    # If advanced integration is available, also process through it
    if USE_ADVANCED_INTEGRATION and _advanced_integration:
        asyncio.create_task(_process_emote_string_advanced(emote_string))

async def _process_emote_string_advanced(emote_string):
    """Process emote string through advanced system"""
    try:
        # Extract emotion from emote string
        clean_text = emote_string.replace("*", "").strip().lower()
        
        # Map common emote strings to emotions
        emotion_map = {
            'happy': 'happy',
            'sad': 'sad', 
            'angry': 'angry',
            'surprised': 'surprised',
            'excited': 'excited',
            'confident': 'confident',
            'defeated': 'sad',
            'neutral': 'neutral',
            'laugh': 'happy',
            'cry': 'sad',
            'smile': 'happy',
            'frown': 'sad'
        }
        
        emotion = emotion_map.get(clean_text, 'neutral')
        await _advanced_integration.set_manual_emotion(emotion, intensity=0.8, duration=2.0)
        
    except Exception as e:
        log_error(f"Error processing emote string in advanced mode: {e}")

def check_emote_string():
    """Enhanced emote string checker with dual-mode support"""
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

    # If we got an emote, run it through the appropriate system
    if EMOTE_ID != -1:
        if USE_ADVANCED_INTEGRATION and _advanced_integration:
            # Process through advanced system while also running legacy
            asyncio.create_task(_run_emote_advanced(clean_emote_text))
        
        # Always run legacy system for backward compatibility
        run_emote()

async def _run_emote_advanced(clean_text):
    """Run emote through advanced system"""
    try:
        # Use the vtuber_integration convenience function
        await apply_ai_emotions(f"*{clean_text}*", "MotionCapture")
        log_info(f"Applied advanced emote: {clean_text}")
    except Exception as e:
        log_error(f"Error running advanced emote: {e}")

def run_emote():
    """Legacy emote runner"""
    asyncio.run(emote())

async def emote():
    """Enhanced emote function with better error handling"""
    try:
        await VTS.connect()
        await VTS.request_authenticate()
        response_data = await VTS.request(VTS.vts_request.requestHotKeyList())
        hotkey_list = []
        for hotkey in response_data["data"]["availableHotkeys"]:
            hotkey_list.append(hotkey["name"])
        
        if EMOTE_ID < len(hotkey_list):
            send_hotkey_request = VTS.vts_request.requestTriggerHotKey(hotkey_list[EMOTE_ID])
            await VTS.request(send_hotkey_request)
            log_info(f"Triggered legacy emote: {hotkey_list[EMOTE_ID]}")
        
        await VTS.close()
        
    except Exception as e:
        log_error(f"Error in legacy emote execution: {e}")

def change_look_level(value):
    """Enhanced look level changer with advanced integration"""
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
        time.sleep(0.02)  # mini rest between
        LOOK_LEVEL_ID = new_look_ID

        # Only change if we are not at center
        if new_look_ID != -1:
            run_set_look()
            
            # Also apply to advanced system if available
            if USE_ADVANCED_INTEGRATION and _advanced_integration:
                asyncio.create_task(_apply_look_advanced(value))
        else:
            CUR_LOOK = 0

async def _apply_look_advanced(value):
    """Apply look direction to advanced system"""
    try:
        # Map look values to subtle emotions
        if abs(value) > 0.5:
            await _advanced_integration.set_manual_emotion('curious', intensity=0.3, duration=1.0)
        elif abs(value) > 0.2:
            await _advanced_integration.set_manual_emotion('attentive', intensity=0.2, duration=0.8)
            
    except Exception as e:
        log_error(f"Error applying look to advanced system: {e}")

def run_clear_look():
    asyncio.run(clear_look())

def run_set_look():
    asyncio.run(set_look())

async def clear_look():
    """Enhanced clear look with error handling"""
    try:
        await VTS.connect()
        await VTS.request_authenticate()

        # Remove the previous look emote
        if CUR_LOOK != 0:
            response_data = await VTS.request(VTS.vts_request.requestHotKeyList())
            hotkey_list = []
            for hotkey in response_data["data"]["availableHotkeys"]:
                hotkey_list.append(hotkey["name"])
            
            if CUR_LOOK < len(hotkey_list):
                send_hotkey_request = VTS.vts_request.requestTriggerHotKey(hotkey_list[CUR_LOOK])
                await VTS.request(send_hotkey_request)

        await VTS.close()
        
    except Exception as e:
        log_error(f"Error clearing look: {e}")

async def set_look():
    """Enhanced set look with error handling"""
    try:
        await VTS.connect()
        await VTS.request_authenticate()

        # Make this configurable. The start of the section of emotes where the looking works
        global look_start_id
        new_look_id = look_start_id + LOOK_LEVEL_ID

        response_data = await VTS.request(VTS.vts_request.requestHotKeyList())
        hotkey_list = []
        for hotkey in response_data["data"]["availableHotkeys"]:
            hotkey_list.append(hotkey["name"])
        
        if new_look_id < len(hotkey_list):
            send_hotkey_request = VTS.vts_request.requestTriggerHotKey(hotkey_list[new_look_id])
            await VTS.request(send_hotkey_request)

            global CUR_LOOK
            CUR_LOOK = new_look_id
            log_info(f"Set look to: {hotkey_list[new_look_id]}")

        await VTS.close()
        
    except Exception as e:
        log_error(f"Error setting look: {e}")

# New Advanced Integration Functions

async def apply_ai_speech_emotion(text: str, speaker: str = "AI"):
    """Apply emotions from AI speech using the best available method"""
    try:
        if USE_ADVANCED_INTEGRATION and _advanced_integration:
            result = await apply_ai_emotions(text, speaker)
            log_info(f"Applied AI speech emotions via advanced system")
            return result
        else:
            # Fallback to legacy emote detection
            emotions = _detect_emotions_from_text(text)
            for emotion in emotions:
                set_emote_string(f"*{emotion}*")
            log_info(f"Applied AI speech emotions via legacy system: {emotions}")
            return True
            
    except Exception as e:
        log_error(f"Error applying AI speech emotion: {e}")
        return False

def _detect_emotions_from_text(text: str) -> list:
    """Simple emotion detection from text for legacy fallback"""
    text_lower = text.lower()
    emotions = []
    
    if any(word in text_lower for word in ['happy', 'joy', 'great', 'awesome', 'wonderful', 'excited']):
        emotions.append('happy')
    if any(word in text_lower for word in ['sad', 'upset', 'disappointed', 'sorry', 'crying']):
        emotions.append('sad')
    if any(word in text_lower for word in ['angry', 'mad', 'frustrated', 'annoyed', 'furious']):
        emotions.append('angry')
    if any(word in text_lower for word in ['surprised', 'wow', 'amazing', 'incredible', 'shocked']):
        emotions.append('surprised')
    if any(word in text_lower for word in ['scared', 'afraid', 'worried', 'nervous', 'terrified']):
        emotions.append('scared')
    
    return emotions if emotions else ['neutral']

async def configure_advanced_behaviors(**behaviors):
    """Configure advanced VTube behaviors if available"""
    if USE_ADVANCED_INTEGRATION and _advanced_integration:
        try:
            result = _advanced_integration.configure_background_behaviors(**behaviors)
            log_info(f"Configured advanced behaviors: {behaviors}")
            return result
        except Exception as e:
            log_error(f"Error configuring advanced behaviors: {e}")
            return False
    else:
        log_info("Advanced behaviors not available in legacy mode")
        return False

def get_vtube_status():
    """Get comprehensive VTube status"""
    status = {
        'advanced_integration_available': ADVANCED_INTEGRATION_AVAILABLE,
        'use_advanced_integration': USE_ADVANCED_INTEGRATION,
        'motion_capture_enabled': MOTION_CAPTURE_ENABLED,
        'voice_analysis_enabled': VOICE_ANALYSIS_ENABLED,
        'current_emote_id': EMOTE_ID,
        'current_emote_string': EMOTE_STRING,
        'current_look': CUR_LOOK,
        'look_level_id': LOOK_LEVEL_ID
    }
    
    if USE_ADVANCED_INTEGRATION and _advanced_integration:
        try:
            advanced_status = _advanced_integration.get_status()
            status['advanced_status'] = advanced_status
        except:
            pass
    
    return status

# Initialization function for easy setup
async def initialize_vtube_studio():
    """Initialize VTube Studio with all available features"""
    log_info("Initializing VTube Studio integration...")
    
    await vtube_studio_connection()
    
    if USE_ADVANCED_INTEGRATION and _advanced_integration:
        # Configure default advanced behaviors
        await configure_advanced_behaviors(
            breathing=True,
            eye_movement=True,
            idle_sway=True,
            micro_expressions=True
        )
        
        # Set reasonable defaults
        _advanced_integration.set_emotion_intensity(0.8)
        _advanced_integration.set_auto_emotion_detection(True)
        
        log_info("Advanced VTube integration initialized with default behaviors")
    
    log_info("VTube Studio integration initialization complete")

# Export the main initialization function
__all__ = [
    'initialize_vtube_studio',
    'apply_ai_speech_emotion', 
    'configure_advanced_behaviors',
    'get_vtube_status',
    'set_emote_string',
    'check_emote_string',
    'change_look_level',
    'analyze_voice_tone'
]
