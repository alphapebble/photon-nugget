# Solar Sage Agentic RAG Chatbot

## Overview

This document outlines the technical architecture and implementation details for extending the Solar Sage application into a fully agentic RAG (Retrieval Augmented Generation) chatbot. The agentic capabilities will enable the system to not only provide information but also take actions on behalf of users, make decisions, and interact with external systems.

## Architecture

The Agentic RAG Chatbot builds upon the existing Solar Sage architecture, extending it with:

1. **Dual-Agent Architecture**: Specialized Retriever and Response Generator agents
2. **Tool Integration Framework**: A system for defining, registering, and executing tools
3. **Memory System**: Short and long-term memory for maintaining conversation context
4. **Action Execution Pipeline**: Secure execution of user-authorized actions

### High-Level Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Interface │────▶│  Agent Router   │────▶│  Orchestrator   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                    │     ▲
                                                    │     │
                 ┌───────────────────────────────┬─┘     └─┐
                 │                               │         │
                 ▼                               ▼         │
┌─────────────────────────┐     ┌─────────────────────────┐
│    Retriever Agent      │────▶│  Response Generator     │
└─────────────────────────┘     └─────────────────────────┘
        │                                    │
        │                                    │
        ▼                                    ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Vector Store   │     │  Tool Registry  │◀───▶│  Weather API    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                      │
                               │                      │
                               ▼                      ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  External APIs  │     │  Memory System  │     │  LLM Provider   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Dual-Agent Workflow

The dual-agent architecture follows a specific workflow:

1. **User Query**: The user submits a question about solar energy
2. **Fetch Context**: The Retriever Agent searches for relevant information
3. **Return Context**: The retrieved context is passed to the orchestrator
4. **Generate Insights**: Optional step to add weather or other data
5. **Generate Response**: The Response Generator Agent creates the answer
6. **Output Response**: The final answer is returned to the user

## Core Components

### 1. RAG System with Strategy Pattern

The RAG (Retrieval Augmented Generation) system uses a Strategy Pattern for document chunking, allowing flexible and interchangeable chunking algorithms:

```python
class ChunkingStrategy(ABC):
    """Abstract base class for document chunking strategies."""

    @abstractmethod
    def chunk_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split a document into chunks according to the strategy."""
        pass
```

The system includes several chunking strategies:

- **Word Count Chunking**: Splits documents into chunks of fixed word count
- **Semantic Chunking**: Respects paragraph and section boundaries
- **Sliding Window Chunking**: Uses overlapping windows for better context preservation

The Strategy Pattern allows selecting the optimal chunking approach based on document type or specific requirements, improving the quality and relevance of retrieved context.

For implementation details, see the Chunking Strategy Implementation in `src/ingestion/strategies/base.py` and Enhanced Pipeline in `src/ingestion/enhanced_pipeline.py`.

### 2. Dual-Agent Architecture

The Dual-Agent Architecture consists of specialized agents with distinct responsibilities:

#### Base Agent

```python
class BaseAgent:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.llm = get_llm()

    def run(self, *args, **kwargs):
        """Run the agent. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement run method")
```

#### Retriever Agent

```python
class RetrieverAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Retriever",
            description="Retrieves relevant context for user queries"
        )

    def fetch_context(self, query, max_documents=5):
        """Fetch relevant context for the query."""
        return get_context_documents(query, n_results=max_documents)
```

#### Response Generator Agent

```python
class ResponseGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ResponseGenerator",
            description="Generates responses based on context and query"
        )

    def generate_response(self, query, context, notes=None):
        """Generate response based on query and context."""
        # Load prompt template and generate response
        # ...
```

#### Agent Orchestrator

