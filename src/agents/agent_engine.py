"""
Agent Engine for Solar Sage.

This module implements the core agent logic for determining when to use tools
and how to process user queries.
"""
from typing import Dict, Any, List, Optional, Tuple
import re
from llm.base import LLMInterface
from agents.tool_registry import ToolRegistry
from agents.memory_system import MemorySystem
from rag.engines.base import rag_answer
from rag.engines.weather_enhanced import weather_enhanced_rag_answer

# Regular expressions for detecting tool usage
TOOL_PATTERN = r"USE_TOOL\[([\w_]+)\]\((.*?)\)"
PARAM_PATTERN = r"(\w+)=(.*?)(?:,\s*\w+=|$)"


class AgentEngine:
    """Core agent logic for Solar Sage."""

    def __init__(
        self,
        llm: LLMInterface,
        tool_registry: ToolRegistry,
        memory_system: MemorySystem,
        require_authorization: bool = True
    ):
        """
        Initialize the agent engine.

        Args:
            llm: Language model interface
            tool_registry: Tool registry
            memory_system: Memory system
            require_authorization: Whether to require user authorization for tools
        """
        self.llm = llm
        self.tool_registry = tool_registry
        self.memory_system = memory_system
        self.require_authorization = require_authorization

    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls from text.

        Args:
            text: Text to extract tool calls from

        Returns:
            List of tool calls with name and parameters
        """
        # TODO: Implement tool call extraction
        # 1. Use regex to find tool calls in the text
        # 2. Extract tool name and parameters
        # 3. Convert parameter values to appropriate types
        # Example implementation:
        tool_calls = []

        for match in re.finditer(TOOL_PATTERN, text):
            tool_name = match.group(1)
            params_text = match.group(2)

            # Extract parameters
            params = {}
            for param_match in re.finditer(PARAM_PATTERN, params_text):
                param_name = param_match.group(1)
                param_value = param_match.group(2).strip()

                # Convert parameter values to appropriate types
                if param_value.lower() == "true":
                    params[param_name] = True
                elif param_value.lower() == "false":
                    params[param_name] = False
                elif param_value.isdigit():
                    params[param_name] = int(param_value)
                elif re.match(r"^\d+\.\d+$", param_value):
                    params[param_name] = float(param_value)
                else:
                    params[param_name] = param_value

            tool_calls.append({
                "tool_name": tool_name,
                "params": params
            })

        return tool_calls

    def _execute_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        user_authorized: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute a list of tool calls.

        Args:
            tool_calls: List of tool calls to execute
            user_authorized: Whether the user has authorized the actions

        Returns:
            List of tool execution results
        """
        # TODO: Implement tool call execution
        # 1. Iterate through the tool calls
        # 2. Execute each tool with the provided parameters
        # 3. Return the results
        # Example implementation:
        results = []

        for call in tool_calls:
            try:
                result = self.tool_registry.execute_tool(
                    call["tool_name"],
                    call["params"],
                    user_authorized
                )
                results.append({
                    "tool_name": call["tool_name"],
                    "success": result["success"],
                    "result": result.get("result"),
                    "error": result.get("error")
                })
            except Exception as e:
                results.append({
                    "tool_name": call["tool_name"],
                    "success": False,
                    "error": str(e)
                })

        return results

    def process_query(
        self,
        user_id: str,
        query: str,
        user_authorized: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user query.

        Args:
            user_id: User identifier
            query: User's query
            user_authorized: Whether the user has authorized tool usage

        Returns:
            Processing result with response and any tool usage
        """
        # TODO: Implement query processing
        # 1. Get recent interactions for context
        # 2. Determine if the query needs tools or RAG
        # 3. Process the query accordingly
        # 4. Store the interaction in memory
        # 5. Return the result
        # Example implementation:
        # Get recent interactions for context
        recent_interactions = self.memory_system.get_recent_interactions(user_id)

        # First, try to determine if tools are needed
        tool_prompt = f"""
        Determine if any tools are needed to answer this query:

        User query: {query}

        Available tools:
        {self._format_available_tools()}

        If tools are needed, respond with USE_TOOL[tool_name](param1=value1, param2=value2)
        Otherwise, respond with NEEDS_RAG.
        """

        tool_response = self.llm.generate(tool_prompt)

        # Check if tools are needed
        if "USE_TOOL" in tool_response:
            # Extract and execute tool calls
            tool_calls = self._extract_tool_calls(tool_response)
            tool_results = self._execute_tool_calls(tool_calls, user_authorized)

            # Generate response with tool results
            response = self._generate_response_with_tools(query, tool_results)

            # Store interaction in memory
            self.memory_system.add_interaction(
                user_id,
                query,
                response,
                tools_used=[call["tool_name"] for call in tool_calls]
            )

            return {
                "response": response,
                "tools_used": [call["tool_name"] for call in tool_calls],
                "tool_results": tool_results
            }
        else:
            # Use RAG to answer the query
            context, response = weather_enhanced_rag_answer(query)

            # Store interaction in memory
            self.memory_system.add_interaction(
                user_id,
                query,
                response,
                context_used=context
            )

            return {
                "response": response,
                "context_used": context
            }

    def _format_available_tools(self) -> str:
        """Format available tools for the prompt."""
        tools = self.tool_registry.list_tools()
        formatted_tools = []

        for tool in tools:
            params = ", ".join([
                f"{param} (required)" for param in tool["required_params"]
            ] + [
                f"{param} (optional)" for param in tool["optional_params"]
            ])

            formatted_tools.append(
                f"{tool['name']}: {tool['description']} - Parameters: {params}"
            )

        return "\n".join(formatted_tools)

    def _generate_response_with_tools(
        self,
        query: str,
        tool_results: List[Dict[str, Any]]
    ) -> str:
        """Generate a response using tool results."""
        # Format tool results for the prompt
        formatted_results = []
        for result in tool_results:
            if result["success"]:
                formatted_results.append(
                    f"Tool {result['tool_name']} returned: {result['result']}"
                )
            else:
                formatted_results.append(
                    f"Tool {result['tool_name']} failed: {result['error']}"
                )

        results_text = "\n".join(formatted_results)

        # Generate response
        response_prompt = f"""
        Generate a helpful response to the user's query using the tool results.

        User query: {query}

        Tool results:
        {results_text}

        Your response should be informative, helpful, and directly address the user's query.
        """

        return self.llm.generate(response_prompt)
