"""
Chat history management functions for the UI application.
"""
import json
import os
import tempfile
from typing import List, Tuple

# Use a temporary file to store chat history
HISTORY_FILE = os.path.join(tempfile.gettempdir(), "photon_nugget_history.json")

def load_chat_history() -> List[Tuple[str, str]]:
    """
    Load chat history from server.

    Returns:
        List of message tuples (user, bot)
    """
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading chat history: {e}")
    return []


def clear_chat() -> Tuple[List[Tuple[str, str]], str, int, bool]:
    """
    Clear the chat history and reset state.

    Returns:
        Tuple containing empty history, empty status message, reset response index, and hidden feedback flag
    """
    # Remove the history file if it exists
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
    except Exception as e:
        print(f"Error clearing chat history: {e}")

    # Clear the UI state
    return [], "", -1, False


def save_chat_history(history: List[Tuple[str, str]]) -> str:
    """
    Save chat history to local storage.

    Args:
        history: The chat history to save

    Returns:
        Confirmation message
    """
    if not history:
        return "No chat history to save."

    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
        return "Chat history saved successfully!"
    except Exception as e:
        print(f"Error saving chat history: {e}")
        return f"Error saving chat history: {str(e)}"


def load_chat_history_from_storage() -> Tuple[List[Tuple[str, str]], str]:
    """
    Load chat history from local storage.

    Returns:
        Tuple containing chat history and confirmation message
    """
    history = load_chat_history()
    if history:
        return history, "Chat history loaded successfully!"
    return [], "No saved history found."
