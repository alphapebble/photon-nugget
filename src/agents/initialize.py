"""
Agent Initialization for Solar Sage.

This module handles the initialization of the agent system, including
registering tools and setting up the agent engine.
"""
from typing import Optional
from llm.base import LLMInterface
from llm.llm_factory import get_llm
from agents.tool_registry import ToolRegistry
from agents.memory_system import MemorySystem
from agents.agent_engine import AgentEngine
from agents.tools.weather_tools import (
    get_current_weather,
    get_weather_forecast,
    get_production_forecast,
    get_weather_alerts
)


def initialize_tools(registry: ToolRegistry) -> None:
    """
    Register all available tools with the registry.

    Args:
        registry: Tool registry to register tools with
    """
    # TODO: Register all available tools
    # Weather tools
    registry.register_tool(
        tool_name="get_current_weather",
        tool_function=get_current_weather,
        tool_description="Get current weather conditions for a location",
        required_params=["location"],
        optional_params=["units"],
        authorization_required=False
    )

    registry.register_tool(
        tool_name="get_weather_forecast",
        tool_function=get_weather_forecast,
        tool_description="Get weather forecast for a location",
        required_params=["location", "days"],
        optional_params=["units"],
        authorization_required=False
    )

    registry.register_tool(
        tool_name="get_production_forecast",
        tool_function=get_production_forecast,
        tool_description="Get solar production forecast based on weather",
        required_params=["location", "system_capacity_kw"],
        optional_params=["days", "panel_type"],
        authorization_required=False
    )

    registry.register_tool(
        tool_name="get_weather_alerts",
        tool_function=get_weather_alerts,
        tool_description="Get weather alerts for a location",
        required_params=["location"],
        optional_params=[],
        authorization_required=False
    )

    # TODO: Register additional tools as they are implemented
    # System tools, notification tools, performance tools, etc.


def initialize_agent(
    llm: Optional[LLMInterface] = None,
    require_authorization: bool = True,
    memory_dir: str = "./data/memory"
) -> AgentEngine:
    """
    Initialize the agent engine with all required components.

    Args:
        llm: Language model interface (created if not provided)
        require_authorization: Whether to require user authorization for tools
        memory_dir: Directory to store memory files

    Returns:
        Initialized agent engine
    """
    # Create LLM if not provided
    if llm is None:
        llm = get_llm()

    # Create tool registry and register tools
    tool_registry = ToolRegistry()
    initialize_tools(tool_registry)

    # Create memory system
    memory_system = MemorySystem(storage_dir=memory_dir)

    # Create and return agent engine
    return AgentEngine(
        llm=llm,
        tool_registry=tool_registry,
        memory_system=memory_system,
        require_authorization=require_authorization
    )
