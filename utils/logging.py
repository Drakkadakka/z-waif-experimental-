import logging
import datetime

# Create a logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define log variables
debug_log = ""
rag_log = ""
kelvin_log = ""

def log_debug(message):
    global debug_log
    debug_log += f"{message}\n"
    logger.debug(message)

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def update_rag_log(message):
    global rag_log
    rag_log += f"{message}\n"
    logger.info(message)

def clear_rag_log():
    global rag_log
    rag_log = ""  # Clear the rag_log
    logger.info("RAG log cleared.")

def update_debug_log(message: str, log_file: str = "debug.log") -> None:
    """
    Updates the debug log file with a timestamped message
    
    Args:
        message (str): The message to log
        log_file (str): The path to the log file (defaults to debug.log)
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")
