"""
Projects router for the Project Intelligence API.

This module provides endpoints for accessing project data.
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from project_intelligence.audit.audit_trail import default_audit_manager

logger = logging.getLogger(__name__)

router = APIRouter()





class StatusChange(BaseModel):
    """Status change data model."""
    timestamp: str
    user_id: str
    old_status: str
    new_status: str


class TaskBasic(BaseModel):
    """Basic task data model."""
    id: str
    name: str
    status: str
    priority: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None
    completion_percentage: Optional[float] = None
    last_modified_by: Optional[str] = None
    last_status_change: Optional[StatusChange] = None


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
    last_modified_by: Optional[str] = None
    last_status_change: Optional[StatusChange] = None


class AuditRecord(BaseModel):
    """Audit record data model."""
    id: str
    timestamp: str
    user_id: str
    action: str
    changes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectDetail(ProjectSummary):
    """Project detail data model."""
    tasks: Dict[str, TaskBasic]
    team_members: List[str]
    status_history: Optional[List[StatusChange]] = None
    

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
            "last_modified_by": project.last_modified_by,
            "last_status_change": project.status_change_history[-1] if project.status_change_history else None,
        }
        
        project_summaries.append(summary)
    
    # Apply status filter
    if status:
        project_summaries = [p for p in project_summaries if p.get("status") == status]
    
    # Apply pagination
    paginated_summaries = project_summaries[offset:offset + limit]
    
    return paginated_summaries


@router.get("/{project_name}/audit", response_model=List[AuditRecord])
async def get_project_audit_trail(
    request: Request,
    project_name: str,
    limit: int = Query(50, description="Maximum number of records to return"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get audit trail for a specific project.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        limit: Maximum number of records to return
        offset: Offset for pagination
        
    Returns:
        List of audit records for the project
    """
    # Get projects from app state
    projects = request.app.state.projects
    
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    # Get audit records for project
    try:
        audit_records = await default_audit_manager.get_records(
            entity_type="project",
            entity_id=project_name,
            limit=limit,
            offset=offset,
        )
        
        # Convert to response format
        return [
            {
                "id": record.id,
                "timestamp": record.timestamp.isoformat(),
                "user_id": record.user_id,
                "action": record.action,
                "changes": record.changes,
                "metadata": record.metadata,
            }
            for record in audit_records
        ]
    except Exception as e:
        logger.error(f"Error getting audit trail: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving audit trail")


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
            "last_modified_by": getattr(task, "last_modified_by", None),
            "last_status_change": task.get_last_status_change() if hasattr(task, "get_last_status_change") else None,
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
        "last_modified_by": project.last_modified_by,
        "last_status_change": project.status_change_history[-1] if project.status_change_history else None,
        "status_history": project.status_change_history,
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


@router.get("/{project_name}/task/{task_id}/audit", response_model=List[AuditRecord])
async def get_task_audit_trail(
    request: Request,
    project_name: str,
    task_id: str,
    limit: int = Query(50, description="Maximum number of records to return"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get audit trail for a specific task.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        task_id: ID of the task
        limit: Maximum number of records to return
        offset: Offset for pagination
        
    Returns:
        List of audit records for the task
    """
    # Get projects from app state
    projects = request.app.state.projects
    
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    project = projects[project_name]
    
    if task_id not in project.tasks:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found in project '{project_name}'")
    
    # Get audit records for task
    try:
        audit_records = await default_audit_manager.get_records(
            entity_type="task",
            entity_id=task_id,
            limit=limit,
            offset=offset,
        )
        
        # Convert to response format
        return [
            {
                "id": record.id,
                "timestamp": record.timestamp.isoformat(),
                "user_id": record.user_id,
                "action": record.action,
                "changes": record.changes,
                "metadata": record.metadata,
            }
            for record in audit_records
        ]
    except Exception as e:
        logger.error(f"Error getting task audit trail: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving task audit trail")


@router.get("/{project_name}/task/{task_id}/last-modifier", response_model=Dict[str, Any])
async def get_task_last_modifier(
    request: Request,
    project_name: str,
    task_id: str,
    field: Optional[str] = Query(None, description="Specific field to check, e.g., 'status'"),
):
    """
    Get information about who last modified a task or a specific field.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        task_id: ID of the task
        field: Optional specific field to check
        
    Returns:
        Information about the last modifier
    """
    # Get projects from app state
    projects = request.app.state.projects
    
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    project = projects[project_name]
    
    if task_id not in project.tasks:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found in project '{project_name}'")
    
    # Get last modifier info
    try:
        modifier_info = await default_audit_manager.get_last_modifier(
            entity_type="task",
            entity_id=task_id,
            field=field,
        )
        
        if not modifier_info:
            return {
                "user_id": project.tasks[task_id].last_modified_by or "unknown",
                "timestamp": project.tasks[task_id].updated_at.isoformat() if project.tasks[task_id].updated_at else None,
                "note": "No detailed audit records found, using basic task information"
            }
        
        return modifier_info
    except Exception as e:
        logger.error(f"Error getting last modifier: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving last modifier information")