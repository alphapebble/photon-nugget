#!/bin/bash
# Hugging Face model download script

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Function to download a model from Hugging Face
download_hf_model() {
    local model_repo=$1
    local local_dir=$2

    # If local_dir is not an absolute path, make it relative to the project root
    if [[ "$local_dir" != /* ]]; then
        # Get the project root directory (parent of scripts directory)
        local project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        local_dir="$project_root/$local_dir"
    fi

    print_header "Downloading Model from Hugging Face"
    print_info "Model: $model_repo"
    print_info "Destination: $local_dir"

    # Check if huggingface_hub is installed
    if ! pip show huggingface_hub > /dev/null 2>&1; then
        print_warning "Installing huggingface_hub..."
        pip install huggingface_hub
    fi

    # Check if HF token is set
    if [ -z "$HF_TOKEN" ]; then
        print_warning "Huggingface token not set. Attempting to download without authentication."
        print_info "For gated models, set HF_TOKEN in your .env file."
    else
        print_info "Logging into Huggingface using environment token..."
        huggingface-cli login --token "$HF_TOKEN" > /dev/null 2>&1
    fi

    # Create local dir if not exists
    mkdir -p "$local_dir"

    # Download using huggingface-cli
    print_info "Downloading model $model_repo into $local_dir ..."
    huggingface-cli download "$model_repo" --local-dir "$local_dir" --local-dir-use-symlinks False --resume-download

    if [ $? -eq 0 ]; then
        print_success "Download completed successfully!"
        print_info "Files are stored in: $local_dir"
        return 0
    else
        print_error "Download failed. Please check your internet connection and HF_TOKEN."
        return 1
    fi
}

# Main function
main() {
    # Load environment variables
    load_env

    # Parse command line arguments
    local model_repo=$1
    local local_dir=$2

    # Check inputs
    if [ -z "$model_repo" ]; then
        echo "Usage: $0 <model_repo> [<local_dir>]"
        echo "Example: $0 mistralai/Mistral-7B-Instruct-v0.2 models/mistral-7b-instruct"
        exit 1
    fi

    # If local_dir is not provided, use the environment variable or default
    if [ -z "$local_dir" ]; then
        # Get models directory from environment variable with fallback to default
        local models_dir=${SOLAR_SAGE_MODELS_DIR:-"models"}

        # Extract model name from repo (last part of the path)
        local model_name=$(basename "$model_repo" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

        # Set local_dir to models_dir/model_name
        local_dir="${models_dir}/${model_name}"

        print_info "No destination directory specified. Using: $local_dir"
    fi

    # Download the model
    download_hf_model "$model_repo" "$local_dir"

    exit $?
}

# Run the main function if the script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
