import gc  # for garbage collection
import torch  # add this import

class ChatHandler:
    def __init__(self):
        self.message_cache = []
        self.max_cache_size = 50  # Adjust based on your needs
        self.model = self.initialize_model()  # Add model initialization
        
    def initialize_model(self):
        # Initialize your model here
        # Example: return AutoModelForCausalLM.from_pretrained("model_name")
        pass

    async def handle_message(self, message):
        # Periodically clear message cache
        if len(self.message_cache) > self.max_cache_size:
            self.message_cache = self.message_cache[-self.max_cache_size:]
            gc.collect()  # Force garbage collection
            
        # Clear CUDA cache if using GPU
        if torch.cuda.is_available():
            torch.cuda.empty_cache() 

def cleanup_resources():
    # Clear CUDA cache if GPU is available
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Force garbage collection
    gc.collect()

def chat_response(self, message):
    try:
        response = self.model.generate(...)  # Use self.model instead of model
        cleanup_resources()
        return response
    except Exception as e:
        cleanup_resources()
        raise e