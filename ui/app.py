#!/usr/bin/env python3
"""
UI application entry point for Solar Sage.
"""
import gradio as gr
from ui.config import SERVER_NAME, SERVER_PORT
from ui.simple_ui import create_ui

def main():
    """Main entry point for the UI application."""
    # Create and launch the UI
    ui = create_ui()
    ui.launch(
        server_name=SERVER_NAME,
        server_port=SERVER_PORT,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()
