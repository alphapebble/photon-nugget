"""
Default configuration for Solar Sage.

This module defines default configuration values used across all environments.
"""

DEFAULT_CONFIG = {
    # Application settings
    "app_name": "Solar Sage",
    "debug": False,
    "log_level": "INFO",

    # Server settings
    "api_host": "0.0.0.0",
    "api_port": 8000,
    "ui_port": 8502,

    # Data settings
    "data_dir": "./data",
    "vector_db_path": "./data/lancedb",
    "vector_db_table": "solar_knowledge",

    # Model settings
    "embedding_model": "all-MiniLM-L6-v2",
    "llm_provider": "ollama",
    "llm_model": "mistral",

    # External API settings
    "openweather_api_key": "",

    # Agent settings
    "require_authorization": True,
    "max_history_items": 10,
    "use_dual_agent": True,
    "max_context_documents": 5,

    # Ingestion settings
    "default_chunk_strategy": "word_count_300_0",
}
