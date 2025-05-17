"""
Base retriever interface for Solar Sage.

This module defines the base interface for retrievers in the Solar Sage system.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseRetriever(ABC):
    """Base class for all retrievers in the system."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve documents based on the query.

        Args:
            query: The query string
            top_k: Number of documents to retrieve
            **kwargs: Additional retriever-specific parameters

        Returns:
            List of retrieved documents with metadata
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the retriever's index.

        Args:
            documents: List of documents to add
        """
        pass

    @abstractmethod
    def delete_documents(self, document_ids: List[str]) -> None:
        """
        Delete documents from the retriever's index.

        Args:
            document_ids: List of document IDs to delete
        """
        pass

    @abstractmethod
    def search_by_metadata(self, metadata_filter: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search documents by metadata.

        Args:
            metadata_filter: Metadata filter criteria
            top_k: Number of documents to retrieve

        Returns:
            List of retrieved documents with metadata
        """
        pass
