"""
Solar Forecasting Tool for the RAG system.

This tool provides solar energy forecasting capabilities to the RAG system,
allowing it to generate insights about solar energy production and cost savings.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from agents.integrations.solar_forecasting import (
    get_solar_demand_forecast,
    get_cost_savings_analysis
)
from agents.tools.base import Tool

class SolarForecastingInput(BaseModel):
    """Input for the solar forecasting tool."""
    
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    location_id: str = Field(..., description="Identifier for the location")
    system_capacity_kw: float = Field(
        ..., description="Capacity of the solar system in kW"
    )
    electricity_rate: Optional[float] = Field(
        None, description="Electricity rate in currency per kWh"
    )
    feed_in_tariff: Optional[float] = Field(
        None, description="Feed-in tariff for excess energy in currency per kWh"
    )

class SolarForecastingTool(Tool):
    """Tool for solar energy forecasting."""
    
    name = "solar_forecasting"
    description = """
    Generate solar energy demand forecasts and cost savings analysis.
    
    This tool provides:
    1. Solar energy production forecasts based on weather and location
    2. Energy demand forecasts based on historical usage patterns
    3. Cost savings analysis based on electricity rates and feed-in tariffs
    
    Use this tool when the user wants to:
    - Understand how much energy their solar system will produce
    - Estimate cost savings from a solar installation
    - Optimize their energy usage based on solar production
    - Plan for energy storage needs
    """
    
    input_schema = SolarForecastingInput
    
    def _run(self, latitude: float, longitude: float, location_id: str, 
             system_capacity_kw: float, electricity_rate: Optional[float] = None,
             feed_in_tariff: Optional[float] = None) -> Dict[str, Any]:
        """
        Run the solar forecasting tool.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            location_id: Identifier for the location
            system_capacity_kw: Capacity of the solar system in kW
            electricity_rate: Electricity rate in currency per kWh
            feed_in_tariff: Feed-in tariff for excess energy in currency per kWh
            
        Returns:
            Solar energy forecast and cost savings analysis
        """
        # Get the solar demand forecast
        forecast = get_solar_demand_forecast(
            latitude, longitude, location_id, system_capacity_kw
        )
        
        # If electricity rate is provided, get cost savings analysis
        cost_savings = None
        if electricity_rate is not None:
            cost_savings = get_cost_savings_analysis(
                latitude, longitude, location_id, system_capacity_kw,
                electricity_rate, feed_in_tariff
            )
        
        # Format the response
        response = {
            "forecast": forecast,
            "cost_savings": cost_savings
        }
        
        return response
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Format the result for display to the user.
        
        Args:
            result: Result from the tool
            
        Returns:
            Formatted result string
        """
        forecast = result["forecast"]
        cost_savings = result["cost_savings"]
        
        # Format the forecast
        output = "# Solar Energy Forecast\n\n"
        
        # System information
        output += f"## System Information\n"
        output += f"- Location: {forecast['location']['lat']}, {forecast['location']['lon']}\n"
        output += f"- System Capacity: {forecast['system_capacity_kw']} kW\n"
        output += f"- Forecast Generated: {forecast['generated_at']}\n\n"
        
        # Daily forecast summary
        output += f"## Daily Forecast Summary\n\n"
        output += "| Date | Production (kWh) | Demand (kWh) | Net (kWh) |\n"
        output += "|------|-----------------|--------------|----------|\n"
        
        for day in forecast["daily_forecast"]:
            output += f"| {day['date']} | {day['production']:.1f} | {day['demand']:.1f} | {day['net']:.1f} |\n"
        
        output += "\n"
        
        # Cost savings analysis if available
        if cost_savings:
            output += f"## Cost Savings Analysis\n\n"
            
            summary = cost_savings["summary"]
            output += f"### Summary ({summary['roi_days']} days)\n\n"
            output += f"- Total Consumption Cost: ${summary['total_consumption_cost']:.2f}\n"
            output += f"- Total Production Value: ${summary['total_production_value']:.2f}\n"
            output += f"- Grid Purchase Cost: ${summary['total_grid_purchase_cost']:.2f}\n"
            output += f"- Grid Export Revenue: ${summary['total_grid_export_revenue']:.2f}\n"
            output += f"- **Net Savings: ${summary['total_net_savings']:.2f}**\n\n"
            
            output += f"### Daily Savings\n\n"
            output += "| Date | Consumption Cost | Production Value | Grid Purchase Cost | Grid Export Revenue | Net Savings |\n"
            output += "|------|-----------------|------------------|-------------------|-------------------|------------|\n"
            
            for day in cost_savings["daily_savings"]:
                output += f"| {day['date']} | ${day['consumption_cost']:.2f} | ${day['production_value']:.2f} | "
                output += f"${day['grid_purchase_cost']:.2f} | ${day['grid_export_revenue']:.2f} | ${day['net_savings']:.2f} |\n"
        
        # Add insights
        output += "\n## Insights\n\n"
        
        # Production insights
        total_production = sum(day["production"] for day in forecast["daily_forecast"])
        total_demand = sum(day["demand"] for day in forecast["daily_forecast"])
        coverage_percent = (total_production / total_demand * 100) if total_demand > 0 else 0
        
        output += f"- Your solar system is expected to produce {total_production:.1f} kWh over the next {forecast['forecast_horizon_days']} days.\n"
        output += f"- This covers approximately {coverage_percent:.1f}% of your expected energy demand.\n"
        
        # Best production day
        best_day = max(forecast["daily_forecast"], key=lambda x: x["production"])
        output += f"- The best day for production is {best_day['date']} with {best_day['production']:.1f} kWh expected.\n"
        
        # Cost insights if available
        if cost_savings:
            daily_savings = cost_savings["summary"]["total_net_savings"] / summary["roi_days"]
            annual_estimate = daily_savings * 365
            
            output += f"- Your estimated daily savings are ${daily_savings:.2f}, which projects to ${annual_estimate:.2f} annually.\n"
            
            # ROI calculation (simplified)
            system_cost_estimate = forecast["system_capacity_kw"] * 1000  # Rough estimate: $1000 per kW
            simple_payback_years = system_cost_estimate / annual_estimate if annual_estimate > 0 else float('inf')
            
            if simple_payback_years < float('inf'):
                output += f"- Based on these savings, a {forecast['system_capacity_kw']} kW system might pay for itself in approximately {simple_payback_years:.1f} years.\n"
        
        return output
