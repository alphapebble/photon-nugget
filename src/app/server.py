"""
Main FastAPI server for Solar Sage.

This module sets up the FastAPI application and includes all routes.
"""
from fastapi import FastAPI
import uvicorn
from typing import Optional

from app.endpoints.chat_endpoints import router as chat_router
from core.config import get_config
from core.logging import get_logger, setup_logging

# Set up logging
setup_logging(log_file="./logs/api_server.log")
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Solar Sage API",
    description="API for Solar Sage, an intelligent solar energy assistant",
    version="1.0.0"
)

# Include routers
app.include_router(chat_router)


def run_server(host: Optional[str] = None, port: Optional[int] = None) -> None:
    """
    Run the API server.

    Args:
        host: Host to run the server on
        port: Port to run the server on
    """
    # Get configuration
    server_host = host or get_config("api_host", "0.0.0.0")
    server_port = port or int(get_config("api_port", "8000"))

    logger.info(f"Starting API server on {server_host}:{server_port}")

    # Run the server
    try:
        # Try to determine the correct module path
        import inspect
        import sys

        # Get the current module's file path
        current_file = inspect.getfile(inspect.currentframe())

        # Always use app.server:app since we're setting PYTHONPATH correctly
        module_path = "app.server:app"

        logger.info(f"Using module path: {module_path}")

        # Import uvicorn again to avoid shadowing
        import uvicorn as uvicorn_run

        uvicorn_run.run(
            module_path,
            host=server_host,
            port=server_port,
            reload=str(get_config("debug", "False")).lower() == "true"
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        # Fallback to running the app directly
        import uvicorn.config
        config = uvicorn.config.Config(app=app, host=server_host, port=server_port)
        server = uvicorn.Server(config)
        server.run()
