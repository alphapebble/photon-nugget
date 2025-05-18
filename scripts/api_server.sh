#!/bin/bash
# API server management script

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Function to start the API server
start_api() {
    local api_port=${1:-8000}
    print_header "Starting Solar Sage API Server"

    # Check if API is already running
    if check_port $api_port; then
        print_warning "API server is already running on port $api_port."
        print_info "Use './scripts/api_server.sh stop $api_port' to stop it first."
        return 1
    else
        print_info "Starting API server on port $api_port..."

        # Make sure Python path is set correctly
        set_python_path

        # Use the new run_api.py script
        if [ -f "scripts/run_api.py" ]; then
            print_info "Using run_api.py script"

            # Run the API server
            python scripts/run_api.py &

            # Store the PID
            API_PID=$!
        else
            print_error "Could not find scripts/run_api.py. Please check your project structure."
            return 1
        fi

        # Wait for the API to start
        print_info "Waiting for API server to start..."
        for i in {1..15}; do
            if check_port $api_port; then
                print_success "API server started successfully on port $api_port (PID: $API_PID)!"
                return 0
            fi
            if [ $i -eq 15 ]; then
                print_error "Failed to start API server. Check logs for errors."
                return 1
            fi
            sleep 1
        done
    fi
}

# Function to stop the API server
stop_api() {
    local api_port=${1:-8000}
    local force=${2:-false}

    print_header "Stopping Solar Sage API Server"

    if check_port $api_port; then
        print_info "API server is running on port $api_port. Stopping it..."
        kill_process_on_port $api_port $force
        return $?
    else
        print_info "No API server running on port $api_port."
        return 0
    fi
}

# Function to restart the API server
restart_api() {
    local api_port=${1:-8000}
    local force=${2:-false}

    print_header "Restarting Solar Sage API Server"

    # Stop the API server
    stop_api $api_port $force

    # Wait a moment
    sleep 2

    # Start the API server
    start_api $api_port

    return $?
}

# Function to check the API server status
status_api() {
    local api_port=${1:-8000}

    print_header "Solar Sage API Server Status"

    if check_port $api_port; then
        local pid=$(get_pid_on_port $api_port)
        print_success "API server is running on port $api_port (PID: $pid)."
        return 0
    else
        print_warning "API server is not running on port $api_port."
        return 1
    fi
}

# Main function
main() {
    # Set Python path
    set_python_path

    # Load environment variables
    load_env

    # Parse command line arguments
    local command=${1:-status}
    local api_port=${2:-8000}
    local force=false

    if [ "$3" = "--force" ]; then
        force=true
    fi

    case $command in
        start)
            start_api $api_port
            ;;
        stop)
            stop_api $api_port $force
            ;;
        restart)
            restart_api $api_port $force
            ;;
        status)
            status_api $api_port
            ;;
        *)
            echo "Usage: $0 [start|stop|restart|status] [port] [--force]"
            echo ""
            echo "Commands:"
            echo "  start       Start the API server"
            echo "  stop        Stop the API server"
            echo "  restart     Restart the API server"
            echo "  status      Check the API server status"
            echo ""
            echo "Options:"
            echo "  port        Port to run the API server on (default: 8000)"
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
