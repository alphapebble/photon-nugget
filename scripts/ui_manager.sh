#!/bin/bash
# UI management script

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Function to start the UI
start_ui() {
    local ui_port=${1:-8502}
    local ui_mode=${2:-main}

    print_header "Starting Solar Sage UI"

    # Check if UI is already running on the specified port
    if check_port $ui_port; then
        print_warning "Port $ui_port is already in use."
        print_info "Use './scripts/ui_manager.sh stop $ui_port' to stop it first."
        return 1
    else
        print_info "Starting UI in $ui_mode mode on port $ui_port..."

        # Make sure Python path is set correctly
        set_python_path

        # Start the UI using the run_ui.py script
        if [ -f "scripts/run_ui.py" ]; then
            print_info "Using run_ui.py script"
            python scripts/run_ui.py &
        else
            print_error "Could not find scripts/run_ui.py. Please check your project structure."
            return 1
        fi
        UI_PID=$!

        # Wait for the UI to start
        print_info "Waiting for UI to start..."
        for i in {1..15}; do
            if check_port $ui_port; then
                print_success "UI started successfully on port $ui_port (PID: $UI_PID)!"
                print_info "Access the UI at http://localhost:$ui_port"
                return 0
            fi
            if [ $i -eq 15 ]; then
                print_error "Failed to start UI. Check logs for errors."
                return 1
            fi
            sleep 1
        done
    fi
}

# Function to stop the UI
stop_ui() {
    local ui_port=${1:-8502}
    local force=${2:-false}

    print_header "Stopping Solar Sage UI"

    if check_port $ui_port; then
        print_info "UI is running on port $ui_port. Stopping it..."
        kill_process_on_port $ui_port $force
        return $?
    else
        print_info "No UI running on port $ui_port."
        return 0
    fi
}

# Function to restart the UI
restart_ui() {
    local ui_port=${1:-8502}
    local ui_mode=${2:-main}
    local force=${3:-false}

    print_header "Restarting Solar Sage UI"

    # Stop the UI
    stop_ui $ui_port $force

    # Wait a moment
    sleep 2

    # Start the UI
    start_ui $ui_port $ui_mode

    return $?
}

# Function to check the UI status
status_ui() {
    local ui_port=${1:-8502}

    print_header "Solar Sage UI Status"

    if check_port $ui_port; then
        local pid=$(get_pid_on_port $ui_port)
        print_success "UI is running on port $ui_port (PID: $pid)."
        print_info "Access the UI at http://localhost:$ui_port"
        return 0
    else
        print_warning "UI is not running on port $ui_port."
        return 1
    fi
}

# Function to find an available port
find_available_port() {
    local start_port=${1:-8502}
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
    local ui_port=${2:-8502}
    local ui_mode=${3:-main}
    local force=false

    if [ "$4" = "--force" ] || [ "$3" = "--force" ]; then
        force=true
    fi

    case $command in
        start)
            start_ui $ui_port $ui_mode
            ;;
        stop)
            stop_ui $ui_port $force
            ;;
        restart)
            restart_ui $ui_port $ui_mode $force
            ;;
        status)
            status_ui $ui_port
            ;;
        *)
            echo "Usage: $0 [start|stop|restart|status] [port] [mode] [--force]"
            echo ""
            echo "Commands:"
            echo "  start       Start the UI"
            echo "  stop        Stop the UI"
            echo "  restart     Restart the UI"
            echo "  status      Check the UI status"
            echo ""
            echo "Options:"
            echo "  port        Port to run the UI on (default: 8502)"
            echo "  mode        UI mode to run (main or evaluation, default: main)"
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
