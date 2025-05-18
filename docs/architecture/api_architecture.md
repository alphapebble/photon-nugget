# Solar Sage API Architecture

This document provides an overview of the Solar Sage API architecture, explaining the different components and how they interact.

## Overview

Solar Sage has a dual API architecture:

1. **Traditional REST API** (`src/api/`): Provides direct access to data and services
2. **Conversational API** (`src/app/`): Provides a chat interface with RAG capabilities

This architecture allows for both direct data access and natural language interactions with the system.

## API Components

### 1. Traditional REST API (`src/api/`)

The traditional REST API provides direct access to solar forecasting and other services. It's structured around resource-based routes.

#### Key Components:

- **Main Application** (`src/api/main.py`): The FastAPI application that includes all routes
- **Routes** (`src/api/routes/`): Resource-based endpoints for different services
  - `solar_forecasting.py`: Endpoints for solar energy forecasting

#### Endpoints:

- `GET /`: Root endpoint that returns basic API information
- `GET /health`: Health check endpoint
- `POST /solar/forecast`: Generate a solar energy forecast for a location

### 2. Conversational API (`src/app/`)

The conversational API provides a chat interface with RAG (Retrieval-Augmented Generation) capabilities. It's designed to handle natural language queries and provide contextually relevant responses.

#### Key Components:

- **Main Application** (`src/app/server.py`): The FastAPI application for the conversational API
- **Endpoints** (`src/app/endpoints/`): Chat and agent endpoints
  - `chat_endpoints.py`: Chat interface with RAG capabilities
- **Models** (`src/app/models/`): Pydantic models for request/response validation
  - `prompt.py`: Models for chat requests and responses

#### Endpoints:

- `GET /`: Root endpoint that confirms the API is running
- `POST /sage`: Main endpoint that processes natural language queries
- `POST /chat`: Legacy endpoint that redirects to /sage (for backward compatibility)

## RAG Engines

The RAG (Retrieval-Augmented Generation) engines are responsible for retrieving relevant information and generating responses to user queries.

### Base RAG Engine

The base RAG engine (`src/rag/engines/base.py`) provides the core functionality for retrieving information and generating responses.

### Weather-Enhanced RAG Engine

The weather-enhanced RAG engine (`src/rag/engines/weather_enhanced.py`) extends the base RAG engine with weather context to provide more relevant responses to weather-related queries.

### Solar-Enhanced RAG Engine

The solar-enhanced RAG engine (`src/rag/engines/solar_enhanced.py`) extends the base RAG engine with solar forecasting context to provide more relevant responses to solar forecasting-related queries.

## Agent Orchestrator

The agent orchestrator (`src/agents/orchestrator.py`) coordinates the dual-agent workflow:

1. **Retriever Agent**: Retrieves relevant information from the knowledge base
2. **Response Generator Agent**: Generates a response based on the retrieved information

## Semantic Metric Layer

The semantic metric layer (`src/core/semantic_metric_layer.py`) provides a centralized repository for all metrics, formulas, and constants used throughout the system. It uses numexpr for efficient and safe formula evaluation.

## UI Integration

The API is integrated with two different user interfaces:

1. **Next.js Frontend**: Communicates with the API through an Axios-based client
2. **Gradio UI**: Communicates with the API through a Python-based client

For detailed information about the UI architecture, see the [UI Architecture](ui_architecture.md) documentation.

## API Documentation

The API is documented using FastAPI's built-in Swagger documentation. The Swagger UI is available at:

```
http://localhost:8000/docs
```

The ReDoc alternative is available at:

```
http://localhost:8000/redoc
```

## Usage Examples

For detailed examples of how to use the API, see the [Shell Commands Reference](../reference/shell_commands.md#api-testing-commands).

## Running the API

For detailed information about how to run the API, see the [Shell Commands Reference](../reference/shell_commands.md#api-server-commands).

## Future Improvements

1. **API Consolidation**: Consider consolidating the two API modules into a single, unified API
2. **Swagger Documentation**: Improve the Swagger documentation for all endpoints
3. **Authentication**: Add authentication for secure access to the API
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Caching**: Add caching for frequently accessed data
6. **WebSocket Support**: Add WebSocket support for real-time updates
7. **GraphQL**: Consider adding a GraphQL API for more flexible queries

## Conclusion

The dual API architecture of Solar Sage provides flexibility in how users interact with the system. The traditional REST API provides direct access to data and services, while the conversational API provides a natural language interface with RAG capabilities. Both APIs are integrated with the dual UI architecture, providing a consistent experience regardless of which UI is used.
