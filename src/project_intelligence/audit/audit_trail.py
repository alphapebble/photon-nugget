"""
Audit Trail module for Project Intelligence.

This module provides functionality for recording and retrieving audit trail records
for actions taken in the system, with a focus on tracking changes to project entities.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic.dataclasses import dataclass
from pydantic import Field

logger = logging.getLogger(__name__)


@dataclass
class AuditRecord:
    """Model for an audit trail record."""

    user_id: str
    action: str
    entity_type: str
    entity_id: str
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    changes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Example:
    # {
    #     "id": "550e8400-e29b-41d4-a716-446655440000",
    #     "timestamp": "2023-07-01T12:30:45.123456",
    #     "user_id": "user123",
    #     "action": "update",
    #     "entity_type": "task",
    #     "entity_id": "task456",
    #     "changes": {
    #         "status": {"old": "in_progress", "new": "completed"},
    #         "assigned_to": {"old": "user789", "new": "user321"},
    #     },
    #     "metadata": {"source": "web_app", "request_id": "req123"},
    #     "ip_address": "192.168.1.1",
    #     "user_agent": "Mozilla/5.0...",
    # }


class AuditTrailManager:
    """
    Manager for audit trail records.
    
    This class provides methods for recording, retrieving, and querying
    audit trail records across the system.
    """

    def __init__(self, storage_provider=None):
        """
        Initialize the audit trail manager.
        
        Args:
            storage_provider: Provider for storing audit records
                (defaults to in-memory storage if None)
        """
        self.storage_provider = storage_provider
        self._in_memory_records = []
        
    async def record(
        self,
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        changes: Dict[str, Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditRecord:
        """
        Record an audit trail entry.
        
        Args:
            user_id: ID of the user who performed the action
            action: Type of action (create, update, delete, etc.)
            entity_type: Type of entity affected (task, project, etc.)
            entity_id: ID of the entity affected
            changes: Dictionary of field changes with old and new values
            metadata: Additional metadata about the action
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            The created audit record
        """
        record = AuditRecord(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes or {},
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        # Store the record
        if self.storage_provider:
            await self.storage_provider.store_record(record)
        else:
            self._in_memory_records.append(record)
            
        logger.info(
            f"Audit trail: {action} on {entity_type} {entity_id} by {user_id}",
            extra={"audit_record_id": record.id},
        )
        
        return record
    
    async def get_records(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditRecord]:
        """
        Get audit trail records with optional filtering.
        
        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            user_id: Filter by user ID
            action: Filter by action type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            List of filtered audit records
        """
        if self.storage_provider:
            return await self.storage_provider.get_records(
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                action=action,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                offset=offset,
            )
        
        # Filter in-memory records
        filtered_records = self._in_memory_records
        
        if entity_type:
            filtered_records = [r for r in filtered_records if r.entity_type == entity_type]
        
        if entity_id:
            filtered_records = [r for r in filtered_records if r.entity_id == entity_id]
        
        if user_id:
            filtered_records = [r for r in filtered_records if r.user_id == user_id]
        
        if action:
            filtered_records = [r for r in filtered_records if r.action == action]
        
        if start_time:
            filtered_records = [r for r in filtered_records if r.timestamp >= start_time]
        
        if end_time:
            filtered_records = [r for r in filtered_records if r.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        filtered_records.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Apply pagination
        paginated_records = filtered_records[offset:offset + limit]
        
        return paginated_records
    
    async def get_entity_history(
        self, entity_type: str, entity_id: str, limit: int = 100
    ) -> List[AuditRecord]:
        """
        Get the complete history for a specific entity.
        
        Args:
            entity_type: Type of the entity
            entity_id: ID of the entity
            limit: Maximum number of records to return
            
        Returns:
            List of audit records for the entity, ordered by timestamp
        """
        records = await self.get_records(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
        )
        
        # Sort by timestamp (oldest first) to show history in chronological order
        records.sort(key=lambda r: r.timestamp)
        
        return records
    
    async def get_recent_activity(
        self, limit: int = 20, user_id: Optional[str] = None
    ) -> List[AuditRecord]:
        """
        Get recent activity across the system.
        
        Args:
            limit: Maximum number of records to return
            user_id: Optional filter by user ID
            
        Returns:
            List of recent audit records
        """
        return await self.get_records(
            user_id=user_id,
            limit=limit,
        )
    
    async def get_last_modifier(
        self, entity_type: str, entity_id: str, field: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about the last user who modified an entity or a specific field.
        
        Args:
            entity_type: Type of the entity
            entity_id: ID of the entity
            field: Optional specific field to check
            
        Returns:
            Dictionary with information about the last modifier
        """
        records = await self.get_records(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=100,  # Get enough history to find field changes
        )
        
        if not records:
            return None
        
        # Sort by timestamp (newest first)
        records.sort(key=lambda r: r.timestamp, reverse=True)
        
        if field:
            # Find the most recent record that modified the specified field
            for record in records:
                if field in record.changes:
                    return {
                        "user_id": record.user_id,
                        "timestamp": record.timestamp,
                        "old_value": record.changes[field].get("old"),
                        "new_value": record.changes[field].get("new"),
                        "audit_record_id": record.id,
                    }
            return None
        
        # If no specific field, return the most recent modifier
        return {
            "user_id": records[0].user_id,
            "timestamp": records[0].timestamp,
            "action": records[0].action,
            "changes": records[0].changes,
            "audit_record_id": records[0].id,
        }


# Singleton instance for easy access
default_audit_manager = AuditTrailManager()