"""
API client for communicating with the backend server.
"""
import time
import requests
from typing import Dict, Any, Optional, List, Tuple

from api.config import (
    BACKEND_URL,
    BACKEND_CHAT_ENDPOINT,
    MAX_RETRIES,
    RETRY_DELAY,
    logger
)
from api.errors import format_api_error

class ApiClient:
    """
    Client for communicating with the backend API.
    """
    def __init__(
        self,
        base_url: str = BACKEND_URL,
        timeout: int = 30,
        max_retries: int = MAX_RETRIES,
        retry_delay: int = RETRY_DELAY
    ):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for transient errors
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make a request to the API with retry mechanism for transient errors.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            retry_count: Current retry attempt

        Returns:
            API response as a dictionary

        Raises:
            Exception: If the request fails after all retries
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.info(f"Making {method} request to {url}")

            if method.upper() == "GET":
                response = requests.get(url, params=data, timeout=self.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.json()
            logger.info(f"Received successful response from {url}")
            return result

        except (requests.ConnectionError, requests.Timeout) as e:
            # These are transient errors, so we can retry
            if retry_count < self.max_retries:
                logger.warning(f"Transient error occurred: {str(e)}. Retrying ({retry_count + 1}/{self.max_retries})...")
                time.sleep(self.retry_delay * (retry_count + 1))  # Exponential backoff
                return self._make_request(method, endpoint, data, retry_count + 1)
            else:
                logger.error(f"Max retries reached. Error: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error in API request: {str(e)}")
            raise

    def chat(self, message: str) -> Dict[str, Any]:
        """
        Send a chat message to the API.

        Args:
            message: User's message

        Returns:
            API response as a dictionary
        """
        return self._make_request("POST", BACKEND_CHAT_ENDPOINT, {"query": message})

def get_model_response(user_message: str, history: List[Tuple[str, str]]) -> str:
    """
    Get a response from the model via the API.

    Args:
        user_message: The user's input message
        history: Chat history

    Returns:
        The model's response or an error message
    """
    client = ApiClient()

    try:
        response = client.chat(user_message)
        return response["response"]
    except Exception as e:
        return format_api_error(e)
