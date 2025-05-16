"""
Unit tests for the Retriever Agent.
"""
import os
import sys
import time
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from agents.retriever_agent import RetrieverAgent

class TestRetrieverAgent(unittest.TestCase):
    """Test cases for the Retriever Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.retriever = RetrieverAgent()
        self.test_query = "How do solar panels work?"
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.retriever.name, "Retriever")
        self.assertEqual(self.retriever.description, "Retrieves relevant context for user queries")
    
    def test_fetch_context(self):
        """Test that the agent can fetch context."""
        # Skip if database doesn't exist
        if not os.path.exists("./data/lancedb/solar_knowledge.lance"):
            self.skipTest("LanceDB database not found or empty")
        
        results = self.retriever.fetch_context(self.test_query, max_documents=3)
        
        # We can't assert exact results since they depend on the database content
        # But we can check that the method returns a list
        self.assertIsInstance(results, list)
    
    def test_run_method(self):
        """Test that the run method works correctly."""
        # Skip if database doesn't exist
        if not os.path.exists("./data/lancedb/solar_knowledge.lance"):
            self.skipTest("LanceDB database not found or empty")
        
        results = self.retriever.run(self.test_query, max_documents=3)
        
        # We can't assert exact results since they depend on the database content
        # But we can check that the method returns a list
        self.assertIsInstance(results, list)

if __name__ == '__main__':
    unittest.main()
