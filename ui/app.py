#!/usr/bin/env python3
"""
UI application entry point for Solar Sage.
"""
import gradio as gr
import argparse
from typing import Optional

from ui.simple_ui import create_ui
from ui.evaluation_dashboard import create_evaluation_dashboard
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
    from ui.template_loader import load_template

    # Load CSS from files
    main_css = load_template("css/simple.css")
    eval_css = load_template("css/evaluation.css")

    # Combine CSS
    combined_css = main_css + eval_css

    # Create a unified interface that can switch between modes
    with gr.Blocks(title="Solar Sage", css=combined_css) as app:
        # Create state for the current mode
        current_mode = gr.State(value=mode)

        # Create the main UI
        main_ui = create_ui()

        # Create the evaluation dashboard
        eval_ui = create_evaluation_dashboard()

        # Add query parameter handling
        @app.load(inputs=current_mode, outputs=None)
        def router(default_mode):
            # Check for mode parameter in URL
            ctx = gr.Context.get()
            requested_mode = None

            # Extract mode from query parameters if available
            if hasattr(ctx, 'request') and ctx.request:
                query_params = getattr(ctx.request, 'query_params', None)
                if query_params and 'mode' in query_params:
                    requested_mode = query_params['mode']
                    logger.info(f"Mode requested via URL: {requested_mode}")

            # Use requested mode or default
            mode_to_use = requested_mode if requested_mode in ["main", "evaluation"] else default_mode
            logger.info(f"Using mode: {mode_to_use}")

            # Update visibility based on mode
            if mode_to_use == "evaluation":
                logger.info("Showing evaluation dashboard")
                return {main_ui: gr.update(visible=False), eval_ui: gr.update(visible=True)}
            else:
                logger.info("Showing main UI")
                return {main_ui: gr.update(visible=True), eval_ui: gr.update(visible=False)}

    # Launch the combined app
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
