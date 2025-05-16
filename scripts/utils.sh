#!/bin/bash
# Utility functions for Solar Sage scripts

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a process is running on a specific port
check_port() {
    local port=$1
    if command_exists lsof; then
        lsof -i:$port -t >/dev/null 2>&1
        return $?
    elif command_exists netstat; then
        netstat -tuln | grep -q ":$port "
        return $?
    else
        echo -e "${YELLOW}Warning: Cannot check port $port. Install lsof or netstat for better port checking.${NC}"
        return 1
    fi
}

# Function to get the PID of a process running on a specific port
get_pid_on_port() {
    local port=$1
    if command_exists lsof; then
        lsof -i:$port -t 2>/dev/null
    elif command_exists netstat; then
        # This is less reliable but a fallback
        netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1
    fi
}

# Function to kill a process running on a specific port
kill_process_on_port() {
    local port=$1
    local force=$2

    local pid=$(get_pid_on_port $port)

    if [ -n "$pid" ]; then
        echo -e "${YELLOW}Killing process with PID $pid on port $port...${NC}"
        if [ "$force" = "true" ]; then
            kill -9 $pid 2>/dev/null
        else
            kill $pid 2>/dev/null
        fi
        sleep 1
        if ! check_port $port; then
            echo -e "${GREEN}Process on port $port successfully terminated.${NC}"
            return 0
        else
            echo -e "${RED}Failed to kill process on port $port. Try with --force option.${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}No process found running on port $port.${NC}"
        return 0
    fi
}

# Function to check if Ollama is running
check_ollama() {
    if command_exists curl; then
        curl -s http://localhost:11434/api/tags >/dev/null 2>&1
        return $?
    else
        echo -e "${YELLOW}Warning: Cannot check Ollama status. Install curl for better Ollama checking.${NC}"
        # Try to check the process instead
        pgrep -f ollama >/dev/null 2>&1
        return $?
    fi
}

# Function to kill Ollama process
kill_ollama() {
    local force=$1

    if check_ollama; then
        echo -e "${YELLOW}Stopping Ollama...${NC}"

        # Try to find the PID
        local pid=$(pgrep -f "ollama serve")

        if [ -n "$pid" ]; then
            echo -e "${YELLOW}Killing Ollama process with PID $pid...${NC}"
            if [ "$force" = "true" ]; then
                kill -9 $pid 2>/dev/null
            else
                kill $pid 2>/dev/null
            fi

            # Wait for process to terminate
            for i in {1..5}; do
                if ! check_ollama; then
                    echo -e "${GREEN}Ollama successfully terminated.${NC}"
                    return 0
                fi
                sleep 1
            done

            echo -e "${RED}Failed to kill Ollama. Try with --force option.${NC}"
            return 1
        else
            echo -e "${RED}Could not find Ollama process ID.${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}Ollama is not running.${NC}"
        return 0
    fi
}

# Function to load environment variables
load_env() {
    if [ -f .env ]; then
        echo -e "${BLUE}Loading environment variables from .env...${NC}"
        set -o allexport
        source .env
        set +o allexport
    else
        echo -e "${YELLOW}.env file not found. Using default environment variables.${NC}"
    fi

    # Set default values for environment variables if not already set
    export SOLAR_SAGE_MODELS_DIR=${SOLAR_SAGE_MODELS_DIR:-"./models"}
    export SOLAR_SAGE_DATA_DIR=${SOLAR_SAGE_DATA_DIR:-"./data"}
    export SOLAR_SAGE_VECTOR_DB_PATH=${SOLAR_SAGE_VECTOR_DB_PATH:-"./data/lancedb"}
    export SOLAR_SAGE_API_PORT=${SOLAR_SAGE_API_PORT:-8000}
    export SOLAR_SAGE_UI_PORT=${SOLAR_SAGE_UI_PORT:-8502}
    export SOLAR_SAGE_LLM_MODEL=${SOLAR_SAGE_LLM_MODEL:-"mistral-7b-instruct"}

    # Create necessary directories if they don't exist
    mkdir -p "${SOLAR_SAGE_MODELS_DIR}"
    mkdir -p "${SOLAR_SAGE_DATA_DIR}"
    mkdir -p "${SOLAR_SAGE_VECTOR_DB_PATH}"

    print_info "Using models directory: ${SOLAR_SAGE_MODELS_DIR}"

    return 0
}

# Function to set Python path and activate virtual environment
set_python_path() {
    # Get the project root directory
    local project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    # Clear any existing PYTHONPATH to avoid duplication
    unset PYTHONPATH

    # Set PYTHONPATH to include both the project root and src directory
    # This allows imports to work from both the root level and within src
    export PYTHONPATH="${project_root}:${project_root}/src"

    echo -e "${BLUE}Python path set to: ${PYTHONPATH}${NC}"

    # Activate virtual environment if it exists
    activate_venv
}

# Function to activate virtual environment
activate_venv() {
    local project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    # Check for different possible virtual environment locations
    if [ -f "${project_root}/venv/bin/activate" ]; then
        echo -e "${BLUE}Activating virtual environment from ${project_root}/venv${NC}"
        source "${project_root}/venv/bin/activate"
    elif [ -f "${project_root}/.venv/bin/activate" ]; then
        echo -e "${BLUE}Activating virtual environment from ${project_root}/.venv${NC}"
        source "${project_root}/.venv/bin/activate"
    elif [ -f "${project_root}/env/bin/activate" ]; then
        echo -e "${BLUE}Activating virtual environment from ${project_root}/env${NC}"
        source "${project_root}/env/bin/activate"
    else
        echo -e "${YELLOW}No virtual environment found. Using system Python.${NC}"
    fi
}

# Function to print a section header
print_header() {
    local title=$1
    echo -e "\n${BLUE}=== $title ===${NC}"
}

# Function to print a success message
print_success() {
    local message=$1
    echo -e "${GREEN}✅ $message${NC}"
}

# Function to print an error message
print_error() {
    local message=$1
    echo -e "${RED}❌ $message${NC}"
}

# Function to print a warning message
print_warning() {
    local message=$1
    echo -e "${YELLOW}⚠️ $message${NC}"
}

# Function to print an info message
print_info() {
    local message=$1
    echo -e "${BLUE}ℹ️ $message${NC}"
}

# Export all functions
export -f command_exists
export -f check_port
export -f get_pid_on_port
export -f kill_process_on_port
export -f check_ollama
export -f kill_ollama
export -f load_env
export -f set_python_path
export -f activate_venv
export -f print_header
export -f print_success
export -f print_error
export -f print_warning
export -f print_info
