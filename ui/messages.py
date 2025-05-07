"""
User-facing messages and error formatting for the UI application.
"""
import requests
from typing import Dict, Any, Type, Callable

# Error messages by exception type
ERROR_MESSAGES: Dict[Type[Exception], str] = {
    requests.ConnectionError: "Connection Error: Could not connect to the server. Please check if the server is running.",
    requests.Timeout: "Timeout Error: The server took too long to respond. Please try again later.",
    requests.RequestException: "Request Error: There was an error making the request to the server.",
}

# HTTP status code error messages
HTTP_ERROR_MESSAGES: Dict[int, str] = {
    400: "Bad Request: The server could not understand the request.",
    401: "Unauthorized: Authentication is required to access this resource.",
    403: "Forbidden: You don't have permission to access this resource.",
    404: "Not Found: The requested endpoint was not found.",
    429: "Too Many Requests: You've sent too many requests. Please wait and try again later.",
    500: "Internal Server Error: The server encountered an unexpected condition.",
    502: "Bad Gateway: The server received an invalid response from an upstream server.",
    503: "Service Unavailable: The server is temporarily unable to handle the request.",
    504: "Gateway Timeout: The upstream server failed to send a response in time."
}

# User interface messages
UI_MESSAGES = {
    # Input validation
    "empty_input": "Please enter a question.",
    
    # Status messages
    "thinking": "Thinking...",
    
    # Feedback messages
    "feedback_prompt": "Was this response helpful?",
    "feedback_positive": "Thank you for your positive feedback!",
    "feedback_negative": "Thank you for your feedback! We'll work to improve.",
    
    # History management
    "history_cleared": "Chat cleared successfully!",
    "history_saved": "Chat history saved successfully!",
    "history_loaded": "Chat history loaded successfully!",
    "no_history_to_save": "No messages to save. Try asking a question first!",
    "no_history_found": "No saved history found. Start a new conversation!",
    
    # Theme messages
    "light_mode": "Light Mode",
    "dark_mode": "Dark Mode"
}

# Format functions for different message types
def format_error_message(error: Exception) -> str:
    """
    Format error messages in a user-friendly way.
    
    Args:
        error: The exception that occurred
        
    Returns:
        A user-friendly error message
    """
    # Check for specific exception types
    for error_type, message in ERROR_MESSAGES.items():
        if isinstance(error, error_type):
            return f"⚠️ {message}"
    
    # Check for HTTP errors
    if isinstance(error, requests.HTTPError) and error.response is not None:
        status_code = error.response.status_code
        if status_code in HTTP_ERROR_MESSAGES:
            return f"⚠️ Server Error: {HTTP_ERROR_MESSAGES[status_code]}"
        else:
            return f"⚠️ HTTP Error: The server returned status code {status_code}."
    
    # Check for JSON parsing errors
    if isinstance(error, ValueError) and "JSON" in str(error):
        return "⚠️ Response Error: The server response was not in the expected format."
    
    # Generic error message
    return f"⚠️ Error: {str(error)}"

def format_status_message(message_key: str, **kwargs: Any) -> str:
    """
    Format a status message with optional parameters.
    
    Args:
        message_key: The key of the message in UI_MESSAGES
        **kwargs: Optional parameters to format into the message
        
    Returns:
        A formatted status message
    """
    message = UI_MESSAGES.get(message_key, message_key)
    if kwargs:
        message = message.format(**kwargs)
    return message

def format_html_message(message_key: str, message_type: str = "info", **kwargs: Any) -> str:
    """
    Format a message as HTML with appropriate styling.
    
    Args:
        message_key: The key of the message in UI_MESSAGES
        message_type: The type of message (info, success, warning, error)
        **kwargs: Optional parameters to format into the message
        
    Returns:
        An HTML-formatted message
    """
    message = format_status_message(message_key, **kwargs)
    
    # Map message types to Font Awesome icons
    icons = {
        "info": "info-circle",
        "success": "check-circle",
        "warning": "exclamation-triangle",
        "error": "exclamation-circle"
    }
    
    icon = icons.get(message_type, "info-circle")
    
    return f'<div class="{message_type}-message"><i class="fas fa-{icon}"></i> {message}</div>'

def format_thinking_animation() -> str:
    """
    Generate HTML for the thinking animation.
    
    Returns:
        HTML string for the thinking animation
    """
    return """
    <div class='thinking-indicator'>
        <div class='thinking-dots'>
            <span></span>
            <span></span>
            <span></span>
        </div>
        <div class='thinking-text'>Thinking...</div>
    </div>
    """
