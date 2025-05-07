"""
User-facing messages for the UI application.
"""
from typing import Any, Dict

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
