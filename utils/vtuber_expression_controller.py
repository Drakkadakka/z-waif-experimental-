from typing import Dict, List, Optional
import asyncio
import logging
from dataclasses import dataclass
import pyvts

@dataclass
class EmoteSequence:
    emotes: List[str]
    durations: List[float]
    intensities: List[float]

class VTuberExpressionController:
    def __init__(self):
        self.current_sequence: Optional[EmoteSequence] = None
        self.sequence_task: Optional[asyncio.Task] = None
        self.vts = None
        self.plugin_info = {
            "plugin_name": "Waifu",
            "developer": "TumblerWarren",
            "authentication_token_path": "./pyvts_token.txt"
        }
        
    async def initialize(self):
        """Initialize VTS connection"""
        try:
            self.vts = pyvts.vts(plugin_info=self.plugin_info)
            await self.vts.connect()
            await self.vts.request_authenticate_token()
            await self.vts.request_authenticate()
            logging.info("VTS connection established")
        except Exception as e:
            logging.error(f"Failed to initialize VTS: {e}")
            self.vts = None
            
    async def set_expression(self, emote: str, intensity: float):
        """Set VTube Studio expression"""
        if not self.vts:
            await self.initialize()
            
        try:
            # Map emote names to VTS parameter names
            parameter = self._map_emote_to_parameter(emote)
            if parameter and self.vts:
                await self.vts.request(
                    self.vts.vts_request.requestSetParameterValue(
                        parameter=parameter,
                        value=intensity
                    )
                )
        except Exception as e:
            logging.error(f"Error setting expression {emote}: {e}")
            
    def _map_emote_to_parameter(self, emote: str) -> str:
        """Map emote names to VTS parameters"""
        # Add your emote to parameter mappings here
        emote_map = {
            "happy": "MouthSmile",
            "sad": "MouthSad",
            "surprised": "EyeOpenLeft",
            "angry": "EyebrowAngry",
            "neutral": "FaceNeutral"
        }
        return emote_map.get(emote.lower(), "FaceNeutral")
        
    async def stream_emotes(self, text: str, emote_sequence: EmoteSequence):
        """Stream emotes as text appears"""
        if self.sequence_task:
            self.sequence_task.cancel()
            
        self.sequence_task = asyncio.create_task(
            self._play_emote_sequence(emote_sequence)
        )
        
    async def _play_emote_sequence(self, sequence: EmoteSequence):
        """Play through a sequence of emotes with timing"""
        try:
            for emote, duration, intensity in zip(
                sequence.emotes, 
                sequence.durations,
                sequence.intensities
            ):
                await self.set_expression(emote, intensity)
                await asyncio.sleep(duration)
        except asyncio.CancelledError:
            logging.info("Emote sequence cancelled")
        except Exception as e:
            logging.error(f"Error in emote sequence: {e}") 