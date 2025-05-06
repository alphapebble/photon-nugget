"""
API communication functions for the UI application.
"""
import time
import requests
from typing import List, Tuple

from ui.config import (
    BACKEND_URL, 
    BACKEND_CHAT_ENDPOINT, 
    MAX_RETRIES, 
    RETRY_DELAY,
    logger
)

def format_error_message(error: Exception) -> str:
    """
    Format error messages in a user-friendly way.
    
    Args:
        error: The exception that occurred
        
    Returns:
        A user-friendly error message
    """
    if isinstance(error, requests.ConnectionError):
        return "⚠️ Connection Error: Could not connect to the server. Please check if the server is running."
    elif isinstance(error, requests.Timeout):
        return "⚠️ Timeout Error: The server took too long to respond. Please try again later."
    elif isinstance(error, requests.HTTPError):
        if error.response.status_code == 404:
            return "⚠️ Server Error: The requested endpoint was not found."
        elif error.response.status_code == 500:
            return "⚠️ Server Error: The server encountered an internal error. Please try again later."
        else:
            return f"⚠️ HTTP Error: The server returned status code {error.response.status_code}."
    elif isinstance(error, requests.RequestException):
        return "⚠️ Request Error: There was an error making the request to the server."
    elif isinstance(error, ValueError) and "JSON" in str(error):
        return "⚠️ Response Error: The server response was not in the expected format."
    else:
        return f"⚠️ Error: {str(error)}"


def ask_model(user_message: str, history: List[Tuple[str, str]], retry_count: int = 0) -> str:
    """
    Send a request to the backend API with retry mechanism for transient errors.
    
    Args:
        user_message: The user's input message
        history: Chat history
        retry_count: Current retry attempt
        
    Returns:
        The model's response or an error message
    """
    try:
        logger.info(f"Sending request to backend: {user_message}")
        response = requests.post(
            f"{BACKEND_URL}{BACKEND_CHAT_ENDPOINT}",
            json={"query": user_message},
            timeout=30  # Add timeout to prevent hanging
        )
        response.raise_for_status()
        result = response.json()
        logger.info("Received successful response from backend")
        return result["response"]
    except (requests.ConnectionError, requests.Timeout) as e:
        # These are transient errors, so we can retry
        if retry_count < MAX_RETRIES:
            logger.warning(f"Transient error occurred: {str(e)}. Retrying ({retry_count + 1}/{MAX_RETRIES})...")
            time.sleep(RETRY_DELAY * (retry_count + 1))  # Exponential backoff
            return ask_model(user_message, history, retry_count + 1)
        else:
            logger.error(f"Max retries reached. Error: {str(e)}")
            return format_error_message(e)
    except Exception as e:
        logger.error(f"Error in ask_model: {str(e)}")
        return format_error_message(e)
