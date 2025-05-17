"""
Retriever Agent for Solar Sage.

This agent is responsible for retrieving relevant context for user queries.
"""
from agents.base_agent import BaseAgent
from retrieval.providers.lancedb import get_context_documents
from typing import List, Dict, Any, Optional

class RetrieverAgent(BaseAgent):
    """Agent responsible for retrieving context."""

    def __init__(self):
        """Initialize the retriever agent."""
        super().__init__(
            name="Retriever",
            description="Retrieves relevant context for user queries"
        )

    def fetch_context(self, query: str, max_documents: int = 5) -> List[str]:
        """
        Fetch relevant context for the query.

        Args:
            query: User query
            max_documents: Maximum number of documents to retrieve

        Returns:
            List of relevant document chunks
        """
        return get_context_documents(query, n_results=max_documents)

    def run(self, query: str, max_documents: int = 5) -> List[str]:
        """
        Run the retriever agent.

        Args:
            query: User query
            max_documents: Maximum number of documents to retrieve

        Returns:
            List of relevant document chunks
        """
        return self.fetch_context(query, max_documents)
