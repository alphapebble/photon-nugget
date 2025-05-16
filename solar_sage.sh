#!/bin/bash
# Solar Sage Main Script
# This script manages all components of the Solar Sage application

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/utils.sh"

# Function to show usage information
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start       Start all components (API, Ollama, UI)"
    echo "  stop        Stop all components"
    echo "  restart     Restart all components"
    echo "  status      Show status of all components"
    echo "  kill        Kill all Solar Sage processes forcefully"
    echo "            Options: --no-ollama, --api-ports MIN-MAX, --ui-ports MIN-MAX"
    echo "  api         Manage API server (start|stop|restart|status)"
    echo "  ollama      Manage Ollama (start|stop|restart|status|pull)"
    echo "  ui          Manage UI (start|stop|restart|status)"
    echo "  download    Download a model from Hugging Face"
    echo "  help        Show this help message"
    echo ""
    echo "Options:"
    echo "  --api-port PORT     Port for the API server (default: 8000)"
    echo "  --ui-port PORT      Port for the UI (default: 8502)"
    echo "  --ui-mode MODE      UI mode (main or evaluation, default: main)"
    echo "  --model MODEL       Ollama model to use (default: llama3)"
    echo "  --force             Force kill processes if they don't stop gracefully"
    echo "  --skip-model        Skip model download and continue with startup"
    echo ""
    echo "Examples:"
    echo "  $0 start                                # Start everything with defaults"
    echo "  $0 start --api-port 8001 --ui-port 8503 # Start with custom ports"
    echo "  $0 start --skip-model                   # Start without downloading the model"
    echo "  $0 start --model llama3 --force         # Force re-download of the model"
    echo "  $0 api start 8000                       # Start only the API server on port 8000"
    echo "  $0 ollama pull llama3                   # Pull the llama3 model"
    echo "  $0 ui start 8502 main                   # Start only the UI in main mode"
    echo "  $0 download mistralai/Mistral-7B-Instruct-v0.2 models/mistral-7b"
    echo ""
    echo "Note: Hugging Face models are stored in the 'models' directory at the project root."
}

# Function to start all components
start_all() {
    local api_port=$1
    local ui_port=$2
    local ui_mode=$3
    local model=$4

    print_header "Starting Solar Sage"

    # Start Ollama
    "$SCRIPT_DIR/scripts/ollama_manager.sh" start

    # Pull the model (unless skip_model flag is set)
    if [ "$skip_model" = "true" ]; then
        print_warning "Skipping model download as requested with --skip-model flag."
        print_info "Some features may not work properly without the model."
    else
        # Pull the model (pass force flag if present)
        if [ "$force" = "true" ]; then
            "$SCRIPT_DIR/scripts/ollama_manager.sh" pull $model --force
        else
            "$SCRIPT_DIR/scripts/ollama_manager.sh" pull $model
        fi
    fi

    # Start the API server
    "$SCRIPT_DIR/scripts/api_server.sh" start $api_port

    # Start the UI
    "$SCRIPT_DIR/scripts/ui_manager.sh" start $ui_port $ui_mode

    print_success "Solar Sage started successfully!"
}

# Function to stop all components
stop_all() {
    local api_port=$1
    local ui_port=$2
    local force=$3

    print_header "Stopping Solar Sage"

    # Stop the UI
    "$SCRIPT_DIR/scripts/ui_manager.sh" stop $ui_port $force

    # Stop the API server
    "$SCRIPT_DIR/scripts/api_server.sh" stop $api_port $force

    # Stop Ollama
    "$SCRIPT_DIR/scripts/ollama_manager.sh" stop $force

    print_success "Solar Sage stopped successfully!"
}

# Function to restart all components
restart_all() {
    local api_port=$1
    local ui_port=$2
    local ui_mode=$3
    local model=$4
    local force=$5

    print_header "Restarting Solar Sage"

    # Stop all components
    stop_all $api_port $ui_port $force

    # Wait a moment
    sleep 2

    # Start all components
    start_all $api_port $ui_port $ui_mode $model
}

# Function to show status of all components
status_all() {
    local api_port=$1
    local ui_port=$2

    print_header "Solar Sage Status"

    # Check Ollama status
    "$SCRIPT_DIR/scripts/ollama_manager.sh" status

    # Check API server status
    "$SCRIPT_DIR/scripts/api_server.sh" status $api_port

    # Check UI status
    "$SCRIPT_DIR/scripts/ui_manager.sh" status $ui_port
}

# Main function
main() {
    # Set Python path
    set_python_path

    # Load environment variables
    load_env

    # Default values from environment variables or fallbacks
    local api_port=${SOLAR_SAGE_API_PORT:-8000}
    local ui_port=${SOLAR_SAGE_UI_PORT:-8502}
    local ui_mode="main"
    local model=${SOLAR_SAGE_LLM_MODEL:-"llama3"}
    local force=false
    local skip_model=false

    # Parse command line arguments
    local command=${1:-help}
    shift || true

    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --api-port)
                api_port="$2"
                shift 2
                ;;
            --ui-port)
                ui_port="$2"
                shift 2
                ;;
            --ui-mode)
                ui_mode="$2"
                shift 2
                ;;
            --model)
                model="$2"
                shift 2
                ;;
            --force)
                force=true
                shift
                ;;
            --skip-model)
                skip_model=true
                shift
                ;;
            *)
                # Save remaining arguments
                remaining_args+=("$1")
                shift
                ;;
        esac
    done

    # Process commands
    case $command in
        start)
            start_all $api_port $ui_port $ui_mode $model
            ;;
        stop)
            stop_all $api_port $ui_port $force
            ;;
        restart)
            restart_all $api_port $ui_port $ui_mode $model $force
            ;;
        status)
            status_all $api_port $ui_port
            ;;
        kill)
            # Pass any remaining arguments to the kill_all.sh script
            "$SCRIPT_DIR/scripts/kill_all.sh" "${remaining_args[@]}"
            ;;
        api)
            "$SCRIPT_DIR/scripts/api_server.sh" "${remaining_args[@]}"
            ;;
        ollama)
            "$SCRIPT_DIR/scripts/ollama_manager.sh" "${remaining_args[@]}"
            ;;
        ui)
            "$SCRIPT_DIR/scripts/ui_manager.sh" "${remaining_args[@]}"
            ;;
        download)
            "$SCRIPT_DIR/scripts/download_hf.sh" "${remaining_args[@]}"
            ;;
        help)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac

    exit $?
}

# Run the main function
main "$@"
