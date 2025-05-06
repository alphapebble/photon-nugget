"""
Configuration settings for the UI application.
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load .env settings
load_dotenv()

# API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_CHAT_ENDPOINT = os.getenv("BACKEND_CHAT_ENDPOINT", "/chat")

# Server Configuration
SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", 8502))

# Retry Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))  # seconds

# UI Configuration
CHATBOT_HEIGHT = 450
APP_TITLE = "Photon-Nugget"
APP_DESCRIPTION = "Private Solar AI Assistant"
MODEL_INFO = "Mistral via Ollama"
KNOWLEDGE_INFO = "Custom Ingested Solar Docs"
GITHUB_LINK = "https://github.com/balijepalli/photon-nugget"
