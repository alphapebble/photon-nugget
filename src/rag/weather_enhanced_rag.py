"""
Weather-enhanced RAG module for Solar Sage.

This module extends the standard RAG engine with weather context
to provide more relevant and personalized answers about solar energy production.
It uses the dual-agent architecture for improved separation of concerns.
"""

from typing import Dict, Any, Optional
from rag.rag_engine import enhanced_rag_answer

def is_weather_related_query(query: str) -> bool:
    """
    Determine if a query is related to weather and solar production.

    Args:
        query: User's question

    Returns:
        Boolean indicating if query is weather-related
    """
    weather_keywords = [
        "weather", "cloud", "rain", "sunny", "forecast",
        "today", "tomorrow", "week", "production", "output",
        "efficiency", "performance", "expect", "prediction",
        "humidity", "temperature", "hot", "cold", "wind",
        "storm", "snow", "fog", "dust", "heatwave", "winter",
        "summer", "spring", "fall", "autumn", "season"
    ]

    query_lower = query.lower()

    # Check for weather-related keywords
    for keyword in weather_keywords:
        if keyword in query_lower:
            return True

    # Check for time-related phrases that might imply weather interest
    time_phrases = ["will", "today", "tomorrow", "next week", "this week", "forecast"]
    for phrase in time_phrases:
        if phrase in query_lower:
            return True

    return False

def get_default_location() -> Dict[str, float]:
    """
    Get default location coordinates.
    This could be extended to load from user preferences.

    Returns:
        Dictionary with lat and lon
    """
    # Default to San Francisco
    return {
        "lat": 37.7749,
        "lon": -122.4194
    }

def handle_weather_query(query: str, user_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Handle a weather-related query about solar production.

    Args:
        query: User's question
        user_location: User's location coordinates (optional)

    Returns:
        Response dictionary
    """
    # Use provided location or default
    location = user_location or get_default_location()

    # Generate enhanced RAG response using the dual-agent architecture
    return enhanced_rag_answer(
        user_query=query,
        lat=location.get("lat"),
        lon=location.get("lon"),
        include_weather=True
    )

def weather_enhanced_rag_answer(
    user_query: str,
    lat: float = None,
    lon: float = None,
    include_weather: bool = True
) -> Dict[str, Any]:
    """
    Generate an answer using RAG with weather context enhancement.

    Args:
        user_query: User's question
        lat: Latitude (optional)
        lon: Longitude (optional)
        include_weather: Whether to include weather context

    Returns:
        Dictionary with response and metadata
    """
    # Use the enhanced_rag_answer function from the dual-agent architecture
    return enhanced_rag_answer(
        user_query=user_query,
        lat=lat,
        lon=lon,
        include_weather=include_weather
    )
