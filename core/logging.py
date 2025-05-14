"""
Logging configuration for Solar Sage.

This module sets up logging for the application.
"""
import logging
import sys
from typing import Optional
import os

from core.config import get_config


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Set up logging for the application.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    """
    # Get log level from config if not provided
    if log_level is None:
        log_level = get_config("log_level", "INFO")
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Configure logging
    logging_config = {
        "level": numeric_level,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
    
    # Add file handler if log file is specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logging_config["filename"] = log_file
    
    # Apply configuration
    logging.basicConfig(**logging_config)
    
    # Add stream handler if logging to file
    if log_file:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(numeric_level)
        formatter = logging.Formatter(logging_config["format"])
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module.
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