```python
class AgentOrchestrator:
    def __init__(self):
        self.retriever_agent = RetrieverAgent()
        self.response_generator_agent = ResponseGeneratorAgent()

    def process_query(self, query, lat=None, lon=None, include_weather=False):
        # Step 1: User Query (already received as input)

        # Step 2: Fetch Context
        context = self.retriever_agent.fetch_context(query)

        # Step 3: Return Context (internal step)

        # Step 4: Generate Insights (optional)
        notes = []
        if include_weather and lat is not None and lon is not None:
            weather_context = get_weather_context_for_rag(lat, lon)
            notes.append(weather_context)

        # Step 5: Generate Response
        response = self.response_generator_agent.generate_response(query, context, notes)

        # Step 6: Output Response
        return {"response": response, "has_weather_context": bool(notes)}
```

### 3. Tool Registry

The Tool Registry manages the available tools and their specifications:

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool_name, tool_function, tool_description, required_params):
        self.tools[tool_name] = {
            "function": tool_function,
            "description": tool_description,
            "required_params": required_params
        }

    def get_tool(self, tool_name):
        return self.tools.get(tool_name)

    def list_tools(self):
        return [{"name": name, "description": tool["description"]}
                for name, tool in self.tools.items()]
```

### 4. Memory System

The Memory System maintains conversation history and user preferences:

```python
class MemorySystem:
    def __init__(self, storage_backend):
        self.storage = storage_backend

    def add_interaction(self, user_id, query, response, tools_used=None):
        # Store interaction in memory
        pass

    def get_recent_interactions(self, user_id, limit=5):
        # Retrieve recent interactions
        pass

    def store_user_preference(self, user_id, preference_key, preference_value):
        # Store user preference
        pass
```

### 5. Weather and Solar Forecasting Integration

Enhanced weather and solar forecasting integration for solar-specific insights:

```python
class WeatherToolkit:
    def __init__(self, weather_api_client):
        self.weather_client = weather_api_client

    def get_production_forecast(self, lat, lon, system_capacity_kw=5.0):
        # Get weather data and calculate production forecast
        pass

    def get_maintenance_recommendations(self, lat, lon):
        # Generate maintenance recommendations based on weather
        pass

    def get_optimal_production_times(self, lat, lon, days_ahead=7):
        # Identify optimal production times based on forecast
        pass
```

### 6. Semantic Metric Layer

The semantic metric layer provides a centralized repository for all metrics, formulas, and constants used throughout the system:

```python
from core.semantic_metric_layer import get_constant, evaluate_formula

# Get a constant metric
irradiance = get_constant('solar_panel.stc.irradiance')  # Returns 1000.0

# Evaluate a calculated metric
params = {
    'day_of_year': 180,
    'radians': math.radians,
    'sin': math.sin
}
declination = evaluate_formula('solar_irradiance.declination_angle', params)
```

The semantic metric layer uses numexpr for efficient and safe formula evaluation, with automatic fallback to Python's eval for complex expressions.

## Implemented Tools

The Agentic RAG Chatbot will include the following tools:

1. **Weather Analysis Tool**

   - Get current weather conditions
   - Forecast solar production based on weather
   - Recommend maintenance based on weather conditions

2. **System Configuration Tool**

   - Calculate optimal panel tilt and orientation
   - Estimate system size based on energy needs
   - Recommend inverter configurations

3. **Performance Analysis Tool**

   - Analyze uploaded SCADA data
   - Compare actual vs. expected production
   - Identify performance issues

4. **Notification Tool**

   - Schedule weather alerts
   - Set up production monitoring alerts
   - Configure maintenance reminders

5. **External Integration Tool**
   - Connect to smart home systems
   - Interface with inverter monitoring APIs
   - Export data to external analytics platforms

## Implementation Plan

### Phase 1: Core Agent Framework

1. ✅ Implement the Dual-Agent Architecture (Retriever and Response Generator)
2. ✅ Create the Agent Orchestrator for workflow coordination
3. ⏳ Implement the Tool Registry
4. ⏳ Develop the Memory System
5. ✅ Integrate with existing RAG and Weather components

### Recent Improvements

1. **Fixed Embedding Model I/O Error**: The system was experiencing an I/O error with the embedding model when trying to encode queries. This has been fixed by disabling the progress bar in the `sentence_transformers` library. The RAG functionality is now working correctly.

2. **Enhanced Logging Configuration**: Logs are now being written to the `logs` directory with separate log files for the API server (`api_server.log`), UI server (`ui_server.log`), and API client (`api_client.log`). This helps with debugging and troubleshooting.

### Troubleshooting

If you encounter any issues with the chat functionality, check the logs in the `logs` directory for more details. The API server logs are particularly useful for diagnosing issues with the RAG system.

### Running and Testing the System

For detailed instructions on running and testing the Solar Sage system, please refer to the [Shell Commands Documentation](shell_commands.md).

This documentation includes:

- Starting and stopping the system
- Managing individual components (API, UI, Ollama)
- Testing the API with curl commands
- Accessing the UI and evaluation dashboard
- Checking logs for debugging

### Phase 2: Tool Implementation

1. Implement Weather Analysis Tool
2. Develop System Configuration Tool
3. Create Performance Analysis Tool
4. Build Notification Tool
5. Implement External Integration Tool

### Phase 3: UI and Experience Enhancement

1. Update UI to support tool interactions
2. Implement user authorization for actions
3. Create visualization for tool outputs
4. Develop feedback mechanism for tool effectiveness

## Usage Examples

### Example 1: Solar Forecast with Dual-Agent Architecture

```
User: What will my solar production be like this week?

