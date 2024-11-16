def clean_response(response: str) -> str:
    """
    Clean and format AI response for Twitch chat
    """
    # Remove multiple newlines
    response = ' '.join(response.split())
    
    # Truncate if too long (Twitch has a 500 char limit)
    if len(response) > 500:
        response = response[:497] + "..."
        
    # Remove any potential unsafe content
    # TODO: Add more content filtering as needed
    
    return response 