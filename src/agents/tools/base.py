"""
Base Tool class for Solar Sage.

This module provides the base class for all tools in the Solar Sage system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel

class Tool(ABC):
    """Base class for all tools in Solar Sage."""
    
    name: str = ""
    description: str = ""
    input_schema: Type[BaseModel] = None
    
    def __init__(self):
        """Initialize the tool."""
        if not self.name:
            raise ValueError("Tool name must be specified")
        if not self.description:
            raise ValueError("Tool description must be specified")
        if not self.input_schema:
            raise ValueError("Tool input schema must be specified")
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the tool with the given parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution results
        """
        # Validate input using the schema
        validated_input = self.input_schema(**kwargs)
        
        # Run the tool implementation
        result = self._run(**validated_input.dict())
        
        return result
    
    @abstractmethod
    def _run(self, **kwargs) -> Dict[str, Any]:
        """
        Implement the tool logic. To be implemented by subclasses.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution results
        """
        pass
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Format the result for display to the user.
        
        Args:
            result: Result from the tool
            
        Returns:
            Formatted result string
        """
        return str(result)
