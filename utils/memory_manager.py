import numpy as np
try:
    from scipy.spatial.distance import cosine
except ImportError:
    raise ImportError("Please install scipy using: pip install scipy")
import json
import os
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count

class MemoryManager:
    def __init__(self, rag_processor, memory_file="long_term_memory.json"):
        self.rag = rag_processor
        self.memory_file = memory_file
        self.memories = self._load_memories()
        
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