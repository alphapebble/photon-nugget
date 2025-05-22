"""
Assignments router for the Project Intelligence API.

This module provides endpoints for accessing assignment recommendations.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class AssignmentCandidate(BaseModel):
    """Assignment candidate data model."""
    name: str
    score: float
    skills_match: float
    workload_factor: float
    reason: str


class AssignmentRecommendation(BaseModel):
    """Assignment recommendation data model."""
    task_id: str
    task_name: str
    project_name: str
    candidates: List[AssignmentCandidate]
    timestamp: str


@router.get("/", response_model=List[AssignmentRecommendation])
async def get_assignment_recommendations(
    request: Request,
    project: Optional[str] = Query(None, description="Filter by project name"),
    limit: int = Query(10, description="Limit the number of recommendations returned"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get assignment recommendations with optional filtering.
    
    Args:
        request: FastAPI request object
        project: Optional project name filter
        limit: Maximum number of recommendations to return
        offset: Offset for pagination
        
    Returns:
        List of filtered assignment recommendations
    """
    # Get assignments from app state
    assignments = request.app.state.assignments
    
    if not assignments:
        return []
    
    # Apply filters
    filtered_assignments = assignments
    
    if project:
        filtered_assignments = [a for a in filtered_assignments if a.get("project_name") == project]
    
    # Apply pagination
    paginated_assignments = filtered_assignments[offset:offset + limit]
    
    return paginated_assignments


@router.get("/task/{task_id}", response_model=AssignmentRecommendation)
async def get_task_assignment(
    request: Request,
    task_id: str,
):
    """
    Get assignment recommendations for a specific task.
    
    Args:
        request: FastAPI request object
        task_id: ID of the task
        
    Returns:
        Assignment recommendation for the task
    """
    # Get assignments from app state
    assignments = request.app.state.assignments
    
    if not assignments:
        raise HTTPException(status_code=404, detail="No assignment recommendations found")
    
    # Find assignment for the specified task
    for assignment in assignments:
        if assignment.get("task_id") == task_id:
            return assignment
    
    raise HTTPException(
        status_code=404,
        detail=f"No assignment recommendation found for task {task_id}"
    )


@router.get("/project/{project_name}", response_model=List[AssignmentRecommendation])
async def get_project_assignments(
    request: Request,
    project_name: str,
    limit: int = Query(10, description="Limit the number of recommendations returned"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get assignment recommendations for a specific project.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        limit: Maximum number of recommendations to return
        offset: Offset for pagination
        
    Returns:
        List of project-specific assignment recommendations
    """
    # Get assignments from app state
    assignments = request.app.state.assignments
    
    if not assignments:
        return []
    
    # Filter for assignments for the specified project
    project_assignments = [a for a in assignments if a.get("project_name") == project_name]
    
    # Apply pagination
    paginated_assignments = project_assignments[offset:offset + limit]
    
    return paginated_assignments


@router.post("/generate", response_model=AssignmentRecommendation)
async def generate_assignment(
    request: Request,
    task_data: Dict,
):
    """
    Generate assignment recommendations for a task.
    
    Args:
        request: FastAPI request object
        task_data: Task data for assignment recommendation
        
    Returns:
        Assignment recommendation for the task
    """
    # This would typically call the AssignmentRecommender in a real implementation
    # For now, return a 501 Not Implemented
    raise HTTPException(
        status_code=501,
        detail="Assignment generation not implemented in the API yet. Use the intelligence module directly."
    )