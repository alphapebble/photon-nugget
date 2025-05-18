# Solar Sage Agentic RAG Chatbot Quick Start Guide

This guide provides instructions for developers to quickly get started with the Solar Sage Agentic RAG Chatbot. The code for this system is already implemented in the repository.

## Prerequisites

Before starting, ensure you have:

1. Python 3.9+ environment
2. Git installed
3. Basic understanding of RAG systems and LLMs

## Setup Development Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/balijepalli/solar-sage.git
   cd solar-sage
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env file to add your API keys and configuration
   ```

5. Start the system:

   ```bash
   # Start all components (API, Ollama, UI)
   ./solar_sage.sh start

   # Or start components individually
   ./solar_sage.sh api start 8000  # Start API server on port 8000
   ./solar_sage.sh ui start 8502   # Start UI on port 8502
   ./solar_sage.sh ollama start    # Start Ollama
   ```

6. Access the UI:
   - Main UI: http://localhost:8502
   - Evaluation Dashboard: http://localhost:8502/?mode=evaluation

## Key Components

The Solar Sage Agentic RAG Chatbot is already implemented in the repository. Here's an overview of the key components:

### 1. Tool Registry

The Tool Registry manages the tools available to the agent. It allows registering, executing, and listing tools.

**Location**: `src/agents/tool_registry.py`

**Key Features**:

- Register tools with descriptions and parameter requirements
- Execute tools with validation
- List available tools for the agent

### 2. Memory System

The Memory System stores conversation history and user preferences.

**Location**: `src/agents/memory_system.py`

**Key Features**:

- Store and retrieve conversation history
- Save user preferences
- Maintain context across sessions

### 3. Agent Engine

The Agent Engine is the core component that processes user queries and decides when to use tools.

**Location**: `src/agents/agent_engine.py`

**Key Features**:

- Process user queries
- Determine when to use tools
- Generate responses using RAG

### 4. Weather Integration

Weather integration tools provide weather data and solar production forecasts.

**Location**: `src/agents/tools/weather_tools.py`

**Key Features**:

- Fetch weather data for a location
- Estimate solar production based on weather
- Generate insights about weather impact on solar systems

### 5. API Integration

The API server exposes endpoints for interacting with the agent.

**Location**: `src/app/server.py`

**Key Features**:

- Chat endpoint for processing queries
- Weather-enhanced RAG capabilities
- Tool execution with authorization

## Testing Your Implementation

1. Run unit tests:

   ```bash
   python -m unittest discover tests
   ```

2. Start the system:

   ```bash
   ./solar_sage.sh start
   ```

3. Test the API server:

   ```bash
   curl -X GET http://localhost:8000/
   ```

4. Test the sage endpoint:

   ```bash
   curl -X POST http://localhost:8000/sage \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What will my solar production be like tomorrow?",
       "lat": 37.7749,
       "lon": -122.4194,
       "include_weather": true
     }'
   ```

5. Access the UI:
   - Main UI: http://localhost:8502
   - Evaluation Dashboard: http://localhost:8502/?mode=evaluation

## Next Steps

The core agent components are already implemented. Here are the next steps you can take:

1. Implement additional tools in the `agents/tools/` directory
2. Update the UI to support agent interactions
3. Add user authentication and authorization
4. Implement monitoring and logging for agent actions

## Troubleshooting

### Common Issues

1. **LLM Not Responding**

   - Check that Ollama is running (if using Ollama)
   - Verify the model is correctly loaded

2. **Tool Execution Errors**

   - Check that all required parameters are provided
   - Verify API keys are correctly set in environment variables

3. **Memory System Errors**
   - Ensure the storage directory is writable
   - Check file permissions

## Resources

- Full implementation guide: `docs/agent_implementation_guide.md`
- Architecture overview: `docs/agentic_rag_chatbot.md`
- Project roadmap: `docs/agentic_rag_roadmap.md`
- Implementation status: `docs/implementation_status.md`
- Shell commands reference: `docs/shell_commands.md`

## Conclusion

This quick start guide provides the essential steps to begin using the Solar Sage Agentic RAG Chatbot. The core agent framework is already implemented, and you can start adding additional tools to enhance the chatbot's capabilities.

For more detailed information, refer to the comprehensive documentation in the `docs/` directory.
