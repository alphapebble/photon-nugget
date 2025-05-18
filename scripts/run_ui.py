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

from core.config import get_config
from core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

def main():
    """Run the Solar Sage UI."""
    port = int(get_config("ui_port", 8502))
    
    logger.info(f"Starting Solar Sage UI on port {port}")
    
    # Run Streamlit
    ui_path = Path(__file__).parent.parent / "src" / "ui" / "main.py"
    subprocess.run([
        "streamlit", "run", str(ui_path),
        "--server.port", str(port),
        "--browser.serverAddress", "localhost",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main()
