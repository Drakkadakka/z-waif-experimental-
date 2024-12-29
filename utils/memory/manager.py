from utils.logging import track_response_time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemoryManager:
    def __init__(self):
        logging.info("Initializing MemoryManager.")
        self.memories = {}
        
    @track_response_time
    def add_memory(self, author, context, platform):
        if author not in self.memories:
            self.memories[author] = []
        self.memories[author].append({
            "context": context,
            "platform": platform
        }) 

    @track_response_time
    def store_emotional_state(self, user_id, emotion, intensity):
        if user_id not in self.memories:
            self.memories[user_id] = []
        self.memories[user_id].append({
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.now()
        })

    @track_response_time
    def get_user_emotional_history(self, user_id):
        return self.memories.get(user_id, []) 