System: [Orchestrator receives the query]
[Retriever Agent fetches relevant solar production documents]
[Orchestrator detects solar forecast-related query]
[Solar-Enhanced RAG Engine fetches weather data and generates solar forecast]
[Response Generator Agent combines context and forecast data]

Response: Based on the weather forecast for your location (37.7749, -122.4194),
I estimate your 5kW system will produce:
- Today: 22.4 kWh (90% of optimal) - Sunny conditions
- Tomorrow: 18.7 kWh (75% of optimal) - Partly cloudy
- Wednesday: 12.5 kWh (50% of optimal) - Cloudy with rain
...
The best production day will be today with clear skies and moderate temperatures.

Your estimated savings this week will be approximately $28.75 based on your
electricity rate of $0.25/kWh. The system will cover about 85% of your
expected energy demand during this period.
```

### Example 2: Maintenance Recommendation with Dual-Agent Architecture

```
User: Should I clean my solar panels this week?

System: [Orchestrator receives the query]
[Retriever Agent fetches relevant panel maintenance documents]
[Orchestrator detects maintenance-related query and fetches weather data]
[Response Generator Agent combines context and weather data]

Response: Based on your location's weather forecast, I don't recommend cleaning
your panels this week. There's rain expected on Thursday which will naturally
clean your panels. Your last recorded cleaning was 3 weeks ago, and the current
dust accumulation is likely minimal. I'll remind you to check again in 2 weeks.
```

### Example 3: Basic Solar Information Query

```
User: How do solar panels work?

System: [Orchestrator receives the query]
[Retriever Agent fetches relevant solar panel technology documents]
[Response Generator Agent creates response from context]

Response: Solar panels work through the photovoltaic effect. When sunlight hits
the semiconductor materials in solar cells (typically silicon), it excites electrons,
creating an electric current. This direct current (DC) is then converted to alternating
current (AC) by an inverter for use in your home. The efficiency of this conversion
depends on factors like panel type, orientation, and weather conditions.
```

## Security Considerations

1. **User Authorization**: All actions require explicit user authorization
2. **Data Privacy**: User data is stored securely and not shared with external systems
3. **API Security**: All external API calls use secure authentication methods
4. **Action Logging**: All agent actions are logged for audit purposes

## Deployment

The Agentic RAG Chatbot can be deployed using the existing deployment infrastructure:

```bash
# Build with agent capabilities enabled
docker build -t solar-sage-agent .

