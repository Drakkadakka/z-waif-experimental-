from ai_handler import AIHandler
from memory_manager import MemoryManager
from rag_processor import MultiprocessRAG
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Please install sentence-transformers using: pip install sentence-transformers")

class TwitchHandler:
    def __init__(self):
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        rag_processor = MultiprocessRAG(embedding_model)
        self.memory_manager = MemoryManager(rag_processor)
        self.ai = AIHandler()
        
    async def process(self, message_data):
        if message_data.get('needs_ai_response', False):
            # Get relevant memories
            relevant_memories = await self.memory_manager.retrieve_relevant_memories(
                message_data['content']
            )
            
            # Add current interaction to memories
            await self.memory_manager.add_memory(
                message_data['content'],
                context={'user_id': message_data['user_id']}
            )
            
            # Create context-aware prompt
            prompt = self._format_prompt(
                content=message_data['content'],
                memories=relevant_memories,
                username=message_data.get('username', 'User')
            )
            
            response = await self.ai.generate_response(prompt)
            return response
        return None
        
    def _format_prompt(self, content, memories, username):
        memory_context = "\n".join(memories) if memories else "No relevant memories."
        return f"""Context: You are a Twitch chat AI assistant.
Relevant memories:
{memory_context}

Current interaction:
{username}: {content}
Assistant: """ 