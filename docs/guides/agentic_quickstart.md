# Solar Sage Agentic RAG Chatbot: Quick Start Guide

This guide provides a quick start for using the Solar Sage Agentic RAG Chatbot. It focuses specifically on the agentic capabilities of the system.

## What is the Agentic RAG Chatbot?

The Solar Sage Agentic RAG Chatbot combines Retrieval-Augmented Generation (RAG) with agentic capabilities to provide not just information but also take actions, make decisions, and interact with external systems. By integrating weather data with RAG systems, it offers solar recommendations, insights, alerts, degradation estimates, and automation workflows.

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.9+** installed on your computer
2. **Git** to download the project
3. **Node.js 16+** for the Next.js frontend

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/alphapebble/solar-sage.git
   cd solar-sage
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env file to add your API keys and configuration
   ```

5. Start the system:

   ```bash
   # Start all components (API, Ollama, UI, Next.js)
   ./solar_sage.sh start
   ```

   For more detailed information about shell commands, see the [Shell Commands Reference](../reference/shell_commands.md).

6. Access the system:

   For detailed information about accessing the system, see the [UI Architecture](../architecture/ui_architecture.md#access-urls) documentation.

## Key Components

The Solar Sage Agentic RAG Chatbot is already implemented in the repository. Here's an overview of the key components:

### 1. Tool Registry

The Tool Registry (`src/agents/tool_registry.py`) manages all available tools and their execution. It provides:

- Tool registration and discovery
- Tool execution with parameter validation
- Authorization checks for sensitive tools

### 2. Memory System

The Memory System (`src/agents/memory_system.py`) maintains conversation history and user preferences. It provides:

- Short-term memory for the current conversation
- Long-term memory for user preferences
- Context management for multi-turn conversations

### 3. Agent Engine

The Agent Engine (`src/agents/agent_engine.py`) coordinates the dual-agent workflow:

1. **Retriever Agent**: Retrieves relevant information from the knowledge base
2. **Response Generator Agent**: Generates a response based on the retrieved information

### 4. Weather Tools

The Weather Tools (`src/agents/tools/weather_tools.py`) provide weather data integration:

- Current weather conditions
- Weather forecasts
- Weather-based recommendations

## Testing the Agentic Capabilities

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

5. Access the UIs:

   For detailed information about accessing the UIs, see the [Shell Commands Reference](../reference/shell_commands.md#access-urls).

## Next Steps

The core agent components are already implemented. Here are the next steps you can take:

1. **Add New Tools**: Create new tools in the `src/agents/tools/` directory
2. **Enhance Memory System**: Add more sophisticated memory capabilities
3. **Improve Authorization**: Implement more granular authorization for sensitive tools
4. **Add External Integrations**: Integrate with external systems like smart home devices
5. **Implement Workflows**: Create multi-step workflows for common tasks

## Resources

- [Agentic RAG Chatbot Architecture](../architecture/agentic_rag_chatbot.md) - Complete architecture documentation
- [UI Architecture](../architecture/ui_architecture.md) - Overview of the dual UI architecture
- [API Architecture](../architecture/api_architecture.md) - Overview of the API architecture
- [Shell Commands Reference](../reference/shell_commands.md) - Comprehensive reference for shell commands
- [Implementation Reference](../reference/agent_implementation_guide.md) - Reference guide for the implemented components
- [Project Roadmap](../development/agentic_rag_roadmap.md) - Implementation timeline and phases

## Conclusion

This quick start guide provides the essential steps to begin using the Solar Sage Agentic RAG Chatbot. The core agent framework is already implemented, and you can start adding additional tools to enhance the chatbot's capabilities.

For more detailed information, refer to the comprehensive documentation in the `docs/` directory.
