import logging
from typing import Dict, Callable
from datetime import datetime, timedelta

class RecoveryManager:
    def __init__(self):
        self.recovery_strategies: Dict[str, Callable] = {}
        self.failure_counts: Dict[str, int] = {}
        self.last_failures: Dict[str, datetime] = {}
        self.max_retries = 3
        self.cooldown_period = timedelta(minutes=5)
        
    async def register_recovery_strategy(self, component: str, strategy: Callable):
        self.recovery_strategies[component] = strategy
        self.failure_counts[component] = 0
        
    async def handle_failure(self, component: str, error: Exception) -> bool:
        if component not in self.recovery_strategies:
            logging.error(f"No recovery strategy for {component}")
            return False
            
        now = datetime.now()
        if component in self.last_failures:
            if now - self.last_failures[component] < self.cooldown_period:
                self.failure_counts[component] += 1
            else:
                self.failure_counts[component] = 1
                
        self.last_failures[component] = now
        
        if self.failure_counts[component] > self.max_retries:
            logging.error(f"Max retries exceeded for {component}")
            return False
            
        try:
            await self.recovery_strategies[component](error)
            return True
        except Exception as e:
            logging.error(f"Recovery failed for {component}: {e}")
            return False 