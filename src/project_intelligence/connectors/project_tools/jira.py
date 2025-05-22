"""
Jira connector for the Project Intelligence System.

This module provides a connector for fetching and processing data from
Jira projects, issues, and sprints.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..base import DataSourceConnector

logger = logging.getLogger(__name__)


class JiraConnector(DataSourceConnector):
    """
    Connector for Jira.
    
    This connector fetches data from Jira projects, issues, and sprints
    using the Jira REST API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Jira connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - base_url: Jira instance URL (required)
                - username: Jira username for basic auth
                - api_token: Jira API token for basic auth
                - oauth: OAuth configuration for Jira Cloud
                - projects: List of project keys to monitor (default: [])
                - jql_filter: Custom JQL filter for issues (default: "")
                - include_comments: Whether to include issue comments (default: True)
                - include_worklogs: Whether to include issue worklogs (default: True)
                - include_changelog: Whether to include issue changelog (default: True)
                - max_results: Maximum number of issues to fetch per project (default: 1000)
                - fields: List of fields to include in issue data (default: all)
                - poll_interval: How often to check for changes in seconds (default: 300)
        """
        super().__init__(config)
        self.base_url = self.config.get("base_url")
        if not self.base_url:
            raise ValueError("Jira base URL is required")
        
        # Remove trailing slash if present
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]
        
        # Authentication
        self.username = self.config.get("username")
        self.api_token = self.config.get("api_token")
        self.oauth_config = self.config.get("oauth")
        
        if not ((self.username and self.api_token) or self.oauth_config):
            raise ValueError("Jira authentication credentials are required")
        
        self.projects = self.config.get("projects", [])
        self.jql_filter = self.config.get("jql_filter", "")
        self.include_comments = self.config.get("include_comments", True)
        self.include_worklogs = self.config.get("include_worklogs", True)
        self.include_changelog = self.config.get("include_changelog", True)
        self.max_results = self.config.get("max_results", 1000)
        self.fields = self.config.get("fields")
        
        self.session = None
        self.last_update_timestamps = {}
    
    async def initialize(self) -> None:
        """Initialize the Jira connector."""
        await super().initialize()
        
        try:
            import aiohttp
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            
            # Initialize last update timestamps for each project
            for project in self.projects:
                self.last_update_timestamps[project] = datetime.now().timestamp() - 86400  # 24 hours ago
            
            logger.info("Jira connector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jira connector: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from Jira.
        
        Returns:
            List of data items from Jira
        """
        await self._check_initialization()
        
        all_items = []
        
        # Fetch issues from each project
        for project in self.projects:
            try:
                project_issues = await self._fetch_project_issues(project)
                all_items.extend(project_issues)
            except Exception as e:
                logger.error(f"Error fetching Jira project {project}: {str(e)}")
        
        # Fetch issues using custom JQL if provided
        if self.jql_filter:
            try:
                custom_issues = await self._fetch_issues_by_jql(self.jql_filter)
                all_items.extend(custom_issues)
            except Exception as e:
                logger.error(f"Error fetching Jira issues with custom JQL: {str(e)}")
        
        return all_items
    
    async def _fetch_project_issues(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Fetch issues from a Jira project.
        
        Args:
            project_key: Key of the project to fetch
            
        Returns:
            List of issue data
        """
        # Build JQL query for issues updated since last check
        last_update = self.last_update_timestamps.get(project_key)
        last_update_date = datetime.fromtimestamp(last_update).strftime("%Y-%m-%d %H:%M")
        
        jql = f"project = {project_key} AND updated >= '{last_update_date}'"
        
        # Fetch issues
        issues = await self._fetch_issues_by_jql(jql)
        
        # Update last update timestamp
        if issues:
            self.last_update_timestamps[project_key] = datetime.now().timestamp()
        
        return issues
    
    async def _fetch_issues_by_jql(self, jql: str) -> List[Dict[str, Any]]:
        """
        Fetch issues using a JQL query.
        
        Args:
            jql: JQL query string
            
        Returns:
            List of issue data
        """
        issues = []
        
        try:
            # Prepare search parameters
            params = {
                "jql": jql,
                "maxResults": 100,  # API typically limits to 100 per request
                "startAt": 0
            }
            
            # Add fields parameter if specified
            if self.fields:
                params["fields"] = ",".join(self.fields)
            
            total_issues = None
            
            # Paginate through results
            while total_issues is None or params["startAt"] < total_issues:
                # Stop if we've reached max_results
                if len(issues) >= self.max_results:
                    break
                
                # Search for issues
                search_result = await self._api_get("search", params)
                
                # Get total issues if not already known
                if total_issues is None:
                    total_issues = search_result.get("total", 0)
                
                # Process issues
                batch_issues = search_result.get("issues", [])
                for issue in batch_issues:
                    processed_issue = await self._process_issue(issue)
                    issues.append(processed_issue)
                
                # Update start position for next page
                params["startAt"] += len(batch_issues)
                
                # If no issues returned, break out of loop
                if not batch_issues:
                    break
        except Exception as e:
            logger.error(f"Error fetching Jira issues with JQL '{jql}': {str(e)}")
        
        return issues
    
    async def _process_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Jira issue.
        
        Args:
            issue: Raw issue data from Jira API
            
        Returns:
            Processed issue data
        """
        issue_id = issue.get("id")
        issue_key = issue.get("key")
        fields = issue.get("fields", {})
        
        # Extract basic issue data
        processed_issue = {
            "source_type": "jira",
            "content_type": "issue",
            "id": issue_id,
            "key": issue_key,
            "self": issue.get("self"),
            "summary": fields.get("summary"),
            "description": fields.get("description"),
            "issue_type": self._extract_field_value(fields.get("issuetype")),
            "status": self._extract_field_value(fields.get("status")),
            "priority": self._extract_field_value(fields.get("priority")),
            "assignee": self._extract_user(fields.get("assignee")),
            "reporter": self._extract_user(fields.get("reporter")),
            "project": self._extract_field_value(fields.get("project")),
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "due_date": fields.get("duedate"),
            "resolution": self._extract_field_value(fields.get("resolution")),
            "resolution_date": fields.get("resolutiondate"),
            "labels": fields.get("labels", []),
            "components": [self._extract_field_value(component) for component in fields.get("components", [])],
            "fix_versions": [self._extract_field_value(version) for version in fields.get("fixVersions", [])],
            "affect_versions": [self._extract_field_value(version) for version in fields.get("affectVersions", [])]
        }
        
        # Extract custom fields
        for field_name, field_value in fields.items():
            if field_name.startswith("customfield_"):
                # Try to get a friendly name from schema if available
                processed_issue[field_name] = field_value
        
        # Get sprint information if available (usually in a custom field)
        sprint_field = None
        for field_name, field_value in fields.items():
            if field_name.startswith("customfield_") and field_value and isinstance(field_value, list):
                # Sprint fields are often stored as strings like "com.atlassian.greenhopper.service.sprint.Sprint@1a2b3c[id=123,...]"
                if any(isinstance(item, str) and "sprint" in item.lower() for item in field_value):
                    sprint_field = field_value
                    break
        
        if sprint_field:
            sprints = []
            for sprint_str in sprint_field:
                if not isinstance(sprint_str, str):
                    continue
                
                # Extract sprint ID, name, state, etc. from sprint string
                sprint_data = {}
                parts = re.findall(r'([^=,\[\]]+)=([^,\[\]]+)', sprint_str)
                for key, value in parts:
                    sprint_data[key.strip()] = value.strip()
                
                if sprint_data:
                    sprints.append(sprint_data)
            
            processed_issue["sprints"] = sprints
        
        # Fetch comments if needed
        if self.include_comments:
            try:
                comments = await self._api_get(f"issue/{issue_key}/comment")
                processed_issue["comments"] = comments.get("comments", [])
            except Exception as e:
                logger.error(f"Error fetching comments for issue {issue_key}: {str(e)}")
                processed_issue["comments"] = []
        
        # Fetch worklogs if needed
        if self.include_worklogs:
            try:
                worklogs = await self._api_get(f"issue/{issue_key}/worklog")
                processed_issue["worklogs"] = worklogs.get("worklogs", [])
            except Exception as e:
                logger.error(f"Error fetching worklogs for issue {issue_key}: {str(e)}")
                processed_issue["worklogs"] = []
        
        # Fetch changelog if needed
        if self.include_changelog:
            try:
                changelog = await self._api_get(f"issue/{issue_key}/changelog")
                processed_issue["changelog"] = changelog.get("values", [])
            except Exception as e:
                logger.error(f"Error fetching changelog for issue {issue_key}: {str(e)}")
                processed_issue["changelog"] = []
        
        return processed_issue
    
    def _extract_field_value(self, field: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract the value of a Jira field.
        
        Args:
            field: Jira field object
            
        Returns:
            Extracted field value
        """
        if not field:
            return None
        
        # Return a simplified version of the field
        return {
            "id": field.get("id"),
            "name": field.get("name"),
            "self": field.get("self")
        }
    
    def _extract_user(self, user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract user information.
        
        Args:
            user: Jira user object
            
        Returns:
            Extracted user information
        """
        if not user:
            return None
        
        return {
            "key": user.get("key"),
            "name": user.get("name"),
            "display_name": user.get("displayName"),
            "email_address": user.get("emailAddress"),
            "active": user.get("active"),
            "self": user.get("self")
        }
    
    async def _api_get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """
        Make a GET request to the Jira API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            Response data as JSON
        """
        if not self.session:
            raise RuntimeError("Jira connector session not initialized")
        
        url = f"{self.base_url}/rest/api/2/{endpoint}"
        
        headers = {
            "Accept": "application/json"
        }
        
        auth = None
        if self.username and self.api_token:
            import base64
            auth_str = f"{self.username}:{self.api_token}"
            encoded_auth = base64.b64encode(auth_str.encode()).decode()
            headers["Authorization"] = f"Basic {encoded_auth}"
        elif self.oauth_config:
            # In a real implementation, you'd handle OAuth authentication here
            pass
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Jira API error: {response.status} - {error_text}")
                    raise Exception(f"Jira API error: {response.status}")
        except Exception as e:
            logger.error(f"Error in Jira API request to {endpoint}: {str(e)}")
            raise
    
    async def close(self) -> None:
        """Close the Jira connector."""
        if self.session:
            await self.session.close()
            self.session = None
        
        await super().close()
        logger.info("Jira connector closed")