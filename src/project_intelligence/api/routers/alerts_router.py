"""
Alerts router for the Project Intelligence API.

This module provides endpoints for accessing alert data.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class Alert(BaseModel):
    """Alert data model."""
    project_name: str
    alert_type: str
    severity: str
    title: str
    description: str
    metadata: Dict
    suggested_actions: Optional[List[str]] = None
    timestamp: str


@router.get("/", response_model=List[Alert])
async def get_alerts(
    request: Request,
    project: Optional[str] = Query(None, description="Filter alerts by project name"),
    severity: Optional[str] = Query(None, description="Filter alerts by severity (low, medium, high, critical)"),
    alert_type: Optional[str] = Query(None, description="Filter alerts by type"),
    limit: int = Query(10, description="Limit the number of alerts returned"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get alerts with optional filtering.
    
    Args:
        request: FastAPI request object
        project: Optional project name filter
        severity: Optional severity filter
        alert_type: Optional alert type filter
        limit: Maximum number of alerts to return
        offset: Offset for pagination
        
    Returns:
        List of filtered alerts
    """
    # Get alerts from app state
    alerts = request.app.state.alerts
    
    if not alerts:
        return []
    
    # Apply filters
    filtered_alerts = alerts
    
    if project:
        filtered_alerts = [a for a in filtered_alerts if a.get("project_name") == project]
    
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a.get("severity") == severity]
    
    if alert_type:
        filtered_alerts = [a for a in filtered_alerts if a.get("alert_type") == alert_type]
    
    # Apply pagination
    paginated_alerts = filtered_alerts[offset:offset + limit]
    
    return paginated_alerts


@router.get("/count", response_model=Dict)
async def get_alert_count(
    request: Request,
    project: Optional[str] = Query(None, description="Filter alerts by project name"),
):
    """
    Get alert counts by severity.
    
    Args:
        request: FastAPI request object
        project: Optional project name filter
        
    Returns:
        Dictionary with alert counts by severity
    """
    # Get alerts from app state
    alerts = request.app.state.alerts
    
    if not alerts:
        return {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
    
    # Apply project filter if provided
    if project:
        alerts = [a for a in alerts if a.get("project_name") == project]
    
    # Count alerts by severity
    counts = {
        "total": len(alerts),
        "critical": len([a for a in alerts if a.get("severity") == "critical"]),
        "high": len([a for a in alerts if a.get("severity") == "high"]),
        "medium": len([a for a in alerts if a.get("severity") == "medium"]),
        "low": len([a for a in alerts if a.get("severity") == "low"]),
    }
    
    return counts


@router.get("/blocked-tasks", response_model=List[Alert])
async def get_blocked_task_alerts(
    request: Request,
    days_blocked: Optional[int] = Query(None, description="Minimum days blocked filter"),
    limit: int = Query(10, description="Limit the number of alerts returned"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get alerts for blocked tasks.
    
    Args:
        request: FastAPI request object
        days_blocked: Optional minimum days blocked filter
        limit: Maximum number of alerts to return
        offset: Offset for pagination
        
    Returns:
        List of blocked task alerts
    """
    # Get alerts from app state
    alerts = request.app.state.alerts
    
    if not alerts:
        return []
    
    # Filter for blocked task alerts
    blocked_alerts = [a for a in alerts if a.get("alert_type") == "blocked_task"]
    
    # Apply days_blocked filter if provided
    if days_blocked is not None:
        blocked_alerts = [
            a for a in blocked_alerts 
            if a.get("metadata", {}).get("blocked_days", 0) >= days_blocked
        ]
    
    # Apply pagination
    paginated_alerts = blocked_alerts[offset:offset + limit]
    
    return paginated_alerts


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    request: Request,
    alert_id: str,
):
    """
    Get a specific alert by ID.
    
    Args:
        request: FastAPI request object
        alert_id: ID of the alert to retrieve
        
    Returns:
        Alert data
    """
    # Get alerts from app state
    alerts = request.app.state.alerts
    
    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found")
    
    # Find alert by ID
    for alert in alerts:
        if alert.get("id") == alert_id:
            return alert
    
    raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")