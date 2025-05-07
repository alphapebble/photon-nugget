"""
API communication functions for the UI application.
"""
from typing import List, Tuple

from api import get_model_response

def ask_model(user_message: str, history: List[Tuple[str, str]]) -> str:
    """
    Send a request to the backend API and get a response.

    Args:
        user_message: The user's input message
        history: Chat history

    Returns:
        The model's response or an error message
    """
    return get_model_response(user_message, history)
