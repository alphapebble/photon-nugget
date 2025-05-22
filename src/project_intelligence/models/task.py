"""
Task model for Project Intelligence.

This module defines the Task class which represents a task in a project.
It includes audit trail integration to track changes to tasks.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Set

from pydantic.dataclasses import dataclass
from pydantic import Field
from dataclasses import field, asdict

from project_intelligence.audit.audit_trail import default_audit_manager

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """
    Task model representing a project task.
    
    This class includes audit trail integration to track changes to task attributes.
    """
    
    id: str
    name: str
    description: Optional[str] = None
    status: str = "todo"  # todo, in_progress, blocked, completed, cancelled
    priority: Optional[str] = None  # low, medium, high, critical
    owner: Optional[str] = None
    assignees: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    story_points: Optional[float] = None
    completion_percentage: float = 0.0
    blockers: List[str] = Field(default_factory=list)
    subtasks: Dict[str, "Task"] = Field(default_factory=dict)
    parent_id: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Audit trail fields
    last_modified_by: Optional[str] = None
    status_change_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    def __post_init__(self):
        """Set default values after initialization."""
        # Set completion_percentage to 100 if status is completed
        if self.status == "completed" and self.completion_percentage < 100:
            self.completion_percentage = 100.0
            self.completion_date = self.completion_date or datetime.now()
            
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    async def update(
        self, 
        data: Dict[str, Any], 
        user_id: str = "system",
        track_changes: bool = True
    ) -> None:
        """
        Update task attributes with audit trail tracking.
        
        Args:
            data: Dictionary of attributes to update
            user_id: ID of the user making the update
            track_changes: Whether to track changes in the audit trail
        """
        # Track original values for audit trail
        changes = {}
        status_changed = False
        old_status = self.status
        
        # Update values
        for key, value in data.items():
            if hasattr(self, key) and getattr(self, key) != value:
                # Record change for audit trail
                if track_changes:
                    changes[key] = {
                        "old": getattr(self, key),
                        "new": value
                    }
                
                # Special handling for status changes
                if key == "status" and value != old_status:
                    status_changed = True
                
                # Update the attribute
                setattr(self, key, value)
        
        if changes:
            # Update the updated_at timestamp
            self.updated_at = datetime.now()
            self.last_modified_by = user_id
            
            # Handle status change history
            if status_changed:
                self.status_change_history.append({
                    "timestamp": self.updated_at,
                    "user_id": user_id,
                    "old_status": old_status,
                    "new_status": self.status
                })
            
            # Record in audit trail
            if track_changes:
                try:
                    await default_audit_manager.record(
                        user_id=user_id,
                        action="update",
                        entity_type="task",
                        entity_id=self.id,
                        changes=changes,
                        metadata={
                            "task_name": self.name,
                            "status": self.status
                        }
                    )
                except Exception as e:
                    logger.error(f"Error recording audit trail for task update: {str(e)}")
    
    async def add_blocker(
        self, 
        blocker: str, 
        user_id: str = "system",
        track_changes: bool = True
    ) -> None:
        """
        Add a blocker to the task.
        
        Args:
            blocker: Description of the blocker
            user_id: ID of the user adding the blocker
            track_changes: Whether to track changes in the audit trail
        """
        if blocker not in self.blockers:
            old_blockers = self.blockers.copy()
            self.blockers.append(blocker)
            
            # Update task status if it's not already blocked
            if self.status != "blocked":
                await self.update(
                    {"status": "blocked"},
                    user_id=user_id,
                    track_changes=track_changes
                )
            
            # Record in audit trail
            if track_changes:
                try:
                    await default_audit_manager.record(
                        user_id=user_id,
                        action="add_blocker",
                        entity_type="task",
                        entity_id=self.id,
                        changes={
                            "blockers": {
                                "old": old_blockers,
                                "new": self.blockers
                            }
                        },
                        metadata={
                            "task_name": self.name,
                            "blocker": blocker
                        }
                    )
                except Exception as e:
                    logger.error(f"Error recording audit trail for adding blocker: {str(e)}")
    
    async def remove_blocker(
        self, 
        blocker: str, 
        user_id: str = "system",
        track_changes: bool = True
    ) -> None:
        """
        Remove a blocker from the task.
        
        Args:
            blocker: Description of the blocker to remove
            user_id: ID of the user removing the blocker
            track_changes: Whether to track changes in the audit trail
        """
        if blocker in self.blockers:
            old_blockers = self.blockers.copy()
            self.blockers.remove(blocker)
            
            # Update status if all blockers are removed
            if not self.blockers and self.status == "blocked":
                await self.update(
                    {"status": "in_progress" if self.completion_percentage > 0 else "todo"},
                    user_id=user_id,
                    track_changes=track_changes
                )
            
            # Record in audit trail
            if track_changes:
                try:
                    await default_audit_manager.record(
                        user_id=user_id,
                        action="remove_blocker",
                        entity_type="task",
                        entity_id=self.id,
                        changes={
                            "blockers": {
                                "old": old_blockers,
                                "new": self.blockers
                            }
                        },
                        metadata={
                            "task_name": self.name,
                            "blocker": blocker
                        }
                    )
                except Exception as e:
                    logger.error(f"Error recording audit trail for removing blocker: {str(e)}")
    
    async def assign(
        self, 
        user_id: str, 
        assigner_id: str = "system",
        track_changes: bool = True
    ) -> None:
        """
        Assign the task to a user.
        
        Args:
            user_id: ID of the user to assign the task to
            assigner_id: ID of the user making the assignment
            track_changes: Whether to track changes in the audit trail
        """
        if user_id not in self.assignees:
            old_assignees = self.assignees.copy()
            old_owner = self.owner
            
            self.assignees.append(user_id)
            
            # Set as owner if there is no owner
            if not self.owner:
                self.owner = user_id
            
            # Record in audit trail
            if track_changes:
                try:
                    changes = {
                        "assignees": {
                            "old": old_assignees,
                            "new": self.assignees
                        }
                    }
                    
                    if old_owner != self.owner:
                        changes["owner"] = {
                            "old": old_owner,
                            "new": self.owner
                        }
                    
                    await default_audit_manager.record(
                        user_id=assigner_id,
                        action="assign",
                        entity_type="task",
                        entity_id=self.id,
                        changes=changes,
                        metadata={
                            "task_name": self.name,
                            "assigned_to": user_id
                        }
                    )
                except Exception as e:
                    logger.error(f"Error recording audit trail for task assignment: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary representation.
        
        Returns:
            Dictionary representation of task
        """
        task_dict = asdict(self)
        del task_dict["subtasks"]
        
        # Convert datetime objects to strings
        for key, value in task_dict.items():
            if isinstance(value, datetime):
                task_dict[key] = value.isoformat()
        
        # Add subtasks
        task_dict["subtasks"] = {task_id: task.to_dict() for task_id, task in self.subtasks.items()}
        
        return task_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        Create a task from dictionary data.
        
        Args:
            data: Dictionary representation of task
            
        Returns:
            Task instance
        """
        # Make a copy to avoid modifying the input
        data_copy = data.copy()
        
        # Handle datetime fields
        for field_name in ["created_at", "updated_at", "due_date", "start_date", "completion_date"]:
            if field_name in data_copy and isinstance(data_copy[field_name], str):
                try:
                    data_copy[field_name] = datetime.fromisoformat(data_copy[field_name])
                except ValueError:
                    data_copy[field_name] = None
        
        # Handle subtasks
        subtasks_data = data_copy.pop("subtasks", {})
        task = cls(**data_copy)
        
        for subtask_id, subtask_data in subtasks_data.items():
            task.subtasks[subtask_id] = cls.from_dict(subtask_data)
        
        return task
    
    def get_last_status_change(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the last status change.
        
        Returns:
            Dictionary with status change information or None
        """
        if not self.status_change_history:
            return None
        
        return self.status_change_history[-1]