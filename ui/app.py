#!/usr/bin/env python3
"""
UI application entry point for Solar Sage.
"""
import gradio as gr
from gradio.routes import Request as GradioRequest
import argparse
from typing import Optional

from ui.components.simple_ui import create_ui
from ui.components.evaluation_dashboard import create_evaluation_dashboard
from core.config import get_config
from core.logging import get_logger, setup_logging

# Set up logging
setup_logging(log_file="./logs/ui_server.log")
logger = get_logger(__name__)

def run_ui(port: Optional[int] = None, share: bool = False, mode: str = "main") -> None:
    """
    Run the UI application.

    Args:
        port: Port to run the UI on
        share: Whether to create a public link for sharing
        mode: UI mode to run ("main" or "evaluation")
    """
    # Get configuration
    server_name = get_config("ui_host", "0.0.0.0")
    server_port = port or int(get_config("ui_port", "8502"))

    logger.info(f"Starting UI server on {server_name}:{server_port}")

    # Get CSS from both UIs
    from ui.utils.template_loader import load_template

    # Load CSS from files
    main_css = load_template("css/simple.css")
    eval_css = load_template("css/evaluation.css")

    # Combine CSS
    combined_css = main_css + eval_css

    # Launch the appropriate UI based on mode
    if mode == "evaluation":
        # Launch evaluation dashboard
        dashboard = create_evaluation_dashboard()
        dashboard.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            show_error=True
        )
    else:
        # Launch main UI
        app = create_ui()
        app.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            show_error=True
        )

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Solar Sage UI")
    parser.add_argument("--port", type=int, help="Port to run the UI on")
    parser.add_argument("--share", action="store_true", help="Create a public link for sharing")
    parser.add_argument("--mode", choices=["main", "evaluation"], default="main",
                      help="UI mode to run (main or evaluation)")
    parser.add_argument("--view", help="View parameter from URL (for internal use)")

    args = parser.parse_args()

    # Run the UI with the specified options
    run_ui(port=args.port, share=args.share, mode=args.mode)
