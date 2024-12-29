import asyncio
import json
import websockets
from utils.performance_metrics import track_performance
import logging
from utils.logging import log_info, log_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIHandler:
    def __init__(self, host="localhost", port=5005):
        log_info("Initializing AIHandler.")
        self.uri = f"ws://{host}:{port}/api/v1/stream"
        
    @track_performance
    async def generate_response(self, prompt, max_tokens=150):
        log_info(f"Generating response for prompt: {prompt}")
        request = {
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "preset": "None",
            "do_sample": True,
            "temperature": 0.8,
            "top_p": 0.9,
            "typical_p": 1,
            "repetition_penalty": 1.18,
            "encoder_repetition_penalty": 1.0,
            "top_k": 40,
            "min_length": 2,
            "no_repeat_ngram_size": 3,
            "num_beams": 1,
            "penalty_alpha": 0,
            "length_penalty": 1,
            "early_stopping": True,
            "seed": -1,
            "add_bos_token": True,
            "stopping_strings": ["\n\n", "User:", "Human:"],
            "stream": True
        }
        
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(json.dumps(request))
            response = ""
            async for message in websocket:
                data = json.loads(message)
                if data["event"] == "text_stream":
                    response += data["text"]
                elif data["event"] == "stream_end":
                    break
            return response.strip() 