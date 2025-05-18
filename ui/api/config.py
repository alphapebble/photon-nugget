"""
Configuration for the API client.

This module provides configuration settings for the API client.
"""
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("api_client")

# API configuration
DEFAULT_API_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
CHAT_ENDPOINT = "/sage"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
