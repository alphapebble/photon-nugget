"""
Unit tests for the Agent Orchestrator.
"""
import os
import sys
import time
import unittest
from unittest.mock import patch, MagicMock

# Add the project root and src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from agents.orchestrator import AgentOrchestrator

class TestAgentOrchestrator(unittest.TestCase):
    """Test cases for the Agent Orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = AgentOrchestrator()
        self.test_query = "How do solar panels work?"

    def test_initialization(self):
        """Test that the orchestrator initializes correctly."""
        self.assertIsNotNone(self.orchestrator.retriever_agent)
        self.assertIsNotNone(self.orchestrator.response_generator_agent)

    def test_process_query_basic(self):
        """Test that the orchestrator can process a basic query."""
        # Skip if database doesn't exist
        if not os.path.exists("./data/lancedb/solar_knowledge.lance"):
            self.skipTest("LanceDB database not found or empty")

        result = self.orchestrator.process_query(self.test_query)

        # Check that the result has the expected structure
        self.assertIsInstance(result, dict)
        self.assertIn('response', result)
        self.assertIn('has_weather_context', result)

        # Check that the response is a non-empty string
        self.assertIsInstance(result['response'], str)
        self.assertTrue(len(result['response']) > 0)

        # Check that weather context is not included by default
        self.assertFalse(result['has_weather_context'])

    @patch('agents.orchestrator.get_weather_context_for_rag')
    def test_process_query_with_weather(self, mock_get_weather):
        """Test that the orchestrator can process a query with weather context."""
        # Mock the weather context function
        mock_get_weather.return_value = "Mock weather context"

        # Skip if database doesn't exist
        if not os.path.exists("./data/lancedb/solar_knowledge.lance"):
            self.skipTest("LanceDB database not found or empty")

        result = self.orchestrator.process_query(
            query="How will weather affect my solar production?",
            lat=37.7749,
            lon=-122.4194,
            include_weather=True
        )

        # Check that the result has the expected structure
        self.assertIsInstance(result, dict)
        self.assertIn('response', result)
        self.assertIn('has_weather_context', result)

        # Check that the response is a non-empty string
        self.assertIsInstance(result['response'], str)
        self.assertTrue(len(result['response']) > 0)

        # Check that weather context is included
        self.assertTrue(result['has_weather_context'])

        # Verify that the weather context function was called
        mock_get_weather.assert_called_once_with(37.7749, -122.4194)

if __name__ == '__main__':
    unittest.main()
