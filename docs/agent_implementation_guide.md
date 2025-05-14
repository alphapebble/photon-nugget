# Solar Sage Agent Implementation Guide

This guide provides detailed implementation instructions for transforming the existing Solar Sage application into an Agentic RAG Chatbot.

## Directory Structure

Add the following directories and files to the existing project structure:

```
solar-sage/
├── agents/                   # Existing agents directory
│   ├── weather_agent.py      # Existing weather agent
│   ├── weather_integration.py # Existing weather integration
│   ├── agent_engine.py       # New: Core agent logic
│   ├── tool_registry.py      # New: Tool management
│   └── memory_system.py      # New: Conversation memory
├── tools/                    # New: Tool implementations
│   ├── weather_tools.py      # Weather-related tools
│   ├── system_tools.py       # System configuration tools
│   ├── performance_tools.py  # Performance analysis tools
│   ├── notification_tools.py # Alert and notification tools
│   └── integration_tools.py  # External system integration
├── rag/                      # Existing RAG components
│   ├── rag_engine.py         # Existing RAG engine
│   ├── weather_enhanced_rag.py # Existing weather RAG
│   └── agent_enhanced_rag.py # New: Agent-enhanced RAG
```

## Step 1: Implement Tool Registry

Create `agents/tool_registry.py`:

```python
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
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools.
        
        Returns:
            List of tool configurations
        """
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
```

## Step 2: Implement Memory System

Create `agents/memory_system.py`:

```python
"""
Memory System for Solar Sage Agent.

This module manages conversation history and user preferences.
"""
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

class MemorySystem:
    """Memory system for agent conversations and user preferences."""
    
    def __init__(self, storage_dir: str = "./data/memory"):
        """
        Initialize the memory system.
        
        Args:
            storage_dir: Directory to store memory files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_user_file(self, user_id: str, file_type: str) -> str:
        """Get the path to a user's file."""
        return os.path.join(self.storage_dir, f"{user_id}_{file_type}.json")
    
    def add_interaction(
        self, 
        user_id: str, 
        query: str, 
        response: str, 
        tools_used: Optional[List[str]] = None,
        context_used: Optional[str] = None
    ) -> None:
        """
        Add a new interaction to the user's history.
        
        Args:
            user_id: User identifier
            query: User's query
            response: System's response
            tools_used: List of tools used in the interaction
            context_used: Context information used for the response
        """
        history_file = self._get_user_file(user_id, "history")
        
        # Load existing history or create new
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new interaction
        history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "tools_used": tools_used or [],
            "context_used": context_used
        })
        
        # Save updated history
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
    
    def get_recent_interactions(
        self, 
        user_id: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent interactions for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        history_file = self._get_user_file(user_id, "history")
        
        if not os.path.exists(history_file):
            return []
        
        with open(history_file, "r") as f:
            history = json.load(f)
        
        return history[-limit:]
    
    def store_user_preference(
        self, 
        user_id: str, 
        preference_key: str, 
        preference_value: Any
    ) -> None:
        """
        Store a user preference.
        
        Args:
            user_id: User identifier
            preference_key: Preference name
            preference_value: Preference value
        """
        prefs_file = self._get_user_file(user_id, "preferences")
        
        # Load existing preferences or create new
        if os.path.exists(prefs_file):
            with open(prefs_file, "r") as f:
                preferences = json.load(f)
        else:
            preferences = {}
        
        # Update preference
        preferences[preference_key] = preference_value
        
        # Save updated preferences
        with open(prefs_file, "w") as f:
            json.dump(preferences, f, indent=2)
    
    def get_user_preference(
        self, 
        user_id: str, 
        preference_key: str, 
        default_value: Any = None
    ) -> Any:
        """
        Get a user preference.
        
        Args:
            user_id: User identifier
            preference_key: Preference name
            default_value: Default value if preference not found
            
        Returns:
            Preference value or default
        """
        prefs_file = self._get_user_file(user_id, "preferences")
        
        if not os.path.exists(prefs_file):
            return default_value
        
        with open(prefs_file, "r") as f:
            preferences = json.load(f)
        
        return preferences.get(preference_key, default_value)
```

## Step 3: Implement Agent Engine

Create `agents/agent_engine.py`:

