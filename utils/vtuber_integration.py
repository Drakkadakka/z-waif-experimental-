from typing import Dict, Optional, Any, List
from collections import deque
import logging
import asyncio
from dataclasses import dataclass
from utils.error_boundary import ErrorBoundary
from utils.logging import log_info, log_error, update_debug_log

# Import advanced controller components
try:
    from utils.advanced_vtube_controller import (
        AdvancedVTubeController, 
        EmotionType, 
        get_controller,
        process_ai_speech as vtube_process_speech
    )
    ADVANCED_CONTROLLER_AVAILABLE = True
except ImportError:
    ADVANCED_CONTROLLER_AVAILABLE = False
    logging.warning("Advanced VTube controller not available, using legacy mode")

@dataclass
class EmotionExpression:
    name: str
    intensity: float
    duration: float
    priority: int = 0

@ErrorBoundary.system()
class VTuberIntegration:
    def __init__(self, use_advanced_controller: bool = True):
        # Legacy compatibility
        self.connected = False
        self.connection_attempts = 0
        self.max_attempts = 3
        self.emote_queue = deque()
        self.current_emote: Optional[EmotionExpression] = None
        self.is_processing = False
        
        # Advanced controller integration
        self.use_advanced_controller = use_advanced_controller and ADVANCED_CONTROLLER_AVAILABLE
        self.advanced_controller: Optional[AdvancedVTubeController] = None
        self.auto_emotion_detection = True
        self.emotion_intensity_multiplier = 0.8
        
        # Legacy VTS API (fallback)
        self.vts = None
        
    async def connect(self):
        """Enhanced connection with advanced controller support"""
        try:
            if self.use_advanced_controller:
                await self._connect_advanced()
            else:
                await self._connect_legacy()
        except Exception as e:
            log_error(f"VTuber connection error: {e}")
            self.connected = False
        finally:
            self.connection_attempts += 1
    
    async def _connect_advanced(self):
        """Connect using advanced controller"""
        try:
            log_info("Connecting with Advanced VTube Controller...")
            self.advanced_controller = await get_controller()
            
            if self.advanced_controller:
                status = self.advanced_controller.get_status()
                self.connected = status['connected']
                
                if self.connected:
                    log_info(f"Advanced VTube Controller connected: {status['model_name']}")
                    update_debug_log(f"VTube FPS: {status['fps']}")
                    update_debug_log(f"Available parameters: {status['available_parameters']}")
                    
                    # Start processing with advanced controller
                    if not self.is_processing:
                        asyncio.create_task(self._process_emote_queue())
                else:
                    log_error("Advanced controller initialized but not connected to VTube Studio")
            else:
                log_error("Failed to initialize advanced controller")
                
        except Exception as e:
            log_error(f"Advanced controller connection failed: {e}")
            # Fallback to legacy
            await self._connect_legacy()
    
    async def _connect_legacy(self):
        """Legacy connection method"""
        try:
            from pyvts import VTubeStudioAPI
            self.vts = VTubeStudioAPI()
            await self.vts.connect()
            self.connected = True
            log_info("Connected using legacy VTube Studio API")
            asyncio.create_task(self._process_emote_queue())
        except (ImportError, ConnectionRefusedError):
            logging.warning("VTubeStudio not available, running in mock mode")
            self.connected = False
        except Exception as e:
            logging.error(f"Legacy VTuber connection error: {e}")
            self.connected = False

    async def _process_emote_queue(self):
        """Enhanced emote processing with advanced controller support"""
        self.is_processing = True
        
        while self.connected:
            if self.emote_queue:
                emote = self.emote_queue.popleft()
                self.current_emote = emote
                
                try:
                    if self.use_advanced_controller and self.advanced_controller:
                        await self._apply_emote_advanced(emote)
                    else:
                        await self._apply_emote_legacy(emote)
                        
                    await asyncio.sleep(emote.duration)
                except Exception as e:
                    log_error(f"Error executing emote {emote.name}: {e}")
                    
                self.current_emote = None
            else:
                await asyncio.sleep(0.1)
                
        self.is_processing = False
    
    async def _apply_emote_advanced(self, emote: EmotionExpression):
        """Apply emote using advanced controller"""
        # Map legacy emotion names to new EmotionType
        emotion_mapping = {
            'joy': EmotionType.HAPPY,
            'sadness': EmotionType.SAD,
            'anger': EmotionType.ANGRY,
            'surprise': EmotionType.SURPRISED,
            'neutral': EmotionType.NEUTRAL,
            'laugh': EmotionType.HAPPY,
            'wink': EmotionType.PLAYFUL,
            'blush': EmotionType.EMBARRASSED,
            'cry': EmotionType.SAD,
            'scared': EmotionType.FEARFUL
        }
        
        emotion_type = emotion_mapping.get(emote.name.lower(), EmotionType.NEUTRAL)
        await self.advanced_controller.set_emotion(
            emotion_type, 
            emote.intensity * self.emotion_intensity_multiplier, 
            emote.duration
        )
        log_info(f"Applied advanced emotion: {emotion_type.value}")
    
    async def _apply_emote_legacy(self, emote: EmotionExpression):
        """Apply emote using legacy VTS API"""
        if self.vts:
            await self.vts.execute_expression(
                emote.name,
                emote.intensity,
                emote.duration
            )
            log_info(f"Applied legacy emotion: {emote.name}")

    async def apply_emotion_expression(self, emotions: List[str], intensity: float = 1.0) -> bool:
        """Apply emotions with enhanced processing"""
        try:
            if not self.connected and self.connection_attempts < self.max_attempts:
                await self.connect()
                
            # Process emotions regardless of connection status
            for emotion in emotions:
                expression = self._map_emotion_to_expression(emotion, intensity)
                self.emote_queue.append(expression)
                log_info(f"Queued emotion: {emotion} (connected: {self.connected})")
                
            if self.connected and not self.is_processing:
                asyncio.create_task(self._process_emote_queue())
            return True
        except Exception as e:
            log_error(f"Error queueing emotion expressions: {e}")
            return False
    
    async def process_ai_speech(self, text: str, speaker: str = "AI") -> bool:
        """New method: Process AI speech for automatic emotion detection"""
        if not self.connected:
            return False
            
        try:
            if self.use_advanced_controller and self.advanced_controller and self.auto_emotion_detection:
                # Use advanced emotion detection
                await vtube_process_speech(text)
                log_info(f"Applied AI speech emotions: {text[:50]}...")
                update_debug_log(f"VTube emotion applied for: {speaker}")
                return True
            else:
                # Fallback to manual emotion detection
                emotions = self._detect_emotions_from_text(text)
                return await self.apply_emotion_expression(emotions, 0.8)
                
        except Exception as e:
            log_error(f"Error processing AI speech: {e}")
            return False
    
    def _detect_emotions_from_text(self, text: str) -> List[str]:
        """Simple emotion detection from text (fallback)"""
        text_lower = text.lower()
        emotions = []
        
        if any(word in text_lower for word in ['happy', 'joy', 'great', 'awesome', 'wonderful']):
            emotions.append('happy')
        if any(word in text_lower for word in ['sad', 'upset', 'disappointed', 'sorry']):
            emotions.append('sad')
        if any(word in text_lower for word in ['angry', 'mad', 'frustrated', 'annoyed']):
            emotions.append('angry')
        if any(word in text_lower for word in ['surprised', 'wow', 'amazing', 'incredible']):
            emotions.append('surprised')
        if any(word in text_lower for word in ['scared', 'afraid', 'worried', 'nervous']):
            emotions.append('scared')
        
        return emotions if emotions else ['neutral']
    
    async def set_manual_emotion(self, emotion: str, intensity: float = 1.0, duration: float = 2.0) -> bool:
        """New method: Manually set an emotion"""
        if not self.connected:
            return False
            
        try:
            if self.use_advanced_controller and self.advanced_controller:
                # Use advanced controller
                emotion_type = None
                for e in EmotionType:
                    if e.value.lower() == emotion.lower():
                        emotion_type = e
                        break
                
                if emotion_type:
                    await self.advanced_controller.set_emotion(emotion_type, intensity, duration)
                    log_info(f"Set manual emotion: {emotion}")
                    return True
                else:
                    log_error(f"Unknown emotion: {emotion}")
                    return False
            else:
                # Use legacy method
                expression = self._map_emotion_to_expression(emotion, intensity)
                expression.duration = duration
                self.emote_queue.append(expression)
                return True
                
        except Exception as e:
            log_error(f"Error setting manual emotion: {e}")
            return False
    
    def configure_background_behaviors(self, **behaviors) -> bool:
        """New method: Configure background behaviors"""
        if self.use_advanced_controller and self.advanced_controller:
            try:
                for behavior_name, enabled in behaviors.items():
                    self.advanced_controller.set_background_behavior(behavior_name, enabled)
                log_info(f"Background behaviors configured: {behaviors}")
                return True
            except Exception as e:
                log_error(f"Error configuring background behaviors: {e}")
                return False
        else:
            log_info("Background behaviors not available in legacy mode")
            return False
    
    def set_auto_emotion_detection(self, enabled: bool):
        """New method: Enable/disable auto emotion detection"""
        self.auto_emotion_detection = enabled
        log_info(f"Auto emotion detection: {'enabled' if enabled else 'disabled'}")
    
    def set_emotion_intensity(self, multiplier: float):
        """New method: Set emotion intensity multiplier"""
        self.emotion_intensity_multiplier = max(0.0, min(2.0, multiplier))
        log_info(f"Emotion intensity set to: {self.emotion_intensity_multiplier}")

    def _map_emotion_to_expression(self, emotion: str, intensity: float) -> EmotionExpression:
        """Enhanced emotion mapping with more emotions"""
        emotion_map = {
            'happy': ('joy', 1),
            'sad': ('sadness', 1),
            'angry': ('anger', 2),
            'surprised': ('surprise', 2),
            'neutral': ('neutral', 0),
            'laugh': ('laugh', 2),
            'wink': ('wink', 1),
            'blush': ('blush', 1),
            'cry': ('cry', 2),
            'scared': ('scared', 2),
            'excited': ('joy', 2),
            'confused': ('neutral', 1),
            'sleepy': ('neutral', 0),
            'love': ('blush', 1),
            'embarrassed': ('blush', 1),
            'playful': ('wink', 1)
        }
        
        vts_name, priority = emotion_map.get(emotion.lower(), ('neutral', 0))
        return EmotionExpression(
            name=vts_name,
            intensity=min(max(intensity, 0.0), 1.0),
            duration=2.0,
            priority=priority
        )
    
    def get_status(self) -> Dict[str, Any]:
        """New method: Get comprehensive status"""
        status = {
            'connected': self.connected,
            'use_advanced_controller': self.use_advanced_controller,
            'advanced_controller_available': ADVANCED_CONTROLLER_AVAILABLE,
            'connection_attempts': self.connection_attempts,
            'emote_queue_length': len(self.emote_queue),
            'current_emote': self.current_emote.name if self.current_emote else None,
            'is_processing': self.is_processing,
            'auto_emotion_detection': self.auto_emotion_detection,
            'emotion_intensity_multiplier': self.emotion_intensity_multiplier
        }
        
        if self.use_advanced_controller and self.advanced_controller:
            status['advanced_status'] = self.advanced_controller.get_status()
            
        return status

    def clear_emote_queue(self):
        """Clear pending emotes"""
        self.emote_queue.clear()
        
    def get_current_emote(self) -> Optional[EmotionExpression]:
        """Get currently playing emote"""
        return self.current_emote
    
    async def shutdown(self):
        """New method: Graceful shutdown"""
        self.connected = False
        self.is_processing = False
        
        if self.use_advanced_controller and self.advanced_controller:
            await self.advanced_controller.shutdown()
            
        if self.vts:
            try:
                await self.vts.close()
            except:
                pass
                
        log_info("VTuber integration shut down")

