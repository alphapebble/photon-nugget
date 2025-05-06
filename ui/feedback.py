"""
Feedback handling functions for the UI application.
"""
from typing import List, Tuple
from ui.config import logger

def record_feedback(feedback_type: str, message_idx: int, history: List[Tuple[str, str]]) -> None:
    """
    Record user feedback for a specific response.

    Args:
        feedback_type: Either 'positive' or 'negative'
        message_idx: Index of the message in history
        history: Current chat history
    """
    if message_idx < 0 or message_idx >= len(history):
        logger.error(f"Invalid message index for feedback: {message_idx}")
        return

    try:
        user_message, bot_response = history[message_idx]

        # In a real application, you would send this to a database or analytics service
        logger.info(f"Feedback recorded: {feedback_type} for message {message_idx}")
        logger.info(f"User message: {user_message}")
        logger.info(f"Bot response: {bot_response}")

        # You could also send this to your backend for storage
        # requests.post(f"{BACKEND_URL}/feedback", json={
        #     "feedback_type": feedback_type,
        #     "user_message": user_message,
        #     "bot_response": bot_response
        # })

    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")


def handle_feedback(feedback_type: str, msg_idx: int, history: List[Tuple[str, str]]) -> Tuple[str, bool]:
    """
    Record feedback and return confirmation message.

    Args:
        feedback_type: Either 'positive' or 'negative'
        msg_idx: Index of the message in history
        history: Current chat history

    Returns:
        Tuple containing confirmation message and visibility flag for feedback row
    """
    # Convert string to int if needed (for Gradio compatibility)
    if isinstance(msg_idx, str) and msg_idx.isdigit():
        msg_idx = int(msg_idx)

    if msg_idx < 0:
        return "No message selected for feedback.", False

    record_feedback(feedback_type, msg_idx, history)
    return f"Thank you for your {feedback_type} feedback!", False
