# 🌞 Private AI Assistant with Solar RAG Augmentation

This project is a fully on-premises Retrieval-Augmented Generation (RAG) chatbot designed for solar energy knowledge queries.  
It combines LanceDB vector retrieval, local embedding generation, and Llama/Mistral model-based generation, served through FastAPI and Gradio UI.

---

## 📚 Features

- 🛡️ Completely offline, on-prem deployment
- 🔍 LanceDB-based local vector retrieval
- 🤖 Local Mistral / Llama model serving
- 📝 Solar domain-specific knowledge ingestion
- 🚀 FastAPI backend + Gradio frontend
- 🐳 Dockerized deployment for easy scaling

---

## 📂 Project Structure

```
private-ai-assistant/
├── ingestion/               # Fetch, parse, clean solar documents
│   ├── fetcher.py            # Fetch PDFs, HTML pages
│   ├── parser.py             # Extract text from PDFs and web pages
│   ├── cleaner.py            # Split and clean text into knowledge units
│   └── ingestion_runner.py   # Run full ingestion pipeline
├── retriever/                
│   └── retriever_lancedb.py   # Store and retrieve documents using LanceDB
├── model/
│   └── chatbot_engine.py      # Load and run local Llama/Mistral model
├── app/
│   └── server.py              # FastAPI backend API
├── ui/
│   └── app.py                 # Gradio UI frontend
├── models/                    # Pre-downloaded local models (Llama, Mistral)
├── data/
│   ├── lancedb/               # LanceDB vector database files
│   ├── docs_raw/              # Raw fetched documents
│   └── docs_clean/            # Cleaned and processed knowledge text
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Dockerfile to containerize the app
├── docker-compose.yml         # (optional) Docker orchestration
├── download_model.sh          # Script to download model locally
└── .env                       # Environment variables (MODEL_PATH, etc.)
```

---

## 🛠️ Tech Stack

- **FastAPI** — API backend
- **Gradio** — Chat frontend
- **LanceDB** — Local vector database
- **Sentence-Transformers** — Text embeddings
- **Transformers / Huggingface** — Model loading
- **Docker** — Optional containerization for deployment
- **PyMuPDF** — PDF parsing for ingestion

---

## 🚀 How to Run

### Install dependencies
```bash
pip install -r requirements.txt
```

### Start backend (FastAPI)
```bash
MODEL_PATH=./models/mistral-7b-instruct uvicorn app.server:app --host 0.0.0.0 --port 8000
```

### Start frontend (Gradio)
```bash
MODEL_PATH=./models/mistral-7b-instruct python ui/app.py
```

### Or build and run via Docker
```bash
docker build -t private-ai-chatbot .
docker run -p 8000:8000 -p 8501:8501 -e MODEL_PATH=./models/mistral-7b-instruct private-ai-chatbot
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