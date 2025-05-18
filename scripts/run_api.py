#!/usr/bin/env python
"""
Run the Solar Sage API.

This script starts the Solar Sage API server.
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.append(str(src_dir))

from core.config import get_config
from core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

def main():
    """Run the Solar Sage API."""
    host = get_config("api_host", "0.0.0.0")
    port = int(get_config("api_port", 8000))

    logger.info(f"Starting Solar Sage API on {host}:{port}")

    # Try to run the app.server module first
    try:
        logger.info("Trying to run app.server module")
        uvicorn.run("app.server:app", host=host, port=port, reload=True)
    except Exception as e:
        logger.error(f"Error running app.server module: {e}")
        logger.info("Falling back to api.main module")
        uvicorn.run("api.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
