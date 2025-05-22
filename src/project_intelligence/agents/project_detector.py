"""
Project detector agent for Project Intelligence.

This module provides the ProjectDetectorAgent class for detecting project information
in documents.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from ..models.extraction import DocumentContext, ProjectExtraction, ProjectStatus, WorkflowState

logger = logging.getLogger(__name__)


class ProjectOutput(BaseModel):
    """Output schema for project detection."""
    
    project_detected: bool = Field(
        ..., description="Whether a project was detected in the document"
    )
    project_name: Optional[str] = Field(
        None, description="Name of the project if detected"
    )
    project_description: Optional[str] = Field(
        None, description="Description of the project if detected"
    )
    project_status: Optional[str] = Field(
        None, description="Status of the project if detected"
    )
    project_owner: Optional[str] = Field(
        None, description="Owner of the project if detected"
    )
    team_members: List[str] = Field(
        default_factory=list, description="Team members of the project if detected"
    )
    start_date: Optional[str] = Field(
        None, description="Start date of the project if detected (ISO format)"
    )
    end_date: Optional[str] = Field(
        None, description="End date of the project if detected (ISO format)"
    )
    confidence: float = Field(
        ..., description="Confidence score for the detection (0.0 to 1.0)"
    )
    requires_human_review: bool = Field(
        False, description="Whether human review is needed for the detection"
    )
    reasoning: str = Field(
        ..., description="Reasoning for the detection decision"
    )


class ProjectDetectorAgent:
    """
    Agent for detecting project information in documents.
    
    This agent analyzes document content to identify project names,
    descriptions, and other project-related information.
    """
    
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """
        Initialize the project detector agent.
        
        Args:
            llm: Language model to use for detection
        """
        from langchain_openai import ChatOpenAI
        
        self.llm = llm or ChatOpenAI(temperature=0, model="gpt-4o")
        self.parser = JsonOutputParser(pydantic_object=ProjectOutput)
        
        self.system_prompt = """
        You are an expert project manager AI assistant that specializes in detecting project information from various types of documents.
        
        Your task is to analyze the provided document and identify if it contains information about a project.
        Look for project names, descriptions, status updates, team members, timelines, and other relevant project information.
        
        Some indicators of project-related content:
        - Mentions of "project", "initiative", "program", or similar terms
        - References to timelines, milestones, or deadlines
        - Discussion of team assignments or responsibilities
        - Status updates or progress reports
        - Resource allocation discussions
        
        Provide your analysis in a structured JSON format, including your confidence level and reasoning.
        """
        
        self.human_prompt = """
        Document Type: {document_type}
        Content: {content}
        Metadata: {metadata}
        
        Analyze this document and detect any project information.
        """
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", self.human_prompt),
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """
        Process a document to detect project information.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            document = state["document"]
            
            # Try to detect project information
            result = await self._detect_project(document)
            
            # Update state based on detection result
            if result.project_detected and result.project_name:
                # Create project extraction
                project = ProjectExtraction(
                    name=result.project_name,
                    description=result.project_description,
                    status=self._parse_status(result.project_status),
                    owner=result.project_owner,
                    team_members=result.team_members,
                    start_date=self._parse_date(result.start_date),
                    end_date=self._parse_date(result.end_date),
                    confidence=result.confidence,
                )
                
                # Update state
                state["project"] = project
                state["confidence"] = result.confidence
                state["requires_human_review"] = result.requires_human_review
            else:
                # No project detected
                state["project"] = None
                state["confidence"] = result.confidence
                state["requires_human_review"] = result.requires_human_review
                
                if result.confidence < 0.3:
                    # Low confidence, add error
                    state["errors"].append(
                        f"Low confidence in project detection: {result.reasoning}"
                    )
            
            return state
        except Exception as e:
            logger.error(f"Error in project detection: {str(e)}")
            state["errors"].append(f"Project detection error: {str(e)}")
            state["requires_human_review"] = True
            return state
    
    async def _detect_project(self, document: DocumentContext) -> ProjectOutput:
        """
        Detect project information in a document.
        
        Args:
            document: Document to analyze
            
        Returns:
            Project detection output
        """
        try:
            # Prepare input for the chain
            chain_input = {
                "document_type": document.type,
                "content": document.content[:8000],  # Limit content length
                "metadata": document.metadata,
            }
            
            # Run the chain
            result = await self.chain.ainvoke(chain_input)
            return result
        except Exception as e:
            logger.error(f"Error detecting project: {str(e)}")
            return ProjectOutput(
                project_detected=False,
                confidence=0.0,
                requires_human_review=True,
                reasoning=f"Error in detection: {str(e)}",
            )
    
    def _parse_status(self, status_str: Optional[str]) -> ProjectStatus:
        """
        Parse project status from string.
        
        Args:
            status_str: Status string to parse
            
        Returns:
            Parsed project status
        """
        if not status_str:
            return ProjectStatus.UNKNOWN
        
        status_lower = status_str.lower()
        
        if any(term in status_lower for term in ["plan", "prep", "initial"]):
            return ProjectStatus.PLANNING
        elif any(term in status_lower for term in ["active", "ongoing", "progress", "current"]):
            return ProjectStatus.ACTIVE
        elif any(term in status_lower for term in ["hold", "pause", "suspend"]):
            return ProjectStatus.ON_HOLD
        elif any(term in status_lower for term in ["complete", "finish", "done"]):
            return ProjectStatus.COMPLETED
        elif any(term in status_lower for term in ["cancel", "abort", "terminate"]):
            return ProjectStatus.CANCELLED
        else:
            return ProjectStatus.UNKNOWN
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed datetime or None
        """
        if not date_str:
            return None
        
        try:
            from datetime import datetime
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            try:
                import dateparser
                return dateparser.parse(date_str)
            except Exception:
                return None