#!/bin/bash
# Kill all Solar Sage processes

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Function to kill all Python processes related to Solar Sage
kill_all_python() {
    print_header "Killing all Python processes related to Solar Sage"

    # Find all Python processes related to Solar Sage
    local pids=$(ps aux | grep -E "python.*ui\.app|python.*src\.cli|python.*app\.server" | grep -v grep | awk '{print $2}')

    if [ -z "$pids" ]; then
        print_info "No Python processes related to Solar Sage found."
        return 0
    else
        print_warning "Found the following Python processes related to Solar Sage:"
        for pid in $pids; do
            local cmd=$(ps -p $pid -o command= 2>/dev/null)
            echo "  PID $pid: $cmd"
        done

        print_warning "Killing all Python processes related to Solar Sage..."
        for pid in $pids; do
            kill -9 $pid 2>/dev/null
            print_info "Killed process with PID $pid"
        done

        print_success "All Python processes related to Solar Sage have been killed."
        return 0
    fi
}

# Function to kill processes on specific ports
kill_ports() {
    print_header "Killing processes on specific ports"

    # Default port ranges for Solar Sage
    local api_port_range=(8000 8010)  # API ports: 8000-8010
    local ui_port_range=(8500 8520)   # UI ports: 8500-8520

    # Check for processes on API ports
    print_info "Checking API ports (${api_port_range[0]}-${api_port_range[1]})..."
    for port in $(seq ${api_port_range[0]} ${api_port_range[1]}); do
        if check_port $port; then
            local pid=$(get_pid_on_port $port)
            if [ -n "$pid" ]; then
                print_warning "Killing process with PID $pid on port $port..."
                kill -9 $pid 2>/dev/null
                sleep 1
                if ! check_port $port; then
                    print_success "Process on port $port successfully terminated."
                else
                    print_error "Failed to kill process on port $port."
                fi
            fi
        fi
    done

    # Check for processes on UI ports
    print_info "Checking UI ports (${ui_port_range[0]}-${ui_port_range[1]})..."
    for port in $(seq ${ui_port_range[0]} ${ui_port_range[1]}); do
        if check_port $port; then
            local pid=$(get_pid_on_port $port)
            if [ -n "$pid" ]; then
                print_warning "Killing process with PID $pid on port $port..."
                kill -9 $pid 2>/dev/null
                sleep 1
                if ! check_port $port; then
                    print_success "Process on port $port successfully terminated."
                else
                    print_error "Failed to kill process on port $port."
                fi
            fi
        fi
    done

    # Check for any other known ports
    local other_ports=(11434)  # Ollama API port

    print_info "Checking other known ports..."
    for port in "${other_ports[@]}"; do
        if check_port $port; then
            print_warning "Found process on port $port (likely Ollama). Not killing automatically."
        fi
    done

    return 0
}

# Function to kill Ollama
kill_ollama_process() {
    print_header "Checking Ollama"

    if check_ollama; then
        print_warning "Ollama is running. Stopping it..."
        kill_ollama true
    else
        print_info "Ollama is not running."
    fi

    return 0
}

# Main function
main() {
    print_header "Killing all Solar Sage processes"

    # Parse command line arguments
    local kill_ollama=true
    local api_min_port=8000
    local api_max_port=8010
    local ui_min_port=8500
    local ui_max_port=8520

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-ollama)
                kill_ollama=false
                shift
                ;;
            --api-ports)
                IFS='-' read -r api_min_port api_max_port <<< "$2"
                shift 2
                ;;
            --ui-ports)
                IFS='-' read -r ui_min_port ui_max_port <<< "$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --no-ollama         Don't kill Ollama"
                echo "  --api-ports MIN-MAX Port range for API servers (default: 8000-8010)"
                echo "  --ui-ports MIN-MAX  Port range for UI servers (default: 8500-8520)"
                echo "  --help              Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information."
                exit 1
                ;;
        esac
    done

    # Override the port ranges in the kill_ports function
    api_port_range=($api_min_port $api_max_port)
    ui_port_range=($ui_min_port $ui_max_port)

    # Kill all Python processes related to Solar Sage
    kill_all_python

    # Kill processes on specific ports
    kill_ports

    # Kill Ollama if requested
    if [ "$kill_ollama" = true ]; then
        kill_ollama_process
    else
        print_info "Skipping Ollama termination as requested."
    fi

    print_success "All Solar Sage processes have been killed."

    return 0
}

# Run the main function if the script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
