"""
API client for the Solar Sage backend.
"""
import requests
import json
from typing import List, Tuple, Optional, Dict, Any
import logging

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

# Create logs directory if it doesn't exist
import os
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger(__name__)

# Default API endpoint
DEFAULT_API_URL = "http://localhost:8000"

def get_model_response(
    message: str,
    history: List[Tuple[str, str]],
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> str:
    """
    Get a response from the model via the API.

    Args:
        message: The user's message
        history: The conversation history
        lat: Optional latitude for weather data
        lon: Optional longitude for weather data

    Returns:
        The model's response as a string
    """
    try:
        # Prepare the request payload
        payload = {
            "query": message  # API expects 'query', not 'message'
        }

        # Add location data if provided
        if lat is not None and lon is not None:
            payload["lat"] = lat
            payload["lon"] = lon
            payload["include_weather"] = True
            logger.info(f"Including weather data for location: lat={lat}, lon={lon}")

        logger.info(f"Sending request to API: {payload}")

        # Make the API request
        api_url = f"{DEFAULT_API_URL}/chat"
        logger.info(f"Making API request to: {api_url}")

        response = requests.post(
            api_url,
            json=payload,
            timeout=60  # 60 second timeout
        )

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info("API request successful")
            return result.get("response", "No response received from API")
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            logger.error(f"Request payload was: {payload}")
            return f"Error: The API returned status code {response.status_code}. Please check if the API server is running."

    except requests.exceptions.ConnectionError:
        logger.error("Connection error when trying to reach the API")
        return "⚠️ I'm sorry, but I can't connect to the API server right now. Please make sure the API server is running by executing `./solar_sage.sh api start` in a separate terminal."

    except Exception as e:
        logger.error(f"Error in get_model_response: {str(e)}")
        return f"⚠️ I'm sorry, but an error occurred: {str(e)}"
