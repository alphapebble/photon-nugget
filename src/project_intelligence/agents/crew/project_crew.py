"""
Project crew manager using CrewAI for the Project Intelligence System.

This module provides the ProjectCrew class that orchestrates a team of AI agents
for extracting, processing, and analyzing project information.
"""

import logging
from typing import Any, Dict, List, Optional

from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI

from ..project_detector import ProjectDetectorAgent
from ..task_manager import TaskManagerAgent
from ..resource_tracker import ResourceTrackerAgent
from ..risk_assessor import RiskAssessorAgent
from ..timeline_analyzer import TimelineAnalyzerAgent
from ..integrator import IntegratorAgent
from ...models.extraction import DocumentContext, ExtractionResult

logger = logging.getLogger(__name__)


class ProjectCrew:
    """
    Crew of AI agents for project intelligence.
    
    This class creates and manages a team of specialized AI agents that work
    together to extract and analyze project information from various sources.
    """
    
    def __init__(self, llm: Optional[Any] = None):
        """
        Initialize the project crew.
        
        Args:
            llm: Language model to use for the agents (defaults to ChatOpenAI)
        """
        self.llm = llm or ChatOpenAI(temperature=0, model="gpt-4o")
        self.agents = self._create_agents()
        self.crew = self._create_crew()
    
    def _create_agents(self) -> Dict[str, Agent]:
        """
        Create the crew agents.
        
        Returns:
            Dictionary of agent instances
        """
        return {
            "project_detector": Agent(
                role="Project Detector",
                goal="Identify project names, descriptions, and status from document content",
                backstory=(
                    "You are an expert in identifying project information from various "
                    "types of communications. You can spot project names, descriptions, "
                    "and basic details even when they're mentioned casually."
                ),
                allow_delegation=True,
                verbose=True,
                llm=self.llm,
            ),
            "task_manager": Agent(
                role="Task Manager",
                goal="Extract task details including status, owners, and deadlines",
                backstory=(
                    "You specialize in identifying tasks, assignments, and deadlines "
                    "from project communications. You can determine task status, owners, "
                    "and dependencies accurately."
                ),
                allow_delegation=True,
                verbose=True,
                llm=self.llm,
            ),
            "resource_tracker": Agent(
                role="Resource Tracker",
                goal="Identify resource allocations, requirements, and availability",
                backstory=(
                    "You excel at spotting mentions of resources including staff, equipment, "
                    "and materials in project communications. You can determine allocated "
                    "quantities and availability status."
                ),
                allow_delegation=True,
                verbose=True,
                llm=self.llm,
            ),
            "timeline_analyzer": Agent(
                role="Timeline Analyzer",
                goal="Extract project timelines, milestones, and schedule information",
                backstory=(
                    "You are skilled at identifying timeline information including start dates, "
                    "end dates, milestones, and schedule dependencies from project communications."
                ),
                allow_delegation=True,
                verbose=True,
                llm=self.llm,
            ),
            "risk_assessor": Agent(
                role="Risk Assessor",
                goal="Identify potential risks, blockers, and issues mentioned in communications",
                backstory=(
                    "You specialize in spotting potential risks, blockers, and issues in project "
                    "communications. You can assess the severity and impact of identified risks."
                ),
                allow_delegation=True,
                verbose=True,
                llm=self.llm,
            ),
            "integrator": Agent(
                role="Information Integrator",
                goal="Combine extracted information into a coherent project overview",
                backstory=(
                    "You excel at synthesizing information from multiple sources into a coherent "
                    "and comprehensive project overview. You can resolve conflicts and inconsistencies "
                    "in the extracted information."
                ),
                allow_delegation=False,
                verbose=True,
                llm=self.llm,
            ),
        }
    
    def _create_crew(self) -> Crew:
        """
        Create the crew with the agents and their tasks.
        
        Returns:
            Configured crew instance
        """
        return Crew(
            agents=list(self.agents.values()),
            tasks=self._create_tasks(),
            verbose=True,
            process=Process.sequential,
        )
    
    def _create_tasks(self) -> List[Task]:
        """
        Create the tasks for the crew.
        
        Returns:
            List of tasks for the crew
        """
        return [
            Task(
                description=(
                    "Analyze the document content and identify any project information, "
                    "including project name, description, status, and basic details."
                ),
                expected_output=(
                    "JSON object with detected project information including name, "
                    "description, status, and confidence score."
                ),
                agent=self.agents["project_detector"],
            ),
            Task(
                description=(
                    "Extract all task information from the document, including task names, "
                    "descriptions, owners, statuses, and deadlines."
                ),
                expected_output=(
                    "JSON list of detected tasks with their attributes."
                ),
                agent=self.agents["task_manager"],
            ),
            Task(
                description=(
                    "Identify all resource information mentioned in the document, "
                    "including staff, equipment, materials, and their allocation."
                ),
                expected_output=(
                    "JSON list of detected resources with their attributes."
                ),
                agent=self.agents["resource_tracker"],
            ),
            Task(
                description=(
                    "Extract timeline information from the document, including start dates, "
                    "end dates, milestones, and schedule dependencies."
                ),
                expected_output=(
                    "JSON object with timeline information."
                ),
                agent=self.agents["timeline_analyzer"],
            ),
            Task(
                description=(
                    "Identify potential risks, blockers, and issues mentioned in the document, "
                    "including their severity and impact."
                ),
                expected_output=(
                    "JSON list of detected risks with their attributes."
                ),
                agent=self.agents["risk_assessor"],
            ),
            Task(
                description=(
                    "Integrate all the extracted information into a coherent project overview, "
                    "resolving any conflicts or inconsistencies."
                ),
                expected_output=(
                    "Comprehensive JSON object with all project information structured "
                    "according to the ExtractionResult schema."
                ),
                agent=self.agents["integrator"],
            ),
        ]
    
    async def process_document(self, document: DocumentContext) -> ExtractionResult:
        """
        Process a document through the crew to extract project information.
        
        Args:
            document: Document to process
            
        Returns:
            Extraction result with project information
        """
        try:
            # Prepare the document context as input for the crew
            document_json = document.model_dump_json()
            
            # Execute the crew tasks
            result = self.crew.kickoff(inputs={"document": document_json})
            
            # Parse the result into an ExtractionResult
            import json
            from pydantic import ValidationError
            
            try:
                # Try to parse the result as JSON
                if isinstance(result, str):
                    result_dict = json.loads(result)
                else:
                    result_dict = result
                
                # Create ExtractionResult from the parsed data
                extraction_result = ExtractionResult.model_validate(result_dict)
                return extraction_result
            except (json.JSONDecodeError, ValidationError) as e:
                logger.error(f"Error parsing crew result: {str(e)}")
                # Return a minimal result with error
                return ExtractionResult(
                    document_id=document.id,
                    document_type=document.type,
                    confidence=0.0,
                    requires_human_review=True,
                    errors=[f"Error parsing crew result: {str(e)}"],
                )
        except Exception as e:
            logger.error(f"Error in crew processing: {str(e)}")
            # Return a minimal result with error
            return ExtractionResult(
                document_id=document.id,
                document_type=document.type,
                confidence=0.0,
                requires_human_review=True,
                errors=[f"Crew processing error: {str(e)}"],
            )