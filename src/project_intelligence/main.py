"""
Project Intelligence System main entry point.

This module provides the main entry point for the Project Intelligence System,
integrating all components for real-time project intelligence extraction.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from .connectors.email import EmailConnector
from .connectors.slack import SlackConnector
from .connectors.spreadsheet import SpreadsheetConnector
from .connectors.teams import TeamsConnector
from .models.extraction import DocumentContext, DocumentType, ExtractionResult
from .models.project import Project, Task, ProjectUpdate, ResourceStatus
from .agents.crew.project_crew import ProjectCrew
from .processing.ray_processor import ray_processor
from .dashboard.dashboard_manager import DashboardManager
from .workflows.extraction_workflow import process_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Project Intelligence System",
    description="AI-driven project intelligence layer for real-time project monitoring",
    version="0.1.0",
)

# Initialize global state
projects: Dict[str, Project] = {}
dashboard_manager = DashboardManager()
crew = ProjectCrew()
connectors = {}

# Initialize background processing
processing_lock = asyncio.Lock()
processing_queue = asyncio.Queue()
is_processing = False


class ConnectorConfig(BaseModel):
    """Configuration for a data connector."""
    
    connector_type: str = Field(..., description="Type of connector (email, slack, teams, spreadsheet)")
    config: Dict[str, Any] = Field(..., description="Configuration for the connector")


class DocumentInput(BaseModel):
    """Input for manual document processing."""
    
    content: str = Field(..., description="Content of the document")
    type: DocumentType = Field(..., description="Type of document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for the document")
    source: Optional[str] = Field(None, description="Source of the document")
    author: Optional[str] = Field(None, description="Author of the document")


@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    logger.info("Starting Project Intelligence System")
    
    # Initialize dashboard
    await dashboard_manager.initialize()
    
    # Initialize Ray processor
    ray_processor.initialize()
    
    # Start background processing
    asyncio.create_task(background_processor())


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Project Intelligence System")
    
    # Shutdown Ray processor
    ray_processor.shutdown()
    
    # Close connectors
    for name, connector in connectors.items():
        await connector.close()


async def background_processor():
    """Background task to process documents from the queue."""
    global is_processing
    
    logger.info("Starting background processor")
    is_processing = True
    
    while is_processing:
        try:
            # Process documents in batches
            batch = []
            while not processing_queue.empty() and len(batch) < 10:
                try:
                    document = processing_queue.get_nowait()
                    batch.append(document)
                except asyncio.QueueEmpty:
                    break
            
            if batch:
                logger.info(f"Processing batch of {len(batch)} documents")
                
                # Process documents
                results = await ray_processor.process_batch(batch)
                
                # Update projects with results
                async with processing_lock:
                    for result in results:
                        if result.project:
                            await update_project_from_result(result)
                
                # Update dashboard
                await dashboard_manager.update(projects)
            
            # Wait before checking queue again
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in background processor: {str(e)}")
            await asyncio.sleep(5)


async def update_project_from_result(result: ExtractionResult) -> None:
    """
    Update projects database with extraction result.
    
    Args:
        result: Extraction result to process
    """
    if not result.project:
        return
    
    project_name = result.project.name
    
    # Create project if it doesn't exist
    if project_name not in projects:
        projects[project_name] = Project(
            name=project_name,
            description=result.project.description,
            status=result.project.status.value,
            owner=result.project.owner,
            team_members=result.project.team_members,
            start_date=result.project.start_date,
            end_date=result.project.end_date,
        )
    
    project = projects[project_name]
    
    # Update project with tasks
    for task_extraction in result.tasks:
        task_id = f"task-{len(project.tasks) + 1}" if not task_extraction.name in [t.name for t in project.tasks.values()] else next(t.id for t in project.tasks.values() if t.name == task_extraction.name)
        
        task = Task(
            id=task_id,
            name=task_extraction.name,
            description=task_extraction.description or "",
            status=task_extraction.status.value,
            owner=task_extraction.owner,
            due_date=task_extraction.due_date,
            created_at=task_extraction.start_date or datetime.now(),
            updated_at=datetime.now(),
            blockers=[str(blocker) for blocker in task_extraction.blockers],
            priority=task_extraction.priority.value,
            completion_percentage=task_extraction.completion_percentage,
        )
        
        project.add_or_update_task(task)
    
    # Update project with resources
    for resource_extraction in result.resources:
        resource = ResourceStatus(
            resource_type=resource_extraction.type.value,
            status=resource_extraction.status.value,
            quantity=resource_extraction.quantity,
            last_updated=datetime.now(),
        )
        
        project.update_resource_status(resource)
    
    # Add project update
    if result.document_type:
        project.add_update(
            ProjectUpdate(
                timestamp=datetime.now(),
                content=f"Information extracted from {result.document_type.value}",
                author="Project Intelligence System",
                update_type="automatic",
            )
        )


@app.post("/register_connector", response_model=Dict[str, str])
async def register_connector(config: ConnectorConfig):
    """
    Register a new data connector.
    
    Args:
        config: Connector configuration
    
    Returns:
        Dictionary with registration status
    """
    try:
        connector_type = config.connector_type.lower()
        
        if connector_type == "email":
            connector = EmailConnector(config.config)
        elif connector_type == "slack":
            connector = SlackConnector(config.config)
        elif connector_type == "teams":
            connector = TeamsConnector(config.config)
        elif connector_type == "spreadsheet":
            connector = SpreadsheetConnector(config.config)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown connector type: {connector_type}")
        
        # Initialize connector
        await connector.initialize()
        
        # Generate connector name
        name = f"{connector_type}-{len([c for c in connectors if c.startswith(connector_type)]) + 1}"
        
        # Register connector
        connectors[name] = connector
        
        return {"status": "success", "message": f"Connector registered as {name}"}
    except Exception as e:
        logger.error(f"Error registering connector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering connector: {str(e)}")


@app.post("/process_document", response_model=Dict[str, str])
async def process_document_endpoint(document: DocumentInput, background_tasks: BackgroundTasks):
    """
    Process a document manually.
    
    Args:
        document: Document to process
        background_tasks: FastAPI background tasks
    
    Returns:
        Dictionary with processing status
    """
    try:
        # Create document context
        from datetime import datetime
        
        doc_context = DocumentContext(
            id=f"manual-{datetime.now().timestamp()}",
            type=document.type,
            content=document.content,
            metadata=document.metadata,
            source=document.source,
            author=document.author,
            created_at=datetime.now(),
        )
        
        # Add to processing queue
        await processing_queue.put(doc_context)
        
        return {"status": "success", "message": "Document queued for processing"}
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.get("/projects", response_model=Dict[str, Any])
async def get_projects():
    """
    Get all projects.
    
    Returns:
        Dictionary of projects
    """
    return {name: project.to_dict() for name, project in projects.items()}


@app.get("/project/{project_name}", response_model=Dict[str, Any])
async def get_project(project_name: str):
    """
    Get a specific project.
    
    Args:
        project_name: Name of the project
    
    Returns:
        Project data
    """
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_name}")
    
    return projects[project_name].to_dict()


@app.get("/stats", response_model=Dict[str, Any])
async def get_stats():
    """
    Get system statistics.
    
    Returns:
        Dictionary of system statistics
    """
    # Get processor stats
    processor_stats = await ray_processor.get_processor_stats()
    
    # Compile system stats
    return {
        "projects": len(projects),
        "connectors": len(connectors),
        "processors": processor_stats,
        "queue_size": processing_queue.qsize(),
    }


@app.post("/poll_connectors", response_model=Dict[str, Any])
async def poll_connectors(background_tasks: BackgroundTasks):
    """
    Poll all connectors for new data.
    
    Args:
        background_tasks: FastAPI background tasks
    
    Returns:
        Dictionary with polling status
    """
    background_tasks.add_task(poll_all_connectors)
    return {"status": "success", "message": "Polling connectors in background"}


async def poll_all_connectors():
    """Poll all connectors for new data."""
    for name, connector in connectors.items():
        try:
            logger.info(f"Polling connector: {name}")
            
            # Fetch data from connector
            data = await connector.fetch_data()
            
            # Convert to document contexts
            documents = []
            for item in data:
                try:
                    doc_type = DocumentType.UNKNOWN
                    if item.get("source_type") == "email":
                        doc_type = DocumentType.EMAIL
                    elif item.get("source_type") == "slack":
                        doc_type = DocumentType.SLACK_MESSAGE
                    elif item.get("source_type") == "teams":
                        doc_type = DocumentType.TEAMS_MESSAGE
                    elif item.get("source_type") == "spreadsheet":
                        doc_type = DocumentType.SPREADSHEET
                    
                    content = ""
                    if "body" in item:
                        content = item["body"]
                    elif "text" in item:
                        content = item["text"]
                    elif "data" in item:
                        import json
                        content = json.dumps(item["data"])
                    
                    doc = DocumentContext(
                        id=f"{name}-{datetime.now().timestamp()}-{hash(str(item))}",
                        type=doc_type,
                        content=content,
                        metadata=item,
                        source=name,
                        author=item.get("sender") or item.get("user_name") or item.get("author"),
                        created_at=item.get("date") or item.get("timestamp") or datetime.now(),
                    )
                    
                    documents.append(doc)
                except Exception as e:
                    logger.error(f"Error creating document context: {str(e)}")
            
            # Add to processing queue
            for doc in documents:
                await processing_queue.put(doc)
            
            logger.info(f"Added {len(documents)} documents from {name} to processing queue")
        except Exception as e:
            logger.error(f"Error polling connector {name}: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)