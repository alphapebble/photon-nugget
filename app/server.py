from fastapi import FastAPI
from app.prompt import ChatRequest, ChatResponse
from rag.rag_engine import rag_answer

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
    # Check if we should use weather-enhanced RAG
    use_weather = (
        hasattr(request, 'include_weather') and
        request.include_weather and 
        hasattr(request, 'lat') and
        request.lat is not None and 
        hasattr(request, 'lon') and
        request.lon is not None
    )
    
    # Use weather-enhanced RAG if requested or if query is weather-related
    if WEATHER_RAG_AVAILABLE and (use_weather or is_weather_related_query(request.query)):
        result = weather_enhanced_rag_answer(
            user_query=request.query,
            lat=request.lat if hasattr(request, 'lat') else None,
            lon=request.lon if hasattr(request, 'lon') else None,
            include_weather=True
        )
        return ChatResponse(
            response=result["response"],
            has_weather_context=result["has_weather_context"],
            weather_summary=result["weather_summary"]
        )
    else:
        # Use standard RAG for non-weather queries
        answer = rag_answer(request.query)
        return ChatResponse(
            response=answer,
            has_weather_context=False
        )

# Add a simple GET endpoint for testing
@app.get("/")
async def root():
    return {"message": "Solar Sage API is running"}
