"""
Metrics router for the Project Intelligence API.

This module provides endpoints for accessing project metrics, including
burn-down charts and velocity trends.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class DataPoint(BaseModel):
    """Data point for metrics."""
    date: str
    value: Union[float, int]


class VelocityMetrics(BaseModel):
    """Velocity metrics data model."""
    average_velocity: float
    velocity_trend: List[DataPoint]
    completed_points_per_period: List[DataPoint]
    prediction_accuracy: Optional[float] = None


class BurndownMetrics(BaseModel):
    """Burndown metrics data model."""
    remaining_work: List[DataPoint]
    ideal_burndown: List[DataPoint]
    completion_date_projection: Optional[str] = None
    is_on_track: bool


class ProjectMetrics(BaseModel):
    """Project metrics data model."""
    project_name: str
    velocity: VelocityMetrics
    burndown: BurndownMetrics
    completion_percentage: float
    days_ahead_behind: int
    task_completion_rate: float


@router.get("/velocity/{project_name}", response_model=VelocityMetrics)
async def get_velocity_metrics(
    request: Request,
    project_name: str,
    periods: int = Query(6, description="Number of time periods to include"),
    period_type: str = Query("week", description="Type of time period (day, week, sprint)"),
):
    """
    Get velocity metrics for a project.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        periods: Number of time periods to include
        period_type: Type of time period (day, week, sprint)
        
    Returns:
        Velocity metrics
    """
    # Get metrics from app state
    metrics = request.app.state.metrics
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics data available")
    
    # Check if project exists
    projects = request.app.state.projects
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    # Get velocity data for the project
    project_metrics = metrics.get("projects", {}).get(project_name, {})
    velocity_data = project_metrics.get("velocity", {})
    
    if not velocity_data:
        # Generate placeholder data if no velocity data exists
        today = datetime.now()
        velocity_trend = []
        completed_points = []
        
        for i in range(periods):
            if period_type == "day":
                date = (today - timedelta(days=periods-i-1)).isoformat()[:10]
            elif period_type == "sprint":
                date = f"Sprint {i+1}"
            else:  # default to week
                date = f"Week {i+1}"
            
            # Generate some random-ish but sensible data
            value = 8 + (i % 3) - 1  # Values between 7-9
            velocity_trend.append({"date": date, "value": value})
            completed_points.append({"date": date, "value": value})
        
        return {
            "average_velocity": 8.0,
            "velocity_trend": velocity_trend,
            "completed_points_per_period": completed_points,
            "prediction_accuracy": 0.85
        }
    
    # Return actual velocity data
    return {
        "average_velocity": velocity_data.get("average", 0.0),
        "velocity_trend": velocity_data.get("trend", []),
        "completed_points_per_period": velocity_data.get("completed_points", []),
        "prediction_accuracy": velocity_data.get("prediction_accuracy")
    }


@router.get("/burndown/{project_name}", response_model=BurndownMetrics)
async def get_burndown_metrics(
    request: Request,
    project_name: str,
):
    """
    Get burndown metrics for a project.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        
    Returns:
        Burndown metrics
    """
    # Get metrics from app state
    metrics = request.app.state.metrics
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics data available")
    
    # Check if project exists
    projects = request.app.state.projects
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    # Get burndown data for the project
    project_metrics = metrics.get("projects", {}).get(project_name, {})
    burndown_data = project_metrics.get("burndown", {})
    
    if not burndown_data:
        # Generate placeholder data if no burndown data exists
        project = projects[project_name]
        total_points = sum(task.story_points for task in project.tasks.values() if hasattr(task, "story_points"))
        total_points = total_points or 100  # Default if no story points
        
        start_date = project.start_date or (datetime.now() - timedelta(days=30))
        end_date = project.end_date or (datetime.now() + timedelta(days=30))
        
        days_total = (end_date - start_date).days
        days_elapsed = (datetime.now() - start_date).days
        
        # Generate remaining work points
        remaining_work = []
        ideal_burndown = []
        
        for day in range(days_total + 1):
            date = (start_date + timedelta(days=day)).isoformat()[:10]
            
            # Ideal burndown is a straight line from total to 0
            ideal_value = total_points * (1 - day / days_total)
            ideal_burndown.append({"date": date, "value": ideal_value})
            
            # Actual burndown (simulated with some variation)
            if day <= days_elapsed:
                # For past days, simulate actual progress
                progress_factor = day / days_total
                random_factor = 0.1 * ((day % 3) - 1)  # Small random variation
                actual_value = total_points * (1 - progress_factor + random_factor)
                actual_value = max(0, actual_value)  # Ensure non-negative
                remaining_work.append({"date": date, "value": actual_value})
        
        # Determine if on track
        latest_value = remaining_work[-1]["value"] if remaining_work else total_points
        ideal_value_now = ideal_burndown[days_elapsed]["value"] if days_elapsed < len(ideal_burndown) else 0
        is_on_track = latest_value <= ideal_value_now * 1.1  # Within 10% of ideal
        
        return {
            "remaining_work": remaining_work,
            "ideal_burndown": ideal_burndown,
            "completion_date_projection": end_date.isoformat()[:10],
            "is_on_track": is_on_track
        }
    
    # Return actual burndown data
    return {
        "remaining_work": burndown_data.get("remaining_work", []),
        "ideal_burndown": burndown_data.get("ideal_burndown", []),
        "completion_date_projection": burndown_data.get("completion_date_projection"),
        "is_on_track": burndown_data.get("is_on_track", False)
    }


@router.get("/project/{project_name}", response_model=ProjectMetrics)
async def get_project_metrics(
    request: Request,
    project_name: str,
):
    """
    Get comprehensive metrics for a project.
    
    Args:
        request: FastAPI request object
        project_name: Name of the project
        
    Returns:
        Comprehensive project metrics
    """
    # Get metrics from app state
    metrics = request.app.state.metrics
    
    # Check if project exists
    projects = request.app.state.projects
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    
    # Get velocity data
    velocity_metrics = await get_velocity_metrics(request, project_name)
    
    # Get burndown data
    burndown_metrics = await get_burndown_metrics(request, project_name)
    
    # Get project completion percentage
    project = projects[project_name]
    completion_percentage = project.get_completion_percentage()
    
    # Calculate days ahead/behind schedule
    days_ahead_behind = 0
    if burndown_metrics.remaining_work and burndown_metrics.ideal_burndown:
        latest_actual = burndown_metrics.remaining_work[-1]["value"]
        
        # Find where this value would be on the ideal burndown
        for i, point in enumerate(burndown_metrics.ideal_burndown):
            if point["value"] <= latest_actual:
                ideal_date = datetime.fromisoformat(point["date"])
                actual_date = datetime.now()
                days_ahead_behind = (ideal_date - actual_date).days
                break
    
    # Calculate task completion rate
    task_completion_rate = 0.0
    completed_tasks = [t for t in project.tasks.values() if t.status == "completed"]
    total_tasks = len(project.tasks)
    
    if total_tasks > 0:
        task_completion_rate = len(completed_tasks) / total_tasks
    
    return {
        "project_name": project_name,
        "velocity": velocity_metrics,
        "burndown": burndown_metrics,
        "completion_percentage": completion_percentage,
        "days_ahead_behind": days_ahead_behind,
        "task_completion_rate": task_completion_rate
    }


@router.get("/summary", response_model=Dict)
async def get_metrics_summary(
    request: Request,
):
    """
    Get a summary of metrics across all projects.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Summary metrics
    """
    # Get metrics from app state
    metrics = request.app.state.metrics
    
    if not metrics:
        # Return placeholder summary if no metrics
        return {
            "total_projects": 0,
            "projects_on_track": 0,
            "projects_at_risk": 0,
            "projects_behind": 0,
            "average_completion": 0.0,
            "average_velocity": 0.0
        }
    
    # Get projects
    projects = request.app.state.projects
    total_projects = len(projects)
    
    if total_projects == 0:
        return {
            "total_projects": 0,
            "projects_on_track": 0,
            "projects_at_risk": 0, 
            "projects_behind": 0,
            "average_completion": 0.0,
            "average_velocity": 0.0
        }
    
    # Calculate summary metrics
    projects_on_track = 0
    projects_at_risk = 0
    projects_behind = 0
    total_completion = 0.0
    total_velocity = 0.0
    
    for project_name, project in projects.items():
        # Get project metrics
        project_metrics = metrics.get("projects", {}).get(project_name, {})
        
        # Determine project status
        burndown = project_metrics.get("burndown", {})
        is_on_track = burndown.get("is_on_track", True)
        days_behind = project_metrics.get("days_behind", 0)
        
        if is_on_track:
            projects_on_track += 1
        elif days_behind <= 7:
            projects_at_risk += 1
        else:
            projects_behind += 1
        
        # Add to totals
        total_completion += project.get_completion_percentage()
        total_velocity += project_metrics.get("velocity", {}).get("average", 0.0)
    
    return {
        "total_projects": total_projects,
        "projects_on_track": projects_on_track,
        "projects_at_risk": projects_at_risk,
        "projects_behind": projects_behind,
        "average_completion": total_completion / total_projects,
        "average_velocity": total_velocity / total_projects
    }