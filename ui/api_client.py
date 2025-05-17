"""
API client for communicating with the Solar Sage backend server.

This module provides a client for interacting with the Solar Sage API,
handling requests, retries, and error formatting.
"""
import time
import requests
import os
import logging
from typing import Dict, Any, Optional, List, Tuple

from ui.api_config import DEFAULT_API_URL, CHAT_ENDPOINT, MAX_RETRIES, RETRY_DELAY
from ui.api_errors import format_api_error

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/api_client.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ApiClient:
    """
    Client for communicating with the backend API.
    """
    def __init__(
        self,
        base_url: str = DEFAULT_API_URL,
        timeout: int = 60,
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
            logger.info(f"Request data: {data}")

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
                raise Exception(f"API request failed after {self.max_retries} retries: {str(e)}")
        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"HTTP error in API request: {str(e)}")
            raise Exception(f"HTTP error: {str(e)}", status_code)
        except Exception as e:
            logger.error(f"Error in API request: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")

    def chat(
        self,
        message: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        include_weather: bool = False
    ) -> Dict[str, Any]:
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

        return self._make_request("POST", CHAT_ENDPOINT, data)


def get_model_response(
    user_message: str,
    history: List[Tuple[str, str]],
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> str:
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

    # Always include weather data if location is provided
    if lat is not None and lon is not None:
        include_weather = True

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
