# Solar Sage Refactoring Guide

This document provides an overview of the refactored Solar Sage codebase structure and guidelines for working with the new organization.

## Directory Structure

The codebase has been refactored to follow a more modular and maintainable structure:

```
solar-sage/
├── agents/            # Agent components
├── api/               # API client and routes
├── app/               # Application server
├── cli/               # Command-line interface
├── config/            # Configuration
├── core/              # Core functionality
├── data/              # Knowledge database
├── deployment/        # Deployment configuration
├── docs/              # Documentation
├── ingestion/         # Document ingestion
├── llm/               # LLM integration
├── models/            # AI models
├── rag/               # Retrieval system
├── retriever/         # Document retrieval
├── scripts/           # Utility scripts
├── tests/             # Test suite
├── tools/             # Agent tools
├── ui/                # Frontend interface
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore file
├── main.py            # Main entry point
├── pyproject.toml     # Python project configuration
├── README.md          # Project README
└── requirements.txt   # Dependencies
```

## Key Changes

1. **Standardized Module Organization**: Each module follows a consistent internal structure with clear separation of concerns.

2. **Core Package**: Added a `core/` directory for shared functionality like configuration, logging, and utilities.

3. **Configuration System**: Moved configuration to a dedicated module with environment-specific settings.

4. **CLI Interface**: Added a command-line interface for running the server, UI, and other commands.

5. **Deployment Configuration**: Added Docker and deployment configuration for easier deployment.

6. **Improved Test Organization**: Restructured tests to mirror the main package structure.

7. **Type Hints and Documentation**: Added type hints and improved documentation throughout the codebase.

## Working with the New Structure

### Running the Application

You can now run the application using the CLI:

```bash
# Run the API server
python -m cli.main server

# Run the UI
python -m cli.main ui

# Ingest a document
python -m cli.main ingest path/to/document.pdf

# List ingested documents
python -m cli.main list
```

### Configuration

Configuration is now managed through environment variables and the `config/` module:

1. Copy `.env.example` to `.env` and customize settings
2. Use `from core.config import get_config` to access configuration values
3. Environment-specific settings are in `config/environments/`

### Development Guidelines

1. **Module Organization**: Keep related functionality together in modules
2. **Type Hints**: Use type hints for all function parameters and return values
3. **Documentation**: Add docstrings to all modules, classes, and functions
4. **Testing**: Write tests for all new functionality
5. **Configuration**: Use the configuration system instead of hardcoded values

### Deployment

The application can be deployed using Docker:

```bash
# Build and run with Docker Compose
docker-compose -f deployment/docker/docker-compose.yml up -d

# Or use the deployment script
bash deployment/scripts/deploy.sh
```

## Migration Guide

If you're working with existing code, follow these steps to migrate to the new structure:

1. Identify the module where your code belongs
2. Move the code to the appropriate module
3. Update imports to use the new module paths
4. Add type hints and improve documentation
5. Update any hardcoded configuration to use the configuration system
6. Write tests for your code

## Migrated Modules

The following modules have been migrated to the new structure:

1. **API Module**: Updated to use the new configuration and logging systems
   - Replaced hardcoded configuration with `core.config`
   - Added proper type hints and improved error handling
   - Integrated with the core logging system

2. **App Module**: Updated to use the new configuration and logging systems
   - Added a `run_server` function for CLI integration
   - Improved error handling and logging
   - Added configuration for host, port, and debug mode

3. **Ingestion Module**: Updated to use the new configuration and logging systems
   - Replaced print statements with proper logging
   - Added configuration for default chunking strategies
   - Improved error handling and type hints

4. **UI Module**: Updated to use the new configuration and logging systems
   - Added a `run_ui` function for CLI integration
   - Improved configuration for host, port, and sharing options
   - Added proper logging

## Conclusion

This refactoring improves the maintainability, testability, and organization of the Solar Sage codebase. By following the guidelines in this document, you can help maintain a clean and consistent codebase.
