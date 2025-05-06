# 🌞 Private AI Assistant with Solar RAG Augmentation

This project is a fully on-premises Retrieval-Augmented Generation (RAG) chatbot designed for solar energy knowledge queries.  
It combines LanceDB vector retrieval, local embedding generation, and Llama/Mistral model-based generation, served through FastAPI and Gradio UI.

---

## 📚 Features

- 🛡️ Completely offline, on-premises deployment
- 🔁 Switchable LLM backend (Ollama, Transformers, OpenAI-ready)
- 📄 Structured prompt templates using YAML + Jinja2
- 🧩 Modular design ready for agentic workflows and LangGraph integration
- 🔍 LanceDB-powered local vector retrieval
- 🤖 Local inference with Mistral / LLaMA models
- 📝 Solar domain-specific document ingestion and embedding
- 🚀 FastAPI backend with Gradio-based chatbot frontend
- 🐳 Dockerized setup for reproducible, scalable deployment



---

## 📂 Project Structure

```
photon-nugget/
├── ingestion/                # Fetch, parse, and clean solar documents (raw → chunks → vector store)
│   ├── fetcher.py            # Download PDFs, HTML pages from various sources
│   ├── parser.py             # Extract readable text from documents
│   ├── cleaner.py            # Clean, split, and preprocess text into knowledge units
│   └── ingestion_runner.py   # Orchestrates the full ingestion pipeline
├── retriever/                # Vector search layer (e.g., using LanceDB, FAISS)
│   └── retriever_lancedb.py  # Store and retrieve documents from LanceDB
├── llm/                      # LLM backends (Ollama, Transformers, etc.)
│   └── chatbot_engine.py     # Unified interface to load and run local models like Mistral/LLaMA
├── app/                      # FastAPI server and request/response models
│   └── server.py             # API routes and logic using Pydantic
├── ui/                       # Frontend interface
│   └── app.py                # Gradio-based UI for user interaction
├── models/                   # Local pre-downloaded models (e.g., mistral-7b-instruct, gemma)
├── data/                     # Input/output artifacts for the pipeline
│   ├── lancedb/              # LanceDB vector database files
│   ├── docs_raw/             # Raw source documents (e.g., PDFs)
│   └── docs_clean/           # Cleaned and chunked text for embedding
├── prompts/                  # YAML + Jinja2 structured prompt templates
│   ├── solar_rag.prompt      # Example prompt with context and query variables
│   └── utils/                # Template loader, renderer
├── evaluation/               # (Optional) Evaluation scripts, metrics (BLEU, ROUGE, etc.)
├── requirements.txt          # Python package dependencies
├── Dockerfile                # Container definition for the app
├── docker-compose.yml        # Multi-container orchestration (Ollama + app + DB)
├── download_model.sh         # Script to download and cache model weights
└── .env                      # Environment variables (MODEL_PATH, USE_OLLAMA, etc.)

```

---

## 🛠️ Tech Stack

- **FastAPI** — Lightweight Python API backend
- **Gradio** — Frontend interface for interactive chat
- **LanceDB** — Embedded vector database for fast document retrieval
- **Sentence-Transformers** — For generating dense vector embeddings
- **Transformers / Ollama / OpenAI** — Switchable LLM backend via unified interface
- **Jinja2 + YAML** — Prompt templating system
- **PyMuPDF** — Robust PDF parsing for document ingestion
- **Docker** — Optional containerization for deployment

---
## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
````

---

### 2. Start Ollama (Optional – for local LLMs like `mistral`)

Install Ollama (if not already installed):

```bash
brew install ollama
```

Start the Ollama server and pull the model:

```bash
ollama serve
ollama pull mistral
```

Or run the helper script:

```bash
./start_ollama.sh mistral
```

---

### 3. Start Backend (FastAPI)

**For Ollama:**

```bash
USE_OLLAMA=true MODEL_NAME=mistral uvicorn app.server:app --host 0.0.0.0 --port 8000
```

**For Transformers:**

```bash
MODEL_PATH=./models/mistral-7b-instruct uvicorn app.server:app --host 0.0.0.0 --port 8000
```

---

### 4. Start Frontend (Gradio UI)

**For Ollama:**

```bash
USE_OLLAMA=true MODEL_NAME=mistral python ui/app.py
```

**For Transformers:**

```bash
MODEL_PATH=./models/mistral-7b-instruct python ui/app.py
```

---

### 5. Or Build and Run via Docker

```bash
docker build -t photon-nugget .
docker run -p 8000:8000 -p 8501:8501 \
  -e USE_OLLAMA=true \
  -e MODEL_NAME=mistral \
  photon-nugget
```

---

### 6. Ingest Domain Knowledge (Optional)

To ingest a PDF into the vector database:

```bash
python -m ingestion.run_ingestion "https://example.com/solar_doc.pdf"
```

---

### 7. Test CLI RAG Pipeline

```bash
python -m rag.rag_cli "What is the recommended tilt angle for solar panels?"
```

---

## 📚 Knowledge Ingestion (Solar Knowledge)

To fetch and store domain-specific solar documents:

```bash
python ingestion/ingestion_runner.py
```

This will:
- Fetch solar installation guides, policies, FAQs
- Parse PDFs and web pages
- Clean text into knowledge units
- Store embeddings into LanceDB

---

## 🌟 Future Enhancements

- ✅ Add document metadata tracking (source, date)
- ✅ Re-rank retrieved documents by relevance
- ✅ Add answer summarization module
- ✅ Integrate multi-turn conversation memory
- ✅ Auto-schedule document refresh and re-ingestion

---

# 🚀 About

This project demonstrates a full **offline RAG pipeline** using open-source components  
for secure, private, knowledge-grounded chatbots in the solar energy domain.

---

# 🛡️ License

MIT License or specify if using specific restricted datasets.