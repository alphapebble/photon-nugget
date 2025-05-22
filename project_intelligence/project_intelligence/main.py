from project_intelligence.orchestration.orchestrator import Orchestrator
from project_intelligence import config # Import the config module

def main():
    """
    Main function to demonstrate the Orchestrator.
    """
    # Instantiate the Orchestrator
    orchestrator = Orchestrator()

    # Define the input source path
    input_file_path = "sample_data/test_document.txt"

    # Define the desired output actions
    # Using DEFAULT_OUTPUT_FILENAME from config
    output_actions = [
        {"type": "json_string"},
        {"type": "json_file", "destination": config.DEFAULT_OUTPUT_FILENAME}
    ]

    # Call the Orchestrator's process_source method
    print(f"Starting processing for: {input_file_path}")
    orchestrator.process_source(
        input_source_path=input_file_path,
        connector_type="file",
        output_types=output_actions
    )
    print("Processing finished.")

if __name__ == "__main__":
    main()
