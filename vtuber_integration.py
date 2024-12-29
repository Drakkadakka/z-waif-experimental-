from typing import Dict, Optional, Any, List
from collections import deque
import logging
import asyncio
from dataclasses import dataclass
from utils.error_boundary import ErrorBoundary

@dataclass
class EmotionExpression:
    name: str
    intensity: float
    duration: float
    priority: int = 0

@ErrorBoundary.system()
class VTuberIntegration:
    def __init__(self):
        self.connected = False
        self.connection_attempts = 0
        self.max_attempts = 3
        self.emote_queue = deque()
        self.current_emote: Optional[EmotionExpression] = None
        self.is_processing = False
        
    async def connect(self):
        try:
            try:
                from pyvts import VTubeStudioAPI
                self.vts = VTubeStudioAPI()
                await self.vts.connect()
                self.connected = True
                asyncio.create_task(self._process_emote_queue())
            except (ImportError, ConnectionRefusedError):
                logging.warning("VTubeStudio not available, running in mock mode")
                self.connected = False
            except Exception as e:
                logging.error(f"VTuber connection error: {e}")
                self.connected = False
        finally:
            self.connection_attempts += 1

    async def _process_emote_queue(self):
        """Process emotes in queue with proper timing"""
        self.is_processing = True
        while self.connected:
            if self.emote_queue:
                emote = self.emote_queue.popleft()
                self.current_emote = emote
                try:
                    await self.vts.execute_expression(
                        emote.name,
                        emote.intensity,
                        emote.duration
                    )
                    await asyncio.sleep(emote.duration)
                except Exception as e:
                    logging.error(f"Error executing emote {emote.name}: {e}")
                self.current_emote = None
            else:
                await asyncio.sleep(0.1)
        self.is_processing = False

    async def apply_emotion_expression(self, emotions: List[str], intensity: float = 1.0) -> bool:
        """Apply emotions even if VTubeStudio isn't connected"""
        try:
            if not self.connected and self.connection_attempts < self.max_attempts:
                await self.connect()
                
            # Process emotions regardless of connection status
            for emotion in emotions:
                expression = self._map_emotion_to_expression(emotion, intensity)
                self.emote_queue.append(expression)
                logging.info(f"Queued emotion: {emotion} (connected: {self.connected})")
                
            if self.connected and not self.is_processing:
                asyncio.create_task(self._process_emote_queue())
            return True
        except Exception as e:
            logging.error(f"Error queueing emotion expressions: {e}")
            return False

    def _map_emotion_to_expression(self, emotion: str, intensity: float) -> EmotionExpression:
        # Enhanced emotion mapping with priorities
        emotion_map = {
            'happy': ('joy', 1),
            'sad': ('sadness', 1),
            'angry': ('anger', 2),  # Higher priority for strong emotions
            'surprised': ('surprise', 2),
            'neutral': ('neutral', 0),
            'laugh': ('laugh', 2),
            'wink': ('wink', 1),
            'blush': ('blush', 1),
            'cry': ('cry', 2),
            'scared': ('scared', 2)
        }
        
        vts_name, priority = emotion_map.get(emotion.lower(), ('neutral', 0))
        return EmotionExpression(
            name=vts_name,
            intensity=min(max(intensity, 0.0), 1.0),
            duration=2.0,
            priority=priority
        )

    def clear_emote_queue(self):
        """Clear pending emotes"""
        self.emote_queue.clear()
        
    def get_current_emote(self) -> Optional[EmotionExpression]:
        """Get currently playing emote"""
        return self.current_emote 