# Global instance for backward compatibility
_global_vtuber_integration: Optional[VTuberIntegration] = None

async def get_vtuber_integration() -> VTuberIntegration:
    """Get global VTuber integration instance"""
    global _global_vtuber_integration
    
    if _global_vtuber_integration is None:
        _global_vtuber_integration = VTuberIntegration()
        await _global_vtuber_integration.connect()
    
    return _global_vtuber_integration

# Convenience functions for easy integration
async def apply_ai_emotions(text: str, speaker: str = "AI") -> bool:
    """Apply emotions from AI text to VTube model"""
    integration = await get_vtuber_integration()
    return await integration.process_ai_speech(text, speaker)

async def set_vtube_emotion(emotion: str, intensity: float = 1.0) -> bool:
    """Set VTube model emotion manually"""
    integration = await get_vtuber_integration()
    return await integration.set_manual_emotion(emotion, intensity)

async def get_vtube_status() -> Dict[str, Any]:
    """Get VTube integration status"""
    integration = await get_vtuber_integration()
    return integration.get_status()

def configure_vtube_behaviors(**behaviors) -> bool:
    """Configure VTube background behaviors"""
    async def _configure():
        integration = await get_vtuber_integration()
        return integration.configure_background_behaviors(**behaviors)
    
    try:
        return asyncio.run(_configure())
    except:
        return False

# Legacy emote mapping for backward compatibility with EmoteLib.json
LEGACY_EMOTE_MAPPING = {
    "Pog": "surprised",
    "Surprise": "surprised", 
    "Cry": "sad",
    "Cries": "sad",
    "Distress": "scared",
    "Angr": "angry",
    "Mad": "angry",
    "Wink": "playful",
    "Sleep": "sleepy",
    "Slumber": "sleepy",
    "Excite": "excited",
    "Frown": "sad",
    "Sad": "sad",
    "Upset": "sad",
    "Seduc": "love",
    "Flirt": "playful",
    "Lovingly": "love",
    "Blush": "embarrassed",
    "Red": "embarrassed",
    "Smile": "happy",
    "Grin": "happy"
}

async def apply_legacy_emote(emote_string: str) -> bool:
    """Apply legacy emote from EmoteLib.json using new system"""
    clean_emote = emote_string.replace("*", "").strip().title()
    
    emotion = LEGACY_EMOTE_MAPPING.get(clean_emote, "neutral")
    integration = await get_vtuber_integration()
    return await integration.set_manual_emotion(emotion, 0.8) 