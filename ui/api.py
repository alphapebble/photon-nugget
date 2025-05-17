"""
API client for the Solar Sage backend.

This module provides a simplified interface to the API client
for use in the UI components.
"""
from typing import List, Tuple, Optional
import logging

# Import the API client
from ui.api_client import get_model_response as client_get_model_response

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
    logger.info(f"Getting model response for message: {message}")
    if lat is not None and lon is not None:
        logger.info(f"Including location data: lat={lat}, lon={lon}")

    # Use the client implementation
    return client_get_model_response(message, history, lat, lon)
