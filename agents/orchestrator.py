"""
Agent Orchestrator for Solar Sage.

This module orchestrates the dual-agent workflow for Solar Sage.
"""
from agents.retriever_agent import RetrieverAgent
from agents.response_generator_agent import ResponseGeneratorAgent
from agents.weather_integration import get_weather_context_for_rag
from typing import Dict, Any, List, Optional
from core.config import get_config

class AgentOrchestrator:
    """Orchestrates the dual-agent workflow."""
    
    def __init__(self):
        """Initialize the orchestrator with agents."""
        self.retriever_agent = RetrieverAgent()
        self.response_generator_agent = ResponseGeneratorAgent()
    
    def process_query(
        self, 
        query: str, 
        lat: Optional[float] = None, 
        lon: Optional[float] = None,
        include_weather: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user query through the dual-agent workflow.
        
        Args:
            query: User query
            lat: Latitude (optional)
            lon: Longitude (optional)
            include_weather: Whether to include weather context
            
        Returns:
            Dictionary with response and metadata
        """
        # Step 1: User Query (already received as input)
        
        # Step 2: Fetch Context
        max_documents = int(get_config("max_context_documents", 5))
        context = self.retriever_agent.fetch_context(query, max_documents)
        
        # Step 3: Return Context (internal step)
        
        # Step 4: Generate Insights (optional)
        notes = []
        weather_summary = None
        
        # Add weather insights if requested and coordinates provided
        if include_weather and lat is not None and lon is not None:
            try:
                weather_context = get_weather_context_for_rag(lat, lon)
                if weather_context:
                    notes.append(weather_context)
                    weather_summary = ["Weather data successfully incorporated"]
            except Exception as e:
                weather_summary = [f"Error fetching weather data: {str(e)}"]
        
        # Step 5: Generate Response
        response = self.response_generator_agent.generate_response(query, context, notes)
        
        # Step 6: Output Response
        return {
            "response": response,
            "has_weather_context": bool(notes),
            "weather_summary": weather_summary
        }
