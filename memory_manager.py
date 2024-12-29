import numpy as np
try:
    from scipy.spatial.distance import cosine
except ImportError:
    raise ImportError("Please install scipy using: pip install scipy")
import json
import os
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count
import logging
from utils.logging import log_info, log_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemoryManager:
    def __init__(self, rag_processor, memory_file="long_term_memory.json"):
        log_info("Initializing MemoryManager.")
        self.rag = rag_processor
        self.memories = {}
        self.interaction_history = []
        self.video_context = {}
        
    def _load_memories(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return []
        
    def save_memories(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
            
    async def add_memory(self, text, context=None):
        """Add new memory with parallel processing"""
        processed_memories = self.rag.process_documents([text])
        
        for memory in processed_memories:
            memory['context'] = context
            self.memories.append(memory)
            
        self.save_memories()
        
    async def retrieve_relevant_memories(self, query, top_k=5):
        """Retrieve relevant memories using parallel processing"""
        query_embedding = self.rag.embedding_model.encode(query)
        
        def calculate_similarity(memory):
            try:
                return 1 - cosine(query_embedding, memory['embedding'])
            except:
                return -1
                
        with Pool(processes=self.rag.max_workers) as pool:
            similarities = pool.map(calculate_similarity, self.memories)
            
        # Get top-k memories
        memory_scores = list(zip(self.memories, similarities))
        memory_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [memory['text'] for memory, score in memory_scores[:top_k] if score > 0] 

    def store_interaction(self, user_id, message, response, context=None):
        log_info(f"Storing interaction for user: {user_id}.")
        if user_id not in self.memories:
            self.memories[user_id] = []
        
        interaction = {
            'timestamp': datetime.now(),
            'message': message,
            'response': response,
            'context': context
        }
        
        self.memories[user_id].append(interaction)
        self.interaction_history.append(interaction)

    def get_recent_interactions(self, user_id, limit=10):
        return self.memories.get(user_id, [])[-limit:]

    def add_memory(self, user_id, context, platform):
        log_info(f"Adding memory for user: {user_id}")
        # Your existing code...