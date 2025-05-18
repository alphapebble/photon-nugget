# Solar Sage Agent Implementation Reference

This document serves as a reference for the Solar Sage Agentic RAG Chatbot implementation. It provides an overview of the key components and their interactions.

## Component Overview

The Solar Sage Agentic RAG Chatbot consists of the following key components:

### Core Agent Components

1. **Tool Registry** (`agents/tool_registry.py`)

   - Manages registration and execution of tools
   - Provides tool validation and authorization checks
   - Maintains a registry of available tools

2. **Memory System** (`agents/memory_system.py`)

   - Stores conversation history
   - Manages user preferences
   - Provides context for agent decisions

3. **Agent Engine** (`agents/agent_engine.py`)

   - Processes user queries
   - Decides when to use tools vs. RAG
   - Coordinates tool execution and response generation

4. **Agent Initialization** (`agents/initialize.py`)
   - Sets up the agent with tools and configuration
   - Provides a unified initialization interface

### Tool Implementations

1. **Weather Tools** (`agents/tools/weather_tools.py`)

   - Provides weather data and forecasts
   - Estimates solar production based on weather
   - Generates maintenance recommendations

2. **System Tools** (Planned)

   - Will provide system configuration tools
   - Will include panel tilt optimization
   - Will include shading analysis

3. **Performance Tools** (Planned)

   - Will analyze SCADA data
   - Will estimate degradation
   - Will compare performance to expectations

4. **Notification Tools** (Planned)

   - Will schedule alerts
   - Will send reminders
   - Will manage notification preferences

5. **Integration Tools** (Planned)
   - Will integrate with smart home systems
   - Will connect to inverter monitoring APIs
   - Will provide data export functionality

### RAG Components

1. **Base RAG Engine** (`rag/engines/base.py`)

   - Provides core RAG functionality
   - Combines retrieval and generation

2. **Weather-Enhanced RAG** (`rag/engines/weather_enhanced.py`)

   - Augments RAG with weather data
   - Provides weather-specific insights

3. **Agent-Enhanced RAG** (`rag/engines/agent_enhanced.py`)
   - Integrates agent capabilities with RAG
   - Enables tool usage within RAG context

## Component Interactions

The components interact in the following way:

```
User Query
    │
    ▼
┌───────────────┐
│  Agent Engine │
└───────┬───────┘
        │
        ├─────────────────┬─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Tool Registry │ │ Memory System │ │   RAG Engine  │
└───────┬───────┘ └───────────────┘ └───────────────┘
        │
        ├─────────────┬─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│  Weather  │ │  System   │ │Performance│ │Notification│
│   Tools   │ │   Tools   │ │   Tools   │ │   Tools   │
└───────────┘ └───────────┘ └───────────┘ └───────────┘
```

## Workflow Description

1. **User Query Processing**:

   - The user submits a query through the UI or API
   - The query is sent to the Agent Engine for processing

2. **Agent Decision Making**:

   - The Agent Engine retrieves recent interactions from the Memory System
   - It decides whether to use tools or RAG based on the query
   - For tool-based queries, it identifies the appropriate tools

3. **Tool Execution**:

   - The Agent Engine requests tool execution from the Tool Registry
   - The Tool Registry validates parameters and authorization
   - The appropriate tool is executed with the provided parameters
   - Results are returned to the Agent Engine

4. **Response Generation**:

   - For tool-based queries, the Agent Engine generates a response using tool results
   - For information queries, the RAG Engine retrieves relevant context and generates a response
   - The response is formatted and returned to the user

5. **Memory Storage**:
   - The interaction is stored in the Memory System
   - User preferences are updated if necessary

## API Integration

The Agent Engine is integrated with the API server through the following endpoints:

- `/sage` - Processes user queries and returns responses (primary endpoint)
- `/chat` - Legacy endpoint that redirects to `/sage` (for backward compatibility)
- `/tools` - Lists available tools and their descriptions
- `/tools/{tool_name}` - Executes a specific tool with parameters

## Next Steps

For information on the current implementation status and next steps, please refer to:

- [Implementation Status](implementation_status.md) - Current status of all components
- [Project Roadmap](agentic_rag_roadmap.md) - Implementation timeline and phases
