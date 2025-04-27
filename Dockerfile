# Base Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and models
COPY app/ ui/ retriever/ ingestion/ model/ models/ ./

# Set transformers offline
ENV TRANSFORMERS_OFFLINE=1

# Expose ports (FastAPI backend and Gradio frontend)
EXPOSE 8000
EXPOSE 8501

# Default command to run (uvicorn + gradio app separately)
CMD ["bash", "-c", "uvicorn app.server:app --host 0.0.0.0 --port 8000 & python ui/app.py"]