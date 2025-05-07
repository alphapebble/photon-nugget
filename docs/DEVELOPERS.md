# Developer Documentation for Solar-Sage

This document provides technical details for developers who want to understand, modify, or contribute to the Solar-Sage project.

## 📂 Project Structure

```
solar-sage/
├── ingestion/                # Fetch, parse, and clean solar documents (raw → chunks → vector store)
│   ├── fetcher.py            # Download PDFs, HTML pages from various sources
│   ├── parser.py             # Extract readable text from documents
│   ├── cleaner.py            # Clean, split, and preprocess text into knowledge units
│   └── ingestion_runner.py   # Orchestrates the full ingestion pipeline
├── retriever/                # Vector search layer (e.g., using LanceDB, FAISS)
│   └── retriever_lancedb.py  # Store and retrieve documents from LanceDB
├── llm/                      # LLM backends (Ollama, Transformers, etc.)
│   └── llm_factory.py        # Unified interface to load and run local models like Mistral/LLaMA
├── rag/                      # RAG pipeline components
│   └── rag_engine.py         # Combines retrieval and generation
├── app/                      # FastAPI server and request/response models
│   ├── server.py             # API routes and logic using Pydantic
│   └── prompt.py             # Prompt templates and formatting
├── ui/                       # Frontend interface
│   ├── app.py                # Gradio-based UI for user interaction
│   ├── api.py                # API communication functions
│   ├── config.py             # UI configuration settings
│   ├── feedback.py           # Feedback handling
│   ├── history.py            # Conversation history management
│   └── theme.py              # Theme and styling
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

### Running Tests

```bash
pytest
```

### Adding Tests

Add new tests in the `tests/` directory, following the existing structure:
- `tests/unit/` for unit tests
- `tests/integration/` for integration tests
- `tests/e2e/` for end-to-end tests

## 🔄 API Reference

### Backend API

The backend API is built with FastAPI and provides the following endpoints:

- `POST /chat` - Send a message to the chatbot
  - Request body: `{"query": "your question here"}`
  - Response: `{"response": "AI response here"}`

### UI Components

The UI is built with Gradio and consists of the following main components:

- `app.py` - Main application file
- `config.py` - Configuration settings
- `api.py` - API communication
- `theme.py` - Theme and styling
- `feedback.py` - Feedback handling
- `history.py` - Conversation history management

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
