"""
Projects router for the Project Intelligence API.

This module provides endpoints for accessing project data.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class TaskBasic(BaseModel):
    """Basic task data model."""
    id: str
    name: str
    status: str
    priority: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None
    completion_percentage: Optional[float] = None


class ProjectSummary(BaseModel):
    """Project summary data model."""
    name: str
    status: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    completion_percentage: float
    task_count: int
    overdue_task_count: int
    blocked_task_count: int


class ProjectDetail(ProjectSummary):
    """Project detail data model."""
    tasks: Dict[str, TaskBasic]
    team_members: List[str]
    

@router.get("/", response_model=List[ProjectSummary])
async def get_projects(
    request: Request,
    status: Optional[str] = Query(None, description="Filter projects by status"),
    limit: int = Query(10, description="Limit the number of projects returned"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get projects with optional filtering.
    
    Args:
        request: FastAPI request object
        status: Optional status filter
        limit: Maximum number of projects to return
        offset: Offset for pagination
        
    Returns:
        List of filtered project summaries
    """
    # Get projects from app state
    projects = request.app.state.projects
    
    if not projects:
        return []
    
    # Create project summaries
    project_summaries = []
    
    for name, project in projects.items():
        # Count tasks by status
        tasks = project.tasks or {}
        overdue_tasks = [
            t for t in tasks.values() 
            if t.due_date and t.due_date < request.app.state.metrics.get("current_date", "") and t.status != "completed"
        ]
        blocked_tasks = [
            t for t in tasks.values() 
            if t.status == "blocked" or (hasattr(t, "blockers") and len(t.blockers) > 0)
        ]
        
        summary = {
            "name": name,
            "status": project.status,
            "description": project.description,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "completion_percentage": project.get_completion_percentage(),
            "task_count": len(tasks),
            "overdue_task_count": len(overdue_tasks),
            "blocked_task_count": len(blocked_tasks),
        }
        
        project_summaries.append(summary)
    
    # Apply status filter
    if status:
        project_summaries = [p for p in project_summaries if p.get("status") == status]
    
    # Apply pagination
    paginated_summaries = project_summaries[offset:offset + limit]
    
    return paginated_summaries


@router.get("/{project_name}", response_model=ProjectDetail)
async def get_project(
    request: Request,
    project_name: str,
):
    """
    Get detailed information for a specific project.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        
    Returns:
        Detailed project information
    """
    # Get projects from app state
    projects = request.app.state.projects
    
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    project = projects[project_name]
    
    # Count tasks by status
    tasks = project.tasks or {}
    task_basics = {}
    
    for task_id, task in tasks.items():
        task_basics[task_id] = {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "priority": task.priority,
            "owner": task.owner,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completion_percentage": task.completion_percentage if hasattr(task, "completion_percentage") else None,
        }
    
    overdue_tasks = [
        t for t in tasks.values() 
        if t.due_date and t.due_date < request.app.state.metrics.get("current_date", "") and t.status != "completed"
    ]
    blocked_tasks = [
        t for t in tasks.values() 
        if t.status == "blocked" or (hasattr(t, "blockers") and len(t.blockers) > 0)
    ]
    
    # Create project detail
    detail = {
        "name": project_name,
        "status": project.status,
        "description": project.description,
        "start_date": project.start_date.isoformat() if project.start_date else None,
        "end_date": project.end_date.isoformat() if project.end_date else None,
        "completion_percentage": project.get_completion_percentage(),
        "task_count": len(tasks),
        "overdue_task_count": len(overdue_tasks),
        "blocked_task_count": len(blocked_tasks),
        "tasks": task_basics,
        "team_members": project.team_members,
    }
    
    return detail


@router.get("/{project_name}/tasks", response_model=Dict[str, TaskBasic])
async def get_project_tasks(
    request: Request,
    project_name: str,
    status: Optional[str] = Query(None, description="Filter tasks by status"),
    owner: Optional[str] = Query(None, description="Filter tasks by owner"),
):
    """
    Get tasks for a specific project with optional filtering.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        status: Optional status filter
        owner: Optional owner filter
        
    Returns:
        Dictionary of filtered tasks
    """
    # Get projects from app state
    projects = request.app.state.projects
    
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    project = projects[project_name]
    tasks = project.tasks or {}
    
    # Create task basics
    task_basics = {}
    
    for task_id, task in tasks.items():
        # Apply filters
        if status and task.status != status:
            continue
        
        if owner and task.owner != owner:
            continue
        
        task_basics[task_id] = {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "priority": task.priority,
            "owner": task.owner,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completion_percentage": task.completion_percentage if hasattr(task, "completion_percentage") else None,
        }
    
    return task_basics


@router.get("/{project_name}/team", response_model=List[str])
async def get_project_team(
    request: Request,
    project_name: str,
):
    """
    Get team members for a specific project.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        
    Returns:
        List of team member names
    """
    # Get projects from app state
    projects = request.app.state.projects
    
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    project = projects[project_name]
    
    return project.team_members or []