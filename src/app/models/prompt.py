from typing import Optional, List
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=5, description="The user's input question.")
    lat: Optional[float] = Field(None, description="Latitude for weather data")
    lon: Optional[float] = Field(None, description="Longitude for weather data")
    include_weather: bool = Field(False, description="Whether to include weather context")
    location_id: Optional[str] = Field(None, description="Location identifier for solar forecasting")
    system_capacity_kw: Optional[float] = Field(None, description="Solar system capacity in kW")
    electricity_rate: Optional[float] = Field(None, description="Electricity rate in currency per kWh")
    feed_in_tariff: Optional[float] = Field(None, description="Feed-in tariff for excess energy in currency per kWh")
    include_solar_forecast: bool = Field(False, description="Whether to include solar forecast context")

class ChatResponse(BaseModel):
    response: str
    has_weather_context: bool = False
    weather_summary: Optional[List[str]] = None
    has_solar_forecast: bool = False
    solar_summary: Optional[List[str]] = None
