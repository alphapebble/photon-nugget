# Shell Commands Reference

This document provides a comprehensive reference for all shell commands available in the Solar Sage project. It serves as the single source of truth for command-line operations.

## Main Script: solar_sage.sh

The `solar_sage.sh` script is the main entry point for managing the Solar Sage system. It provides commands for starting, stopping, and managing all components.

### Basic Usage

```bash
./solar_sage.sh [COMMAND] [OPTIONS]
```

### Available Commands

| Command    | Description                                            |
| ---------- | ------------------------------------------------------ |
| `start`    | Start all components (API, Ollama, UI, Next.js)        |
| `stop`     | Stop all components                                    |
| `restart`  | Restart all components                                 |
| `status`   | Show status of all components                          |
| `kill`     | Kill all Solar Sage processes forcefully               |
| `api`      | Manage API server (start\|stop\|restart\|status)       |
| `ollama`   | Manage Ollama (start\|stop\|restart\|status\|pull)     |
| `ui`       | Manage Gradio UI (start\|stop\|restart\|status)        |
| `next`     | Manage Next.js frontend (start\|stop\|restart\|status) |
| `download` | Download a model from Hugging Face                     |
| `help`     | Show help message                                      |

### Global Options

| Option            | Description                                        |
| ----------------- | -------------------------------------------------- |
| `--api-port PORT` | Port for the API server (default: 8000)            |
| `--ui-port PORT`  | Port for the Gradio UI (default: 7860)             |
| `--next-port PORT`| Port for the Next.js frontend (default: 3000)      |
| `--model MODEL`   | Ollama model to use (default: llama3)              |
| `--force`         | Force kill processes if they don't stop gracefully |
| `--skip-model`    | Skip model download and continue with startup      |

## API Server Commands

Commands for managing the API server.

### Starting the API Server

```bash
# Start the API server on the default port (8000)
./solar_sage.sh api start

# Start the API server on a specific port
./solar_sage.sh api start 8000
```

### Stopping the API Server

```bash
# Stop the API server on the default port
./solar_sage.sh api stop

# Stop the API server on a specific port
./solar_sage.sh api stop 8000

# Force stop the API server
./solar_sage.sh api stop 8000 --force
```

### Checking API Server Status

```bash
# Check the status of the API server on the default port
./solar_sage.sh api status

# Check the status of the API server on a specific port
./solar_sage.sh api status 8000
```

## Gradio UI Commands

Commands for managing the Gradio UI.

### Starting the Gradio UI

```bash
# Start the Gradio UI on the default port (7860)
./solar_sage.sh ui start

# Start the Gradio UI on a specific port
./solar_sage.sh ui start 7860
```

### Stopping the Gradio UI

```bash
# Stop the Gradio UI on the default port
./solar_sage.sh ui stop

# Stop the Gradio UI on a specific port
./solar_sage.sh ui stop 7860

# Force stop the Gradio UI
./solar_sage.sh ui stop 7860 --force
```

### Checking Gradio UI Status

```bash
# Check the status of the Gradio UI on the default port
./solar_sage.sh ui status

# Check the status of the Gradio UI on a specific port
./solar_sage.sh ui status 7860
```

## Next.js Frontend Commands

Commands for managing the Next.js frontend.

### Starting the Next.js Frontend

```bash
# Start the Next.js frontend on the default port (3000)
./solar_sage.sh next start

# Start the Next.js frontend on a specific port
./solar_sage.sh next start 3000
```

### Stopping the Next.js Frontend

```bash
# Stop the Next.js frontend on the default port
./solar_sage.sh next stop

# Stop the Next.js frontend on a specific port
./solar_sage.sh next stop 3000

# Force stop the Next.js frontend
./solar_sage.sh next stop 3000 --force
```

### Checking Next.js Frontend Status

```bash
# Check the status of the Next.js frontend on the default port
./solar_sage.sh next status

# Check the status of the Next.js frontend on a specific port
./solar_sage.sh next status 3000
```

## Ollama Commands

Commands for managing Ollama.

### Starting Ollama

```bash
# Start Ollama
./solar_sage.sh ollama start
```

### Stopping Ollama

```bash
# Stop Ollama
./solar_sage.sh ollama stop

# Force stop Ollama
./solar_sage.sh ollama stop --force
```

### Pulling Ollama Models

```bash
# Pull the default model (llama3)
./solar_sage.sh ollama pull

# Pull a specific model
./solar_sage.sh ollama pull mistral

# Force re-pull a model
./solar_sage.sh ollama pull mistral --force
```

## System Management Commands

Commands for managing the entire system.

### Starting All Components

```bash
# Start all components with default settings
./solar_sage.sh start

# Start with custom ports
./solar_sage.sh start --api-port 8000 --ui-port 7860 --next-port 3000

# Start without downloading the model
./solar_sage.sh start --skip-model

# Start with a specific model
./solar_sage.sh start --model mistral
```

### Stopping All Components

```bash
# Stop all components
./solar_sage.sh stop

# Force stop all components
./solar_sage.sh stop --force
```

### Killing All Processes

```bash
# Kill all Solar Sage processes
./solar_sage.sh kill

# Kill all processes except Ollama
./solar_sage.sh kill --no-ollama
```

## Model Management Commands

Commands for managing models.

### Downloading Hugging Face Models

```bash
# Download a model from Hugging Face
./solar_sage.sh download mistralai/Mistral-7B-Instruct-v0.2 models/mistral-7b
```

## API Testing Commands

Commands for testing the API.

### Testing the API Server

```bash
# Test the API server is running
curl -X GET http://localhost:8000/
```

### Testing the Sage Endpoint

```bash
# Test the sage endpoint with a basic query
curl -X POST http://localhost:8000/sage \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about solar panels"}'

# Test the sage endpoint with weather data
curl -X POST http://localhost:8000/sage \
  -H "Content-Type: application/json" \
  -d '{"query": "How will weather affect my solar production?", "lat": 37.7749, "lon": -122.4194, "include_weather": true}'
```

## Access URLs

This section provides a comprehensive list of all access URLs for the Solar Sage system.

### API Server

- **API Root**: http://localhost:8000/
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Next.js Frontend

- **Main UI**: http://localhost:3000
- **Chat Interface**: http://localhost:3000/chat
- **Solar Forecast**: http://localhost:3000/solar-forecast
- **Evaluation Dashboard**: http://localhost:3000/evaluation
- **About Page**: http://localhost:3000/about

### Gradio UI

- **Main UI**: http://localhost:7860
- **Evaluation Dashboard**: http://localhost:7860/?view=evaluation

### Ollama

- **Ollama API**: http://localhost:11434

## Log Files

This section provides information about log files for the Solar Sage system.

### API Server Logs

```bash
# View API server logs
cat logs/api_server.log
```

### Gradio UI Logs

```bash
# View Gradio UI logs
cat logs/ui_server.log
```

### Next.js Frontend Logs

```bash
# View Next.js frontend logs
cat logs/next.log
```

### API Client Logs

```bash
# View API client logs
cat logs/api_client.log
```
