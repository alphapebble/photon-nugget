# Developer Documentation for Solar-Sage

This document provides technical details for developers who want to understand, modify, or contribute to the Solar-Sage project.

## 📂 Project Structure

```
solar-sage/
├── src/                      # Source code
│   ├── agents/               # Agent components
│   │   ├── types/            # Agent type implementations
│   │   │   ├── retriever.py  # Retrieval agent
│   │   │   └── response_generator.py # Response generation agent
│   │   ├── integrations/     # External integrations
│   │   │   └── weather.py    # Weather integration
│   │   └── tools/            # Agent tools
│   ├── app/                  # Application server
│   │   ├── endpoints/        # API endpoints
│   │   ├── middleware/       # API middleware
│   │   ├── models/           # API models
│   │   └── server.py         # FastAPI server
│   ├── core/                 # Core functionality
│   │   ├── config/           # Configuration management
│   │   └── utils/            # Utility functions
│   ├── ingestion/            # Document ingestion
│   │   ├── processors/       # Document processors
│   │   │   ├── cleaner.py    # Text cleaning
│   │   │   └── parser.py     # Document parsing
│   │   └── strategies/       # Chunking strategies
│   ├── llm/                  # LLM backends
│   │   ├── base.py           # Base LLM interface
│   │   └── llm_factory.py    # LLM factory
│   ├── rag/                  # RAG pipeline components
│   │   ├── engines/          # RAG engine implementations
│   │   │   ├── base.py       # Base RAG engine
│   │   │   └── weather_enhanced.py # Weather-enhanced RAG
│   │   └── prompts/          # Prompt templates
│   └── retrieval/            # Document retrieval
│       ├── base.py           # Base retriever interface
│       └── providers/        # Retriever implementations
│           └── lancedb.py    # LanceDB retriever
├── ui/                       # Frontend interface
│   ├── app.py                # Main UI entry point
│   ├── config.py             # UI configuration settings
│   ├── theme.py              # UI theme and styling
│   ├── api/                  # API client
│   │   ├── client.py         # API client implementation
│   │   ├── config.py         # API client configuration
│   │   └── errors.py         # API error handling
│   ├── components/           # UI components
│   │   ├── simple_ui.py      # Main UI implementation
│   │   ├── evaluation_dashboard.py # Evaluation dashboard UI
│   │   ├── weather_dashboard.py # Weather dashboard UI
│   │   └── scada.py          # SCADA data visualization
│   ├── utils/                # Utility functions
│   │   ├── template_loader.py # Template loading utilities
│   │   ├── feedback.py       # Feedback handling
│   │   ├── history.py        # Conversation history management
│   │   └── messages.py       # Message formatting
│   └── templates/            # HTML/CSS/JS templates
├── models/                   # Local pre-downloaded models (e.g., mistral-7b-instruct, gemma)
├── data/                     # Input/output artifacts for the pipeline
│   ├── lancedb/              # LanceDB vector database files
│   ├── docs_raw/             # Raw source documents (e.g., PDFs)
│   └── docs_clean/           # Cleaned and chunked text for embedding
├── prompts/                  # YAML + Jinja2 structured prompt templates
│   ├── solar_rag.prompt      # Example prompt with context and query variables
│   └── utils/                # Template loader, renderer
├── docs/                     # Documentation
│   └── images/               # Screenshots and images
├── requirements.txt          # Python package dependencies
├── Dockerfile                # Container definition for the app
├── docker-compose.yml        # Multi-container orchestration (Ollama + app + DB)
└── .env                      # Environment variables (MODEL_PATH, USE_OLLAMA, etc.)
```

## 🛠️ Tech Stack

- **FastAPI** — Lightweight Python API backend
- **Gradio** — Frontend interface for interactive chat
- **LanceDB** — Embedded vector database for fast document retrieval
- **Sentence-Transformers** — For generating dense vector embeddings
- **Transformers / Ollama / OpenAI** — Switchable LLM backend via unified interface
- **Jinja2 + YAML** — Prompt templating system
- **PyMuPDF** — Robust PDF parsing for document ingestion
- **Docker** — Optional containerization for deployment

## 🚀 Development Setup

### Environment Setup

For development, it's recommended to use a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running in Development Mode

For faster development iterations, you can run the backend with auto-reload:

```bash
uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
```

### Code Style and Linting

We use:

- Black for code formatting
- isort for import sorting
- flake8 for linting

Run these tools before submitting a pull request:

```bash
black .
isort .
flake8
```

## 🧪 Testing

For comprehensive testing instructions, see the [Testing Guide](testing_guide.md).

### Running Tests

```bash
# Run all unit tests
python -m unittest discover tests/unit

# Run specific test category
python -m unittest discover tests/unit/agents
python -m unittest discover tests/unit/rag

# Run specific test file
python -m unittest tests/unit/agents/test_tool_registry.py
```

### Adding Tests

Add new tests in the `tests/` directory, following the existing structure:

- `tests/unit/` for unit tests
- `tests/integration/` for integration tests
- `tests/e2e/` for end-to-end tests
- `tests/evaluation/` for RAG evaluation tests

## 🔄 API Reference

For a comprehensive overview of the API architecture, see the [API Architecture Documentation](api_architecture.md).

### Backend API

The backend API is built with FastAPI and provides the following endpoints:

#### Conversational API (`src/app/`)

- `POST /sage` - Send a message to the chatbot (primary endpoint)
  - Request body: `{"query": "your question here"}`
  - Response: `{"response": "AI response here"}`
- `POST /chat` - Legacy endpoint that redirects to `/sage` (for backward compatibility)

#### Traditional REST API (`src/api/`)

- `POST /solar/forecast` - Generate a solar energy forecast
  - Request body: `{"latitude": 37.7749, "longitude": -122.4194, "location_id": "home", "system_capacity_kw": 5.0}`
  - Response: Detailed solar forecast data

### UI Components

The UI is built with Gradio and consists of the following main components:

#### Core UI

- `app.py` - Main application file that launches the UI
- `config.py` - UI configuration settings
- `theme.py` - UI theme and styling

#### UI Components

- `components/simple_ui.py` - Main UI implementation with chat interface
- `components/evaluation_dashboard.py` - Dashboard for RAG evaluation metrics
- `components/weather_dashboard.py` - Weather data visualization dashboard
- `components/scada.py` - SCADA data visualization components

#### API Client

- `api/client.py` - Core API client implementation
- `api/config.py` - API client configuration settings
- `api/errors.py` - API error handling

#### Utilities

- `utils/template_loader.py` - HTML/CSS/JS template loading utilities
- `utils/feedback.py` - Feedback handling
- `utils/history.py` - Conversation history management
- `utils/messages.py` - Message formatting

## 🌟 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📚 Advanced Topics

### Adding New Models

To add support for a new model:

1. Update `llm/llm_factory.py` to include the new model
2. Add model-specific parameters in `app/config.py`
3. Update the documentation

### Customizing the RAG Pipeline

The RAG pipeline can be customized by:

1. Modifying `rag/rag_engine.py` to change the retrieval or generation logic
2. Updating prompt templates in `prompts/`
3. Adjusting retrieval parameters in `retriever/retriever_lancedb.py`

### Docker Deployment

For production deployment, use Docker:

```bash
# Build the Docker image
docker build -t solar-sage .

# Run the container
docker run -p 8000:8000 -p 8502:8502 solar-sage
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
