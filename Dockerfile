# Base Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY ui/ ./ui/
COPY retriever.py .
COPY chatbot_engine.py .

# Copy pre-downloaded models
COPY models/ ./models/

# Set environment to offline for transformers
ENV TRANSFORMERS_OFFLINE=1

# Expose ports (FastAPI backend and Gradio frontend)
EXPOSE 8000
EXPOSE 8501

# Default command to run (uvicorn + gradio app separately)
CMD ["bash", "-c", "uvicorn app.server:app --host 0.0.0.0 --port 8000 & python ui/app.py"]