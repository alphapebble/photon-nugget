#!/usr/bin/env python3
"""
Main application entry point for Solar Sage Conversational UI.
"""
import argparse
import gradio as gr
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from ui.app import run_ui

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Solar Sage Conversational UI")
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to run the server on (default: 7860)"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public link for sharing"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Run the UI
    run_ui(port=args.port, share=args.share)
