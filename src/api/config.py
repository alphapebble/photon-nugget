"""
Configuration for the API client.
"""
import logging
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api_client")

# API configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
BACKEND_CHAT_ENDPOINT = "/chat"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
