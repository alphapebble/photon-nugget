#!/bin/bash

MODEL_NAME="${1:-mistral}"  # default to 'mistral' if not passed

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
  echo "Ollama is not installed. Install it from https://ollama.com/download"
  exit 1
fi

# Pull model if not already pulled
echo "Checking if '$MODEL_NAME' model is available..."
if ! ollama list | grep -q "$MODEL_NAME"; then
  echo "Pulling model: $MODEL_NAME"
  ollama pull "$MODEL_NAME"
else
  echo "Model '$MODEL_NAME' already present."
fi

# Start Ollama server
echo "Starting Ollama server..."
ollama serve
