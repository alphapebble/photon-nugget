"""
Unit tests for the Weather-Enhanced RAG.
"""
import os
import sys
import time
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from rag.weather_enhanced_rag import weather_enhanced_rag_answer, handle_weather_query, is_weather_related_query

class TestWeatherEnhancedRag(unittest.TestCase):
    """Test cases for the Weather-Enhanced RAG."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_query = "How will clouds affect my solar panels?"
        self.test_location = {"lat": 37.7749, "lon": -122.4194}
    
    def test_is_weather_related_query(self):
        """Test that the is_weather_related_query function works correctly."""
        # Test weather-related queries
        weather_queries = [
            "How does weather affect solar panels?",
            "Will rain reduce my solar output?",
            "What happens to solar panels in cloudy conditions?",
            "How efficient are solar panels in winter?",
            "Will tomorrow be a good day for solar production?"
        ]
        
        for query in weather_queries:
            self.assertTrue(is_weather_related_query(query), f"Query should be weather-related: {query}")
        
        # Test non-weather-related queries
        non_weather_queries = [
            "How do solar panels work?",
            "What is the lifespan of a solar panel?",
            "How much do solar panels cost?",
            "Are solar panels worth the investment?",
            "How are solar panels manufactured?"
        ]
        
        for query in non_weather_queries:
            self.assertFalse(is_weather_related_query(query), f"Query should not be weather-related: {query}")
    
    @patch('rag.weather_enhanced_rag.enhanced_rag_answer')
    def test_weather_enhanced_rag_answer(self, mock_enhanced_rag):
        """Test that the weather_enhanced_rag_answer function works correctly."""
        # Mock the enhanced_rag_answer function
        mock_result = {
            'response': 'Mock response',
            'has_weather_context': True,
            'weather_summary': ['Weather data successfully incorporated']
        }
        mock_enhanced_rag.return_value = mock_result
        
        result = weather_enhanced_rag_answer(
            user_query=self.test_query,
            lat=37.7749,
            lon=-122.4194,
            include_weather=True
        )
        
        # Check that the enhanced_rag_answer function was called with the correct arguments
        mock_enhanced_rag.assert_called_once_with(
            user_query=self.test_query,
            lat=37.7749,
            lon=-122.4194,
            include_weather=True
        )
        
        # Check that the result matches the mock result
        self.assertEqual(result, mock_result)
    
    @patch('rag.weather_enhanced_rag.enhanced_rag_answer')
    def test_handle_weather_query(self, mock_enhanced_rag):
        """Test that the handle_weather_query function works correctly."""
        # Mock the enhanced_rag_answer function
        mock_result = {
            'response': 'Mock response',
            'has_weather_context': True,
            'weather_summary': ['Weather data successfully incorporated']
        }
        mock_enhanced_rag.return_value = mock_result
        
        result = handle_weather_query(
            query=self.test_query,
            user_location=self.test_location
        )
        
        # Check that the enhanced_rag_answer function was called with the correct arguments
        mock_enhanced_rag.assert_called_once_with(
            user_query=self.test_query,
            lat=self.test_location.get("lat"),
            lon=self.test_location.get("lon"),
            include_weather=True
        )
        
        # Check that the result matches the mock result
        self.assertEqual(result, mock_result)

if __name__ == '__main__':
    unittest.main()
