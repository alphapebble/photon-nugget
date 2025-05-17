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

You can run the application using our convenient startup script:

```bash
# Start all components (API, Ollama, UI)
./solar_sage.sh start

# Or start components individually
./solar_sage.sh api start 8000  # Start API server on port 8000
./solar_sage.sh ui start 8502   # Start UI on port 8502
./solar_sage.sh ollama start    # Start Ollama

# Check status of all components
./solar_sage.sh status

# Stop all components
./solar_sage.sh stop

# Get help on all available commands
./solar_sage.sh help
```

For a complete reference of all available shell commands, see the [Shell Commands Documentation](docs/shell_commands.md).

Keep the terminal windows open while using the application.

> **Note:** All scripts automatically set up the Python path and environment variables for you. If you need to customize settings, you can create a `.env` file in the project root.

### Alternative: Start Components Using CLI

If you prefer to use the CLI directly:

```bash
# First, add src to your Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src  # Linux/macOS
# OR
set PYTHONPATH=%PYTHONPATH%;%cd%\src     # Windows

# Run the API server
python -m cli.main server

# Run the UI
python -m cli.main ui
```

This will start the web interface. You'll see a URL like `http://0.0.0.0:8502` or `http://127.0.0.1:8502` in the terminal.

### Step 4: Access the UI

Once the UI is running, you can access it in your web browser:

- **Main UI**: http://localhost:8502
- **Evaluation Dashboard**: http://localhost:8502/?mode=evaluation

You can switch between the main UI and evaluation dashboard using the links in the header.

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

### Setting Up Your Development Environment

#### Marking the Source Root

The project uses a `src` directory as the source root. You should mark this directory as a source root in your IDE:

**PyCharm:**

1. Right-click on the `src` directory
2. Select "Mark Directory as" > "Sources Root"

**VS Code:**

1. Add this to your `.vscode/settings.json`:
   ```json
   {
     "python.analysis.extraPaths": ["./src"]
   }
   ```
2. If using a virtual environment, make sure to select it as your Python interpreter

**Command Line:**
If you're not using an IDE, you can add the `src` directory to your Python path:

```bash
# Linux/macOS
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Windows (Command Prompt)
set PYTHONPATH=%PYTHONPATH%;%cd%\src

# Windows (PowerShell)
$env:PYTHONPATH += ";$(Get-Location)\src"
```

### Agentic RAG Chatbot

Solar Sage is being extended with agentic capabilities to provide not just information but also take actions, make decisions, and interact with external systems. Check out the following documentation:

- [Agentic RAG Chatbot Architecture](docs/agentic_rag_chatbot.md) - Complete architecture documentation including dual-agent implementation
- [Implementation Guide](docs/agent_implementation_guide.md) - Detailed implementation instructions
- [Project Roadmap](docs/agentic_rag_roadmap.md) - Implementation timeline and phases
- [Implementation Status](docs/implementation_status.md) - Current status and next steps
- [Quick Start Guide](docs/agentic_quickstart.md) - Get started quickly with implementation
- [Agentic System Vision](docs/agentic_vision.md) - Future vision for true agentic capabilities

### Project Structure

The codebase follows a modular structure with a clean separation of concerns. The project is organized into several key components:

- **src/** - Backend source code (marked as source root)

  - **agents/** - Agent components for autonomous reasoning
  - **app/** - FastAPI server and API endpoints
  - **core/** - Core utilities and configuration
  - **ingestion/** - Document processing pipeline
  - **llm/** - LLM integration with various backends
  - **rag/** - Retrieval-Augmented Generation system
  - **retrieval/** - Vector database retrieval

- **ui/** - Frontend interface with Gradio
  - **api/** - API client for backend communication
  - **components/** - UI components and views
  - **utils/** - Utility functions
  - **templates/** - HTML/CSS/JS templates

For a detailed breakdown of the project structure, please see the [Developer Documentation](docs/DEVELOPERS.md).

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

> **Note:** The CLI commands assume that you have added the `src` directory to your Python path or marked it as a source root in your IDE.

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
# Using Mistral model (with src in Python path)
SOLAR_SAGE_LLM_PROVIDER=ollama SOLAR_SAGE_LLM_MODEL=mistral PYTHONPATH=$PYTHONPATH:$(pwd)/src python -m cli.main server

# Using Llama model (with src in Python path)
SOLAR_SAGE_LLM_PROVIDER=ollama SOLAR_SAGE_LLM_MODEL=llama PYTHONPATH=$PYTHONPATH:$(pwd)/src python -m cli.main server
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

> **Note:** The Docker Compose file is located in the `deployment/docker/` directory. There is no Docker Compose file in the root directory.

The Docker setup includes:

- API server container
- UI container
- Ollama container for local LLM support
- Shared volume for data persistence

### Testing

Solar Sage includes a comprehensive test suite:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test category
python -m unittest discover tests/unit
python -m unittest discover tests/integration

# Run dual-agent architecture tests
python tests/run_dual_agent_tests.py

# Run tests with evaluation (may take longer)
python tests/run_dual_agent_tests.py --with-evaluation
```

#### RAG Evaluation System

Solar Sage includes a specialized RAG evaluation system that measures the quality of responses using multiple metrics:

- **Basic Metrics**: Keyword matching, response time, response length
- **RAGAS Metrics**: Faithfulness, answer relevancy, context relevancy, context precision/recall
- **NLP Metrics**: BLEU, ROUGE, cosine similarity

You can run the evaluation from the command line:

```bash
# Run evaluation with default settings
python -m src.cli.main evaluate

# Run with specific options
python -m src.cli.main evaluate --csv path/to/questions.csv --references path/to/answers.json --no-dual-agent --weather
```

To view evaluation results in a dashboard:

```bash
# Launch the UI with the evaluation dashboard
./solar_sage.sh ui start 8502 main

# Then access the evaluation dashboard at:
http://localhost:8502/?mode=evaluation
```

You can also switch between the main UI and evaluation dashboard using the links in the header.

#### AI Testing with Giskard

We have a [planned integration with Giskard](docs/giskard_testing_plan.md), an open-source testing framework specifically designed for AI/ML models. This will help detect issues like bias, performance problems, and security vulnerabilities in our RAG system and LLM integration.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/) for the user interface
- Powered by [Mistral AI](https://mistral.ai/) models
- Uses [LanceDB](https://lancedb.github.io/lancedb/) for knowledge retrieval
