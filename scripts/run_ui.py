#!/usr/bin/env python
"""
Run the Solar Sage UI.

This script starts the Solar Sage UI server.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.append(str(src_dir))

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.config import get_config
from core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

def main():
    """Run the Solar Sage UI."""
    port = int(get_config("ui_port", 7860))

    logger.info(f"Starting Solar Sage Conversational UI on port {port}")

    # Run the Gradio UI
    ui_app_path = Path(__file__).parent.parent / "ui_app.py"

    # Check if the UI app exists
    if not ui_app_path.exists():
        logger.error(f"UI app not found at {ui_app_path}")
        sys.exit(1)

    # Run the UI app
    subprocess.run([
        sys.executable, str(ui_app_path),
        "--port", str(port)
    ])

if __name__ == "__main__":
    main()
