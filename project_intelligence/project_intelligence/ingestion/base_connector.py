from abc import ABC, abstractmethod

class BaseConnector(ABC):
    """
    Abstract base class for data connectors.
    """

    @abstractmethod
    def fetch_data(self, source: str) -> list[str]:
        """
        Abstract method to fetch data from a source.

        Args:
            source: The data source (e.g., file path, API endpoint).

        Returns:
            A list of text strings.
        """
        pass
