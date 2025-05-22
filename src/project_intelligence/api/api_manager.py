"""
API Manager for Project Intelligence.

This module provides the APIManager class for setting up and running the FastAPI application
that serves the intelligent features of the project management system.
"""

import logging
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from project_intelligence.api.routers import (
    alerts_router,
    assignments_router,
    audit_router,
    metrics_router,
    projects_router,
    recommendations_router,
)
from project_intelligence.audit.audit_trail import AuditTrailManager, default_audit_manager
from project_intelligence.models.project import Project
from project_intelligence.privacy.pii_masking import PIIMasker, default_pii_masker

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
        audit_manager: Optional[AuditTrailManager] = None,
        pii_masker: Optional[PIIMasker] = None,
    ):
        """
        Initialize the API manager.
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            enable_cors: Whether to enable CORS middleware
            cors_origins: List of allowed CORS origins
            audit_manager: Optional audit trail manager instance
            pii_masker: Optional PII masker instance
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
        
        # Set up audit and privacy
        self.audit_manager = audit_manager or default_audit_manager
        self.pii_masker = pii_masker or default_pii_masker
        
        # Shared data store for the API
        self.projects: Dict[str, Project] = {}
        self.alerts = []
        self.recommendations = []
        self.assignments = []
        self.metrics = {}
        
        # Initialize routers
        self._setup_routers()
        
        # Add middleware for logging and PII masking
        self._setup_middleware()
    
    def _setup_routers(self) -> None:
        """Set up API routers."""
        # Include all routers
        self.app.include_router(alerts_router.router, prefix="/api/alerts", tags=["alerts"])
        self.app.include_router(assignments_router.router, prefix="/api/assignments", tags=["assignments"])
        self.app.include_router(audit_router.router, prefix="/api/audit", tags=["audit"])
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
        self.app.state.audit_manager = self.audit_manager
        self.app.state.pii_masker = self.pii_masker
    
    def _setup_middleware(self) -> None:
        """Set up middleware for logging and PII masking."""
        
        @self.app.middleware("http")
        async def audit_log_middleware(request: Request, call_next):
            # Extract user info from request if available
            user_id = "unknown"
            
            # Try to get user from auth headers
            if "authorization" in request.headers:
                # In a real app, you would decode and validate the token
                user_id = "authenticated_user"  # Placeholder
            
            # Get client info
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
            # Process the request
            response = await call_next(request)
            
            # Log the request with PII masking if needed
            path = request.url.path
            method = request.method
            
            # Skip audit logging for some paths
            if not path.startswith("/api/audit") and not path == "/status":
                # Create audit record for API access
                try:
                    entity_type = path.split("/")[2] if len(path.split("/")) > 2 else "unknown"
                    entity_id = path.split("/")[3] if len(path.split("/")) > 3 else "all"
                    
                    await self.audit_manager.record(
                        user_id=user_id,
                        action=f"api_{method.lower()}",
                        entity_type=entity_type,
                        entity_id=entity_id,
                        metadata={
                            "path": path,
                            "status_code": response.status_code,
                        },
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                except Exception as e:
                    logger.error(f"Error creating audit record: {str(e)}")
            
            return response
        
        @self.app.middleware("http")
        async def pii_masking_middleware(request: Request, call_next):
            # Process the request
            response = await call_next(request)
            
            # Check if response should be masked for PII
            if "application/json" in response.headers.get("content-type", ""):
                # In a real implementation, you would modify the response body
                # to mask PII before returning it to the client
                # This is a simplified example
                pass
            
            return response
    
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
        user_id: str = "system",
    ) -> None:
        """
        Update the data available through the API.
        
        Args:
            projects: Dictionary of project objects
            alerts: List of alert dictionaries
            recommendations: List of recommendation dictionaries
            assignments: List of assignment recommendation dictionaries
            metrics: Dictionary of project metrics
            user_id: User ID for audit trail
        """
        # Track changes for audit trail
        old_projects = list(self.projects.keys())
        new_projects = list(projects.keys())
        
        # Update data
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
        
        # Record audit trail for the update
        try:
            # Log project changes
            added_projects = set(new_projects) - set(old_projects)
            removed_projects = set(old_projects) - set(new_projects)
            updated_projects = set(old_projects).intersection(set(new_projects))
            
            if added_projects or removed_projects or updated_projects:
                await self.audit_manager.record(
                    user_id=user_id,
                    action="update_projects",
                    entity_type="projects",
                    entity_id="all",
                    changes={
                        "projects": {
                            "old": old_projects,
                            "new": new_projects
                        }
                    },
                    metadata={
                        "added": list(added_projects),
                        "removed": list(removed_projects),
                        "updated": list(updated_projects),
                    }
                )
                
            # Log other data updates
            if alerts is not None:
                await self.audit_manager.record(
                    user_id=user_id,
                    action="update_alerts",
                    entity_type="alerts",
                    entity_id="all",
                    metadata={"count": len(alerts)}
                )
                
            if recommendations is not None:
                await self.audit_manager.record(
                    user_id=user_id,
                    action="update_recommendations",
                    entity_type="recommendations",
                    entity_id="all",
                    metadata={"count": len(recommendations)}
                )
                
            if assignments is not None:
                await self.audit_manager.record(
                    user_id=user_id,
                    action="update_assignments",
                    entity_type="assignments",
                    entity_id="all",
                    metadata={"count": len(assignments)}
                )
                
            if metrics is not None:
                await self.audit_manager.record(
                    user_id=user_id,
                    action="update_metrics",
                    entity_type="metrics",
                    entity_id="all",
                    metadata={"timestamp": metrics.get("current_date")}
                )
        except Exception as e:
            logger.error(f"Error recording audit trail: {str(e)}")
        
        logger.info("API data updated successfully")