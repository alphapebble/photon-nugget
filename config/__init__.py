"""
Configuration module for Solar Sage.

This module provides access to configuration settings for different environments.
"""
import os
from typing import Dict, Any

# Import environment-specific configurations
from config.default import DEFAULT_CONFIG

# Determine environment
ENV = os.environ.get("SOLAR_SAGE_ENV", "development")

# Import environment-specific config
if ENV == "production":
    from config.environments.production import PRODUCTION_CONFIG as ENV_CONFIG
elif ENV == "development":
    from config.environments.development import DEVELOPMENT_CONFIG as ENV_CONFIG
else:
    ENV_CONFIG = {}

# Combine configurations
CONFIG = {**DEFAULT_CONFIG, **ENV_CONFIG}

# Override with environment variables
for key in CONFIG:
    env_key = f"SOLAR_SAGE_{key.upper()}"
    if env_key in os.environ:
        CONFIG[key] = os.environ[env_key]


def get_config(key: str, default: Any = None) -> Any:
    """
    Get a configuration value.
    
    Args:
        key: Configuration key
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    return CONFIG.get(key, default)


def get_all_config() -> Dict[str, Any]:
    """
    Get all configuration values.
    
    Returns:
        Dictionary of all configuration values
    """
    return CONFIG.copy()
