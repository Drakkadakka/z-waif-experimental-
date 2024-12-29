from typing import Dict, Any, Optional, List
import time
import logging
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PerformanceMetrics:
    response_time: float
    timestamp: datetime
    function_name: str
    success: bool

class PerformanceTracker:
    def __init__(self, history_retention_days: int = 7):
        self.metrics_history: Dict[str, List[PerformanceMetrics]] = {}
        self.retention_period = timedelta(days=history_retention_days)
        
    def track_performance(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    end_time = time.time()
                    self._record_metrics(func.__name__, end_time - start_time, success)
            return wrapper
        return decorator
        
    def _record_metrics(self, function_name: str, response_time: float, success: bool):
        if function_name not in self.metrics_history:
            self.metrics_history[function_name] = []
            
        self.metrics_history[function_name].append(
            PerformanceMetrics(
                response_time=response_time,
                timestamp=datetime.now(),
                function_name=function_name,
                success=success
            )
        )
        self._cleanup_old_metrics()
        
        if response_time > 1.0:  # Alert on slow responses
            logging.warning(f"Slow response time in {function_name}: {response_time:.2f}s")
            
    def _cleanup_old_metrics(self):
        cutoff_time = datetime.now() - self.retention_period
        for func_name in self.metrics_history:
            self.metrics_history[func_name] = [
                metric for metric in self.metrics_history[func_name]
                if metric.timestamp > cutoff_time
            ]