import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Attempting to import required ML packages...")
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    import torch
    logger.info("Successfully imported transformers and torch packages")
except ImportError as e:
    logger.error(f"Failed to import required packages: {str(e)}")
    logger.info("Please install required packages using: pip install transformers torch bitsandbytes")

def setup_model_config():
    # Optimal quantization config for 16GB VRAM
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    # Model configuration
    model_config = {
        "model_id": "facebook/opt-6.7b",  # No authentication required
        "device_map": "auto",
        "torch_dtype": torch.float16,
        "quantization_config": quantization_config,
    }

    return model_config

def load_model():
    config = setup_model_config()
    
    model = AutoModelForCausalLM.from_pretrained(
        config["model_id"],
        device_map=config["device_map"],
        torch_dtype=config["torch_dtype"],
        quantization_config=config["quantization_config"]
    )
    
    tokenizer = AutoTokenizer.from_pretrained(config["model_id"])
    
    return model, tokenizer 