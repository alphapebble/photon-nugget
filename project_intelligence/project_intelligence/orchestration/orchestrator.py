from project_intelligence.ingestion.file_connector import FileConnector
from project_intelligence.processing.entity_extractor import EntityExtractor
from project_intelligence.output.output_manager import OutputManager

class Orchestrator:
    """
    Orchestrates the project intelligence extraction process.
    """

    def __init__(self):
        """
        Initializes the Orchestrator with instances of EntityExtractor and OutputManager.
        """
        self.entity_extractor = EntityExtractor()
        self.output_manager = OutputManager()
        # Future configurations can be loaded here

    def process_source(self, input_source_path: str, connector_type: str = "file", output_types: list[dict] = None):
        """
        Processes data from an input source, extracts entities, and handles output.

        Args:
            input_source_path: The path to the input data (e.g., file path).
            connector_type: Specifies the type of connector to use (default: "file").
            output_types: A list of dictionaries specifying output actions.
                          Example: [{"type": "json_string"}, {"type": "json_file", "destination": "output/data.json"}]
        """
        if output_types is None:
            output_types = [{"type": "json_string"}] # Default output

        raw_data_list = []

        try:
            if connector_type == "file":
                connector = FileConnector()
                raw_data_list = connector.fetch_data(input_source_path)
            # Add other connector types here (e.g., "api", "database")
            # elif connector_type == "api":
            #     connector = ApiConnector(config.API_DETAILS) # Assuming config holds API details
            #     raw_data_list = connector.fetch_data(input_source_path)
            else:
                print(f"Error: Unsupported connector type '{connector_type}'.")
                return
        except Exception as e:
            print(f"Error during data ingestion: {e}")
            return

        if not raw_data_list:
            print(f"No data fetched from source: {input_source_path} using connector: {connector_type}")
            return

        for text_content in raw_data_list:
            if not isinstance(text_content, str):
                print(f"Warning: Expected string data from connector, got {type(text_content)}. Skipping.")
                continue

            extracted_entities = self.entity_extractor.extract_entities(text_content)

            for output_action in output_types:
                action_type = output_action.get("type")
                destination = output_action.get("destination")
                try:
                    if action_type == "json_string":
                        self.output_manager.handle_output(extracted_entities, output_type="json_string")
                    elif action_type == "json_file":
                        if destination:
                            self.output_manager.handle_output(extracted_entities, output_type="json_file", destination=destination)
                        else:
                            print("Error: 'destination' not provided for 'json_file' output type.")
                    else:
                        print(f"Warning: Unsupported output action type '{action_type}'.")
                except Exception as e:
                    print(f"Error during output handling for action {action_type}: {e}")
        print(f"Successfully processed source: {input_source_path}")
