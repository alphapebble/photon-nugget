"""
Chat API endpoints for Solar Sage.

This module implements FastAPI endpoints for chat interactions.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.prompt import ChatRequest, ChatResponse
from rag.engines.base import rag_answer
from core.logging import get_logger

# Set up logging
logger = get_logger(__name__)

# Import weather-enhanced RAG if available, otherwise use a fallback
try:
    from rag.engines.weather_enhanced import weather_enhanced_rag_answer, is_weather_related_query
    WEATHER_RAG_AVAILABLE = True
except ImportError:
    WEATHER_RAG_AVAILABLE = False

    # Fallback functions if weather_enhanced_rag is not available
    def is_weather_related_query(query: str) -> bool:
        return False

    def weather_enhanced_rag_answer(user_query: str, lat=None, lon=None, include_weather=False):
        answer = rag_answer(user_query)
        return {
            "response": answer,
            "has_weather_context": False,
            "weather_summary": []
        }

# Import solar-enhanced RAG if available, otherwise use a fallback
try:
    from rag.engines.solar_enhanced import solar_enhanced_rag_answer
    from rag.engines.solar_enhanced import format_solar_forecast_context
    SOLAR_RAG_AVAILABLE = True

    def is_solar_forecast_related_query(query: str) -> bool:
        """
        Determine if a query is related to solar forecasting and production.
        """
        forecast_keywords = [
            "forecast", "predict", "production", "output", "generate",
            "kwh", "kilowatt", "energy", "power", "electricity",
            "bill", "cost", "save", "saving", "savings",
            "roi", "return", "investment", "payback", "break even",
            "efficiency", "performance", "expect", "prediction"
        ]

        query_lower = query.lower()

        # Check for forecast-related keywords
        for keyword in forecast_keywords:
            if keyword in query_lower:
                return True

        return False
except ImportError:
    SOLAR_RAG_AVAILABLE = False

    # Fallback functions if solar_enhanced_rag is not available
    def is_solar_forecast_related_query(query: str) -> bool:
        return False

    def solar_enhanced_rag_answer(user_query: str, **kwargs):
        answer = rag_answer(user_query)
        return {
            "response": answer,
            "has_weather_context": False,
            "weather_summary": [],
            "has_solar_forecast": False,
            "solar_summary": []
        }

router = APIRouter()

@router.post("/sage", response_model=ChatResponse)
async def sage(request: ChatRequest):
    """
    Process a chat request and return a response.

    If weather data is requested and coordinates are provided,
    use the weather-enhanced RAG system.

    If solar forecast data is relevant, use the solar-enhanced RAG system.
    """
    try:
        logger.info(f"Received chat request: {request}")

        # Check if we should use weather-enhanced RAG
        use_weather = (
            hasattr(request, 'include_weather') and
            request.include_weather and
            hasattr(request, 'lat') and
            request.lat is not None and
            hasattr(request, 'lon') and
            request.lon is not None
        )

        # Check if we should use solar-enhanced RAG
        use_solar = (
            hasattr(request, 'include_solar_forecast') and
            request.include_solar_forecast and
            hasattr(request, 'lat') and
            request.lat is not None and
            hasattr(request, 'lon') and
            request.lon is not None and
            hasattr(request, 'location_id') and
            request.location_id is not None and
            hasattr(request, 'system_capacity_kw') and
            request.system_capacity_kw is not None
        )

        logger.info(f"Use weather: {use_weather}")
        logger.info(f"Use solar: {use_solar}")
        logger.info(f"WEATHER_RAG_AVAILABLE: {WEATHER_RAG_AVAILABLE}")
        logger.info(f"SOLAR_RAG_AVAILABLE: {SOLAR_RAG_AVAILABLE}")
        logger.info(f"Query: {request.query}")

        if hasattr(request, 'lat') and hasattr(request, 'lon'):
            logger.info(f"Location: lat={request.lat}, lon={request.lon}")

        # Use solar-enhanced RAG if requested or if query is solar forecast-related
        if SOLAR_RAG_AVAILABLE and (use_solar or is_solar_forecast_related_query(request.query)):
            logger.info("Using solar-enhanced RAG")
            try:
                result = solar_enhanced_rag_answer(
                    user_query=request.query,
                    lat=request.lat if hasattr(request, 'lat') else None,
                    lon=request.lon if hasattr(request, 'lon') else None,
                    location_id=request.location_id if hasattr(request, 'location_id') else None,
                    system_capacity_kw=request.system_capacity_kw if hasattr(request, 'system_capacity_kw') else None,
                    electricity_rate=request.electricity_rate if hasattr(request, 'electricity_rate') else None,
                    feed_in_tariff=request.feed_in_tariff if hasattr(request, 'feed_in_tariff') else None,
                    include_weather=use_weather,
                    include_solar_forecast=True
                )
                logger.info("Solar-enhanced RAG completed successfully")
                return ChatResponse(
                    response=result["response"],
                    has_weather_context=result.get("has_weather_context", False),
                    weather_summary=result.get("weather_summary", None),
                    has_solar_forecast=result.get("has_solar_forecast", False),
                    solar_summary=result.get("solar_summary", None)
                )
            except Exception as e:
                logger.error(f"Error in solar-enhanced RAG: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error in solar-enhanced RAG: {str(e)}")
        # Use weather-enhanced RAG if requested or if query is weather-related
        elif WEATHER_RAG_AVAILABLE and (use_weather or is_weather_related_query(request.query)):
            logger.info("Using weather-enhanced RAG")
            try:
                result = weather_enhanced_rag_answer(
                    user_query=request.query,
                    lat=request.lat if hasattr(request, 'lat') else None,
                    lon=request.lon if hasattr(request, 'lon') else None,
                    include_weather=True
                )
                logger.info("Weather-enhanced RAG completed successfully")
                return ChatResponse(
                    response=result["response"],
                    has_weather_context=result["has_weather_context"],
                    weather_summary=result["weather_summary"]
                )
            except Exception as e:
                logger.error(f"Error in weather-enhanced RAG: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error in weather-enhanced RAG: {str(e)}")
        else:
            # Use standard RAG for non-weather, non-solar queries
            logger.info("Using standard RAG")
            try:
                answer = rag_answer(request.query)
                logger.info("Standard RAG completed successfully")
                return ChatResponse(
                    response=answer,
                    has_weather_context=False,
                    has_solar_forecast=False
                )
            except Exception as e:
                logger.error(f"Error in standard RAG: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error in standard RAG: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Add a simple GET endpoint for testing
@router.get("/")
async def root():
    return {"message": "Solar Sage API is running"}

# Keep the /chat endpoint for backward compatibility
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat request and return a response (for backward compatibility).
    This endpoint calls the sage endpoint.
    """
    return await sage(request)
