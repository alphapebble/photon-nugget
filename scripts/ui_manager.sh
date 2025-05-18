#!/bin/bash
# Gradio UI management script

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Function to start the Gradio UI
start_ui() {
    local ui_port=${1:-7860}

    print_header "Starting Solar Sage Conversational UI"

    # Check if UI is already running on the specified port
    if check_port $ui_port; then
        print_warning "Port $ui_port is already in use."
        print_info "Use './scripts/ui_manager.sh stop $ui_port' to stop it first."
        return 1
    else
        print_info "Starting Conversational UI on port $ui_port..."

        # Make sure Python path is set correctly
        set_python_path

        # Create logs directory if it doesn't exist
        mkdir -p "$(dirname "$SCRIPT_DIR")/logs"

        # Start the UI using the run_ui.py script
        if [ -f "scripts/run_ui.py" ]; then
            print_info "Using run_ui.py script"
            # Set environment variables for the UI
            export SOLAR_SAGE_UI_PORT=$ui_port

            # Run the UI script and redirect output to log file
            python scripts/run_ui.py > "$(dirname "$SCRIPT_DIR")/logs/gradio_ui.log" 2>&1 &
        else
            print_error "Could not find scripts/run_ui.py. Please check your project structure."
            return 1
        fi
        UI_PID=$!

        # Wait for the UI to start
        print_info "Waiting for Conversational UI to start..."
        for i in {1..15}; do
            if check_port $ui_port; then
                print_success "Conversational UI started successfully on port $ui_port (PID: $UI_PID)!"
                print_info "Access the Conversational UI at http://localhost:$ui_port"
                return 0
            fi
            if [ $i -eq 15 ]; then
                print_error "Failed to start Conversational UI. Check logs/gradio_ui.log for errors."
                return 1
            fi
            sleep 1
        done
    fi
}

# Function to stop the Gradio UI
stop_ui() {
    local ui_port=${1:-7860}
    local force=${2:-false}

    print_header "Stopping Solar Sage Conversational UI"

    if check_port $ui_port; then
        print_info "Conversational UI is running on port $ui_port. Stopping it..."
        kill_process_on_port $ui_port $force
        return $?
    else
        print_info "No Conversational UI running on port $ui_port."
        return 0
    fi
}

# Function to restart the Gradio UI
restart_ui() {
    local ui_port=${1:-7860}
    local force=${2:-false}

    print_header "Restarting Solar Sage Conversational UI"

    # Stop the UI
    stop_ui $ui_port $force

    # Wait a moment
    sleep 2

    # Start the UI
    start_ui $ui_port

    return $?
}

# Function to check the Gradio UI status
status_ui() {
    local ui_port=${1:-7860}

    print_header "Solar Sage Conversational UI Status"

    if check_port $ui_port; then
        local pid=$(get_pid_on_port $ui_port)
        print_success "Conversational UI is running on port $ui_port (PID: $pid)."
        print_info "Access the Conversational UI at http://localhost:$ui_port"
        return 0
    else
        print_warning "Conversational UI is not running on port $ui_port."
        return 1
    fi
}

# Function to find an available port
find_available_port() {
    local start_port=${1:-7860}
    local max_attempts=${2:-10}

    local port=$start_port

    for i in $(seq 1 $max_attempts); do
        if ! check_port $port; then
            echo $port
            return 0
        fi
        port=$((port + 1))
    done

    echo -1
    return 1
}

# Main function
main() {
    # Set Python path
    set_python_path

    # Parse command line arguments
    local command=${1:-status}
    local ui_port=${2:-7860}
    local force=false

    if [ "$3" = "--force" ]; then
        force=true
    fi

    case $command in
        start)
            start_ui $ui_port
            ;;
        stop)
            stop_ui $ui_port $force
            ;;
        restart)
            restart_ui $ui_port $force
            ;;
        status)
            status_ui $ui_port
            ;;
        *)
            echo "Usage: $0 [start|stop|restart|status] [port] [--force]"
            echo ""
            echo "Commands:"
            echo "  start       Start the Conversational UI"
            echo "  stop        Stop the Conversational UI"
            echo "  restart     Restart the Conversational UI"
            echo "  status      Check the Conversational UI status"
            echo ""
            echo "Options:"
            echo "  port        Port to run the Conversational UI on (default: 7860)"
            echo "  --force     Force kill the process if it doesn't stop gracefully"
            exit 1
            ;;
    esac

    exit $?
}

# Run the main function if the script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
