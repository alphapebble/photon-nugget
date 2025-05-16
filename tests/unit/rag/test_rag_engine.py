"""
Unit tests for the RAG Engine.
"""
import os
import sys
import time
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from rag.rag_engine import rag_answer, enhanced_rag_answer

class TestRagEngine(unittest.TestCase):
    """Test cases for the RAG Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_query = "What are the benefits of solar energy?"
    
    def test_rag_answer(self):
        """Test that the rag_answer function works correctly."""
        # Skip if database doesn't exist
        if not os.path.exists("./data/lancedb/solar_knowledge.lance"):
            self.skipTest("LanceDB database not found or empty")
        
        response = rag_answer(self.test_query)
        
        # We can't assert exact response content since it depends on the LLM and database
        # But we can check that the function returns a non-empty string
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    
    @patch('rag.rag_engine.orchestrator')
    def test_enhanced_rag_answer(self, mock_orchestrator):
        """Test that the enhanced_rag_answer function works correctly."""
        # Mock the orchestrator
        mock_result = {
            'response': 'Mock response',
            'has_weather_context': True,
            'weather_summary': ['Weather data successfully incorporated']
        }
        mock_orchestrator.process_query.return_value = mock_result
        
        result = enhanced_rag_answer(
            user_query="How does weather impact solar panel efficiency?",
            lat=37.7749,
            lon=-122.4194,
            include_weather=True
        )
        
        # Check that the orchestrator was called with the correct arguments
        mock_orchestrator.process_query.assert_called_once_with(
            query="How does weather impact solar panel efficiency?",
            lat=37.7749,
            lon=-122.4194,
            include_weather=True
        )
        
        # Check that the result matches the mock result
        self.assertEqual(result, mock_result)

if __name__ == '__main__':
    unittest.main()
