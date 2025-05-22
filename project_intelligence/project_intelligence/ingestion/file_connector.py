from project_intelligence.ingestion.base_connector import BaseConnector

class FileConnector(BaseConnector):
    """
    Connector for reading data from text files.
    """

    def fetch_data(self, file_path: str) -> list[str]:
        """
        Fetches data from a text file.

        Args:
            file_path: The path to the text file.

        Returns:
            A list containing the file content as a single string.
            Returns an empty list if the file cannot be read.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [content]
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return []
        except IOError:
            print(f"Error: Could not read file at {file_path}")
            return []
