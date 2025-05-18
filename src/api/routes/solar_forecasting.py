"""
Solar Forecasting API routes for Solar Sage.

This module provides API endpoints for solar energy forecasting.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from agents.integrations.solar_forecasting import (
    get_solar_demand_forecast,
    get_cost_savings_analysis
)
from rag.engines.solar_enhanced import solar_enhanced_rag_answer

router = APIRouter(
    prefix="/solar",
    tags=["solar"],
    responses={404: {"description": "Not found"}},
)

class SolarForecastRequest(BaseModel):
    """Request model for solar forecast."""
    
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    location_id: str = Field(..., description="Identifier for the location")
    system_capacity_kw: float = Field(..., description="Capacity of the solar system in kW")
    electricity_rate: Optional[float] = Field(None, description="Electricity rate in currency per kWh")
    feed_in_tariff: Optional[float] = Field(None, description="Feed-in tariff for excess energy in currency per kWh")

class SolarRagRequest(BaseModel):
    """Request model for solar-enhanced RAG."""
    
    query: str = Field(..., description="User query")
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    location_id: str = Field(..., description="Identifier for the location")
    system_capacity_kw: float = Field(..., description="Capacity of the solar system in kW")
    electricity_rate: Optional[float] = Field(None, description="Electricity rate in currency per kWh")
    feed_in_tariff: Optional[float] = Field(None, description="Feed-in tariff for excess energy in currency per kWh")
    include_weather: bool = Field(True, description="Whether to include weather context")
    include_solar_forecast: bool = Field(True, description="Whether to include solar forecast")

@router.post("/forecast")
async def solar_forecast(request: SolarForecastRequest) -> Dict[str, Any]:
    """
    Get a solar energy demand forecast.
    
    Args:
        request: Solar forecast request
        
    Returns:
        Solar energy demand forecast
    """
    try:
        forecast = get_solar_demand_forecast(
            request.latitude,
            request.longitude,
            request.location_id,
            request.system_capacity_kw
        )
        
        return {"forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

@router.post("/cost-savings")
async def cost_savings(request: SolarForecastRequest) -> Dict[str, Any]:
    """
    Get a cost savings analysis for a solar system.
    
    Args:
        request: Solar forecast request
        
    Returns:
        Cost savings analysis
    """
    if request.electricity_rate is None:
        raise HTTPException(status_code=400, detail="Electricity rate is required")
    
    try:
        cost_savings = get_cost_savings_analysis(
            request.latitude,
            request.longitude,
            request.location_id,
            request.system_capacity_kw,
            request.electricity_rate,
            request.feed_in_tariff
        )
        
        return {"cost_savings": cost_savings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cost savings analysis: {str(e)}")

@router.post("/rag")
async def solar_rag(request: SolarRagRequest) -> Dict[str, Any]:
    """
    Get a solar-enhanced RAG response.
    
    Args:
        request: Solar RAG request
        
    Returns:
        Solar-enhanced RAG response
    """
    try:
        response = solar_enhanced_rag_answer(
            user_query=request.query,
            lat=request.latitude,
            lon=request.longitude,
            location_id=request.location_id,
            system_capacity_kw=request.system_capacity_kw,
            electricity_rate=request.electricity_rate,
            feed_in_tariff=request.feed_in_tariff,
            include_weather=request.include_weather,
            include_solar_forecast=request.include_solar_forecast
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating RAG response: {str(e)}")

@router.get("/forecast")
async def get_solar_forecast(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
    location_id: str = Query(..., description="Identifier for the location"),
    system_capacity_kw: float = Query(..., description="Capacity of the solar system in kW")
) -> Dict[str, Any]:
    """
    Get a solar energy demand forecast.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        location_id: Identifier for the location
        system_capacity_kw: Capacity of the solar system in kW
        
    Returns:
        Solar energy demand forecast
    """
    try:
        forecast = get_solar_demand_forecast(
            latitude,
            longitude,
            location_id,
            system_capacity_kw
        )
        
        return {"forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

@router.get("/cost-savings")
async def get_cost_savings(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
    location_id: str = Query(..., description="Identifier for the location"),
    system_capacity_kw: float = Query(..., description="Capacity of the solar system in kW"),
    electricity_rate: float = Query(..., description="Electricity rate in currency per kWh"),
    feed_in_tariff: Optional[float] = Query(None, description="Feed-in tariff for excess energy in currency per kWh")
) -> Dict[str, Any]:
    """
    Get a cost savings analysis for a solar system.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        location_id: Identifier for the location
        system_capacity_kw: Capacity of the solar system in kW
        electricity_rate: Electricity rate in currency per kWh
        feed_in_tariff: Feed-in tariff for excess energy in currency per kWh
        
    Returns:
        Cost savings analysis
    """
    try:
        cost_savings = get_cost_savings_analysis(
            latitude,
            longitude,
            location_id,
            system_capacity_kw,
            electricity_rate,
            feed_in_tariff
        )
        
        return {"cost_savings": cost_savings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cost savings analysis: {str(e)}")

@router.get("/rag")
async def get_solar_rag(
    query: str = Query(..., description="User query"),
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
    location_id: str = Query(..., description="Identifier for the location"),
    system_capacity_kw: float = Query(..., description="Capacity of the solar system in kW"),
    electricity_rate: Optional[float] = Query(None, description="Electricity rate in currency per kWh"),
    feed_in_tariff: Optional[float] = Query(None, description="Feed-in tariff for excess energy in currency per kWh"),
    include_weather: bool = Query(True, description="Whether to include weather context"),
    include_solar_forecast: bool = Query(True, description="Whether to include solar forecast")
) -> Dict[str, Any]:
    """
    Get a solar-enhanced RAG response.
    
    Args:
        query: User query
        latitude: Latitude of the location
        longitude: Longitude of the location
        location_id: Identifier for the location
        system_capacity_kw: Capacity of the solar system in kW
        electricity_rate: Electricity rate in currency per kWh
        feed_in_tariff: Feed-in tariff for excess energy in currency per kWh
        include_weather: Whether to include weather context
        include_solar_forecast: Whether to include solar forecast
        
    Returns:
        Solar-enhanced RAG response
    """
    try:
        response = solar_enhanced_rag_answer(
            user_query=query,
            lat=latitude,
            lon=longitude,
            location_id=location_id,
            system_capacity_kw=system_capacity_kw,
            electricity_rate=electricity_rate,
            feed_in_tariff=feed_in_tariff,
            include_weather=include_weather,
            include_solar_forecast=include_solar_forecast
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating RAG response: {str(e)}")
