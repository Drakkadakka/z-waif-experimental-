import logging

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
