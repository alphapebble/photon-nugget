# Solar Sage Dual-Agent Architecture

## Overview

The Solar Sage application now implements a dual-agent architecture for its RAG (Retrieval Augmented Generation) system. This architecture separates the retrieval and response generation concerns into two specialized agents, providing better modularity, maintainability, and performance.

## Architecture Components

### 1. Retriever Agent

The Retriever Agent is responsible for:
- Processing user queries to understand information needs
- Retrieving relevant documents from the vector database
- Optimizing search parameters for better context retrieval
- Returning a curated set of context documents

### 2. Response Generator Agent

The Response Generator Agent is responsible for:
- Processing the user query and retrieved context
- Incorporating additional insights (e.g., weather data)
- Generating coherent, accurate, and helpful responses
- Formatting responses appropriately for the user

### 3. Agent Orchestrator

The Agent Orchestrator coordinates the workflow between agents:
- Receives the initial user query
- Calls the Retriever Agent to fetch relevant context
- Gathers additional insights if needed (e.g., weather data)
- Passes context and insights to the Response Generator Agent
- Returns the final response to the user

## Workflow

The dual-agent workflow follows these steps:

1. **User Query**: The user submits a question about solar energy
2. **Fetch Context**: The Retriever Agent searches for relevant information
3. **Return Context**: The retrieved context is passed to the orchestrator
4. **Generate Insights**: Optional step to add weather or other data
5. **Generate Response**: The Response Generator Agent creates the answer
6. **Output Response**: The final answer is returned to the user

## Implementation

The dual-agent architecture is implemented in the following files:

- `agents/base_agent.py`: Base class for all agents
- `agents/retriever_agent.py`: Implementation of the Retriever Agent
- `agents/response_generator_agent.py`: Implementation of the Response Generator Agent
- `agents/orchestrator.py`: Coordination of the dual-agent workflow
- `rag/rag_engine.py`: Updated RAG engine using the dual-agent architecture
- `rag/prompts/dual_agent_rag.prompt`: Specialized prompt template for the dual-agent system

## Configuration

The dual-agent architecture can be configured through environment variables or the `.env` file:

```
SOLAR_SAGE_USE_DUAL_AGENT=true
SOLAR_SAGE_MAX_CONTEXT_DOCUMENTS=5
```

## Benefits

The dual-agent architecture provides several benefits:

1. **Separation of Concerns**: Each agent focuses on a specific task
2. **Improved Maintainability**: Easier to update or replace individual components
3. **Better Performance**: Specialized agents can be optimized for their specific tasks
4. **Enhanced Extensibility**: Easier to add new capabilities to specific parts of the system
5. **Clearer Debugging**: Issues can be isolated to specific agents

## Future Enhancements

The dual-agent architecture provides a foundation for future enhancements:

1. **Additional Specialized Agents**: Add agents for specific tasks (e.g., data analysis)
2. **Agent Memory**: Implement persistent memory for better context awareness
3. **Tool Integration**: Add tools that agents can use to perform actions
4. **Multi-Step Reasoning**: Implement more complex reasoning chains between agents
5. **Model Switching**: Use different models for different agents based on their requirements
