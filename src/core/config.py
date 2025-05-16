"""
Global configuration for Solar Sage.

This module provides access to configuration settings from various sources:
- Environment variables
- Configuration files
- Default values
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Default configuration
DEFAULT_CONFIG = {
    "app_name": "Solar Sage",
    "debug": False,
    "log_level": "INFO",
    "api_host": "0.0.0.0",
    "api_port": 8000,
    "ui_port": 8502,
    "data_dir": "./data",
    "vector_db_path": "./data/lancedb",
    "vector_db_table": "solar_knowledge",
    "embedding_model": "all-MiniLM-L6-v2",
    "llm_provider": "ollama",
    "llm_model": "mistral",
    "openweather_api_key": "",
}


def get_config(key: str, default: Any = None) -> Any:
    """
    Get a configuration value.
    
    Args:
        key: Configuration key
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    # Check environment variables first (convert to uppercase with prefix)
    env_key = f"SOLAR_SAGE_{key.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Check default config
    if key in DEFAULT_CONFIG:
        return DEFAULT_CONFIG[key]
    
    # Return provided default
    return default


def get_all_config() -> Dict[str, Any]:
    """
    Get all configuration values.
    
    Returns:
        Dictionary of all configuration values
    """
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables
    for key in config:
        env_key = f"SOLAR_SAGE_{key.upper()}"
        if env_key in os.environ:
            config[key] = os.environ[env_key]
    
    return config
