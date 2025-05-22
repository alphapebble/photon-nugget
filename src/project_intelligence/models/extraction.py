"""
Extraction models for the Project Intelligence System.

This module provides Pydantic models for the extraction process, defining
the structure of extracted project information.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Types of documents that can be processed."""
    
    EMAIL = "email"
    SLACK_MESSAGE = "slack_message"
    TEAMS_MESSAGE = "teams_message"
    SPREADSHEET = "spreadsheet"
    TEXT_DOCUMENT = "text_document"
    ISSUE = "issue"
    CALENDAR_EVENT = "calendar_event"
    UNKNOWN = "unknown"


class DocumentContext(BaseModel):
    """Context information about a document being processed."""
    
    id: str = Field(..., description="Unique identifier for the document")
    type: DocumentType = Field(..., description="Type of document")
    content: str = Field(..., description="Raw content of the document")
    metadata: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, description="Additional metadata about the document"
    )
    author: Optional[str] = Field(None, description="Author of the document")
    created_at: Optional[datetime] = Field(None, description="Creation time of the document")
    source: Optional[str] = Field(None, description="Source of the document")


class TaskStatus(str, Enum):
    """Status of a task."""
    
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PENDING = "pending"
    UNKNOWN = "unknown"


class TaskPriority(str, Enum):
    """Priority of a task."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    UNKNOWN = "unknown"


class ProjectStatus(str, Enum):
    """Status of a project."""
    
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ResourceType(str, Enum):
    """Type of resource."""
    
    STAFF = "staff"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    BUDGET = "budget"
    TIME = "time"
    UNKNOWN = "unknown"


class ResourceStatus(str, Enum):
    """Status of a resource."""
    
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    DEPLETED = "depleted"
    LOW = "low"
    SUFFICIENT = "sufficient"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """Level of risk."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ProjectExtraction(BaseModel):
    """Extracted project information."""
    
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    status: ProjectStatus = Field(ProjectStatus.UNKNOWN, description="Status of the project")
    owner: Optional[str] = Field(None, description="Owner of the project")
    team_members: List[str] = Field(default_factory=list, description="Team members working on the project")
    start_date: Optional[datetime] = Field(None, description="Start date of the project")
    end_date: Optional[datetime] = Field(None, description="End date of the project")
    metadata: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, description="Additional metadata about the project"
    )
    confidence: float = Field(0.0, description="Confidence score for the extraction")


class TaskExtraction(BaseModel):
    """Extracted task information."""
    
    name: str = Field(..., description="Name of the task")
    description: Optional[str] = Field(None, description="Description of the task")
    status: TaskStatus = Field(TaskStatus.UNKNOWN, description="Status of the task")
    priority: TaskPriority = Field(TaskPriority.UNKNOWN, description="Priority of the task")
    owner: Optional[str] = Field(None, description="Owner of the task")
    assignees: List[str] = Field(default_factory=list, description="People assigned to the task")
    due_date: Optional[datetime] = Field(None, description="Due date of the task")
    start_date: Optional[datetime] = Field(None, description="Start date of the task")
    completion_date: Optional[datetime] = Field(None, description="Completion date of the task")
    completion_percentage: Optional[float] = Field(None, description="Completion percentage of the task")
    parent_task: Optional[str] = Field(None, description="Parent task ID")
    blockers: List[str] = Field(default_factory=list, description="Blockers for the task")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies for the task")
    tags: List[str] = Field(default_factory=list, description="Tags for the task")
    metadata: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, description="Additional metadata about the task"
    )
    confidence: float = Field(0.0, description="Confidence score for the extraction")


class ResourceExtraction(BaseModel):
    """Extracted resource information."""
    
    name: str = Field(..., description="Name of the resource")
    type: ResourceType = Field(ResourceType.UNKNOWN, description="Type of resource")
    status: ResourceStatus = Field(ResourceStatus.UNKNOWN, description="Status of the resource")
    quantity: Optional[float] = Field(None, description="Quantity of the resource")
    unit: Optional[str] = Field(None, description="Unit of measurement for the resource")
    owner: Optional[str] = Field(None, description="Owner of the resource")
    allocated_to: Optional[str] = Field(None, description="Project or task the resource is allocated to")
    start_date: Optional[datetime] = Field(None, description="Start date of resource allocation")
    end_date: Optional[datetime] = Field(None, description="End date of resource allocation")
    metadata: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, description="Additional metadata about the resource"
    )
    confidence: float = Field(0.0, description="Confidence score for the extraction")


class TimelineExtraction(BaseModel):
    """Extracted timeline information."""
    
    start_date: Optional[datetime] = Field(None, description="Start date of the timeline")
    end_date: Optional[datetime] = Field(None, description="End date of the timeline")
    milestones: List[Dict[str, Union[str, datetime]]] = Field(
        default_factory=list, description="Milestones in the timeline"
    )
    dependencies: List[Dict[str, str]] = Field(
        default_factory=list, description="Dependencies between timeline items"
    )
    critical_path: List[str] = Field(
        default_factory=list, description="Items on the critical path"
    )
    metadata: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, description="Additional metadata about the timeline"
    )
    confidence: float = Field(0.0, description="Confidence score for the extraction")


class RiskExtraction(BaseModel):
    """Extracted risk information."""
    
    name: str = Field(..., description="Name of the risk")
    description: Optional[str] = Field(None, description="Description of the risk")
    level: RiskLevel = Field(RiskLevel.UNKNOWN, description="Level of the risk")
    impact: Optional[str] = Field(None, description="Impact of the risk")
    probability: Optional[float] = Field(None, description="Probability of the risk occurring")
    mitigation: Optional[str] = Field(None, description="Mitigation strategy for the risk")
    owner: Optional[str] = Field(None, description="Owner of the risk")
    affected_tasks: List[str] = Field(
        default_factory=list, description="Tasks affected by the risk"
    )
    metadata: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, description="Additional metadata about the risk"
    )
    confidence: float = Field(0.0, description="Confidence score for the extraction")


class ExtractionResult(BaseModel):
    """Result of the extraction process."""
    
    project: Optional[ProjectExtraction] = Field(None, description="Extracted project information")
    tasks: List[TaskExtraction] = Field(default_factory=list, description="Extracted task information")
    resources: List[ResourceExtraction] = Field(default_factory=list, description="Extracted resource information")
    timeline: Optional[TimelineExtraction] = Field(None, description="Extracted timeline information")
    risks: List[RiskExtraction] = Field(default_factory=list, description="Extracted risk information")
    confidence: float = Field(0.0, description="Overall confidence score for the extraction")
    requires_human_review: bool = Field(False, description="Whether the extraction requires human review")
    errors: List[str] = Field(default_factory=list, description="Errors encountered during extraction")
    document_id: str = Field(..., description="ID of the document that was processed")
    document_type: DocumentType = Field(..., description="Type of document that was processed")