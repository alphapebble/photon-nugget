"""
Main API module for Solar Sage.

This module provides the main FastAPI application for Solar Sage.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_config
from core.logging import get_logger
from api.routes.solar_forecasting import router as solar_router

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Solar Sage API",
    description="API for Solar Sage, a solar energy assistant with RAG capabilities",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(solar_router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Solar Sage API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    host = get_config("api_host", "0.0.0.0")
    port = int(get_config("api_port", 8000))
    
    logger.info(f"Starting Solar Sage API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
