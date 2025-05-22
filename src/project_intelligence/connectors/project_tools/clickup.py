"""
ClickUp connector for the Project Intelligence System.

This module provides a connector for fetching and processing data from
ClickUp tasks, lists, and spaces.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..base import DataSourceConnector

logger = logging.getLogger(__name__)


class ClickUpConnector(DataSourceConnector):
    """
    Connector for ClickUp.
    
    This connector fetches data from ClickUp workspaces, spaces, folders, lists, and tasks
    using the ClickUp API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ClickUp connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - api_token: ClickUp API token (required)
                - workspace_ids: List of workspace IDs to monitor (default: [])
                - space_ids: List of space IDs to monitor (default: [])
                - folder_ids: List of folder IDs to monitor (default: [])
                - list_ids: List of list IDs to monitor (default: [])
                - include_subtasks: Whether to include subtasks (default: True)
                - include_comments: Whether to include task comments (default: True)
                - include_time_tracking: Whether to include time tracking data (default: True)
                - include_custom_fields: Whether to include custom fields (default: True)
                - include_checklists: Whether to include checklists (default: True)
                - statuses: List of task statuses to filter by (default: all)
                - max_tasks: Maximum number of tasks to fetch (default: 1000)
                - poll_interval: How often to check for changes in seconds (default: 300)
        """
        super().__init__(config)
        self.api_token = self.config.get("api_token")
        if not self.api_token:
            raise ValueError("ClickUp API token is required")
        
        self.workspace_ids = self.config.get("workspace_ids", [])
        self.space_ids = self.config.get("space_ids", [])
        self.folder_ids = self.config.get("folder_ids", [])
        self.list_ids = self.config.get("list_ids", [])
        self.include_subtasks = self.config.get("include_subtasks", True)
        self.include_comments = self.config.get("include_comments", True)
        self.include_time_tracking = self.config.get("include_time_tracking", True)
        self.include_custom_fields = self.config.get("include_custom_fields", True)
        self.include_checklists = self.config.get("include_checklists", True)
        self.statuses = self.config.get("statuses", [])
        self.max_tasks = self.config.get("max_tasks", 1000)
        
        self.session = None
        self.last_update_timestamps = {}
    
    async def initialize(self) -> None:
        """Initialize the ClickUp connector."""
        await super().initialize()
        
        try:
            import aiohttp
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            
            # Initialize last update timestamps
            current_time = datetime.now().timestamp() - 86400  # 24 hours ago
            
            for workspace_id in self.workspace_ids:
                self.last_update_timestamps[f"workspace_{workspace_id}"] = current_time
            
            for space_id in self.space_ids:
                self.last_update_timestamps[f"space_{space_id}"] = current_time
            
            for folder_id in self.folder_ids:
                self.last_update_timestamps[f"folder_{folder_id}"] = current_time
            
            for list_id in self.list_ids:
                self.last_update_timestamps[f"list_{list_id}"] = current_time
            
            logger.info("ClickUp connector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ClickUp connector: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from ClickUp.
        
        Returns:
            List of data items from ClickUp
        """
        await self._check_initialization()
        
        all_items = []
        
        # Fetch tasks from workspaces, spaces, folders, and lists
        try:
            # First fetch from workspaces
            for workspace_id in self.workspace_ids:
                try:
                    workspace_tasks = await self._fetch_workspace_tasks(workspace_id)
                    all_items.extend(workspace_tasks)
                except Exception as e:
                    logger.error(f"Error fetching tasks from workspace {workspace_id}: {str(e)}")
            
            # Fetch from spaces
            for space_id in self.space_ids:
                try:
                    space_tasks = await self._fetch_space_tasks(space_id)
                    all_items.extend(space_tasks)
                except Exception as e:
                    logger.error(f"Error fetching tasks from space {space_id}: {str(e)}")
            
            # Fetch from folders
            for folder_id in self.folder_ids:
                try:
                    folder_tasks = await self._fetch_folder_tasks(folder_id)
                    all_items.extend(folder_tasks)
                except Exception as e:
                    logger.error(f"Error fetching tasks from folder {folder_id}: {str(e)}")
            
            # Fetch from lists
            for list_id in self.list_ids:
                try:
                    list_tasks = await self._fetch_list_tasks(list_id)
                    all_items.extend(list_tasks)
                except Exception as e:
                    logger.error(f"Error fetching tasks from list {list_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching data from ClickUp: {str(e)}")
        
        return all_items
    
    async def _fetch_workspace_tasks(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Fetch tasks from a ClickUp workspace.
        
        Args:
            workspace_id: ID of the workspace
            
        Returns:
            List of task data
        """
        # Get all spaces in the workspace
        spaces = await self._api_get(f"team/{workspace_id}/space")
        
        all_tasks = []
        for space in spaces.get("spaces", []):
            space_id = space.get("id")
            space_tasks = await self._fetch_space_tasks(space_id)
            all_tasks.extend(space_tasks)
        
        # Update timestamp
        self.last_update_timestamps[f"workspace_{workspace_id}"] = datetime.now().timestamp()
        
        return all_tasks
    
    async def _fetch_space_tasks(self, space_id: str) -> List[Dict[str, Any]]:
        """
        Fetch tasks from a ClickUp space.
        
        Args:
            space_id: ID of the space
            
        Returns:
            List of task data
        """
        # Get all folders in the space
        folders = await self._api_get(f"space/{space_id}/folder")
        
        all_tasks = []
        
        # Get tasks from folders
        for folder in folders.get("folders", []):
            folder_id = folder.get("id")
            folder_tasks = await self._fetch_folder_tasks(folder_id)
            all_tasks.extend(folder_tasks)
        
        # Get tasks from folderless lists
        lists = await self._api_get(f"space/{space_id}/list")
        for list_item in lists.get("lists", []):
            list_id = list_item.get("id")
            list_tasks = await self._fetch_list_tasks(list_id)
            all_tasks.extend(list_tasks)
        
        # Update timestamp
        self.last_update_timestamps[f"space_{space_id}"] = datetime.now().timestamp()
        
        return all_tasks
    
    async def _fetch_folder_tasks(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        Fetch tasks from a ClickUp folder.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            List of task data
        """
        # Get all lists in the folder
        lists = await self._api_get(f"folder/{folder_id}/list")
        
        all_tasks = []
        for list_item in lists.get("lists", []):
            list_id = list_item.get("id")
            list_tasks = await self._fetch_list_tasks(list_id)
            all_tasks.extend(list_tasks)
        
        # Update timestamp
        self.last_update_timestamps[f"folder_{folder_id}"] = datetime.now().timestamp()
        
        return all_tasks
    
    async def _fetch_list_tasks(self, list_id: str) -> List[Dict[str, Any]]:
        """
        Fetch tasks from a ClickUp list.
        
        Args:
            list_id: ID of the list
            
        Returns:
            List of task data
        """
        # Determine date to filter by (tasks updated since last check)
        last_update = self.last_update_timestamps.get(f"list_{list_id}")
        last_update_date = datetime.fromtimestamp(last_update).strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare query parameters
        params = {
            "subtasks": "true" if self.include_subtasks else "false",
            "include_closed": "true",
            "date_updated_gt": last_update_date
        }
        
        # Add status filter if specified
        if self.statuses:
            params["statuses[]"] = self.statuses
        
        # Get tasks
        tasks_response = await self._api_get(f"list/{list_id}/task", params)
        
        all_tasks = []
        for task in tasks_response.get("tasks", []):
            processed_task = await self._process_task(task)
            all_tasks.append(processed_task)
            
            # If we've reached the maximum number of tasks, stop
            if len(all_tasks) >= self.max_tasks:
                break
        
        # Update timestamp
        self.last_update_timestamps[f"list_{list_id}"] = datetime.now().timestamp()
        
        return all_tasks
    
    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a ClickUp task.
        
        Args:
            task: Raw task data from ClickUp API
            
        Returns:
            Processed task data
        """
        task_id = task.get("id")
        
        # Build a structured representation of the task
        processed_task = {
            "source_type": "clickup",
            "content_type": "task",
            "id": task_id,
            "name": task.get("name"),
            "description": task.get("description"),
            "status": task.get("status", {}).get("status"),
            "priority": task.get("priority", {}).get("priority") if task.get("priority") else None,
            "due_date": task.get("due_date"),
            "start_date": task.get("start_date"),
            "date_created": task.get("date_created"),
            "date_updated": task.get("date_updated"),
            "date_closed": task.get("date_closed"),
            "creator": self._extract_user(task.get("creator")),
            "assignees": [self._extract_user(assignee) for assignee in task.get("assignees", [])],
            "watchers": [self._extract_user(watcher) for watcher in task.get("watchers", [])],
            "parent": task.get("parent"),
            "tags": task.get("tags", []),
            "url": task.get("url"),
            "list": {
                "id": task.get("list", {}).get("id"),
                "name": task.get("list", {}).get("name")
            },
            "folder": {
                "id": task.get("folder", {}).get("id"),
                "name": task.get("folder", {}).get("name")
            },
            "space": {
                "id": task.get("space", {}).get("id"),
                "name": task.get("space", {}).get("name")
            },
            "time_estimate": task.get("time_estimate"),
            "time_spent": task.get("time_spent")
        }
        
        # Add custom fields if included
        if self.include_custom_fields and "custom_fields" in task:
            processed_task["custom_fields"] = []
            for field in task.get("custom_fields", []):
                processed_field = {
                    "id": field.get("id"),
                    "name": field.get("name"),
                    "type": field.get("type"),
                    "value": field.get("value")
                }
                processed_task["custom_fields"].append(processed_field)
        
        # Add checklists if included
        if self.include_checklists and "checklists" in task:
            processed_task["checklists"] = []
            for checklist in task.get("checklists", []):
                processed_checklist = {
                    "id": checklist.get("id"),
                    "name": checklist.get("name"),
                    "items": []
                }
                
                for item in checklist.get("items", []):
                    processed_item = {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "resolved": item.get("resolved"),
                        "assignee": self._extract_user(item.get("assignee")) if item.get("assignee") else None
                    }
                    processed_checklist["items"].append(processed_item)
                
                processed_task["checklists"].append(processed_checklist)
        
        # Add comments if included
        if self.include_comments:
            try:
                comments_response = await self._api_get(f"task/{task_id}/comment")
                comments = []
                
                for comment in comments_response.get("comments", []):
                    processed_comment = {
                        "id": comment.get("id"),
                        "comment": comment.get("comment", {}).get("text", ""),
                        "date": comment.get("date"),
                        "user": self._extract_user(comment.get("user"))
                    }
                    comments.append(processed_comment)
                
                processed_task["comments"] = comments
            except Exception as e:
                logger.error(f"Error fetching comments for task {task_id}: {str(e)}")
                processed_task["comments"] = []
        
        # Add time tracking data if included
        if self.include_time_tracking:
            try:
                time_response = await self._api_get(f"task/{task_id}/time")
                time_entries = []
                
                for entry in time_response.get("data", []):
                    processed_entry = {
                        "id": entry.get("id"),
                        "task_id": entry.get("task", {}).get("id"),
                        "wid": entry.get("wid"),
                        "user": self._extract_user(entry.get("user")),
                        "start": entry.get("start"),
                        "end": entry.get("end"),
                        "duration": entry.get("duration"),
                        "description": entry.get("description")
                    }
                    time_entries.append(processed_entry)
                
                processed_task["time_entries"] = time_entries
            except Exception as e:
                logger.error(f"Error fetching time entries for task {task_id}: {str(e)}")
                processed_task["time_entries"] = []
        
        return processed_task
    
    def _extract_user(self, user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract user information.
        
        Args:
            user: ClickUp user object
            
        Returns:
            Extracted user information
        """
        if not user:
            return None
        
        return {
            "id": user.get("id"),
            "username": user.get("username"),
            "email": user.get("email"),
            "color": user.get("color"),
            "profile_picture": user.get("profilePicture")
        }
    
    async def _api_get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """
        Make a GET request to the ClickUp API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            Response data as JSON
        """
        if not self.session:
            raise RuntimeError("ClickUp connector session not initialized")
        
        url = f"https://api.clickup.com/api/v2/{endpoint}"
        
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"ClickUp API error: {response.status} - {error_text}")
                    raise Exception(f"ClickUp API error: {response.status}")
        except Exception as e:
            logger.error(f"Error in ClickUp API request to {endpoint}: {str(e)}")
            raise
    
    async def close(self) -> None:
        """Close the ClickUp connector."""
        if self.session:
            await self.session.close()
            self.session = None
        
        await super().close()
        logger.info("ClickUp connector closed")