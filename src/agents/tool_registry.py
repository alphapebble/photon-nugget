"""
Tool Registry for Solar Sage Agent.

This module manages the registration and retrieval of tools that the agent can use.
"""
from typing import Dict, Any, Callable, List, Optional


class ToolRegistry:
    """Registry for agent tools."""

    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        tool_name: str,
        tool_function: Callable,
        tool_description: str,
        required_params: List[str],
        optional_params: Optional[List[str]] = None,
        authorization_required: bool = False
    ) -> None:
        """
        Register a new tool in the registry.

        Args:
            tool_name: Unique identifier for the tool
            tool_function: Function to execute when tool is called
            tool_description: Human-readable description of the tool
            required_params: List of required parameter names
            optional_params: List of optional parameter names
            authorization_required: Whether user authorization is needed
        """
        # TODO: Implement tool registration
        # The tool should be stored in self.tools with all its metadata
        # Example implementation:
        self.tools[tool_name] = {
            "function": tool_function,
            "description": tool_description,
            "required_params": required_params,
            "optional_params": optional_params or [],
            "authorization_required": authorization_required
        }

    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool by name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool configuration or None if not found
        """
        # TODO: Implement tool retrieval
        # Return the tool configuration from self.tools or None if not found
        # Example implementation:
        return self.tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools.

        Returns:
            List of tool configurations
        """
        # TODO: Implement tool listing
        # Return a list of all tools with their metadata
        # Example implementation:
        return [
            {
                "name": name,
                "description": tool["description"],
                "required_params": tool["required_params"],
                "optional_params": tool["optional_params"],
                "authorization_required": tool["authorization_required"]
            }
            for name, tool in self.tools.items()
        ]

    def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        user_authorized: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters to pass to the tool
            user_authorized: Whether the user has authorized this action

        Returns:
            Tool execution results

        Raises:
            ValueError: If tool not found or missing required parameters
            PermissionError: If authorization required but not provided
        """
        # TODO: Implement tool execution
        # 1. Get the tool from the registry
        # 2. Check that all required parameters are provided
        # 3. Check that the user is authorized if required
        # 4. Execute the tool function with the parameters
        # 5. Return the result or error information
        # Example implementation:
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Check required parameters
        missing_params = [
            param for param in tool["required_params"]
            if param not in params
        ]
        if missing_params:
            raise ValueError(
                f"Missing required parameters for tool '{tool_name}': {missing_params}"
            )

        # Check authorization
        if tool["authorization_required"] and not user_authorized:
            raise PermissionError(
                f"Tool '{tool_name}' requires user authorization"
            )

        # Execute tool function with parameters
        try:
            result = tool["function"](**params)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
