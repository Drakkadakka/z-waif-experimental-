class DynamicExpressionMapper:
    def __init__(self):
        # Define a mapping of emotions to expressions
        self.expression_map = {
            "happy": "😊",
            "sad": "😢",
            "angry": "😠",
            "surprised": "😲",
            "neutral": "😐",
            "fearful": "😨",
            "disgusted": "🤢"
        }

    def get_expression(self, emotion):
        """Get the corresponding expression for a given emotion."""
        return self.expression_map.get(emotion, "🤔")  # Default to thinking face if emotion not found

# Example usage
if __name__ == "__main__":
    mapper = DynamicExpressionMapper()
    print(mapper.get_expression("happy"))  # Output: 😊
    print(mapper.get_expression("unknown"))  # Output: 🤔
