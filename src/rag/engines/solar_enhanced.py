"""
Solar-Enhanced RAG Engine for Solar Sage.

This module provides RAG functionality enhanced with solar energy forecasting
and cost savings analysis.
"""
from typing import Dict, Any, Optional
from agents.orchestrator import AgentOrchestrator
from agents.integrations.solar_forecasting import (
    get_solar_demand_forecast,
    get_cost_savings_analysis
)
from agents.integrations.weather import get_weather_context_for_rag
from core.config import get_config
from core.logging import get_logger

logger = get_logger(__name__)

# Initialize the orchestrator
orchestrator = AgentOrchestrator()

def solar_enhanced_rag_answer(
    user_query: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    location_id: Optional[str] = None,
    system_capacity_kw: Optional[float] = None,
    electricity_rate: Optional[float] = None,
    feed_in_tariff: Optional[float] = None,
    include_weather: bool = True,
    include_solar_forecast: bool = True
) -> Dict[str, Any]:
    """
    Generate an enhanced answer with solar forecasting using the dual-agent RAG workflow.

    Args:
        user_query: User query
        lat: Latitude (optional)
        lon: Longitude (optional)
        location_id: Location identifier (optional)
        system_capacity_kw: Solar system capacity in kW (optional)
        electricity_rate: Electricity rate in currency per kWh (optional)
        feed_in_tariff: Feed-in tariff for excess energy in currency per kWh (optional)
        include_weather: Whether to include weather context
        include_solar_forecast: Whether to include solar forecast

    Returns:
        Dictionary with response and metadata
    """
    # Prepare additional context
    additional_context = ""
    
    # Add weather context if requested and location is provided
    if include_weather and lat is not None and lon is not None:
        try:
            weather_context = get_weather_context_for_rag(lat, lon)
            additional_context += weather_context + "\n\n"
        except Exception as e:
            logger.error(f"Error getting weather context: {e}")
    
    # Add solar forecast if requested and required parameters are provided
    if (include_solar_forecast and lat is not None and lon is not None and 
            location_id is not None and system_capacity_kw is not None):
        try:
            # Get solar demand forecast
            forecast = get_solar_demand_forecast(
                lat, lon, location_id, system_capacity_kw
            )
            
            # Get cost savings analysis if electricity rate is provided
            cost_savings = None
            if electricity_rate is not None:
                cost_savings = get_cost_savings_analysis(
                    lat, lon, location_id, system_capacity_kw,
                    electricity_rate, feed_in_tariff
                )
            
            # Format solar forecast context
            solar_context = format_solar_forecast_context(forecast, cost_savings)
            additional_context += solar_context
        except Exception as e:
            logger.error(f"Error getting solar forecast: {e}")
    
    # Process the query with additional context
    result = orchestrator.process_query(
        query=user_query,
        additional_context=additional_context if additional_context else None
    )
    
    # Add solar forecast data to the result if available
    if (include_solar_forecast and lat is not None and lon is not None and 
            location_id is not None and system_capacity_kw is not None):
        try:
            # Get solar demand forecast
            forecast = get_solar_demand_forecast(
                lat, lon, location_id, system_capacity_kw
            )
            
            # Get cost savings analysis if electricity rate is provided
            cost_savings = None
            if electricity_rate is not None:
                cost_savings = get_cost_savings_analysis(
                    lat, lon, location_id, system_capacity_kw,
                    electricity_rate, feed_in_tariff
                )
            
            # Add forecast data to result
            result["solar_forecast"] = {
                "forecast": forecast,
                "cost_savings": cost_savings
            }
        except Exception as e:
            logger.error(f"Error getting solar forecast data: {e}")
    
    return result


def format_solar_forecast_context(
    forecast: Dict[str, Any], cost_savings: Optional[Dict[str, Any]] = None
) -> str:
    """
    Format solar forecast data as context for the RAG system.
    
    Args:
        forecast: Solar demand forecast
        cost_savings: Cost savings analysis
        
    Returns:
        Formatted context string
    """
    context = "SOLAR ENERGY FORECAST CONTEXT:\n"
    
    # System information
    context += f"- System Capacity: {forecast['system_capacity_kw']} kW\n"
    context += f"- Location: {forecast['location']['lat']}, {forecast['location']['lon']}\n\n"
    
    # Daily forecast summary (next 3 days)
    context += "DAILY FORECAST SUMMARY (NEXT 3 DAYS):\n"
    for day in forecast["daily_forecast"][:3]:
        context += f"- {day['date']}: Production: {day['production']:.1f} kWh, "
        context += f"Demand: {day['demand']:.1f} kWh, "
        context += f"Net: {day['net']:.1f} kWh\n"
    
    context += "\n"
    
    # Production insights
    total_production = sum(day["production"] for day in forecast["daily_forecast"])
    total_demand = sum(day["demand"] for day in forecast["daily_forecast"])
    coverage_percent = (total_production / total_demand * 100) if total_demand > 0 else 0
    
    context += "PRODUCTION INSIGHTS:\n"
    context += f"- Expected production over next {forecast['forecast_horizon_days']} days: {total_production:.1f} kWh\n"
    context += f"- Expected demand over next {forecast['forecast_horizon_days']} days: {total_demand:.1f} kWh\n"
    context += f"- Solar coverage of demand: {coverage_percent:.1f}%\n"
    
    # Best production day
    best_day = max(forecast["daily_forecast"], key=lambda x: x["production"])
    context += f"- Best production day: {best_day['date']} with {best_day['production']:.1f} kWh expected\n\n"
    
    # Cost savings if available
    if cost_savings:
        summary = cost_savings["summary"]
        daily_savings = summary["total_net_savings"] / summary["roi_days"]
        annual_estimate = daily_savings * 365
        
        context += "COST SAVINGS INSIGHTS:\n"
        context += f"- Electricity rate: ${summary['electricity_rate']:.2f} per kWh\n"
        context += f"- Feed-in tariff: ${summary['feed_in_tariff']:.2f} per kWh\n"
        context += f"- Estimated daily savings: ${daily_savings:.2f}\n"
        context += f"- Projected annual savings: ${annual_estimate:.2f}\n"
        
        # ROI calculation (simplified)
        system_cost_estimate = forecast["system_capacity_kw"] * 1000  # Rough estimate: $1000 per kW
        simple_payback_years = system_cost_estimate / annual_estimate if annual_estimate > 0 else float('inf')
        
        if simple_payback_years < float('inf'):
            context += f"- Estimated payback period: {simple_payback_years:.1f} years\n"
    
    return context
