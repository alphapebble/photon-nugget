from fastapi import FastAPI, HTTPException
import uvicorn
from typing import Optional

from app.prompt import ChatRequest, ChatResponse
from rag.rag_engine import rag_answer
from core.config import get_config
from core.logging import get_logger, setup_logging

# Set up logging
setup_logging(log_file="./logs/api_server.log")
logger = get_logger(__name__)

# Import weather-enhanced RAG if available, otherwise use a fallback
try:
    from rag.weather_enhanced_rag import weather_enhanced_rag_answer, is_weather_related_query
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

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
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
@app.get("/")
async def root():
    return {"message": "Solar Sage API is running"}


def run_server(host: Optional[str] = None, port: Optional[int] = None) -> None:
    """
    Run the API server.

    Args:
        host: Host to run the server on
        port: Port to run the server on
    """
    # Get configuration
    server_host = host or get_config("api_host", "0.0.0.0")
    server_port = port or int(get_config("api_port", "8000"))

    logger.info(f"Starting API server on {server_host}:{server_port}")

    # Run the server
    try:
        # Try to determine the correct module path
        import inspect
        import sys

        # Get the current module's file path
        current_file = inspect.getfile(inspect.currentframe())

        # Always use app.server:app since we're setting PYTHONPATH correctly
        module_path = "app.server:app"

        logger.info(f"Using module path: {module_path}")

        # Import uvicorn again to avoid shadowing
        import uvicorn as uvicorn_run

        uvicorn_run.run(
            module_path,
            host=server_host,
            port=server_port,
            reload=str(get_config("debug", "False")).lower() == "true"
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        # Fallback to running the app directly
        import uvicorn.config
        config = uvicorn.config.Config(app=app, host=server_host, port=server_port)
        server = uvicorn.Server(config)
        server.run()
