from typing import List, Optional
import asyncio
from dataclasses import dataclass

@dataclass
class VisualResult:
    image_path: str
    metadata_tags: List[str]
    confidence: float

class VisualHandler:
    def __init__(self, config_manager):
        self.config = config_manager
        self.current_stream = None
        
    async def process_visual(self, prompt: str) -> VisualResult:
        self.current_stream = asyncio.create_task(self._generate_visual(prompt))
        try:
            result = await self.current_stream
            return result
        except asyncio.CancelledError:
            return None

    def interrupt_stream(self):
        if self.current_stream and not self.current_stream.done():
            self.current_stream.cancel()

    async def reroll_result(self, prompt: str) -> VisualResult:
        self.interrupt_stream()
        return await self.process_visual(prompt) 