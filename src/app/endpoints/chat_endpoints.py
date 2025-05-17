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
        contexts, answer = rag_answer(user_query)
        return {
            "response": answer,
            "has_weather_context": False,
            "weather_summary": []
        }

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat request and return a response.

    If weather data is requested and coordinates are provided,
    use the weather-enhanced RAG system.
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

        logger.info(f"Use weather: {use_weather}")
        logger.info(f"WEATHER_RAG_AVAILABLE: {WEATHER_RAG_AVAILABLE}")
        logger.info(f"Query: {request.query}")

        if hasattr(request, 'lat') and hasattr(request, 'lon'):
            logger.info(f"Location: lat={request.lat}, lon={request.lon}")

        # Use weather-enhanced RAG if requested or if query is weather-related
        if WEATHER_RAG_AVAILABLE and (use_weather or is_weather_related_query(request.query)):
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
            # Use standard RAG for non-weather queries
            logger.info("Using standard RAG")
            try:
                answer = rag_answer(request.query)
                logger.info("Standard RAG completed successfully")
                return ChatResponse(
                    response=answer,
                    has_weather_context=False
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
