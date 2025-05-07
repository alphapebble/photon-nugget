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

# Server Configuration
SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", 8504))

# UI Configuration
CHATBOT_HEIGHT = 450
APP_TITLE = "SolarSage"
APP_DESCRIPTION = "Intelligent Solar Energy Assistant"
MODEL_INFO = "Mistral via Ollama"
KNOWLEDGE_INFO = "Custom Ingested Solar Docs"
GITHUB_LINK = "https://github.com/balijepalli/photon-nugget"
