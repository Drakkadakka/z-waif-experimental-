from ai_handler import AIHandler

class DiscordHandler:
    def __init__(self):
        self.ai = AIHandler()
        
    async def process(self, message_data):
        """Process messages from Discord"""
        if message_data.get('needs_ai_response', False):
            prompt = self._format_prompt(message_data['content'])
            response = await self.ai.generate_response(prompt)
            return response
        return None
        
    def _format_prompt(self, content):
        return f"User: {content}\nAssistant: " 