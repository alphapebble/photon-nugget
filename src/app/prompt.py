from typing import Optional, List
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=5, description="The user's input question.")
    lat: Optional[float] = Field(None, description="Latitude for weather data")
    lon: Optional[float] = Field(None, description="Longitude for weather data")
    include_weather: bool = Field(False, description="Whether to include weather context")

class ChatResponse(BaseModel):
    response: str
    has_weather_context: bool = False
    weather_summary: Optional[List[str]] = None
