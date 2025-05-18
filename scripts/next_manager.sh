#!/bin/bash
# Next.js frontend management script

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Function to start the Next.js frontend
start_next() {
    local next_port=${1:-3000}

    print_header "Starting Solar Sage Next.js Frontend"

    # Check if Next.js is already running on the specified port
    if check_port $next_port; then
        print_warning "Port $next_port is already in use."
        print_info "Use './scripts/next_manager.sh stop $next_port' to stop it first."
        return 1
    else
        print_info "Starting Next.js frontend on port $next_port..."

        # Navigate to the frontend directory
        cd "$(dirname "$SCRIPT_DIR")/frontend" || {
            print_error "Could not navigate to frontend directory."
            return 1
        }

        # Start Next.js in development mode
        npm run dev -- -p $next_port > ../logs/next.log 2>&1 &
        NEXT_PID=$!

        # Wait for the Next.js server to start
        print_info "Waiting for Next.js to start..."
        for i in {1..15}; do
            if check_port $next_port; then
                print_success "Next.js started successfully on port $next_port (PID: $NEXT_PID)!"
                print_info "Access the frontend at http://localhost:$next_port"
                
                # Return to the original directory
                cd - > /dev/null
                return 0
            fi
            if [ $i -eq 15 ]; then
                print_error "Failed to start Next.js. Check logs/next.log for errors."
                
                # Return to the original directory
                cd - > /dev/null
                return 1
            fi
            sleep 1
        done
    fi
}

# Function to stop the Next.js frontend
stop_next() {
    local next_port=${1:-3000}
    local force=${2:-false}

    print_header "Stopping Solar Sage Next.js Frontend"

    if check_port $next_port; then
        print_info "Next.js is running on port $next_port. Stopping it..."
        kill_process_on_port $next_port $force
        return $?
    else
        print_info "No Next.js server running on port $next_port."
        return 0
    fi
}

# Function to restart the Next.js frontend
restart_next() {
    local next_port=${1:-3000}
    local force=${2:-false}

    print_header "Restarting Solar Sage Next.js Frontend"

    # Stop the Next.js server
    stop_next $next_port $force

    # Wait a moment
    sleep 2

    # Start the Next.js server
    start_next $next_port

    return $?
}

# Function to check the Next.js frontend status
status_next() {
    local next_port=${1:-3000}

    print_header "Solar Sage Next.js Frontend Status"

    if check_port $next_port; then
        local pid=$(get_pid_on_port $next_port)
        print_success "Next.js is running on port $next_port (PID: $pid)."
        print_info "Access the frontend at http://localhost:$next_port"
        return 0
    else
        print_warning "Next.js is not running on port $next_port."
        return 1
    fi
}

# Function to find an available port
find_available_port() {
    local start_port=${1:-3000}
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
    # Parse command line arguments
    local command=${1:-status}
    local next_port=${2:-3000}
    local force=false

    if [ "$3" = "--force" ]; then
        force=true
    fi

    case $command in
        start)
            start_next $next_port
            ;;
        stop)
            stop_next $next_port $force
            ;;
        restart)
            restart_next $next_port $force
            ;;
        status)
            status_next $next_port
            ;;
        *)
            echo "Usage: $0 [start|stop|restart|status] [port] [--force]"
            echo ""
            echo "Commands:"
            echo "  start       Start the Next.js frontend"
            echo "  stop        Stop the Next.js frontend"
            echo "  restart     Restart the Next.js frontend"
            echo "  status      Check the Next.js frontend status"
            echo ""
            echo "Options:"
            echo "  port        Port to run the Next.js frontend on (default: 3000)"
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
