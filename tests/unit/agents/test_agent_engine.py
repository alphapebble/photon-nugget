"""
Unit tests for the Agent Engine.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root and src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from agents.agent_engine import AgentEngine
from agents.tool_registry import ToolRegistry
from agents.memory_system import MemorySystem

class TestAgentEngine(unittest.TestCase):
    """Test cases for the Agent Engine."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_llm = MagicMock()
        self.mock_tool_registry = MagicMock(spec=ToolRegistry)
        self.mock_memory_system = MagicMock(spec=MemorySystem)

        # Create the agent engine
        self.agent_engine = AgentEngine(
            llm=self.mock_llm,
            tool_registry=self.mock_tool_registry,
            memory_system=self.mock_memory_system,
            require_authorization=True
        )

        # Test data
        self.user_id = "test_user"
        self.query = "What's the weather like today?"
        self.user_authorized = True

    def test_initialization(self):
        """Test that the agent engine initializes correctly."""
        self.assertEqual(self.agent_engine.llm, self.mock_llm)
        self.assertEqual(self.agent_engine.tool_registry, self.mock_tool_registry)
        self.assertEqual(self.agent_engine.memory_system, self.mock_memory_system)
        self.assertEqual(self.agent_engine.require_authorization, True)

    def test_extract_tool_calls(self):
        """Test that tool calls can be extracted from text."""
        # Test text with a single tool call
        text = "USE_TOOL[get_weather](location=NewYork)"
        tool_calls = self.agent_engine._extract_tool_calls(text)

        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0]["tool_name"], "get_weather")
        self.assertIn("location", tool_calls[0]["params"])

        # Test text with no tool calls
        text = "There are no tool calls in this text."
        tool_calls = self.agent_engine._extract_tool_calls(text)

        self.assertEqual(len(tool_calls), 0)

    @patch('agents.agent_engine.weather_enhanced_rag_answer')
    def test_process_query_with_rag(self, mock_rag_answer):
        """Test that queries can be processed with RAG."""
        # Set up mocks
        self.mock_llm.generate.return_value = "NEEDS_RAG"
        mock_rag_answer.return_value = ("Sample context", "Sample response")
        self.mock_memory_system.get_recent_interactions.return_value = []

        # Process a query
        result = self.agent_engine.process_query(
            user_id=self.user_id,
            query=self.query,
            user_authorized=self.user_authorized
        )

        # Check that the LLM was called
        self.mock_llm.generate.assert_called_once()

        # Check that RAG was used
        mock_rag_answer.assert_called_once_with(self.query)

        # Check that the interaction was stored
        self.mock_memory_system.add_interaction.assert_called_once_with(
            self.user_id,
            self.query,
            "Sample response",
            context_used="Sample context"
        )

        # Check the result
        self.assertEqual(result["response"], "Sample response")
        self.assertEqual(result["context_used"], "Sample context")

    def test_process_query_with_tools(self):
        """Test that queries can be processed with tools."""
        # Set up mocks
        self.mock_llm.generate.return_value = "USE_TOOL[get_weather](location=NewYork)"
        self.mock_memory_system.get_recent_interactions.return_value = []

        # Mock tool execution
        self.mock_tool_registry.execute_tool.return_value = {
            "success": True,
            "result": {"temperature": 25, "conditions": "sunny"}
        }

        # Process a query
        result = self.agent_engine.process_query(
            user_id=self.user_id,
            query=self.query,
            user_authorized=self.user_authorized
        )

        # Check that the LLM was called twice (once for tool decision, once for response)
        self.assertEqual(self.mock_llm.generate.call_count, 2)

        # Check that the tool was executed
        self.mock_tool_registry.execute_tool.assert_called_once()
        call_args = self.mock_tool_registry.execute_tool.call_args[0]
        self.assertEqual(call_args[0], "get_weather")
        self.assertEqual(call_args[1], {"location": "NewYork"})

        # Check that the interaction was stored
        self.mock_memory_system.add_interaction.assert_called_once()

        # Check the result
        self.assertIn("response", result)
        self.assertIn("tools_used", result)
        self.assertEqual(result["tools_used"], ["get_weather"])
        self.assertIn("tool_results", result)

    def test_format_available_tools(self):
        """Test that available tools can be formatted for prompts."""
        # Set up mock
        self.mock_tool_registry.list_tools.return_value = [
            {
                "name": "get_weather",
                "description": "Get current weather",
                "required_params": ["location"],
                "optional_params": ["units"]
            },
            {
                "name": "get_forecast",
                "description": "Get weather forecast",
                "required_params": ["location", "days"],
                "optional_params": []
            }
        ]

        # Format tools
        formatted_tools = self.agent_engine._format_available_tools()

        # Check the result
        self.assertIn("get_weather", formatted_tools)
        self.assertIn("Get current weather", formatted_tools)
        self.assertIn("location (required)", formatted_tools)
        self.assertIn("units (optional)", formatted_tools)
        self.assertIn("get_forecast", formatted_tools)
        self.assertIn("Get weather forecast", formatted_tools)
        self.assertIn("location (required)", formatted_tools)
        self.assertIn("days (required)", formatted_tools)

if __name__ == '__main__':
    unittest.main()
