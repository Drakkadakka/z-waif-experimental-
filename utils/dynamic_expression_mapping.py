import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DynamicExpressionMapper:
    def __init__(self):
        logging.info("Initializing DynamicExpressionMapper.")
        # Expanded mapping of emotions to expressions
        self.expression_map = {
            "happy": "😊",
            "very_happy": "😁",
            "sad": "😢",
            "very_sad": "😭",
            "angry": "😠",
            "frustrated": "😤",
            "surprised": "😲",
            "neutral": "😐",
            "excited": "🎉",
            "confused": "🤔",
            "bored": "😴",
            "anxious": "😟",
            "disgusted": "🤢",
            "hopeful": "🌈",
            # Add more emotions as needed
        }

    def get_expression(self, emotion):
        logging.info(f"Getting expression for emotion: {emotion}.")
        """Get the corresponding expression for a given emotion."""
        return self.expression_map.get(emotion, "🤔")  # Default to thinking face if emotion not found

# Example usage
if __name__ == "__main__":
    mapper = DynamicExpressionMapper()
    print(mapper.get_expression("happy"))  # Output: 😊
    print(mapper.get_expression("unknown"))  # Output: 🤔