# Run with agent configuration
docker run -p 8000:8000 -p 8502:8502 \
  -e ENABLE_AGENT=true \
  -e OPENWEATHER_API_KEY=your_key \
  -e TOOL_AUTHORIZATION_REQUIRED=true \
  solar-sage-agent
```

## Implementation Files

The dual-agent architecture is implemented in the following files:

- `agents/base_agent.py`: Base class for all agents
- `agents/types/retriever.py`: Implementation of the Retriever Agent
- `agents/types/response_generator.py`: Implementation of the Response Generator Agent
- `agents/orchestrator.py`: Coordination of the dual-agent workflow
- `rag/engines/base.py`: Updated RAG engine using the dual-agent architecture
- `rag/engines/weather_enhanced.py`: Weather-enhanced RAG engine
- `rag/engines/solar_enhanced.py`: Solar-enhanced RAG engine
- `rag/prompts/dual_agent_rag.prompt`: Specialized prompt template for the dual-agent system
- `core/semantic_metric_layer.py`: Semantic metric layer for calculations
- `agents/integrations/weather.py`: Weather integration
- `agents/integrations/solar_forecasting.py`: Solar forecasting integration
- `agents/integrations/solar_irradiance.py`: Solar irradiance calculations

## Configuration

The dual-agent architecture can be configured through environment variables or the `.env` file:

```
# Dual-Agent Configuration
SOLAR_SAGE_USE_DUAL_AGENT=true
SOLAR_SAGE_MAX_CONTEXT_DOCUMENTS=5

# Weather Integration
OPENWEATHER_API_KEY=your_api_key

# Solar Forecasting
SOLAR_SAGE_FORECAST_HORIZON_DAYS=7
SOLAR_SAGE_DATA_RESOLUTION_HOURS=1.0

# Semantic Metric Layer
SOLAR_SAGE_FORMULAS_PATH=src/config/formulas.yaml
```

## Future Enhancements

The dual-agent architecture provides a foundation for future enhancements:

1. **Additional Specialized Agents**: Add agents for specific tasks (e.g., data analysis)
2. **Agent Memory**: Implement persistent memory for better context awareness
3. **Tool Integration**: Add tools that agents can use to perform actions
4. **Multi-Step Reasoning**: Implement more complex reasoning chains between agents
5. **Model Switching**: Use different models for different agents based on their requirements
6. **Enhanced Semantic Metric Layer**: Add more metrics and formulas for solar energy calculations
7. **Advanced Solar Forecasting**: Implement more sophisticated solar forecasting algorithms
8. **Financial Analysis**: Add financial analysis tools for ROI and payback period calculations
9. **Integration with Smart Home Systems**: Connect with smart home systems for energy optimization

## Conclusion

The Solar Sage Agentic RAG Chatbot extends the existing application with powerful agent capabilities, enabling it to not only provide information but also take actions to help users optimize their solar energy systems.

The implementation of the Dual-Agent Architecture with specialized Retriever and Response Generator agents provides a solid foundation for the system. This architecture offers several benefits:

1. **Separation of Concerns**: Each agent focuses on a specific task
2. **Improved Modularity**: Easier to maintain and extend each component independently
3. **Enhanced Flexibility**: Can add more specialized agents in the future
4. **Better Context Management**: More control over how context is retrieved and used
5. **Clearer Debugging**: Issues can be isolated to specific agents

The integration of the semantic metric layer provides a centralized repository for all metrics, formulas, and constants used throughout the system. This ensures consistency in calculations and makes it easy to modify formulas without changing code.

The solar forecasting integration enables the system to provide accurate predictions of solar energy production based on weather forecasts and system characteristics. This helps users optimize their energy usage and maximize the benefits of their solar energy systems.

By leveraging the existing RAG, weather integration, and semantic metric layer components, the agent can provide highly personalized and actionable insights while maintaining compatibility with the current LLM provider.
