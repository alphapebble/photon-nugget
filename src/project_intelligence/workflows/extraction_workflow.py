"""
LangGraph workflow orchestrator for Project Intelligence.

This module defines the LangGraph-based workflow for extracting project intelligence
from various data sources.
"""

import logging
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, TypedDict, Union

import langgraph.graph as lg
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from ..agents.document_analyzer import DocumentAnalyzerAgent
from ..agents.integrator import IntegratorAgent
from ..agents.project_detector import ProjectDetectorAgent
from ..agents.resource_tracker import ResourceTrackerAgent
from ..agents.risk_assessor import RiskAssessorAgent
from ..agents.task_manager import TaskManagerAgent
from ..agents.timeline_analyzer import TimelineAnalyzerAgent
from ..models.extraction import (
    DocumentContext,
    ExtractionResult,
    ProjectExtraction,
    ResourceExtraction,
    RiskExtraction,
    TaskExtraction,
    TimelineExtraction,
)

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """The state maintained through the workflow."""
    
    # Input data
    document: DocumentContext
    
    # Extraction results
    project: Optional[ProjectExtraction]
    tasks: List[TaskExtraction]
    resources: List[ResourceExtraction]
    timeline: Optional[TimelineExtraction]
    risks: List[RiskExtraction]
    
    # Process metadata
    errors: List[str]
    confidence: float
    requires_human_review: bool
    
    # Processing agents
    agents: Dict[str, Any]
    
    # Results
    result: Optional[ExtractionResult]


class ExtractionOutcome(str, Enum):
    """Possible outcomes of the extraction process."""
    
    NEXT_AGENT = "next_agent"
    PROJECT_DETECTED = "project_detected"
    NO_PROJECT = "no_project"
    TASKS_EXTRACTED = "tasks_extracted"
    RESOURCES_EXTRACTED = "resources_extracted"
    TIMELINE_EXTRACTED = "timeline_extracted"
    RISKS_EXTRACTED = "risks_extracted"
    EXTRACTION_COMPLETE = "extraction_complete"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"
    ERROR = "error"


def create_workflow() -> lg.Graph:
    """
    Create the extraction workflow graph.
    
    Returns:
        LangGraph workflow for project intelligence extraction
    """
    # Initialize agents
    project_detector = ProjectDetectorAgent()
    task_manager = TaskManagerAgent()
    resource_tracker = ResourceTrackerAgent()
    timeline_analyzer = TimelineAnalyzerAgent()
    risk_assessor = RiskAssessorAgent()
    integrator = IntegratorAgent()
    
    # Define workflow nodes
    workflow = lg.Graph()
    
    # Add agent nodes
    workflow.add_node("detect_project", project_detector.process)
    workflow.add_node("extract_tasks", task_manager.process)
    workflow.add_node("extract_resources", resource_tracker.process)
    workflow.add_node("extract_timeline", timeline_analyzer.process)
    workflow.add_node("assess_risks", risk_assessor.process)
    workflow.add_node("integrate_results", integrator.process)
    
    # Define conditional edges
    def route_after_project_detection(state: WorkflowState) -> str:
        """Route after project detection."""
        if state.get("errors") and len(state["errors"]) > 0:
            return "error"
        elif state.get("requires_human_review", False):
            return "requires_human_review"
        elif state.get("project") is not None:
            return "project_detected"
        else:
            return "no_project"
    
    def route_after_task_extraction(state: WorkflowState) -> str:
        """Route after task extraction."""
        if state.get("errors") and len(state["errors"]) > 0:
            return "error"
        elif state.get("requires_human_review", False):
            return "requires_human_review"
        else:
            return "tasks_extracted"
    
    def route_after_resource_extraction(state: WorkflowState) -> str:
        """Route after resource extraction."""
        if state.get("errors") and len(state["errors"]) > 0:
            return "error"
        elif state.get("requires_human_review", False):
            return "requires_human_review"
        else:
            return "resources_extracted"
    
    def route_after_timeline_extraction(state: WorkflowState) -> str:
        """Route after timeline extraction."""
        if state.get("errors") and len(state["errors"]) > 0:
            return "error"
        elif state.get("requires_human_review", False):
            return "requires_human_review"
        else:
            return "timeline_extracted"
    
    def route_after_risk_assessment(state: WorkflowState) -> str:
        """Route after risk assessment."""
        if state.get("errors") and len(state["errors"]) > 0:
            return "error"
        elif state.get("requires_human_review", False):
            return "requires_human_review"
        else:
            return "risks_extracted"
    
    def route_after_integration(state: WorkflowState) -> str:
        """Route after integration."""
        if state.get("errors") and len(state["errors"]) > 0:
            return "error"
        elif state.get("requires_human_review", False):
            return "requires_human_review"
        else:
            return "extraction_complete"
    
    # Add edges
    workflow.add_conditional_edges(
        "detect_project",
        route_after_project_detection,
        {
            "project_detected": "extract_tasks",
            "no_project": END,
            "error": END,
            "requires_human_review": END,
        },
    )
    
    workflow.add_conditional_edges(
        "extract_tasks",
        route_after_task_extraction,
        {
            "tasks_extracted": "extract_resources",
            "error": END,
            "requires_human_review": END,
        },
    )
    
    workflow.add_conditional_edges(
        "extract_resources",
        route_after_resource_extraction,
        {
            "resources_extracted": "extract_timeline",
            "error": END,
            "requires_human_review": END,
        },
    )
    
    workflow.add_conditional_edges(
        "extract_timeline",
        route_after_timeline_extraction,
        {
            "timeline_extracted": "assess_risks",
            "error": END,
            "requires_human_review": END,
        },
    )
    
    workflow.add_conditional_edges(
        "assess_risks",
        route_after_risk_assessment,
        {
            "risks_extracted": "integrate_results",
            "error": END,
            "requires_human_review": END,
        },
    )
    
    workflow.add_conditional_edges(
        "integrate_results",
        route_after_integration,
        {
            "extraction_complete": END,
            "error": END,
            "requires_human_review": END,
        },
    )
    
    # Compile the workflow
    return workflow.compile()


# Initialize the extraction workflow
extraction_workflow = create_workflow()


async def process_document(document: DocumentContext) -> ExtractionResult:
    """
    Process a document through the extraction workflow.
    
    Args:
        document: The document context to process
        
    Returns:
        Extraction result
    """
    # Initialize workflow state
    initial_state: WorkflowState = {
        "document": document,
        "project": None,
        "tasks": [],
        "resources": [],
        "timeline": None,
        "risks": [],
        "errors": [],
        "confidence": 0.0,
        "requires_human_review": False,
        "agents": {},
        "result": None,
    }
    
    try:
        # Execute the workflow
        final_state = await extraction_workflow.acall(initial_state)
        
        # Return the result
        if final_state.get("result"):
            return final_state["result"]
        else:
            # Create a result from the final state
            return ExtractionResult(
                project=final_state.get("project"),
                tasks=final_state.get("tasks", []),
                resources=final_state.get("resources", []),
                timeline=final_state.get("timeline"),
                risks=final_state.get("risks", []),
                confidence=final_state.get("confidence", 0.0),
                requires_human_review=final_state.get("requires_human_review", False),
                errors=final_state.get("errors", []),
                document_id=document.id,
                document_type=document.type,
            )
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return ExtractionResult(
            project=None,
            tasks=[],
            resources=[],
            timeline=None,
            risks=[],
            confidence=0.0,
            requires_human_review=True,
            errors=[f"Workflow error: {str(e)}"],
            document_id=document.id,
            document_type=document.type,
        )