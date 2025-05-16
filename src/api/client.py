"""
API client for communicating with the backend server.
"""
import time
import requests
from typing import Dict, Any, Optional, List, Tuple

from core.config import get_config
from core.logging import get_logger
from core.exceptions import APIError

# Get logger
logger = get_logger(__name__)

# API configuration
BACKEND_URL = get_config("api_url", "http://localhost:8000")
BACKEND_CHAT_ENDPOINT = "/chat"
MAX_RETRIES = int(get_config("api_max_retries", "3"))
RETRY_DELAY = int(get_config("api_retry_delay", "1"))

# Error messages by exception type
ERROR_MESSAGES: Dict[type, str] = {
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


def format_api_error(error: Exception) -> str:
    """
    Format API error messages in a user-friendly way.

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
            APIError: If the request fails after all retries
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
                raise APIError(f"API request failed after {self.max_retries} retries: {str(e)}")
        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"HTTP error in API request: {str(e)}")
            raise APIError(f"HTTP error: {str(e)}", status_code=status_code)
        except Exception as e:
            logger.error(f"Error in API request: {str(e)}")
            raise APIError(f"API request failed: {str(e)}")

    def chat(self, message: str, lat: Optional[float] = None, lon: Optional[float] = None, include_weather: bool = False) -> Dict[str, Any]:
        """
        Send a chat message to the API.

        Args:
            message: User's message
            lat: Latitude (optional)
            lon: Longitude (optional)
            include_weather: Whether to include weather context

        Returns:
            API response as a dictionary
        """
        data = {
            "query": message
        }

        # Add weather parameters if provided
        if include_weather and lat is not None and lon is not None:
            data["lat"] = lat
            data["lon"] = lon
            data["include_weather"] = True

        return self._make_request("POST", BACKEND_CHAT_ENDPOINT, data)

def get_model_response(user_message: str, history: List[Tuple[str, str]],
                   lat: Optional[float] = None, lon: Optional[float] = None) -> str:
    """
    Get a response from the model via the API.

    Args:
        user_message: The user's input message
        history: Chat history
        lat: Latitude (optional)
        lon: Longitude (optional)

    Returns:
        The model's response or an error message
    """
    client = ApiClient()

    # Check if the query is weather-related
    weather_keywords = [
        "weather", "cloud", "rain", "sunny", "forecast",
        "today", "tomorrow", "week", "production", "output",
        "efficiency", "performance", "expect", "prediction",
        "humidity", "temperature", "hot", "cold", "wind"
    ]

    # Determine if we should include weather data
    include_weather = any(keyword in user_message.lower() for keyword in weather_keywords)

    try:
        response = client.chat(
            message=user_message,
            lat=lat,
            lon=lon,
            include_weather=include_weather
        )
        return response["response"]
    except Exception as e:
        return format_api_error(e)
