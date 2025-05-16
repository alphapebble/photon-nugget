#!/bin/bash
# Initialize the database with a sample table

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Function to initialize the database
init_db() {
    print_header "Initializing Solar Sage Database"
    
    # Set Python path
    set_python_path
    
    # Create a Python script to initialize the database
    TMP_SCRIPT=$(mktemp)
    cat > $TMP_SCRIPT << 'EOF'
import os
import lancedb
import numpy as np
from datetime import datetime

# Get configuration
db_path = os.environ.get("SOLAR_SAGE_VECTOR_DB_PATH", "./data/lancedb")
table_name = os.environ.get("SOLAR_SAGE_VECTOR_DB_TABLE", "solar_knowledge")

print(f"Initializing database at {db_path} with table {table_name}")

# Create the database directory if it doesn't exist
os.makedirs(db_path, exist_ok=True)

# Connect to the database
db = lancedb.connect(db_path)

# Check if the table already exists
if table_name in db.table_names():
    print(f"Table {table_name} already exists")
else:
    # Create a sample table with minimal data
    print(f"Creating table {table_name} with sample data")
    
    # Create sample data
    data = [
        {
            "id": "sample1",
            "doc_source": "sample_document.txt",
            "text": "Solar panels convert sunlight into electricity through the photovoltaic effect.",
            "vector": np.random.rand(384).astype(np.float32),  # Random embedding vector
            "metadata": {
                "source_type": "text",
                "created_at": datetime.now().isoformat()
            }
        },
        {
            "id": "sample2",
            "doc_source": "sample_document.txt",
            "text": "Regular maintenance of solar panels includes cleaning and inspection for optimal performance.",
            "vector": np.random.rand(384).astype(np.float32),  # Random embedding vector
            "metadata": {
                "source_type": "text",
                "created_at": datetime.now().isoformat()
            }
        }
    ]
    
    # Create the table
    db.create_table(table_name, data)
    print(f"Table {table_name} created successfully with {len(data)} sample records")

print("Database initialization complete")
EOF
    
    # Run the Python script
    python $TMP_SCRIPT
    
    # Clean up
    rm $TMP_SCRIPT
    
    print_success "Database initialization complete"
}

# Main function
main() {
    # Load environment variables
    load_env
    
    # Initialize the database
    init_db
    
    exit $?
}

# Run the main function if the script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
