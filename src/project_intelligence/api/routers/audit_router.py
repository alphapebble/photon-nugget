"""
Audit router for the Project Intelligence API.

This module provides endpoints for accessing audit trail data.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from project_intelligence.audit.audit_trail import AuditRecord

logger = logging.getLogger(__name__)

router = APIRouter()


class AuditRecordResponse(BaseModel):
    """Audit record response model."""
    id: str
    timestamp: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: Dict[str, Dict]
    metadata: Dict = Field(default_factory=dict)


class LastModifierResponse(BaseModel):
    """Last modifier response model."""
    user_id: str
    timestamp: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    audit_record_id: str


@router.get("/", response_model=List[AuditRecordResponse])
async def get_audit_records(
    request: Request,
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    limit: int = Query(100, description="Maximum number of records to return"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get audit trail records with optional filtering.
    
    Args:
        request: FastAPI request object
        entity_type: Optional entity type filter
        entity_id: Optional entity ID filter
        user_id: Optional user ID filter
        action: Optional action type filter
        start_time: Optional start time filter
        end_time: Optional end time filter
        limit: Maximum number of records to return
        offset: Offset for pagination
        
    Returns:
        List of filtered audit records
    """
    # Parse time filters if provided
    start_datetime = datetime.fromisoformat(start_time) if start_time else None
    end_datetime = datetime.fromisoformat(end_time) if end_time else None
    
    # Get access to the audit manager
    audit_manager = request.app.state.audit_manager
    
    if not audit_manager:
        raise HTTPException(status_code=503, detail="Audit trail service not available")
    
    # Get records from audit manager
    records = await audit_manager.get_records(
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        action=action,
        start_time=start_datetime,
        end_time=end_datetime,
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
            "entity_type": record.entity_type,
            "entity_id": record.entity_id,
            "changes": record.changes,
            "metadata": record.metadata,
        }
        for record in records
    ]


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditRecordResponse])
async def get_entity_history(
    request: Request,
    entity_type: str,
    entity_id: str,
    limit: int = Query(100, description="Maximum number of records to return"),
):
    """
    Get the complete history for a specific entity.
    
    Args:
        request: FastAPI request object
        entity_type: Type of the entity
        entity_id: ID of the entity
        limit: Maximum number of records to return
        
    Returns:
        List of audit records for the entity
    """
    # Get access to the audit manager
    audit_manager = request.app.state.audit_manager
    
    if not audit_manager:
        raise HTTPException(status_code=503, detail="Audit trail service not available")
    
    # Get entity history
    records = await audit_manager.get_entity_history(
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
    )
    
    # Convert to response format
    return [
        {
            "id": record.id,
            "timestamp": record.timestamp.isoformat(),
            "user_id": record.user_id,
            "action": record.action,
            "entity_type": record.entity_type,
            "entity_id": record.entity_id,
            "changes": record.changes,
            "metadata": record.metadata,
        }
        for record in records
    ]


@router.get("/last-modifier/{entity_type}/{entity_id}", response_model=LastModifierResponse)
async def get_last_modifier(
    request: Request,
    entity_type: str,
    entity_id: str,
    field: Optional[str] = Query(None, description="Specific field to check"),
):
    """
    Get information about the last user who modified an entity or a specific field.
    
    Args:
        request: FastAPI request object
        entity_type: Type of the entity
        entity_id: ID of the entity
        field: Optional specific field to check
        
    Returns:
        Information about the last modifier
    """
    # Get access to the audit manager
    audit_manager = request.app.state.audit_manager
    
    if not audit_manager:
        raise HTTPException(status_code=503, detail="Audit trail service not available")
    
    # Get last modifier info
    modifier_info = await audit_manager.get_last_modifier(
        entity_type=entity_type,
        entity_id=entity_id,
        field=field,
    )
    
    if not modifier_info:
        raise HTTPException(
            status_code=404,
            detail=f"No audit records found for {entity_type} {entity_id}"
        )
    
    # Convert timestamp to string if it's a datetime
    if isinstance(modifier_info.get("timestamp"), datetime):
        modifier_info["timestamp"] = modifier_info["timestamp"].isoformat()
    
    return modifier_info


@router.get("/recent-activity", response_model=List[AuditRecordResponse])
async def get_recent_activity(
    request: Request,
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(20, description="Maximum number of records to return"),
):
    """
    Get recent activity across the system.
    
    Args:
        request: FastAPI request object
        user_id: Optional filter by user ID
        limit: Maximum number of records to return
        
    Returns:
        List of recent audit records
    """
    # Get access to the audit manager
    audit_manager = request.app.state.audit_manager
    
    if not audit_manager:
        raise HTTPException(status_code=503, detail="Audit trail service not available")
    
    # Get recent activity
    records = await audit_manager.get_recent_activity(
        limit=limit,
        user_id=user_id,
    )
    
    # Convert to response format
    return [
        {
            "id": record.id,
            "timestamp": record.timestamp.isoformat(),
            "user_id": record.user_id,
            "action": record.action,
            "entity_type": record.entity_type,
            "entity_id": record.entity_id,
            "changes": record.changes,
            "metadata": record.metadata,
        }
        for record in records
    ]