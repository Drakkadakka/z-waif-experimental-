from typing import Optional, AsyncGenerator
import asyncio
import logging
from utils.vtuber_expression_controller import VTuberExpressionController
from utils.config import Config

class StreamHandler:
    def __init__(self):
        self.current_task: Optional[asyncio.Task] = None
        
    async def stream_with_expressions(
        self,
        text_generator: AsyncGenerator[str, None],
        expression_controller: VTuberExpressionController
    ):
        try:
            if self.current_task:
                self.current_task.cancel()
                
            async for chunk in text_generator:
                # Check for stopping strings
                if any(stop in chunk for stop in Config().ui.stopping_strings):
                    break
                    
                # Update expressions as text streams
                await expression_controller.stream_emotes(chunk)
                yield chunk
                
        except asyncio.CancelledError:
            logging.info("Stream interrupted")
        finally:
            self.current_task = None 