"""
Tests for the core.config module.
"""
import os
import pytest
from typing import Dict, Any

from core.config import get_config, get_all_config


def test_get_config() -> None:
    """Test get_config function."""
    # Test with default value
    assert get_config("non_existent_key", "default") == "default"
    
    # Test with existing key
    assert get_config("app_name") == "Solar Sage"


def test_get_all_config() -> None:
    """Test get_all_config function."""
    config = get_all_config()
    
    # Check that config is a dictionary
    assert isinstance(config, dict)
    
    # Check that it contains expected keys
    assert "app_name" in config
    assert "debug" in config
    assert "log_level" in config


def test_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test environment variable override."""
    # Set environment variable
    monkeypatch.setenv("SOLAR_SAGE_APP_NAME", "Test App")
    
    # Check that it overrides the config
    assert get_config("app_name") == "Test App"
    
    # Check that it's included in all config
    assert get_all_config()["app_name"] == "Test App"
