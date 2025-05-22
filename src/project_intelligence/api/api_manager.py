"""
API Manager for Project Intelligence.

This module provides the APIManager class for setting up and running the FastAPI application
that serves the intelligent features of the project management system.
"""

import logging
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from project_intelligence.api.routers import (
    alerts_router,
    assignments_router,
    metrics_router,
    projects_router,
    recommendations_router,
)
from project_intelligence.models.project import Project

logger = logging.getLogger(__name__)


class APIManager:
    """
    Manages the FastAPI application for serving intelligent project features.
    
    This class sets up the FastAPI application with the necessary routers and
    middleware, and provides methods for running the server and updating the
    data accessed by the API endpoints.
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        enable_cors: bool = True,
        cors_origins: Optional[List[str]] = None,
    ):
        """
        Initialize the API manager.
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            enable_cors: Whether to enable CORS middleware
            cors_origins: List of allowed CORS origins
        """
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="Project Intelligence API",
            description="API for accessing intelligent project management features",
            version="1.0.0",
        )
        
        # Set up CORS if enabled
        if enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=cors_origins or ["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Shared data store for the API
        self.projects: Dict[str, Project] = {}
        self.alerts = []
        self.recommendations = []
        self.assignments = []
        self.metrics = {}
        
        # Initialize routers
        self._setup_routers()
    
    def _setup_routers(self) -> None:
        """Set up API routers."""
        # Include all routers
        self.app.include_router(alerts_router.router, prefix="/api/alerts", tags=["alerts"])
        self.app.include_router(assignments_router.router, prefix="/api/assignments", tags=["assignments"])
        self.app.include_router(metrics_router.router, prefix="/api/metrics", tags=["metrics"])
        self.app.include_router(projects_router.router, prefix="/api/projects", tags=["projects"])
        self.app.include_router(
            recommendations_router.router, prefix="/api/recommendations", tags=["recommendations"]
        )
        
        # Set up context for routers to access shared data
        self.app.state.projects = self.projects
        self.app.state.alerts = self.alerts
        self.app.state.recommendations = self.recommendations
        self.app.state.assignments = self.assignments
        self.app.state.metrics = self.metrics
    
    async def start(self) -> None:
        """Start the API server."""
        logger.info(f"Starting API server on {self.host}:{self.port}")
        
        # Add a healthcheck endpoint
        @self.app.get("/status", tags=["status"])
        async def status():
            return {"status": "ok"}
        
        # Start the server
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def update(
        self,
        projects: Dict[str, Project],
        alerts: List[dict] = None,
        recommendations: List[dict] = None,
        assignments: List[dict] = None,
        metrics: dict = None,
    ) -> None:
        """
        Update the data available through the API.
        
        Args:
            projects: Dictionary of project objects
            alerts: List of alert dictionaries
            recommendations: List of recommendation dictionaries
            assignments: List of assignment recommendation dictionaries
            metrics: Dictionary of project metrics
        """
        self.projects = projects
        self.app.state.projects = projects
        
        if alerts is not None:
            self.alerts = alerts
            self.app.state.alerts = alerts
        
        if recommendations is not None:
            self.recommendations = recommendations
            self.app.state.recommendations = recommendations
        
        if assignments is not None:
            self.assignments = assignments
            self.app.state.assignments = assignments
        
        if metrics is not None:
            self.metrics = metrics
            self.app.state.metrics = metrics
        
        logger.info("API data updated successfully")