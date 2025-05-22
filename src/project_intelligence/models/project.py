"""
Project data models for the Project Intelligence System.

This module provides data models for projects, tasks, updates, and resources.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union


@dataclass
class Task:
    """
    Data model for a project task.
    """
    id: str
    name: str
    description: str = ""
    status: str = "pending"
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    blockers: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    priority: str = "medium"
    completion_percentage: Optional[float] = None
    parent_id: Optional[str] = None
    
    def update(self, **kwargs) -> None:
        """
        Update task attributes.
        
        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()


@dataclass
class ProjectUpdate:
    """
    Data model for a project update.
    """
    timestamp: datetime
    content: str
    author: str
    update_type: str = "general"  # general, progress, blocker, milestone, etc.
    related_task_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceStatus:
    """
    Data model for resource status.
    """
    resource_type: str  # staff, equipment, material, etc.
    status: str  # available, allocated, depleted, etc.
    quantity: Optional[int] = None
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Project:
    """
    Data model for a project.
    """
    name: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "active"  # active, completed, on_hold, cancelled
    owner: Optional[str] = None
    team_members: List[str] = field(default_factory=list)
    tasks: Dict[str, Task] = field(default_factory=dict)
    updates: List[ProjectUpdate] = field(default_factory=list)
    resources: Dict[str, ResourceStatus] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_or_update_task(self, task: Task) -> None:
        """
        Add a new task or update an existing one.
        
        Args:
            task: The task to add or update
        """
        self.tasks[task.id] = task
        self.updated_at = datetime.now()
    
    def remove_task(self, task_id: str) -> None:
        """
        Remove a task.
        
        Args:
            task_id: ID of the task to remove
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.updated_at = datetime.now()
    
    def add_update(self, update: ProjectUpdate) -> None:
        """
        Add a project update.
        
        Args:
            update: The update to add
        """
        self.updates.append(update)
        self.updated_at = datetime.now()
    
    def update_resource_status(self, resource: ResourceStatus) -> None:
        """
        Update resource status.
        
        Args:
            resource: The resource status
        """
        self.resources[resource.resource_type] = resource
        self.updated_at = datetime.now()
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task or None if not found
        """
        return self.tasks.get(task_id)
    
    def get_tasks_by_owner(self, owner: str) -> List[Task]:
        """
        Get all tasks assigned to an owner.
        
        Args:
            owner: Owner name
            
        Returns:
            List of tasks
        """
        return [task for task in self.tasks.values() if task.owner == owner]
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: Task status
            
        Returns:
            List of tasks
        """
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Get all overdue tasks.
        
        Returns:
            List of overdue tasks
        """
        now = datetime.now()
        return [
            task for task in self.tasks.values() 
            if task.due_date and task.due_date < now and task.status != "completed"
        ]
    
    def get_completion_percentage(self) -> float:
        """
        Calculate project completion percentage based on tasks.
        
        Returns:
            Completion percentage (0-100)
        """
        if not self.tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in self.tasks.values() if task.status == "completed")
        return (completed_tasks / len(self.tasks)) * 100
    
    def get_latest_update(self) -> Optional[ProjectUpdate]:
        """
        Get the most recent project update.
        
        Returns:
            Most recent update or None if no updates exist
        """
        if not self.updates:
            return None
        
        return max(self.updates, key=lambda update: update.timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert project to dictionary.
        
        Returns:
            Dictionary representation of the project
        """
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "owner": self.owner,
            "team_members": self.team_members,
            "tasks": {
                task_id: {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "status": task.status,
                    "owner": task.owner,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                    "blockers": task.blockers,
                    "tags": task.tags,
                    "priority": task.priority,
                    "completion_percentage": task.completion_percentage,
                    "parent_id": task.parent_id
                } for task_id, task in self.tasks.items()
            },
            "updates": [
                {
                    "timestamp": update.timestamp.isoformat(),
                    "content": update.content,
                    "author": update.author,
                    "update_type": update.update_type,
                    "related_task_ids": update.related_task_ids,
                    "metadata": update.metadata
                } for update in self.updates
            ],
            "resources": {
                resource_type: {
                    "resource_type": resource.resource_type,
                    "status": resource.status,
                    "quantity": resource.quantity,
                    "last_updated": resource.last_updated.isoformat() if resource.last_updated else None,
                    "metadata": resource.metadata
                } for resource_type, resource in self.resources.items()
            },
            "tags": self.tags,
            "metadata": self.metadata,
            "completion_percentage": self.get_completion_percentage()
        }