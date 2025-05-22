"""
Monitor base class for the Project Intelligence System.

This module provides the abstract base class for all monitors
used by the Project Intelligence System.
"""

import abc
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from ..models.project import Project

logger = logging.getLogger(__name__)


class Monitor(abc.ABC):
    """
    Abstract base class for project monitors.
    
    A monitor is responsible for analyzing project data and generating
    insights, alerts, or other information.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the monitor.
        
        Args:
            config: Configuration dictionary for the monitor
        """
        self.config = config or {}
        self.last_run = None
        self.results = {}
    
    @abc.abstractmethod
    async def run(self, projects: Dict[str, Project]) -> Dict[str, Any]:
        """
        Run the monitor on the given projects.
        
        Args:
            projects: Dictionary of projects to monitor
            
        Returns:
            Dictionary of monitor results
        """
        self.last_run = datetime.now()
        return {}
    
    def get_last_results(self) -> Dict[str, Any]:
        """
        Get the results from the last run.
        
        Returns:
            Dictionary of results from the last run
        """
        return self.results
    
    def get_last_run_time(self) -> Optional[datetime]:
        """
        Get the time of the last run.
        
        Returns:
            Datetime of the last run, or None if never run
        """
        return self.last_run