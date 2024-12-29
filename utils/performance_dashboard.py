from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from .performance_tracker import PerformanceMetrics
from .resource_monitor import ResourceStats

class PerformanceDashboard:
    def __init__(self):
        self.performance_tracker = None
        self.resource_monitor = None
        
    async def initialize(self, perf_tracker, resource_monitor):
        self.performance_tracker = perf_tracker
        self.resource_monitor = resource_monitor
        
    async def get_performance_summary(self, time_window: timedelta = timedelta(hours=1)) -> Dict:
        cutoff_time = datetime.now() - time_window
        summary = {
            'response_times': {},
            'resource_usage': {
                'cpu': [],
                'memory': []
            },
            'error_rates': {}
        }
        
        # Analyze response times
        for func_name, metrics in self.performance_tracker.metrics_history.items():
            recent_metrics = [m for m in metrics if m.timestamp > cutoff_time]
            if recent_metrics:
                avg_response = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
                error_rate = len([m for m in recent_metrics if not m.success]) / len(recent_metrics)
                summary['response_times'][func_name] = avg_response
                summary['error_rates'][func_name] = error_rate
                
        # Add resource usage data
        for component, stats in self.resource_monitor.stats_history.items():
            recent_stats = [s for s in stats if s.timestamp > cutoff_time.timestamp()]
            if recent_stats:
                summary['resource_usage']['cpu'].extend([s.cpu_percent for s in recent_stats])
                summary['resource_usage']['memory'].extend([s.memory_percent for s in recent_stats])
                
        return summary 