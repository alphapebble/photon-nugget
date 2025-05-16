#!/bin/bash
# Ollama management script

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Function to check if a model is available in Ollama
check_model_available() {
    local model=$1

    if command_exists curl; then
        local response=$(curl -s http://localhost:11434/api/tags)
        if echo $response | grep -q "\"name\":\"$model\""; then
            return 0
        else
            return 1
        fi
    else
        print_warning "Cannot check model availability. Install curl for better model checking."
        return 1
    fi
}

# Function to start Ollama
start_ollama() {
    print_header "Starting Ollama"

    # Check if Ollama is already running
    if check_ollama; then
        print_success "Ollama is already running."
        return 0
    else
        print_info "Ollama is not running. Starting Ollama..."

        # Start Ollama
        if command_exists ollama; then
            ollama serve &
            OLLAMA_PID=$!

            # Wait for Ollama to start
            print_info "Waiting for Ollama to start..."
            for i in {1..15}; do
                if check_ollama; then
                    print_success "Ollama started successfully (PID: $OLLAMA_PID)!"
                    return 0
                fi
                if [ $i -eq 15 ]; then
                    print_error "Failed to start Ollama. Please start it manually."
                    return 1
                fi
                sleep 1
            done
        else
            print_error "Ollama is not installed. Please install Ollama first."
            print_info "Visit https://ollama.ai/download for installation instructions."
            return 1
        fi
    fi
}

# Function to stop Ollama
stop_ollama() {
    local force=${1:-false}

    print_header "Stopping Ollama"

    kill_ollama $force
    return $?
}

# Function to restart Ollama
restart_ollama() {
    local force=${1:-false}

    print_header "Restarting Ollama"

    # Stop Ollama
    stop_ollama $force

    # Wait a moment
    sleep 2

    # Start Ollama
    start_ollama

    return $?
}

# Function to check Ollama status
status_ollama() {
    print_header "Ollama Status"

    if check_ollama; then
        local pid=$(pgrep -f "ollama serve")
        print_success "Ollama is running (PID: $pid)."

        # List available models
        if command_exists curl; then
            print_info "Available models:"
            curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | while read -r model; do
                echo "  - $model"
            done
        fi

        return 0
    else
        print_warning "Ollama is not running."
        return 1
    fi
}

# Function to pull a model
pull_model() {
    local model=${1:-llama3}
    local force=${2:-false}

    print_header "Checking Ollama Model: $model"

    # Check if Ollama is running
    if ! check_ollama; then
        print_error "Ollama is not running. Start it first with './scripts/ollama_manager.sh start'"
        return 1
    fi

    # Check if the model is already available
    if check_model_available $model && [ "$force" != "true" ]; then
        print_success "Model '$model' is already available. No need to download again."
        print_info "Use --force flag to re-download the model if needed."
        return 0
    else
        if [ "$force" = "true" ]; then
            print_info "Force flag detected. Re-downloading model '$model'..."
        else
            print_info "Model '$model' is not available. Downloading model..."
        fi

        # Check if a download is already in progress
        local download_pid=$(pgrep -f "ollama pull $model")
        if [ -n "$download_pid" ]; then
            print_warning "A download for model '$model' is already in progress (PID: $download_pid)."
            print_info "You can either:"
            print_info "1. Wait for the download to complete"
            print_info "2. Kill the download process with 'kill $download_pid' and try again"
            print_info "3. Use --skip-model flag to skip model download and continue"

            # Ask if the user wants to continue without the model
            read -p "Do you want to continue without waiting for the model? (y/n): " skip_model
            if [[ "$skip_model" =~ ^[Yy]$ ]]; then
                print_warning "Continuing without model '$model'. Some features may not work properly."
                return 0
            else
                print_info "Waiting for model download to complete..."
                # Wait for the download to complete
                while kill -0 $download_pid 2>/dev/null; do
                    sleep 5
                    echo -n "."
                done
                echo ""
                if check_model_available $model; then
                    print_success "Model '$model' is now available and ready to use!"
                    return 0
                else
                    print_error "Model download seems to have failed. Please try again."
                    return 1
                fi
            fi
        fi

        # Pull the model
        if command_exists ollama; then
            # Show a message about the download process
            print_info "This may take several minutes depending on your internet connection."
            print_info "The model will be downloaded only once and cached for future use."
            print_info "You can press Ctrl+C to cancel the download and continue without the model."
            print_info "To resume the download later, run './solar_sage.sh ollama pull $model'"

            # Pull the model
            ollama pull $model

            # Check if the model was pulled successfully
            if check_model_available $model; then
                print_success "Model '$model' is now available and ready to use!"
                return 0
            else
                print_error "Failed to pull model '$model'. Please pull it manually."
                print_info "Run 'ollama pull $model' to pull the model."
                return 1
            fi
        else
            print_error "Ollama is not installed. Please install Ollama first."
            print_info "Visit https://ollama.ai/download for installation instructions."
            return 1
        fi
    fi
}

# Main function
main() {
    # Parse command line arguments
    local command=${1:-status}
    local model=${2:-llama3}
    local force=false

    if [ "$3" = "--force" ] || [ "$2" = "--force" ]; then
        force=true
        # If --force is the second argument, use default model
        if [ "$2" = "--force" ]; then
            model="llama3"
        fi
    fi

    case $command in
        start)
            start_ollama
            ;;
        stop)
            stop_ollama $force
            ;;
        restart)
            restart_ollama $force
            ;;
        status)
            status_ollama
            ;;
        pull)
            pull_model $model $force
            ;;
        *)
            echo "Usage: $0 [start|stop|restart|status|pull] [model|--force] [--force]"
            echo ""
            echo "Commands:"
            echo "  start       Start Ollama"
            echo "  stop        Stop Ollama"
            echo "  restart     Restart Ollama"
            echo "  status      Check Ollama status"
            echo "  pull        Pull a model"
            echo ""
            echo "Options:"
            echo "  model       Model to pull (default: llama3)"
            echo "  --force     Force kill processes or re-download models even if already available"
            exit 1
            ;;
    esac

    exit $?
}

# Run the main function if the script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
