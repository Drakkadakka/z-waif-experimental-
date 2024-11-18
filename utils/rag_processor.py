from multiprocessing import Pool, cpu_count
import numpy as np
from datetime import datetime
import logging

class MultiprocessRAG:
    def __init__(self, embedding_model, chunk_size=1000, max_workers=None):
        self.chunk_size = chunk_size
        self.embedding_model = embedding_model
        self.max_workers = max_workers or (cpu_count() - 1)
        
    def _chunk_processor(self, text_chunk):
        """Process individual chunks in separate processes"""
        try:
            embedding = self.embedding_model.encode(text_chunk)
            return {
                'text': text_chunk,
                'embedding': embedding,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error processing chunk: {e}")
            return None
            
    def process_documents(self, documents):
        """Process multiple documents in parallel"""
        chunks = self._split_documents(documents)
        
        with Pool(processes=self.max_workers) as pool:
            results = pool.map(self._chunk_processor, chunks)
            
        return [r for r in results if r is not None]
        
    def _split_documents(self, documents):
        """Split documents into chunks for processing"""
        chunks = []
        for doc in documents:
            # Simple splitting strategy - can be made more sophisticated
            words = doc.split()
            for i in range(0, len(words), self.chunk_size):
                chunk = ' '.join(words[i:i + self.chunk_size])
                chunks.append(chunk)
        return chunks 