```python
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
from rag.rag_engine import rag_answer
from rag.weather_enhanced_rag import weather_enhanced_rag_answer

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
    
    def _generate_tool_decision(
        self, 
        query: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """
        Generate a decision about whether to use tools.
        
        Args:
            query: User query
            user_context: User context information
            
        Returns:
            Decision text with tool calls if needed
        """
        # List available tools
        tools_list = "\n".join([
            f"- {tool['name']}: {tool['description']} (Params: {', '.join(tool['required_params'])})"
            for tool in self.tool_registry.list_tools()
        ])
        
        # Create prompt for tool decision
        prompt = f"""
You are an intelligent solar energy assistant that can use tools to help users.

USER QUERY: {query}

AVAILABLE TOOLS:
{tools_list}

USER CONTEXT:
- Location: {user_context.get('lat', 'Unknown')}, {user_context.get('lon', 'Unknown')}
- System Size: {user_context.get('system_size_kw', 'Unknown')} kW
- Panel Type: {user_context.get('panel_type', 'Unknown')}

Determine if you need to use any tools to answer this query.
If you need to use a tool, respond with:
USE_TOOL[tool_name](param1=value1, param2=value2)

If you don't need to use a tool, respond with:
NO_TOOL_NEEDED

Your decision:
"""
        
        # Generate decision
        return self.llm.generate(prompt)
    
    def process_query(
        self, 
        query: str, 
        user_id: str,
        user_context: Dict[str, Any],
        user_authorized: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user query.
        
        Args:
            query: User query
            user_id: User identifier
            user_context: User context information
            user_authorized: Whether the user has authorized tool usage
            
        Returns:
            Response with text and metadata
        """
        # Get recent interactions for context
        recent_interactions = self.memory_system.get_recent_interactions(user_id)
        
        # Decide whether to use tools
        tool_decision = self._generate_tool_decision(query, user_context)
        
        # Extract tool calls
        tool_calls = self._extract_tool_calls(tool_decision)
        
        # If tools are needed, execute them
        tools_used = []
        tool_results = []
        
        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call["tool_name"]
                params = tool_call["params"]
                
                try:
                    # Execute tool
                    result = self.tool_registry.execute_tool(
                        tool_name, 
                        params,
                        user_authorized=user_authorized
                    )
                    
                    tools_used.append(tool_name)
                    tool_results.append({
                        "tool": tool_name,
                        "params": params,
                        "result": result
                    })
                except Exception as e:
                    tool_results.append({
                        "tool": tool_name,
                        "params": params,
                        "error": str(e)
                    })
        
        # Generate response based on tool results or RAG
        if tool_results:
            # Format tool results for prompt
            results_text = "\n".join([
                f"TOOL: {result['tool']}\n"
                f"PARAMS: {result['params']}\n"
                f"RESULT: {result.get('result', {}).get('result', 'Error: ' + result.get('error', 'Unknown error'))}\n"
                for result in tool_results
            ])
            
            # Create prompt with tool results
            response_prompt = f"""
You are an intelligent solar energy assistant that helps users with solar energy questions.

USER QUERY: {query}

TOOL RESULTS:
{results_text}

Based on the tool results above, provide a helpful and informative response to the user's query.
Your response should be conversational and easy to understand.
"""
            
            response_text = self.llm.generate(response_prompt)
        else:
            # Use RAG for information queries
            if "lat" in user_context and "lon" in user_context:
                # Use weather-enhanced RAG if location is available
                result = weather_enhanced_rag_answer(
                    user_query=query,
                    lat=user_context.get("lat"),
                    lon=user_context.get("lon"),
                    include_weather=True
                )
                response_text = result["response"]
                context_used = "Weather-enhanced RAG"
            else:
                # Use standard RAG
                response_text = rag_answer(query)
                context_used = "Standard RAG"
        
        # Store interaction in memory
        self.memory_system.add_interaction(
            user_id=user_id,
            query=query,
            response=response_text,
            tools_used=tools_used,
            context_used=context_used if not tool_results else "Tool-based"
        )
        
        # Return response with metadata
        return {
            "response": response_text,
            "tools_used": tools_used,
            "tool_results": tool_results if tool_results else None,
            "requires_authorization": any(
                self.tool_registry.get_tool(tool)["authorization_required"]
                for tool in tools_used
            ) if tools_used else False
        }
```

