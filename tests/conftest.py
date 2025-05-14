"""
Pytest configuration for Solar Sage.

This module provides fixtures and configuration for tests.
"""
import os
import tempfile
import pytest
from typing import Dict, Any, Generator

# Set test environment
os.environ["SOLAR_SAGE_ENV"] = "test"


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """
    Create a temporary directory for tests.
    
    Yields:
        Temporary directory path
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """
    Get test configuration.
    
    Returns:
        Test configuration
    """
    return {
        "app_name": "Solar Sage Test",
        "debug": True,
        "log_level": "DEBUG",
        "api_host": "localhost",
        "api_port": 8001,
        "ui_port": 8503,
        "data_dir": "./test_data",
        "vector_db_path": "./test_data/lancedb",
        "vector_db_table": "test_knowledge",
        "embedding_model": "all-MiniLM-L6-v2",
        "llm_provider": "mock",
        "llm_model": "mock",
        "openweather_api_key": "test_key",
        "require_authorization": False,
        "max_history_items": 5,
        "default_chunk_strategy": "word_count_300_0",
    }
