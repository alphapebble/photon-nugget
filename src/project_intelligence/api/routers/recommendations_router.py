"""
Recommendations router for the Project Intelligence API.

This module provides endpoints for accessing rescheduling recommendations.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class ReschedulableTask(BaseModel):
    """Reschedulable task data model."""
    project_name: str
    task_id: str
    task_name: str
    current_due_date: Optional[str] = None
    suggested_due_date: Optional[str] = None
    priority: Optional[str] = None


class RescheduleRecommendation(BaseModel):
    """Reschedule recommendation data model."""
    type: str
    owner: str
    period_start: str
    period_end: str
    task_count: int
    reschedulable_tasks: List[ReschedulableTask]
    reason: str
    timestamp: str


@router.get("/", response_model=List[RescheduleRecommendation])
async def get_recommendations(
    request: Request,
    owner: Optional[str] = Query(None, description="Filter recommendations by task owner"),
    limit: int = Query(10, description="Limit the number of recommendations returned"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get rescheduling recommendations with optional filtering.
    
    Args:
        request: FastAPI request object
        owner: Optional task owner filter
        limit: Maximum number of recommendations to return
        offset: Offset for pagination
        
    Returns:
        List of filtered recommendations
    """
    # Get recommendations from app state
    recommendations = request.app.state.recommendations
    
    if not recommendations:
        return []
    
    # Apply filters
    filtered_recommendations = recommendations
    
    if owner:
        filtered_recommendations = [r for r in filtered_recommendations if r.get("owner") == owner]
    
    # Apply pagination
    paginated_recommendations = filtered_recommendations[offset:offset + limit]
    
    return paginated_recommendations


@router.get("/upcoming", response_model=List[RescheduleRecommendation])
async def get_upcoming_recommendations(
    request: Request,
    days: int = Query(7, description="Number of days to look ahead"),
    limit: int = Query(10, description="Limit the number of recommendations returned"),
):
    """
    Get upcoming rescheduling recommendations for the next X days.
    
    Args:
        request: FastAPI request object
        days: Number of days to look ahead
        limit: Maximum number of recommendations to return
        
    Returns:
        List of upcoming recommendations
    """
    # Get recommendations from app state
    recommendations = request.app.state.recommendations
    
    if not recommendations:
        return []
    
    # Filter for upcoming recommendations within the specified days
    now = datetime.now()
    upcoming_recommendations = []
    
    for rec in recommendations:
        try:
            period_start = datetime.fromisoformat(rec.get("period_start", ""))
            days_until = (period_start - now).days
            
            if 0 <= days_until <= days:
                upcoming_recommendations.append(rec)
        except (ValueError, TypeError):
            # Skip recommendations with invalid date format
            continue
    
    # Sort by start date and apply limit
    upcoming_recommendations.sort(
        key=lambda r: datetime.fromisoformat(r.get("period_start", "9999-12-31"))
    )
    limited_recommendations = upcoming_recommendations[:limit]
    
    return limited_recommendations


@router.get("/by-project/{project_name}", response_model=List[RescheduleRecommendation])
async def get_project_recommendations(
    request: Request,
    project_name: str,
    limit: int = Query(10, description="Limit the number of recommendations returned"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get rescheduling recommendations for a specific project.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        limit: Maximum number of recommendations to return
        offset: Offset for pagination
        
    Returns:
        List of project-specific recommendations
    """
    # Get recommendations from app state
    recommendations = request.app.state.recommendations
    
    if not recommendations:
        return []
    
    # Filter for recommendations containing tasks from the specified project
    project_recommendations = []
    
    for rec in recommendations:
        reschedulable_tasks = rec.get("reschedulable_tasks", [])
        project_tasks = [
            t for t in reschedulable_tasks if t.get("project_name") == project_name
        ]
        
        if project_tasks:
            # Create a copy of the recommendation with only project-specific tasks
            rec_copy = rec.copy()
            rec_copy["reschedulable_tasks"] = project_tasks
            project_recommendations.append(rec_copy)
    
    # Apply pagination
    paginated_recommendations = project_recommendations[offset:offset + limit]
    
    return paginated_recommendations


@router.get("/by-owner/{owner}", response_model=List[RescheduleRecommendation])
async def get_owner_recommendations(
    request: Request,
    owner: str,
    limit: int = Query(10, description="Limit the number of recommendations returned"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get rescheduling recommendations for a specific owner.
    
    Args:
        request: FastAPI request object
        owner: Task owner
        limit: Maximum number of recommendations to return
        offset: Offset for pagination
        
    Returns:
        List of owner-specific recommendations
    """
    # Get recommendations from app state
    recommendations = request.app.state.recommendations
    
    if not recommendations:
        return []
    
    # Filter for recommendations for the specified owner
    owner_recommendations = [r for r in recommendations if r.get("owner") == owner]
    
    # Apply pagination
    paginated_recommendations = owner_recommendations[offset:offset + limit]
    
    return paginated_recommendations