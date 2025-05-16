#!/usr/bin/env python3
"""
Main application entry point for Photon-Nugget.
"""
import argparse
import gradio as gr

from ui.config import SERVER_NAME, SERVER_PORT
from ui.simple_ui import create_ui

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Photon-Nugget Solar AI Assistant")
    parser.add_argument(
        "--port",
        type=int,
        default=SERVER_PORT,
        help=f"Port to run the server on (default: {SERVER_PORT})"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=SERVER_NAME,
        help=f"Host to run the server on (default: {SERVER_NAME})"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public link for sharing"
    )
    parser.add_argument(
        "--ui",
        type=str,
        choices=["simple", "modern"],
        default="simple",
        help="UI version to use (default: simple)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Create and launch the UI
    ui = create_ui()
    ui.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True
    )
