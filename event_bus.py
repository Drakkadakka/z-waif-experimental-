from typing import Dict, List, Callable, Any
import asyncio
import logging

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        
    async def subscribe(self, event_type: str, callback: Callable):
        async with self._lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(callback)
            
    async def publish(self, event_type: str, data: Any = None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logging.error(f"Error in event handler: {e}") 