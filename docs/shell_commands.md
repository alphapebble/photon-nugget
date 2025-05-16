# Solar Sage Shell Commands

This document provides a reference for all the shell commands available in the Solar Sage project.

## Main Commands

The `solar_sage.sh` script is the main entry point for managing the Solar Sage system. It provides commands for starting, stopping, and managing all components.

### Basic Usage

```bash
./solar_sage.sh [COMMAND] [OPTIONS]
```

### Available Commands

| Command | Description |
|---------|-------------|
| `start` | Start all components (API, Ollama, UI) |
| `stop` | Stop all components |
| `restart` | Restart all components |
| `status` | Show status of all components |
| `kill` | Kill all Solar Sage processes forcefully |
| `api` | Manage API server (start\|stop\|restart\|status) |
| `ollama` | Manage Ollama (start\|stop\|restart\|status\|pull) |
| `ui` | Manage UI (start\|stop\|restart\|status) |
| `download` | Download a model from Hugging Face |
| `help` | Show help message |

### Options

| Option | Description |
|--------|-------------|
| `--api-port PORT` | Port for the API server (default: 8000) |
| `--ui-port PORT` | Port for the UI (default: 8502) |
| `--ui-mode MODE` | UI mode (main or evaluation, default: main) |
| `--model MODEL` | Ollama model to use (default: llama3) |
| `--force` | Force kill processes if they don't stop gracefully |
| `--skip-model` | Skip model download and continue with startup |

## Examples

### Starting the System

Start all components with default settings:
```bash
./solar_sage.sh start
```

Start with custom ports:
```bash
./solar_sage.sh start --api-port 8001 --ui-port 8503
```

Start without downloading the model:
```bash
./solar_sage.sh start --skip-model
```

Force re-download of the model:
```bash
./solar_sage.sh start --model llama3 --force
```

### Managing Individual Components

Start only the API server:
```bash
./solar_sage.sh api start 8000
```

Pull the llama3 model:
```bash
./solar_sage.sh ollama pull llama3
```

Start only the UI:
```bash
./solar_sage.sh ui start 8502 main
```

Download a Hugging Face model:
```bash
./solar_sage.sh download mistralai/Mistral-7B-Instruct-v0.2 models/mistral-7b
```

### Stopping Components

Stop all components:
```bash
./solar_sage.sh stop
```

Stop only the API server:
```bash
./solar_sage.sh api stop 8000
```

Stop only the UI:
```bash
./solar_sage.sh ui stop 8502
```

### Checking Status

Check status of all components:
```bash
./solar_sage.sh status
```

Check status of the API server:
```bash
./solar_sage.sh api status 8000
```

Check status of the UI:
```bash
./solar_sage.sh ui status 8502
```

Check status of Ollama:
```bash
./solar_sage.sh ollama status
```

## API Testing Commands

You can test the API directly using curl commands:

Test the API server is running:
```bash
curl -X GET http://localhost:8000/
```

Test the chat endpoint with a basic query:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about solar panels"}'
```

Test the chat endpoint with weather data:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How will weather affect my solar production?", "lat": 37.7749, "lon": -122.4194, "include_weather": true}'
```

Verbose output for debugging:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about solar panels"}' -v
```

## Accessing the UI

The main UI is available at:
```
http://localhost:8502
```

The evaluation dashboard is available at:
```
http://localhost:8502/?mode=evaluation
```

You can switch between the main UI and the evaluation dashboard using the links in the header.

## Checking Logs

Check the API server logs:
```bash
cat logs/api_server.log
```

Check the UI server logs:
```bash
cat logs/ui_server.log
```

Check the API client logs:
```bash
cat logs/api_client.log
```
