import psutil
import time
import logging
import threading
from collections import deque
import datetime
import os

# Configure logging
logging.basicConfig(
    filename='performance.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Store historical data
MAX_POINTS = 60  # Keep last 60 data points
cpu_history = deque(maxlen=MAX_POINTS)
memory_history = deque(maxlen=MAX_POINTS)
time_history = deque(maxlen=MAX_POINTS)

def track_performance(func):
    """Decorator to track function performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Function '{func.__name__}' took {elapsed_time:.4f} seconds")
        return result
    return wrapper

def get_system_metrics():
    """Get current system metrics"""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    
    # Store in history
    cpu_history.append(cpu)
    memory_history.append(memory)
    time_history.append(current_time)
    
    return {
        'cpu': list(cpu_history),
        'memory': list(memory_history),
        'time': list(time_history)
    }

def monitor_system_resources():
    """Monitor system resources continuously"""
    while True:
        metrics = get_system_metrics()
        if metrics['cpu'][-1] > 90:
            logging.warning(f"High CPU usage: {metrics['cpu'][-1]}%")
        if metrics['memory'][-1] > 90:
            logging.warning(f"High memory usage: {metrics['memory'][-1]}%")
        time.sleep(5)

def start_resource_monitoring():
    """Start the resource monitoring in a background thread"""
    monitor_thread = threading.Thread(target=monitor_system_resources, daemon=True)
    monitor_thread.start()

def cleanup_logs(log_file='performance.log', days=7):
    """Clean up old log files"""
    try:
        file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(
            os.path.getctime(log_file)
        )
        if file_age.days > days:
            os.remove(log_file)
            logging.info(f"Removed old log file: {log_file}")
    except Exception as e:
        logging.error(f"Error cleaning up logs: {e}")
