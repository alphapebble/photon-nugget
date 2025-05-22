"""
Core module for the Project Intelligence System.

This module provides the main class for the AI-driven project intelligence layer
that monitors and organizes project information from various sources.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .connectors.base import DataSourceConnector
from .extractors.information_extractor import InformationExtractor
from .models.project import Project, Task, ProjectUpdate, ResourceStatus
from .dashboard.dashboard_manager import DashboardManager
from .monitors.monitor_base import Monitor

logger = logging.getLogger(__name__)


class ProjectIntelligenceSystem:
    """
    Main class for the AI-driven project intelligence system.
    
    This system connects to various data sources, extracts project information,
    structures it, and presents it in a dashboard. It also monitors project
    resources and progress in real-time.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ProjectIntelligenceSystem.
        
        Args:
            config: Configuration dictionary for the system
        """
        self.config = config or {}
        self.connectors: Dict[str, DataSourceConnector] = {}
        self.extractor = InformationExtractor()
        self.dashboard_manager = DashboardManager()
        self.monitors: Dict[str, Monitor] = {}
        self.projects: Dict[str, Project] = {}
        self.is_running = False
        self.processing_lock = asyncio.Lock()
        
        logger.info("Project Intelligence System initialized")
    
    def register_connector(self, name: str, connector: DataSourceConnector) -> None:
        """
        Register a data source connector.
        
        Args:
            name: Name identifier for the connector
            connector: The connector instance
        """
        self.connectors[name] = connector
        logger.info(f"Registered connector: {name}")
    
    def register_monitor(self, name: str, monitor: Monitor) -> None:
        """
        Register a project monitor.
        
        Args:
            name: Name identifier for the monitor
            monitor: The monitor instance
        """
        self.monitors[name] = monitor
        logger.info(f"Registered monitor: {name}")
    
    async def process_data_source(self, connector_name: str) -> List[Dict[str, Any]]:
        """
        Process data from a specific source and extract information.
        
        Args:
            connector_name: Name of the connector to use
            
        Returns:
            List of extracted information items
        """
        if connector_name not in self.connectors:
            logger.error(f"Connector not found: {connector_name}")
            return []
        
        connector = self.connectors[connector_name]
        try:
            # Fetch raw data from the source
            raw_data = await connector.fetch_data()
            
            # Extract structured information
            extracted_info = await self.extractor.extract_information(raw_data)
            
            # Update projects database
            await self._update_projects(extracted_info)
            
            return extracted_info
        except Exception as e:
            logger.error(f"Error processing data from {connector_name}: {str(e)}")
            return []
    
    async def _update_projects(self, information_items: List[Dict[str, Any]]) -> None:
        """
        Update projects database with extracted information.
        
        Args:
            information_items: List of extracted information items
        """
        async with self.processing_lock:
            for item in information_items:
                item_type = item.get("type")
                project_name = item.get("project_name")
                
                if not project_name:
                    logger.warning(f"Missing project name in item: {item}")
                    continue
                
                # Create project if it doesn't exist
                if project_name not in self.projects:
                    self.projects[project_name] = Project(
                        name=project_name,
                        created_at=datetime.now()
                    )
                
                project = self.projects[project_name]
                
                # Update project based on item type
                if item_type == "task":
                    project.add_or_update_task(Task(
                        id=item.get("id") or f"task-{len(project.tasks) + 1}",
                        name=item.get("name", "Unnamed Task"),
                        description=item.get("description", ""),
                        status=item.get("status", "pending"),
                        owner=item.get("owner"),
                        due_date=item.get("due_date"),
                        created_at=datetime.now(),
                        blockers=item.get("blockers", [])
                    ))
                elif item_type == "update":
                    project.add_update(ProjectUpdate(
                        timestamp=datetime.now(),
                        content=item.get("content", ""),
                        author=item.get("author", "Unknown"),
                        update_type=item.get("update_type", "general")
                    ))
                elif item_type == "resource":
                    project.update_resource_status(ResourceStatus(
                        resource_type=item.get("resource_type", "unknown"),
                        status=item.get("status", "unknown"),
                        quantity=item.get("quantity"),
                        last_updated=datetime.now()
                    ))
    
    async def run_monitors(self) -> Dict[str, Any]:
        """
        Run all registered monitors and collect their results.
        
        Returns:
            Dictionary of monitor results
        """
        results = {}
        for name, monitor in self.monitors.items():
            try:
                results[name] = await monitor.run(self.projects)
            except Exception as e:
                logger.error(f"Error running monitor {name}: {str(e)}")
                results[name] = {"error": str(e)}
        
        return results
    
    async def update_dashboard(self) -> None:
        """Update the dashboard with current project information."""
        try:
            await self.dashboard_manager.update(self.projects)
            logger.info("Dashboard updated successfully")
        except Exception as e:
            logger.error(f"Error updating dashboard: {str(e)}")
    
    async def start(self) -> None:
        """Start the project intelligence system."""
        if self.is_running:
            logger.warning("System is already running")
            return
        
        self.is_running = True
        logger.info("Starting Project Intelligence System")
        
        # Initialize connectors
        for name, connector in self.connectors.items():
            await connector.initialize()
        
        # Start monitor loop
        asyncio.create_task(self._monitoring_loop())
    
    async def _monitoring_loop(self) -> None:
        """Background loop for continuous monitoring."""
        while self.is_running:
            try:
                # Process data from all connectors
                for connector_name in self.connectors:
                    await self.process_data_source(connector_name)
                
                # Run all monitors
                await self.run_monitors()
                
                # Update dashboard
                await self.update_dashboard()
                
                # Wait for next cycle
                await asyncio.sleep(self.config.get("monitoring_interval", 300))  # Default: 5 minutes
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Wait a bit before retrying
    
    async def stop(self) -> None:
        """Stop the project intelligence system."""
        if not self.is_running:
            logger.warning("System is not running")
            return
        
        self.is_running = False
        logger.info("Stopping Project Intelligence System")
        
        # Close connectors
        for name, connector in self.connectors.items():
            await connector.close()