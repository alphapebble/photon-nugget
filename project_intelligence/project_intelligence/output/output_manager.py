import json
import os

class OutputManager:
    """
    Manages the output of extracted project intelligence.
    """

    def __init__(self):
        """
        Initializes the OutputManager.
        """
        pass

    def handle_output(self, extracted_data: dict, output_type: str = "json_string", destination: str = None):
        """
        Handles the output of extracted data, either as a JSON string or by saving to a JSON file.

        Args:
            extracted_data: The dictionary of entities from EntityExtractor.
            output_type: The desired output format ("json_string" or "json_file").
            destination: Optional file path for "json_file" output.

        Returns:
            A JSON string if output_type is "json_string", otherwise None.

        Raises:
            ValueError: If an unsupported output_type is provided.
            TypeError: If destination is not provided for "json_file".
        """
        if output_type == "json_string":
            return json.dumps(extracted_data, indent=4)
        elif output_type == "json_file":
            if destination is None:
                raise TypeError("Destination must be provided for json_file output type.")
            
            # Ensure the output directory exists
            output_dir = os.path.dirname(destination)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except OSError as e:
                    print(f"Error creating directory {output_dir}: {e}")
                    return None # Or re-raise the exception

            try:
                with open(destination, 'w', encoding='utf-8') as f:
                    json.dump(extracted_data, f, indent=4)
                print(f"Data successfully saved to {destination}")
                return None
            except IOError as e:
                print(f"Error writing to file {destination}: {e}")
                return None # Or re-raise the exception
        else:
            raise ValueError(f"Unsupported output_type: {output_type}. Supported types are 'json_string' and 'json_file'.")
