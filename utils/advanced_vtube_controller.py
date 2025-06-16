import asyncio
import logging
import time
import json
import os
import threading
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from collections import deque, defaultdict
from enum import Enum
import math
import random
import numpy as np
from scipy import interpolate
import pyvts

# Configure advanced logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionType(Enum):
    """14+ emotion types for comprehensive expression control"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    CONTEMPT = "contempt"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CONFUSED = "confused"
    SLEEPY = "sleepy"
    FOCUSED = "focused"
    LOVE = "love"
    EMBARRASSED = "embarrassed"
    DETERMINED = "determined"
    PLAYFUL = "playful"
    MISCHIEVOUS = "mischievous"
    SERENE = "serene"

class FallbackLevel(Enum):
    """5-tier fallback system for maximum reliability"""
    DIRECT_CONNECTION = 1
    WEBSOCKET_RETRY = 2
    ALTERNATIVE_PORT = 3
    MOCK_MODE = 4
    EMERGENCY_LOGGING = 5

@dataclass
class ParameterUpdate:
    """Represents a single parameter update with easing"""
    parameter: str
    target_value: float
    current_value: float = 0.0
    duration: float = 1.0
    start_time: float = field(default_factory=time.time)
    easing_function: str = "ease_in_out"
    priority: int = 0

@dataclass
class BackgroundBehavior:
    """Background behavior configuration"""
    name: str
    parameters: Dict[str, Tuple[float, float]]  # param: (min, max)
    frequency: float  # Updates per second
    enabled: bool = True
    phase_offset: float = 0.0

@dataclass
class ModelConfiguration:
    """Auto-discovered model configuration"""
    model_name: str
    available_parameters: List[str]
    parameter_ranges: Dict[str, Tuple[float, float]]
    hotkeys: List[str]
    custom_mappings: Dict[str, str] = field(default_factory=dict)

class EasingFunctions:
    """Collection of easing functions for smooth animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in_out(t: float) -> float:
        return 3 * t**2 - 2 * t**3
    
    @staticmethod
    def ease_in(t: float) -> float:
        return t**2
    
    @staticmethod
    def ease_out(t: float) -> float:
        return 1 - (1 - t)**2
    
    @staticmethod
    def bounce(t: float) -> float:
        if t < 0.5:
            return 2 * t**2
        else:
            return 1 - 2 * (1 - t)**2

