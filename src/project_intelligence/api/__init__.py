"""
API module for Project Intelligence.

This module provides FastAPI endpoints for accessing the intelligent features
of the project management system.
"""

from project_intelligence.api.api_manager import APIManager
from project_intelligence.api.routers import (
    alerts_router,
    assignments_router,
    metrics_router,
    projects_router,
    recommendations_router,
)

__all__ = [
    "APIManager",
    "alerts_router",
    "assignments_router",
    "metrics_router",
    "projects_router",
    "recommendations_router",
]