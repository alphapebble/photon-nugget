"""
RAG Engine for Solar Sage.

This module provides the core RAG functionality using the dual-agent architecture.
"""
from typing import Dict, Any, Optional
from agents.orchestrator import AgentOrchestrator
from core.config import get_config

# Initialize the orchestrator
orchestrator = AgentOrchestrator()

def rag_answer(user_query: str) -> str:
    """
    Generate an answer for a user query using the dual-agent RAG workflow.

    Args:
        user_query: User query

    Returns:
        Generated response
    """
    result = orchestrator.process_query(user_query)
    return result["response"]

def enhanced_rag_answer(
    user_query: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    include_weather: bool = False
) -> Dict[str, Any]:
    """
    Generate an enhanced answer with metadata using the dual-agent RAG workflow.

    Args:
        user_query: User query
        lat: Latitude (optional)
        lon: Longitude (optional)
        include_weather: Whether to include weather context

    Returns:
        Dictionary with response and metadata
    """
    return orchestrator.process_query(
        query=user_query,
        lat=lat,
        lon=lon,
        include_weather=include_weather
    )
