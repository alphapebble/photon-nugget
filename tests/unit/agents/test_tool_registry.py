"""
Unit tests for the Tool Registry.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock

# Add the project root and src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from agents.tool_registry import ToolRegistry

class TestToolRegistry(unittest.TestCase):
    """Test cases for the Tool Registry."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
        
        # Create a mock tool function
        self.mock_tool = MagicMock(return_value={"result": "success"})
        
        # Register the mock tool
        self.registry.register_tool(
            tool_name="test_tool",
            tool_function=self.mock_tool,
            tool_description="A test tool",
            required_params=["param1"],
            optional_params=["param2"],
            authorization_required=False
        )
        
        # Register another tool that requires authorization
        self.registry.register_tool(
            tool_name="auth_tool",
            tool_function=self.mock_tool,
            tool_description="A tool requiring authorization",
            required_params=["param1"],
            optional_params=[],
            authorization_required=True
        )

    def test_register_tool(self):
        """Test that tools can be registered."""
        # Check that the tool was registered
        self.assertIn("test_tool", self.registry.tools)
        self.assertIn("auth_tool", self.registry.tools)
        
        # Check that the tool properties were set correctly
        tool = self.registry.tools["test_tool"]
        self.assertEqual(tool["description"], "A test tool")
        self.assertEqual(tool["required_params"], ["param1"])
        self.assertEqual(tool["optional_params"], ["param2"])
        self.assertEqual(tool["authorization_required"], False)

    def test_get_tool(self):
        """Test that tools can be retrieved."""
        # Get an existing tool
        tool = self.registry.get_tool("test_tool")
        self.assertIsNotNone(tool)
        self.assertEqual(tool["description"], "A test tool")
        
        # Get a non-existent tool
        tool = self.registry.get_tool("non_existent_tool")
        self.assertIsNone(tool)

    def test_list_tools(self):
        """Test that tools can be listed."""
        tools = self.registry.list_tools()
        self.assertEqual(len(tools), 2)
        
        # Check that the tool properties are included in the list
        tool_names = [tool["name"] for tool in tools]
        self.assertIn("test_tool", tool_names)
        self.assertIn("auth_tool", tool_names)

    def test_execute_tool(self):
        """Test that tools can be executed."""
        # Execute a tool with valid parameters
        result = self.registry.execute_tool(
            tool_name="test_tool",
            params={"param1": "value1", "param2": "value2"}
        )
        
        # Check that the tool was called with the correct parameters
        self.mock_tool.assert_called_once_with(param1="value1", param2="value2")
        
        # Check that the result is correct
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], {"result": "success"})

    def test_execute_tool_missing_params(self):
        """Test that executing a tool with missing parameters raises an error."""
        with self.assertRaises(ValueError):
            self.registry.execute_tool(
                tool_name="test_tool",
                params={"param2": "value2"}  # Missing required param1
            )

    def test_execute_tool_not_found(self):
        """Test that executing a non-existent tool raises an error."""
        with self.assertRaises(ValueError):
            self.registry.execute_tool(
                tool_name="non_existent_tool",
                params={}
            )

    def test_execute_tool_authorization(self):
        """Test that executing a tool requiring authorization checks authorization."""
        # Execute without authorization
        with self.assertRaises(PermissionError):
            self.registry.execute_tool(
                tool_name="auth_tool",
                params={"param1": "value1"},
                user_authorized=False
            )
        
        # Execute with authorization
        result = self.registry.execute_tool(
            tool_name="auth_tool",
            params={"param1": "value1"},
            user_authorized=True
        )
        
        # Check that the tool was called with the correct parameters
        self.mock_tool.assert_called_with(param1="value1")
        
        # Check that the result is correct
        self.assertTrue(result["success"])

if __name__ == '__main__':
    unittest.main()
