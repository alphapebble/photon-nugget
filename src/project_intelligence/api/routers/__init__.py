"""
API routers for Project Intelligence.

This package contains FastAPI routers for different endpoints
of the Project Intelligence API.
"""

from project_intelligence.api.routers import (
    alerts_router,
    assignments_router,
    metrics_router,
    projects_router,
    recommendations_router,
)

__all__ = [
    "alerts_router",
    "assignments_router",
    "metrics_router",
    "projects_router",
    "recommendations_router",
]