"""
Unit tests for the Response Generator Agent.
"""
import os
import sys
import time
import unittest

# Add the project root and src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from agents.types.response_generator import ResponseGeneratorAgent

class TestResponseGeneratorAgent(unittest.TestCase):
    """Test cases for the Response Generator Agent."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = ResponseGeneratorAgent()
        self.test_query = "How do solar panels work?"
        self.test_context = [
            "Solar panels work through the photovoltaic effect, converting sunlight into electricity.",
            "When sunlight hits the semiconductor materials in solar cells, it excites electrons, creating an electric current.",
            "This direct current (DC) is then converted to alternating current (AC) by an inverter for use in homes."
        ]

    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.generator.name, "ResponseGenerator")
        self.assertEqual(self.generator.description, "Generates responses based on context and query")

    def test_generate_response(self):
        """Test that the agent can generate responses."""
        response = self.generator.generate_response(self.test_query, self.test_context)

        # We can't assert exact response content since it depends on the LLM
        # But we can check that the method returns a non-empty string
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_run_method(self):
        """Test that the run method works correctly."""
        response = self.generator.run(self.test_query, self.test_context)

        # We can't assert exact response content since it depends on the LLM
        # But we can check that the method returns a non-empty string
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

if __name__ == '__main__':
    unittest.main()