class AdvancedVTubeController:
    """Complete AI control system for VTube Studio with 20 FPS updates"""
    
    def __init__(self, target_fps: int = 20):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        
        # Connection management
        self.vts = None
        self.connected = False
        self.fallback_level = FallbackLevel.DIRECT_CONNECTION
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
        # Model configuration
        self.model_config: Optional[ModelConfiguration] = None
        self.auto_discovery_complete = False
        
        # Parameter management
        self.active_parameters: Dict[str, ParameterUpdate] = {}
        self.parameter_queue = deque()
        self.current_values: Dict[str, float] = {}
        
        # Background behaviors
        self.background_behaviors: Dict[str, BackgroundBehavior] = {}
        self.behavior_states: Dict[str, float] = {}
        
        # Emotion system
        self.emotion_mappings: Dict[EmotionType, Dict[str, float]] = {}
        self.current_emotion = EmotionType.NEUTRAL
        self.emotion_intensity = 0.0
        
        # Threading and async
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        self.last_update_time = time.time()
        
        # Performance tracking
        self.actual_fps = 0.0
        self.frame_times = deque(maxlen=60)
        
        # Initialize systems
        self._setup_default_behaviors()
        self._setup_default_emotion_mappings()
        
    async def initialize(self) -> bool:
        """Zero-configuration initialization with automatic model discovery"""
        logger.info("Initializing Advanced VTube Studio Controller...")
        
        # Attempt connection with fallback system
        if await self._connect_with_fallback():
            await self._discover_model_configuration()
            await self._setup_adaptive_parameter_mapping()
            self._start_update_loop()
            logger.info("VTube Studio Controller initialized successfully!")
            return True
        else:
            logger.error("Failed to initialize VTube Studio Controller")
            return False
    
    async def _connect_with_fallback(self) -> bool:
        """Multi-tier fallback connection system"""
        ports = [8001, 8002, 8003, 8080, 9001]
        
        for attempt in range(self.max_connection_attempts):
            for level in FallbackLevel:
                self.fallback_level = level
                logger.info(f"Connection attempt {attempt + 1}, fallback level: {level.name}")
                
                try:
                    if level == FallbackLevel.DIRECT_CONNECTION:
                        await self._attempt_direct_connection()
                    elif level == FallbackLevel.WEBSOCKET_RETRY:
                        await self._attempt_websocket_retry()
                    elif level == FallbackLevel.ALTERNATIVE_PORT:
                        await self._attempt_alternative_ports(ports)
                    elif level == FallbackLevel.MOCK_MODE:
                        self._setup_mock_mode()
                        return True
                    elif level == FallbackLevel.EMERGENCY_LOGGING:
                        self._setup_emergency_logging()
                        return True
                    
                    if self.connected:
                        logger.info(f"Connected successfully at fallback level: {level.name}")
                        return True
                        
                except Exception as e:
                    logger.warning(f"Fallback level {level.name} failed: {e}")
                    continue
                    
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    async def _attempt_direct_connection(self):
        """Direct connection attempt"""
        self.vts = pyvts.vts(
            plugin_info={
                "plugin_name": "Advanced-Z-Waif",
                "developer": "AI-Controller",
                "authentication_token_path": "./advanced_vts_token.txt",
            },
            vts_api_info={
                "version": "1.0",
                "name": "VTubeStudioPublicAPI",
                "port": int(os.environ.get("VTUBE_STUDIO_API_PORT", 8001))
            }
        )
        
        await self.vts.connect()
        await self.vts.request_authenticate_token()
        await self.vts.request_authenticate()
        self.connected = True
    
    async def _attempt_websocket_retry(self):
        """Retry WebSocket connection with different settings"""
        if self.vts:
            await self.vts.close()
        await asyncio.sleep(1)
        await self._attempt_direct_connection()
    
    async def _attempt_alternative_ports(self, ports: List[int]):
        """Try alternative ports"""
        for port in ports:
            try:
                self.vts = pyvts.vts(
                    plugin_info={
                        "plugin_name": "Advanced-Z-Waif",
                        "developer": "AI-Controller",
                        "authentication_token_path": "./advanced_vts_token.txt",
                    },
                    vts_api_info={
                        "version": "1.0",
                        "name": "VTubeStudioPublicAPI",
                        "port": port
                    }
                )
                
                await self.vts.connect()
                await self.vts.request_authenticate_token()
                await self.vts.request_authenticate()
                self.connected = True
                logger.info(f"Connected on alternative port: {port}")
                return
            except Exception as e:
                logger.debug(f"Port {port} failed: {e}")
                continue
    
    def _setup_mock_mode(self):
        """Setup mock mode for testing without VTube Studio"""
        logger.warning("Running in MOCK MODE - VTube Studio not available")
        self.connected = True  # Simulate connection
    
    def _setup_emergency_logging(self):
        """Emergency logging mode"""
        logger.error("EMERGENCY MODE - All operations will be logged only")
        self.connected = True  # Simulate connection for logging
    
    async def _discover_model_configuration(self):
        """Automatic model discovery and configuration"""
        if self.fallback_level in [FallbackLevel.MOCK_MODE, FallbackLevel.EMERGENCY_LOGGING]:
            self._setup_default_model_config()
            return
            
        try:
            # Get current model info
            model_response = await self.vts.request(self.vts.vts_request.requestCurrentModel())
            model_name = model_response.get("data", {}).get("modelName", "Unknown")
            
            # Get available parameters
            params_response = await self.vts.request(self.vts.vts_request.requestParameterList())
            parameters = params_response.get("data", {}).get("parameters", [])
            
            # Get hotkeys
            hotkeys_response = await self.vts.request(self.vts.vts_request.requestHotKeyList())
            hotkeys = [hk["name"] for hk in hotkeys_response.get("data", {}).get("availableHotkeys", [])]
            
            # Build configuration
            available_params = [p["name"] for p in parameters]
            param_ranges = {}
            
            for param in parameters:
                param_ranges[param["name"]] = (param.get("min", 0.0), param.get("max", 1.0))
            
            self.model_config = ModelConfiguration(
                model_name=model_name,
                available_parameters=available_params,
                parameter_ranges=param_ranges,
                hotkeys=hotkeys
            )
            
            logger.info(f"Discovered model: {model_name} with {len(available_params)} parameters")
            self.auto_discovery_complete = True
            
        except Exception as e:
            logger.error(f"Model discovery failed: {e}")
            self._setup_default_model_config()
    
    def _setup_default_model_config(self):
        """Setup default model configuration for fallback"""
        self.model_config = ModelConfiguration(
            model_name="Default",
            available_parameters=[
                "FacePositionX", "FacePositionY", "FaceRotationZ",
                "EyeOpenLeft", "EyeOpenRight", "EyeballX", "EyeballY",
                "BrowLeftY", "BrowRightY", "MouthForm", "MouthOpenY"
            ],
            parameter_ranges={param: (-1.0, 1.0) for param in [
                "FacePositionX", "FacePositionY", "FaceRotationZ",
                "EyeOpenLeft", "EyeOpenRight", "EyeballX", "EyeballY",
                "BrowLeftY", "BrowRightY", "MouthForm", "MouthOpenY"
            ]},
            hotkeys=[]
        )
        self.auto_discovery_complete = True
    
    async def _setup_adaptive_parameter_mapping(self):
        """Setup adaptive parameter mapping for any VTube Studio model"""
        if not self.model_config:
            return
            
        # Intelligent parameter mapping based on common naming patterns
        param_patterns = {
            # Face position and rotation
            'face_x': ['FacePositionX', 'HeadX', 'Face_X'],
            'face_y': ['FacePositionY', 'HeadY', 'Face_Y'],
            'face_rotation': ['FaceRotationZ', 'HeadRotZ', 'Face_Rotation'],
            
            # Eyes
            'eye_left_open': ['EyeOpenLeft', 'LeftEyeOpen', 'Eye_L_Open'],
            'eye_right_open': ['EyeOpenRight', 'RightEyeOpen', 'Eye_R_Open'],
            'eyeball_x': ['EyeballX', 'EyesX', 'Eye_X'],
            'eyeball_y': ['EyeballY', 'EyesY', 'Eye_Y'],
            
            # Eyebrows
            'brow_left': ['BrowLeftY', 'LeftBrowY', 'Brow_L_Y'],
            'brow_right': ['BrowRightY', 'RightBrowY', 'Brow_R_Y'],
            
            # Mouth
            'mouth_open': ['MouthOpenY', 'MouthOpen', 'Mouth_Open_Y'],
            'mouth_form': ['MouthForm', 'MouthShape', 'Mouth_Form'],
            'mouth_smile': ['MouthSmile', 'Smile', 'Mouth_Smile'],
            
            # Body
            'body_rotation_x': ['BodyRotationX', 'BodyX', 'Body_Rot_X'],
            'body_rotation_y': ['BodyRotationY', 'BodyY', 'Body_Rot_Y'],
            'body_rotation_z': ['BodyRotationZ', 'BodyZ', 'Body_Rot_Z'],
        }
        
        # Map available parameters to standardized names
        for standard_name, possible_names in param_patterns.items():
            for param_name in possible_names:
                if param_name in self.model_config.available_parameters:
                    self.model_config.custom_mappings[standard_name] = param_name
                    break
        
        logger.info(f"Mapped {len(self.model_config.custom_mappings)} parameters")
    
    def _setup_default_behaviors(self):
        """Setup default background behavior loops"""
        self.background_behaviors = {
            'breathing': BackgroundBehavior(
                name='breathing',
                parameters={'body_rotation_x': (-0.02, 0.02)},
                frequency=0.3,  # Slow breathing
                enabled=True
            ),
            'eye_movement': BackgroundBehavior(
                name='eye_movement',
                parameters={'eyeball_x': (-0.3, 0.3), 'eyeball_y': (-0.2, 0.2)},
                frequency=0.1,  # Occasional eye movement
                enabled=True
            ),
            'idle_sway': BackgroundBehavior(
                name='idle_sway',
                parameters={'face_x': (-0.01, 0.01), 'face_rotation': (-0.5, 0.5)},
                frequency=0.05,  # Very slow swaying
                enabled=True
            ),
            'micro_expressions': BackgroundBehavior(
                name='micro_expressions',
                parameters={'brow_left': (-0.05, 0.05), 'brow_right': (-0.05, 0.05)},
                frequency=0.02,  # Subtle micro-expressions
                enabled=True
            )
        }
    
    def _setup_default_emotion_mappings(self):
        """Setup comprehensive emotion to parameter mappings"""
        self.emotion_mappings = {
            EmotionType.HAPPY: {
                'mouth_smile': 0.8,
                'eye_left_open': 0.9,
                'eye_right_open': 0.9,
                'brow_left': 0.1,
                'brow_right': 0.1
            },
            EmotionType.SAD: {
                'mouth_form': -0.6,
                'eye_left_open': 0.3,
                'eye_right_open': 0.3,
                'brow_left': -0.3,
                'brow_right': -0.3,
                'face_y': -0.1
            },
            EmotionType.ANGRY: {
                'mouth_form': -0.4,
                'brow_left': -0.8,
                'brow_right': -0.8,
                'eye_left_open': 0.6,
                'eye_right_open': 0.6
            },
            EmotionType.SURPRISED: {
                'eye_left_open': 1.0,
                'eye_right_open': 1.0,
                'mouth_open': 0.5,
                'brow_left': 0.6,
                'brow_right': 0.6
            },
            EmotionType.FEARFUL: {
                'eye_left_open': 1.0,
                'eye_right_open': 1.0,
                'brow_left': 0.4,
                'brow_right': 0.4,
                'mouth_form': -0.3,
                'face_y': 0.1
            },
            EmotionType.EXCITED: {
                'eye_left_open': 1.0,
                'eye_right_open': 1.0,
                'mouth_smile': 1.0,
                'brow_left': 0.3,
                'brow_right': 0.3,
                'face_y': 0.05
            },
            EmotionType.SLEEPY: {
                'eye_left_open': 0.2,
                'eye_right_open': 0.2,
                'mouth_form': 0.1,
                'face_y': -0.05
            },
            EmotionType.LOVE: {
                'eye_left_open': 0.7,
                'eye_right_open': 0.7,
                'mouth_smile': 0.6,
                'brow_left': 0.2,
                'brow_right': 0.2
            },
            EmotionType.EMBARRASSED: {
                'eye_left_open': 0.4,
                'eye_right_open': 0.4,
                'mouth_form': 0.3,
                'face_rotation': 0.1
            },
            EmotionType.PLAYFUL: {
                'eye_left_open': 0.8,
                'eye_right_open': 1.0,  # Winking effect
                'mouth_smile': 0.7,
                'face_rotation': 0.05
            },
            EmotionType.NEUTRAL: {
                'eye_left_open': 0.8,
                'eye_right_open': 0.8,
                'mouth_form': 0.0,
                'brow_left': 0.0,
                'brow_right': 0.0
            }
        }
    
    def _start_update_loop(self):
        """Start the 20 FPS update loop"""
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info(f"Started {self.target_fps} FPS update loop")
    
    def _update_loop(self):
        """Main update loop running at target FPS"""
        while self.running:
            frame_start = time.time()
            
            try:
                # Update parameters with easing
                self._update_parameters()
                
                # Update background behaviors
                self._update_background_behaviors()
                
                # Send parameter updates to VTube Studio
                asyncio.run(self._send_parameter_updates())
                
                # Calculate performance metrics
                frame_time = time.time() - frame_start
                self.frame_times.append(frame_time)
                
                if len(self.frame_times) >= 10:
                    avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                    self.actual_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                
                # Sleep for remaining frame time
                sleep_time = max(0, self.frame_time - frame_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Update loop error: {e}")
                time.sleep(0.1)
    
    def _update_parameters(self):
        """Update parameters with smooth easing transitions"""
        current_time = time.time()
        completed_params = []
        
        for param_name, update in self.active_parameters.items():
            # Calculate progress (0.0 to 1.0)
            elapsed = current_time - update.start_time
            progress = min(elapsed / update.duration, 1.0)
            
            # Apply easing function
            easing_func = getattr(EasingFunctions, update.easing_function, EasingFunctions.linear)
            eased_progress = easing_func(progress)
            
            # Calculate current value
            value_delta = update.target_value - update.current_value
            current_value = update.current_value + (value_delta * eased_progress)
            
            # Update current values
            self.current_values[param_name] = current_value
            
            # Check if animation is complete
            if progress >= 1.0:
                completed_params.append(param_name)
        
        # Remove completed animations
        for param_name in completed_params:
            del self.active_parameters[param_name]
    
    def _update_background_behaviors(self):
        """Update background behavior loops"""
        current_time = time.time()
        
        for behavior_name, behavior in self.background_behaviors.items():
            if not behavior.enabled:
                continue
                
            # Calculate phase based on time and frequency
            phase = (current_time * behavior.frequency + behavior.phase_offset) * 2 * math.pi
            
            for param_name, (min_val, max_val) in behavior.parameters.items():
                # Generate smooth oscillation
                oscillation = math.sin(phase)
                value = min_val + (max_val - min_val) * (oscillation + 1) / 2
                
                # Only update if not being actively controlled
                if param_name not in self.active_parameters:
                    self.current_values[param_name] = value
    
    async def _send_parameter_updates(self):
        """Send parameter updates to VTube Studio"""
        if not self.connected or not self.model_config:
            return
            
        if self.fallback_level in [FallbackLevel.MOCK_MODE, FallbackLevel.EMERGENCY_LOGGING]:
            # Log updates in mock/emergency mode
            if self.current_values:
                logger.debug(f"Mock update: {dict(list(self.current_values.items())[:3])}")
            return
        
        try:
            # Batch parameter updates for efficiency
            updates = []
            for param_name, value in self.current_values.items():
                # Map to actual VTS parameter name
                vts_param = self.model_config.custom_mappings.get(param_name, param_name)
                
                if vts_param in self.model_config.available_parameters:
                    # Clamp value to parameter range
                    min_val, max_val = self.model_config.parameter_ranges.get(vts_param, (-1.0, 1.0))
                    clamped_value = max(min_val, min(max_val, value))
                    
                    updates.append({
                        "parameterId": vts_param,
                        "value": clamped_value
                    })
            
            if updates:
                # Send batch update
                request = self.vts.vts_request.requestSetMultiParameterValue(updates)
                await self.vts.request(request)
                
        except Exception as e:
            logger.error(f"Failed to send parameter updates: {e}")
            # Attempt reconnection on failure
            if self.connection_attempts < self.max_connection_attempts:
                asyncio.create_task(self._reconnect())
    
    async def _reconnect(self):
        """Attempt to reconnect with fallback system"""
        self.connection_attempts += 1
        logger.info("Attempting to reconnect...")
        
        self.connected = False
        await asyncio.sleep(1)
        
        if await self._connect_with_fallback():
            self.connection_attempts = 0
            logger.info("Reconnection successful!")
        else:
            logger.error("Reconnection failed")
    
    # Public API Methods
    
    async def set_emotion(self, emotion: EmotionType, intensity: float = 1.0, duration: float = 2.0, easing: str = "ease_in_out"):
        """Set emotion with smooth transitions"""
        self.current_emotion = emotion
        self.emotion_intensity = intensity
        
        if emotion not in self.emotion_mappings:
            logger.warning(f"Unknown emotion: {emotion}")
            return
        
        # Get emotion parameter mappings
        emotion_params = self.emotion_mappings[emotion]
        
        # Create parameter updates with easing
        for param_name, target_value in emotion_params.items():
            # Scale by intensity
            scaled_value = target_value * intensity
            
            # Create smooth transition
            current_value = self.current_values.get(param_name, 0.0)
            
            self.active_parameters[param_name] = ParameterUpdate(
                parameter=param_name,
                target_value=scaled_value,
                current_value=current_value,
                duration=duration,
                start_time=time.time(),
                easing_function=easing,
                priority=1
            )
        
        logger.info(f"Set emotion: {emotion.value} (intensity: {intensity})")
    
    async def detect_emotion_from_speech(self, text: str) -> List[EmotionType]:
        """Automatic emotion detection from AI speech text"""
        emotions = []
        text_lower = text.lower()
        
        # Emotion detection patterns
        emotion_patterns = {
            EmotionType.HAPPY: ['happy', 'joy', 'smile', 'laugh', 'excited', 'wonderful', 'great', 'awesome'],
            EmotionType.SAD: ['sad', 'cry', 'tear', 'upset', 'sorry', 'unfortunate', 'disappointed'],
            EmotionType.ANGRY: ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated'],
            EmotionType.SURPRISED: ['wow', 'amazing', 'incredible', 'unbelievable', 'shocked', 'surprised'],
            EmotionType.FEARFUL: ['scared', 'afraid', 'fear', 'worried', 'nervous', 'anxious'],
            EmotionType.LOVE: ['love', 'adore', 'cherish', 'romantic', 'heart', 'dear'],
            EmotionType.EMBARRASSED: ['embarrassed', 'shy', 'blush', 'awkward', 'uncomfortable'],
            EmotionType.EXCITED: ['excited', 'thrilled', 'energetic', 'enthusiastic', 'pumped'],
            EmotionType.SLEEPY: ['tired', 'sleepy', 'exhausted', 'drowsy', 'yawn'],
            EmotionType.PLAYFUL: ['playful', 'tease', 'fun', 'silly', 'mischief'],
            EmotionType.CONFUSED: ['confused', 'puzzled', 'lost', 'uncertain', 'unclear'],
            EmotionType.DETERMINED: ['determined', 'focused', 'committed', 'resolved'],
            EmotionType.SERENE: ['calm', 'peaceful', 'serene', 'tranquil', 'relaxed']
        }
        
        # Check for emotion keywords
        for emotion, patterns in emotion_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    emotions.append(emotion)
                    break
        
        # Default to neutral if no emotions detected
        if not emotions:
            emotions.append(EmotionType.NEUTRAL)
        
        return emotions
    
    async def apply_speech_emotions(self, text: str, intensity: float = 0.8):
        """Apply emotions detected from speech with automatic transitions"""
        emotions = await self.detect_emotion_from_speech(text)
        
        for emotion in emotions:
            await self.set_emotion(emotion, intensity, duration=1.5)
            await asyncio.sleep(0.2)  # Brief delay between emotions
    
    def set_background_behavior(self, behavior_name: str, enabled: bool):
        """Enable/disable background behaviors"""
        if behavior_name in self.background_behaviors:
            self.background_behaviors[behavior_name].enabled = enabled
            logger.info(f"Background behavior '{behavior_name}': {'enabled' if enabled else 'disabled'}")
    
    def add_custom_behavior(self, name: str, parameters: Dict[str, Tuple[float, float]], frequency: float):
        """Add custom background behavior"""
        self.background_behaviors[name] = BackgroundBehavior(
            name=name,
            parameters=parameters,
            frequency=frequency,
            enabled=True
        )
        logger.info(f"Added custom behavior: {name}")
    
    async def set_parameter(self, parameter: str, value: float, duration: float = 1.0, easing: str = "ease_in_out"):
        """Set individual parameter with smooth transition"""
        current_value = self.current_values.get(parameter, 0.0)
        
        self.active_parameters[parameter] = ParameterUpdate(
            parameter=parameter,
            target_value=value,
            current_value=current_value,
            duration=duration,
            start_time=time.time(),
            easing_function=easing,
            priority=0
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information"""
        return {
            'connected': self.connected,
            'fallback_level': self.fallback_level.name,
            'fps': round(self.actual_fps, 1),
            'target_fps': self.target_fps,
            'model_name': self.model_config.model_name if self.model_config else 'Unknown',
            'available_parameters': len(self.model_config.available_parameters) if self.model_config else 0,
            'active_parameters': len(self.active_parameters),
            'background_behaviors': {name: behavior.enabled for name, behavior in self.background_behaviors.items()},
            'current_emotion': self.current_emotion.value,
            'emotion_intensity': self.emotion_intensity,
            'auto_discovery_complete': self.auto_discovery_complete
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Advanced VTube Controller...")
        
        self.running = False
        
        if self.update_thread:
            self.update_thread.join(timeout=5.0)
        
        if self.vts and self.connected:
            try:
                await self.vts.close()
            except Exception as e:
                logger.error(f"Error closing VTS connection: {e}")
        
        logger.info("Shutdown complete")

# Global controller instance
_controller_instance: Optional[AdvancedVTubeController] = None

async def get_controller() -> AdvancedVTubeController:
    """Get global controller instance (singleton pattern)"""
    global _controller_instance
    
    if _controller_instance is None:
        _controller_instance = AdvancedVTubeController()
        await _controller_instance.initialize()
    
    return _controller_instance

# Convenience functions for easy integration
async def set_emotion(emotion: str, intensity: float = 1.0):
    """Convenience function to set emotion"""
    controller = await get_controller()
    emotion_type = EmotionType(emotion.lower()) if emotion.lower() in [e.value for e in EmotionType] else EmotionType.NEUTRAL
    await controller.set_emotion(emotion_type, intensity)

async def process_ai_speech(text: str):
    """Process AI speech for automatic emotion detection and application"""
    controller = await get_controller()
    await controller.apply_speech_emotions(text)

async def get_vtube_status():
    """Get VTube Studio controller status"""
    controller = await get_controller()
    return controller.get_status()

if __name__ == "__main__":
    # Example usage
    async def main():
        controller = AdvancedVTubeController()
        
        if await controller.initialize():
            print("Controller initialized successfully!")
            print(f"Status: {controller.get_status()}")
            
            # Test emotions
            await controller.set_emotion(EmotionType.HAPPY, 0.8)
            await asyncio.sleep(3)
            
            await controller.set_emotion(EmotionType.SURPRISED, 1.0)
            await asyncio.sleep(3)
            
            # Test speech processing
            await controller.apply_speech_emotions("I'm so excited about this new feature!")
            await asyncio.sleep(5)
            
            await controller.shutdown()
        else:
            print("Failed to initialize controller")
    
    asyncio.run(main())
