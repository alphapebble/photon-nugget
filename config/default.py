"""
Default configuration for Solar Sage.

This module defines default configuration values used across all environments.
"""

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
    "require_authorization": True,
    "max_history_items": 10,
    "default_chunk_strategy": "word_count_300_0",
}
