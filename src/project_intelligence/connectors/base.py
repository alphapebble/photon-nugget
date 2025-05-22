"""
Base connector class for data sources.

This module provides the abstract base class for all data source connectors
used by the Project Intelligence System.
"""

import abc
from typing import Any, Dict, List, Optional, Union
import logging
import asyncio

logger = logging.getLogger(__name__)


class DataSourceConnector(abc.ABC):
    """
    Abstract base class for data source connectors.
    
    A data source connector is responsible for connecting to a specific data source
    (e.g., email, Slack, Teams, spreadsheets) and fetching data from it.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the connector.
        
        Args:
            config: Configuration dictionary for the connector
        """
        self.config = config or {}
        self.is_initialized = False
        self.last_fetch_time = None
    
    @abc.abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the connector.
        
        This method should be called before using the connector to establish
        connections, authenticate with the data source, etc.
        """
        self.is_initialized = True
    
    @abc.abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from the source.
        
        Returns:
            List of data items from the source
        """
        pass
    
    @abc.abstractmethod
    async def close(self) -> None:
        """
        Close the connector.
        
        This method should be called to clean up resources when the connector
        is no longer needed.
        """
        self.is_initialized = False
    
    async def _check_initialization(self) -> None:
        """
        Check if the connector is initialized.
        
        Raises:
            RuntimeError: If the connector is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} is not initialized")