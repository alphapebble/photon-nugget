#!/usr/bin/env python3
"""
UI application entry point for Solar Sage.
"""
import gradio as gr
from typing import Optional

from ui.simple_ui import create_ui
from core.config import get_config
from core.logging import get_logger, setup_logging

# Set up logging
setup_logging()
logger = get_logger(__name__)

def run_ui(port: Optional[int] = None, share: bool = False) -> None:
    """
    Run the UI application.

    Args:
        port: Port to run the UI on
        share: Whether to create a public link for sharing
    """
    # Get configuration
    server_name = get_config("ui_host", "0.0.0.0")
    server_port = port or int(get_config("ui_port", "8502"))

    logger.info(f"Starting UI on {server_name}:{server_port}")

    # Create and launch the UI
    ui = create_ui()
    ui.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        show_error=True
    )

if __name__ == "__main__":
    run_ui()
