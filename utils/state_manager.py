from typing import Dict, Any, Optional
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ComponentState:
    status: str
    last_updated: datetime
    metadata: Dict[str, Any]

class StateManager:
    def __init__(self):
        self.states: Dict[str, ComponentState] = {}
        self._lock = asyncio.Lock()
        
    async def update_state(self, component: str, status: str, metadata: Dict[str, Any] = None):
        async with self._lock:
            self.states[component] = ComponentState(
                status=status,
                last_updated=datetime.now(),
                metadata=metadata or {}
            )
            logging.info(f"State updated for {component}: {status}")
            
    async def get_state(self, component: str) -> Optional[ComponentState]:
        return self.states.get(component)
        
    async def get_all_states(self) -> Dict[str, ComponentState]:
        return self.states.copy() 