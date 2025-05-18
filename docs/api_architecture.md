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

## Usage Examples

### Using the Sage Endpoint

The sage endpoint is the primary way to interact with the Solar Sage system. It accepts natural language queries and returns contextually relevant responses.

#### Basic Query

```bash
curl -X POST "http://localhost:8000/sage" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What factors affect solar panel efficiency?"
  }'
```

#### Weather-Enhanced Query

```bash
curl -X POST "http://localhost:8000/sage" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How will the weather affect my solar production today?",
    "lat": 37.7749,
    "lon": -122.4194,
    "include_weather": true
  }'
```

#### Solar Forecast Query

```bash
curl -X POST "http://localhost:8000/sage" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How much solar energy can I expect to produce tomorrow?",
    "lat": 37.7749,
    "lon": -122.4194,
    "include_weather": true,
    "location_id": "home",
    "system_capacity_kw": 5.0,
    "electricity_rate": 0.25,
    "include_solar_forecast": true
  }'
```

> Note: The legacy `/chat` endpoint is still available for backward compatibility and redirects to the `/sage` endpoint.

### Using the Solar Forecast Endpoint

The solar forecast endpoint provides direct access to solar energy forecasting without the natural language interface.

```bash
curl -X POST "http://localhost:8000/solar/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.7749,
    "longitude": -122.4194,
    "location_id": "home",
    "system_capacity_kw": 5.0
  }'
```

## Running the API

### Starting the API Server

The API server can be started using the provided script:

```bash
# Start the API server
./scripts/api_server.sh start

# Stop the API server
./scripts/api_server.sh stop 8000
```

Alternatively, you can run the API server directly:

```bash
# Run with Python path set correctly
PYTHONPATH=$PYTHONPATH:$(pwd)/src python scripts/run_api.py
```

### Testing the API

The API can be tested using the provided test script:

```bash
# Test the health endpoint
./scripts/test_api.sh health

# Test the basic chat endpoint
./scripts/test_api.sh chat

# Test the weather-enhanced chat endpoint
./scripts/test_api.sh weather-chat

# Test the solar-enhanced chat endpoint
./scripts/test_api.sh solar-chat

# Test the solar forecast endpoint
./scripts/test_api.sh solar-forecast

# Run all tests
./scripts/test_api.sh all
```

The test script supports various options to customize the test parameters:

```bash
# Test with custom location
./scripts/test_api.sh --lat 40.7128 --lon -74.0060 solar-chat

# Test with custom system capacity
./scripts/test_api.sh --capacity 10.0 solar-forecast

# Test with custom electricity rate
./scripts/test_api.sh --rate 0.30 --feed-in 0.15 solar-chat
```

For a full list of options, run:

```bash
./scripts/test_api.sh --help
```

## Future Improvements

1. **API Consolidation**: Consider consolidating the two API modules into a single, unified API
2. **Swagger Documentation**: Improve the Swagger documentation for all endpoints
3. **Authentication**: Add authentication for secure access to the API
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Caching**: Add caching for frequently accessed data

## Conclusion

The dual API architecture of Solar Sage provides flexibility in how users interact with the system. The traditional REST API provides direct access to data and services, while the conversational API provides a natural language interface with RAG capabilities.