## Step 4: Implement a Sample Weather Tool

Create `tools/weather_tools.py`:

```python
"""
Weather tools for Solar Sage Agent.

This module implements weather-related tools for the agent.
"""
from typing import Dict, Any, List
from agents.weather_integration import (
    get_weather_for_location,
    estimate_production_impact,
    generate_weather_insights
)

def get_production_forecast(
    lat: float, 
    lon: float, 
    system_capacity_kw: float = 5.0
) -> Dict[str, Any]:
    """
    Get solar production forecast based on weather.
    
    Args:
        lat: Latitude
        lon: Longitude
        system_capacity_kw: System capacity in kW
        
    Returns:
        Production forecast data
    """
    # Get weather data
    weather_data = get_weather_for_location(lat, lon)
    
    # Estimate production impact
    impact = estimate_production_impact(
        weather_data, 
        system_capacity_kw=system_capacity_kw
    )
    
    # Generate insights
    insights = generate_weather_insights(impact)
    
    # Format response
    daily_forecast = []
    for day in impact["daily_forecast"]:
        daily_forecast.append({
            "date": day["date"],
            "expected_kwh": round(day["expected_kwh"], 1),
            "production_factor": round(day["production_factor"] * 100, 1),
            "weather": day["weather"]
        })
    
    return {
        "current": {
            "expected_kwh": round(impact["current"]["expected_kwh"], 1),
            "production_factor": round(impact["current"]["production_factor"] * 100, 1),
            "weather": impact["current"]["weather"]
        },
        "daily_forecast": daily_forecast,
        "insights": insights
    }
```

## Step 5: Register Tools and Initialize Agent

Create `agents/initialize.py`:

```python
"""
Initialize the Solar Sage Agent.

This module sets up the agent with tools and configuration.
"""
from llm.llm_factory import get_llm
from agents.tool_registry import ToolRegistry
from agents.memory_system import MemorySystem
from agents.agent_engine import AgentEngine
from tools.weather_tools import get_production_forecast

def initialize_agent(require_authorization: bool = True) -> AgentEngine:
    """
    Initialize the agent with tools and configuration.
    
    Args:
        require_authorization: Whether to require user authorization for tools
        
    Returns:
        Configured agent engine
    """
    # Initialize components
    llm = get_llm()
    tool_registry = ToolRegistry()
    memory_system = MemorySystem()
    
    # Register tools
    tool_registry.register_tool(
        tool_name="get_production_forecast",
        tool_function=get_production_forecast,
        tool_description="Get solar production forecast based on weather",
        required_params=["lat", "lon"],
        optional_params=["system_capacity_kw"],
        authorization_required=False
    )
    
    # Initialize agent engine
    agent = AgentEngine(
        llm=llm,
        tool_registry=tool_registry,
        memory_system=memory_system,
        require_authorization=require_authorization
    )
    
    return agent
```

## Step 6: Integrate with API Server

Update `app/server.py` to include agent capabilities:

```python
# Add imports
from agents.initialize import initialize_agent

# Initialize agent
agent = initialize_agent(require_authorization=True)

@app.post("/agent_chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    """
    Process a chat request using the agent.
    """
    # Process query with agent
    result = agent.process_query(
        query=request.query,
        user_id=request.user_id,
        user_context={
            "lat": request.lat if hasattr(request, 'lat') else None,
            "lon": request.lon if hasattr(request, 'lon') else None,
            "system_size_kw": request.system_size_kw if hasattr(request, 'system_size_kw') else None,
            "panel_type": request.panel_type if hasattr(request, 'panel_type') else None
        },
        user_authorized=request.authorized if hasattr(request, 'authorized') else False
    )
    
    return AgentChatResponse(
        response=result["response"],
        tools_used=result["tools_used"],
        requires_authorization=result["requires_authorization"]
    )
```

## Conclusion

This implementation guide provides the core components needed to transform Solar Sage into an Agentic RAG Chatbot. Additional tools can be implemented following the same pattern, and the UI can be updated to support agent interactions and authorization requests.

For a complete implementation, you would need to:

1. Implement additional tools in the `tools/` directory
2. Update the UI to handle authorization requests
3. Add visualization components for tool outputs
4. Implement user authentication and session management
5. Add monitoring and logging for agent actions
