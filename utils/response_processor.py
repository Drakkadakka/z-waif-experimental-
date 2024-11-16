class ResponseProcessor:
    def __init__(self):
        self.platform_formatters = {
            "twitch": self.format_twitch_response,
            "discord": self.format_discord_response
        }
        
    async def process_response(self, response, platform, user_context):
        """Process and format AI response based on platform and context"""
        # Apply platform-specific formatting
        formatted_response = self.platform_formatters.get(
            platform, 
            lambda x: x
        )(response)
        
        # Add appropriate emotes/emoji
        formatted_response = self.add_platform_emotes(formatted_response, platform)
        
        # Adjust response style based on user context
        formatted_response = self.adjust_style(formatted_response, user_context)
        
        return formatted_response 