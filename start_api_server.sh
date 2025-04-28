#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    set -o allexport
    source .env
    set +o allexport
else
    echo ".env file not found. Skipping environment variable loading."
fi

# Start the API server
python -m app.server
