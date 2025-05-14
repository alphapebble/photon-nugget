"""
Custom exceptions for Solar Sage.

This module defines custom exceptions used throughout the application.
"""
from typing import Optional, Any, Dict


class SolarSageError(Exception):
    """Base exception for all Solar Sage errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(SolarSageError):
    """Raised when there is a configuration error."""
    pass


class APIError(SolarSageError):
    """Raised when there is an API error."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, details)
        self.status_code = status_code


class LLMError(SolarSageError):
    """Raised when there is an error with the LLM."""
    pass


class RAGError(SolarSageError):
    """Raised when there is an error with the RAG system."""
    pass


class WeatherAPIError(SolarSageError):
    """Raised when there is an error with the Weather API."""
    pass


class AgentError(SolarSageError):
    """Raised when there is an error with an agent."""
    pass


class ToolError(SolarSageError):
    """Raised when there is an error with a tool."""
    pass


class AuthorizationError(SolarSageError):
    """Raised when there is an authorization error."""
    pass
