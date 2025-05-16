"""
Base Agent class for Solar Sage.

This module provides the base class for all agents in the Solar Sage system.
"""
from llm.llm_factory import get_llm
from typing import Dict, Any, List, Optional

class BaseAgent:
    """Base class for all agents in Solar Sage."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the agent.
        
        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        self.llm = get_llm()  # Use existing LLM factory
        
    def run(self, *args, **kwargs):
        """
        Run the agent. To be implemented by subclasses.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            Agent output
        """
        raise NotImplementedError("Subclasses must implement run method")
