import psutil
import logging
from dataclasses import dataclass
from typing import Dict, Optional
import time

@dataclass
class ResourceStats:
    cpu_percent: float
    memory_percent: float
    timestamp: float

class ResourceMonitor:
    def __init__(self):
        self.stats_history: Dict[str, list[ResourceStats]] = {}
        self.warning_thresholds = {
            'cpu': 80.0,
            'memory': 80.0
        }

    async def monitor_resources(self, component_name: str) -> ResourceStats:
        stats = ResourceStats(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            timestamp=time.time()
        )
        
        if component_name not in self.stats_history:
            self.stats_history[component_name] = []
        
        self.stats_history[component_name].append(stats)
        
        # Check thresholds
        if stats.cpu_percent > self.warning_thresholds['cpu']:
            logging.warning(f"High CPU usage ({stats.cpu_percent}%) in {component_name}")
        if stats.memory_percent > self.warning_thresholds['memory']:
            logging.warning(f"High memory usage ({stats.memory_percent}%) in {component_name}")
            
        return stats 