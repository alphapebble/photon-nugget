# 🌞 Solar-Sage: Intelligent Solar Energy Assistant

Solar-Sage is a domain-aware AI assistant designed to support engineers, site operators, and analysts in the solar energy lifecycle — from site planning to QA audits and performance diagnostics. Powered by LLMs and integrated with geospatial pipelines (e.g., point cloud analysis, CAD deviation detection, thermal anomaly classification), it answers questions, explains results, and guides workflows through a conversational interface.

## 🤖 Agentic RAG Chatbot

Solar-Sage is evolving into an **Agentic RAG Chatbot** that not only provides information but can also take actions, make decisions, and interact with external systems. By integrating weather data with RAG systems, it offers solar recommendations, insights, alerts, degradation estimates, and automation workflows. See the [Agentic RAG documentation](#agentic-rag-chatbot) for implementation details.

## 🌟 What Can It Do?

### Current Capabilities
- Answer questions about solar panels, installation, and energy
- Provide weather-enhanced solar insights
- Work completely offline on your computer
- Provide accurate information from reliable solar energy sources
- Remember your conversation history
- Switch between light and dark mode for comfortable viewing

### Upcoming Agentic Capabilities
- Generate solar production forecasts based on weather data
- Provide maintenance recommendations based on weather conditions
- Identify optimal times for solar production
- Analyze performance data and detect issues
- Schedule alerts and notifications
- Connect with smart home systems and inverter monitoring APIs

## 🚀 Quick Start Guide (For Everyone)

### Prerequisites

Before you begin, make sure you have:

1. **Python 3.9+** installed on your computer
   - [Download Python](https://www.python.org/downloads/) if you don't have it

2. **Git** to download the project
   - [Download Git](https://git-scm.com/downloads) if you don't have it

### Step 1: Download the Project

Open your terminal (Command Prompt on Windows) and run:

```bash
git clone https://github.com/balijepalli/solar-sage.git
cd solar-sage
```

### Step 2: Set Up the Environment

Create a virtual environment and install the required packages:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Start the Application

You can run the application using the CLI:

```bash
# Run the API server
python -m cli.main server

# Run the UI
python -m cli.main ui
```

Keep the terminal windows open while using the application.

### Alternative: Start Components Separately

If you prefer to start the components separately:

```bash
# Start the backend server
# On Windows:
set SOLAR_SAGE_LLM_PROVIDER=ollama
set SOLAR_SAGE_LLM_MODEL=mistral
python -m app.server

# On macOS/Linux:
SOLAR_SAGE_LLM_PROVIDER=ollama SOLAR_SAGE_LLM_MODEL=mistral python -m app.server

# Start the UI in another terminal
python -m ui.app
```

This will start the web interface. You'll see a URL like `http://0.0.0.0:8502` or `http://127.0.0.1:8502` in the terminal.

### Step 5: Use the Application

1. Open your web browser and go to the URL shown in the terminal (usually http://127.0.0.1:8502)
2. Type your solar energy question in the text box
3. Click "Ask" or press Enter to get an answer
4. Enjoy your conversation with the AI assistant!

## 🔍 Using Advanced Features

### Dark Mode

Click the "Toggle Dark Mode" button to switch between light and dark themes.

### Conversation History

- **Save History**: Click "Save History" to save your current conversation
- **Load History**: Click "Load History" to restore a previously saved conversation
- **Clear Chat**: Click "Clear Chat" to start a new conversation

### Feedback

After receiving an answer, you can provide feedback by clicking:
- 👍 Yes - if the answer was helpful
- 👎 No - if the answer wasn't helpful

## 🛠️ Troubleshooting

### Common Issues and Solutions

1. **"Connection Error" when asking a question**
   - Make sure the backend server is running (Step 3)
   - Check that you're using the correct URL in your browser

2. **"Module not found" errors**
   - Make sure you've activated the virtual environment
   - Try reinstalling the requirements: `pip install -r requirements.txt`

3. **Slow responses**
   - The AI model needs time to think, especially on the first question
   - Responses should get faster after the first few questions

4. **Application crashes or freezes**
   - Restart both the backend server and the UI
   - Make sure your computer meets the minimum requirements

### Getting Help

If you encounter problems not covered here:
1. Check the [GitHub Issues](https://github.com/balijepalli/solar-sage/issues) page
2. Create a new issue with details about your problem

## 📚 For Developers

If you're a developer interested in the technical details or want to contribute to the project, check out the [Developer Documentation](docs/DEVELOPERS.md).

### Agentic RAG Chatbot

Solar Sage is being extended with agentic capabilities to provide not just information but also take actions, make decisions, and interact with external systems. Check out the following documentation:

- [Agentic RAG Chatbot Architecture](docs/agentic_rag_chatbot.md) - Overview of the agentic architecture
- [Dual-Agent Architecture](docs/dual_agent_architecture.md) - Specialized retriever and response generator agents
- [Implementation Guide](docs/agent_implementation_guide.md) - Detailed implementation instructions
- [Project Roadmap](docs/agentic_rag_roadmap.md) - Implementation timeline and phases
- [Implementation Status](docs/implementation_status.md) - Current status and next steps
- [Quick Start Guide](docs/agentic_quickstart.md) - Get started quickly with implementation
- [Chunking Strategy Implementation](ingestion/chunking_strategy.py) - Flexible document chunking strategies for RAG

### Project Structure

The codebase follows a modular structure:

```
solar-sage/
├── agents/            # Agent components
│   ├── agent_engine.py        # Core agent logic
│   ├── base_agent.py          # Base agent class
│   ├── initialize.py          # Agent setup
│   ├── memory_system.py       # Conversation memory
│   ├── orchestrator.py        # Dual-agent workflow coordination
│   ├── response_generator_agent.py # Response generation agent
│   ├── retriever_agent.py     # Context retrieval agent
│   ├── tool_registry.py       # Tool management
│   ├── weather_agent.py       # Weather data fetching
│   └── weather_integration.py # Weather processing
├── api/               # API client and routes
├── app/               # Application server
│   └── agent_endpoints.py     # Agent API endpoints
├── cli/               # Command-line interface
│   ├── commands/             # CLI commands
│   └── main.py               # CLI entry point
├── config/            # Configuration
│   ├── environments/         # Environment-specific settings
│   ├── default.py            # Default configuration
│   └── __init__.py           # Configuration loader
├── core/              # Core functionality
│   ├── config.py             # Configuration utilities
│   ├── exceptions.py         # Custom exceptions
│   ├── logging.py            # Logging setup
│   └── utils/                # Shared utilities
├── data/              # Knowledge database
├── deployment/        # Deployment configuration
│   ├── docker/               # Docker configuration
│   ├── kubernetes/           # Kubernetes configuration
│   └── scripts/              # Deployment scripts
├── docs/              # Documentation
│   ├── DEVELOPERS.md         # Developer guide
│   ├── agentic_rag_chatbot.md # Agentic architecture
│   ├── agent_implementation_guide.md # Implementation guide
│   ├── agentic_rag_roadmap.md # Project roadmap
│   ├── implementation_status.md # Current status
│   └── agentic_quickstart.md # Quick start guide
├── ingestion/         # Document ingestion
│   ├── chunking_strategy.py  # Chunking strategy pattern
│   └── enhanced_pipeline.py  # Enhanced ingestion pipeline
├── llm/               # LLM integration
├── models/            # AI models
├── rag/               # Retrieval system
│   ├── agent_enhanced_rag.py # Agent-enhanced RAG
│   ├── rag_engine.py         # Dual-agent RAG implementation
│   └── weather_enhanced_rag.py # Weather-enhanced RAG
│   ├── prompts/              # Prompt templates
│   │   ├── dual_agent_rag.prompt # Dual-agent prompt template
│   │   ├── solar_rag.prompt      # Basic RAG prompt template
│   │   └── template_loader.py    # Template loading utilities
├── retriever/         # Document retrieval
├── scripts/           # Utility scripts
├── tests/             # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── tools/             # Agent tools
│   ├── integration_tools.py  # External system integration
│   ├── notification_tools.py # Alerts and notifications
│   ├── performance_tools.py  # Performance analysis
│   ├── system_tools.py       # System configuration
│   └── weather_tools.py      # Weather-related tools
├── ui/                # Frontend interface
├── .env.example       # Example environment variables
├── main.py            # Main entry point
├── pyproject.toml     # Python project configuration
└── README.md          # Project README
```

### Command-Line Interface

Solar Sage provides a command-line interface (CLI) for common tasks:

```bash
# Run the API server
python -m cli.main server [--host HOST] [--port PORT]

# Run the UI
python -m cli.main ui [--port PORT]

# Ingest a document
python -m cli.main ingest SOURCE [--db-path DB_PATH] [--table TABLE] [--model MODEL] [--strategy STRATEGY]

# List ingested documents
python -m cli.main list [--db-path DB_PATH] [--table TABLE]
```

For help on any command:

```bash
python -m cli.main --help
python -m cli.main COMMAND --help
```

### Configuration System

Solar Sage uses a flexible configuration system that supports:

1. **Environment Variables**: Set variables with the `SOLAR_SAGE_` prefix
2. **Configuration Files**: Environment-specific settings in `config/environments/`
3. **Default Values**: Fallback values defined in `config/default.py`

To configure the application:

1. Copy `.env.example` to `.env` and customize settings:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your preferred settings:
   ```
   SOLAR_SAGE_ENV=development
   SOLAR_SAGE_LOG_LEVEL=INFO
   SOLAR_SAGE_API_HOST=0.0.0.0
   SOLAR_SAGE_API_PORT=8000
   SOLAR_SAGE_UI_PORT=8502
   SOLAR_SAGE_LLM_PROVIDER=ollama
   SOLAR_SAGE_LLM_MODEL=mistral
   ```

3. Access configuration in code:
   ```python
   from core.config import get_config

   # Get a configuration value with a default fallback
   api_port = get_config("api_port", 8000)
   ```

### Running with Different Models

You can use different AI models by setting the appropriate environment variables:

```bash
# Using Mistral model
SOLAR_SAGE_LLM_PROVIDER=ollama SOLAR_SAGE_LLM_MODEL=mistral python -m cli.main server

# Using Llama model
SOLAR_SAGE_LLM_PROVIDER=ollama SOLAR_SAGE_LLM_MODEL=llama python -m cli.main server
```

Or by editing your `.env` file:

```
SOLAR_SAGE_LLM_PROVIDER=ollama
SOLAR_SAGE_LLM_MODEL=mistral
```

### Docker Deployment

You can deploy Solar Sage using Docker:

```bash
# Build and run with Docker Compose
docker-compose -f deployment/docker/docker-compose.yml up -d

# Or use the deployment script
bash deployment/scripts/deploy.sh
```

The Docker setup includes:
- API server container
- UI container
- Ollama container for local LLM support
- Shared volume for data persistence

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/) for the user interface
- Powered by [Mistral AI](https://mistral.ai/) models
- Uses [LanceDB](https://lancedb.github.io/lancedb/) for knowledge retrieval
