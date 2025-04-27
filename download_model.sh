#!/bin/bash

set -e

# Check if huggingface_hub is installed
if ! pip show huggingface_hub > /dev/null 2>&1; then
  echo "Installing huggingface_hub..."
  pip install huggingface_hub
fi

# Check if HF token is set
if [ -z "$HF_TOKEN" ]; then
  echo "Error: Huggingface token not set. Please run 'export HF_TOKEN=your_token_here'"
  exit 1
fi

# Login using token
echo "Logging into Huggingface using environment token..."
huggingface-cli login --token "$HF_TOKEN"

# Inputs
MODEL_REPO=$1
LOCAL_DIR=$2

# Check inputs
if [ -z "$MODEL_REPO" ] || [ -z "$LOCAL_DIR" ]; then
  echo "Usage: bash download_model.sh <model_repo> <local_dir>"
  echo "Example: bash download_model.sh mistralai/Mistral-7B-Instruct-v0.2 models/mistral-7b-instruct"
  exit 1
fi

# Create local dir if not exists
mkdir -p "$LOCAL_DIR"

# Download using huggingface-cli
echo "Downloading model $MODEL_REPO into $LOCAL_DIR ..."
huggingface-cli download "$MODEL_REPO" --local-dir "$LOCAL_DIR" --local-dir-use-symlinks False --resume-download

echo "✅ Download completed successfully!"
echo "Files are stored in: $LOCAL_DIR"
