"""
Notion connector for the Project Intelligence System.

This module provides a connector for fetching and processing data from
Notion databases, pages, and blocks.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..base import DataSourceConnector

logger = logging.getLogger(__name__)


class NotionConnector(DataSourceConnector):
    """
    Connector for Notion.
    
    This connector fetches data from Notion databases, pages, and blocks
    using the Notion API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Notion connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - api_key: Notion API key (required)
                - database_ids: List of database IDs to monitor (default: [])
                - page_ids: List of page IDs to monitor (default: [])
                - filter_by_tags: List of tags to filter content by (default: [])
                - max_pages: Maximum number of pages to fetch per database (default: 100)
                - include_archived: Whether to include archived items (default: False)
                - poll_interval: How often to check for changes in seconds (default: 300)
        """
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("Notion API key is required")
        
        self.database_ids = self.config.get("database_ids", [])
        self.page_ids = self.config.get("page_ids", [])
        self.filter_by_tags = self.config.get("filter_by_tags", [])
        self.max_pages = self.config.get("max_pages", 100)
        self.include_archived = self.config.get("include_archived", False)
        
        self.client = None
        self.last_update_timestamps = {}
    
    async def initialize(self) -> None:
        """Initialize the Notion connector."""
        await super().initialize()
        
        try:
            # Initialize Notion client
            try:
                from notion_client import AsyncClient
            except ImportError:
                logger.error("Notion client not installed. Please install with: pip install notion-client")
                raise
            
            self.client = AsyncClient(auth=self.api_key)
            
            # Initialize last update timestamps
            for db_id in self.database_ids:
                self.last_update_timestamps[f"db_{db_id}"] = datetime.now().timestamp() - 86400  # 24 hours ago
            
            for page_id in self.page_ids:
                self.last_update_timestamps[f"page_{page_id}"] = datetime.now().timestamp() - 86400  # 24 hours ago
            
            logger.info("Notion connector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Notion connector: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from Notion.
        
        Returns:
            List of data items from Notion
        """
        await self._check_initialization()
        
        all_items = []
        
        # Fetch databases
        for db_id in self.database_ids:
            try:
                db_items = await self._fetch_database_items(db_id)
                all_items.extend(db_items)
            except Exception as e:
                logger.error(f"Error fetching Notion database {db_id}: {str(e)}")
        
        # Fetch pages
        for page_id in self.page_ids:
            try:
                page_item = await self._fetch_page(page_id)
                if page_item:
                    all_items.append(page_item)
            except Exception as e:
                logger.error(f"Error fetching Notion page {page_id}: {str(e)}")
        
        return all_items
    
    async def _fetch_database_items(self, database_id: str) -> List[Dict[str, Any]]:
        """
        Fetch items from a Notion database.
        
        Args:
            database_id: ID of the database
            
        Returns:
            List of items from the database
        """
        items = []
        
        try:
            # Create filter for last update time
            last_update = self.last_update_timestamps.get(f"db_{database_id}")
            filter_params = {
                "filter": {
                    "timestamp": "last_edited_time",
                    "last_edited_time": {
                        "after": datetime.fromtimestamp(last_update).isoformat()
                    }
                }
            }
            
            if not self.include_archived:
                filter_params["filter"]["archived"] = False
            
            # Apply tag filters if specified
            if self.filter_by_tags:
                # This is a simplified approach - would need to be adapted to your actual tag structure
                tag_filter = {
                    "property": "Tags",
                    "multi_select": {
                        "contains": self.filter_by_tags[0]  # Just using the first tag for simplicity
                    }
                }
                if "filter" in filter_params:
                    # Convert to compound filter
                    filter_params["filter"] = {
                        "and": [
                            filter_params["filter"],
                            tag_filter
                        ]
                    }
                else:
                    filter_params["filter"] = tag_filter
            
            # Query database
            response = await self.client.databases.query(
                database_id=database_id,
                **filter_params,
                page_size=min(self.max_pages, 100)  # API limit is 100
            )
            
            # Process results
            for page in response.get("results", []):
                try:
                    # Extract properties from page
                    properties = page.get("properties", {})
                    
                    # Build structured item
                    item = {
                        "source_type": "notion",
                        "content_type": "database_item",
                        "database_id": database_id,
                        "page_id": page.get("id"),
                        "created_time": page.get("created_time"),
                        "last_edited_time": page.get("last_edited_time"),
                        "url": page.get("url"),
                        "properties": await self._extract_properties(properties),
                        "raw_page": page
                    }
                    
                    # Fetch page content if needed
                    if self.config.get("fetch_page_content", True):
                        page_content = await self._fetch_page_content(page.get("id"))
                        item["content"] = page_content
                    
                    items.append(item)
                except Exception as e:
                    logger.error(f"Error processing Notion database item: {str(e)}")
            
            # Update last update timestamp
            if response.get("results"):
                self.last_update_timestamps[f"db_{database_id}"] = datetime.now().timestamp()
            
            # Handle pagination (simplified - in a real implementation, you'd handle this more robustly)
            if response.get("has_more") and len(response.get("results", [])) < self.max_pages:
                next_cursor = response.get("next_cursor")
                if next_cursor:
                    # In a real implementation, you'd use this cursor to fetch more pages
                    pass
        except Exception as e:
            logger.error(f"Error querying Notion database {database_id}: {str(e)}")
        
        return items
    
    async def _fetch_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a Notion page.
        
        Args:
            page_id: ID of the page
            
        Returns:
            Page data or None if error
        """
        try:
            # Retrieve page
            page = await self.client.pages.retrieve(page_id=page_id)
            
            # Check if page was updated since last check
            last_update = self.last_update_timestamps.get(f"page_{page_id}")
            page_update = datetime.fromisoformat(page.get("last_edited_time").replace("Z", "+00:00")).timestamp()
            
            if page_update <= last_update:
                return None
            
            # Extract properties
            properties = await self._extract_properties(page.get("properties", {}))
            
            # Fetch page content
            content = await self._fetch_page_content(page_id)
            
            # Build structured item
            item = {
                "source_type": "notion",
                "content_type": "page",
                "page_id": page_id,
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time"),
                "url": page.get("url"),
                "properties": properties,
                "content": content,
                "raw_page": page
            }
            
            # Update last update timestamp
            self.last_update_timestamps[f"page_{page_id}"] = datetime.now().timestamp()
            
            return item
        except Exception as e:
            logger.error(f"Error fetching Notion page {page_id}: {str(e)}")
            return None
    
    async def _fetch_page_content(self, page_id: str) -> str:
        """
        Fetch the content of a Notion page.
        
        Args:
            page_id: ID of the page
            
        Returns:
            Page content as text
        """
        try:
            blocks = await self.client.blocks.children.list(block_id=page_id)
            
            content = []
            for block in blocks.get("results", []):
                block_text = await self._extract_block_text(block)
                if block_text:
                    content.append(block_text)
            
            return "\n\n".join(content)
        except Exception as e:
            logger.error(f"Error fetching Notion page content for {page_id}: {str(e)}")
            return ""
    
    async def _extract_block_text(self, block: Dict[str, Any]) -> str:
        """
        Extract text from a Notion block.
        
        Args:
            block: Notion block data
            
        Returns:
            Block text
        """
        block_type = block.get("type")
        if not block_type:
            return ""
        
        # Get the value for this block type
        block_value = block.get(block_type)
        if not block_value:
            return ""
        
        # Extract text based on block type
        if block_type == "paragraph":
            return self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "heading_1":
            return "# " + self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "heading_2":
            return "## " + self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "heading_3":
            return "### " + self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "bulleted_list_item":
            return "• " + self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "numbered_list_item":
            return "1. " + self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "to_do":
            checked = "✓ " if block_value.get("checked", False) else "☐ "
            return checked + self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "toggle":
            return "▶ " + self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "code":
            return f"```{block_value.get('language', '')}\n{self._extract_rich_text(block_value.get('rich_text', []))}\n```"
        elif block_type == "quote":
            return "> " + self._extract_rich_text(block_value.get("rich_text", []))
        elif block_type == "callout":
            emoji = block_value.get("icon", {}).get("emoji", "")
            return f"{emoji} {self._extract_rich_text(block_value.get('rich_text', []))}"
        else:
            # For other block types, just try to get any text
            if "rich_text" in block_value:
                return self._extract_rich_text(block_value.get("rich_text", []))
            return f"[{block_type} block]"
    
    def _extract_rich_text(self, rich_text: List[Dict[str, Any]]) -> str:
        """
        Extract text from rich text objects.
        
        Args:
            rich_text: List of rich text objects
            
        Returns:
            Extracted text
        """
        texts = []
        for text_obj in rich_text:
            if "text" in text_obj and "content" in text_obj["text"]:
                texts.append(text_obj["text"]["content"])
        return "".join(texts)
    
    async def _extract_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract properties from Notion properties.
        
        Args:
            properties: Notion properties object
            
        Returns:
            Extracted properties
        """
        extracted = {}
        
        for key, prop in properties.items():
            prop_type = prop.get("type")
            if not prop_type:
                continue
            
            # Extract value based on property type
            if prop_type == "title":
                extracted[key] = self._extract_rich_text(prop.get("title", []))
            elif prop_type == "rich_text":
                extracted[key] = self._extract_rich_text(prop.get("rich_text", []))
            elif prop_type == "number":
                extracted[key] = prop.get("number")
            elif prop_type == "select":
                select_obj = prop.get("select")
                if select_obj:
                    extracted[key] = select_obj.get("name")
            elif prop_type == "multi_select":
                multi_select = prop.get("multi_select", [])
                extracted[key] = [item.get("name") for item in multi_select if "name" in item]
            elif prop_type == "date":
                date_obj = prop.get("date")
                if date_obj:
                    start = date_obj.get("start")
                    end = date_obj.get("end")
                    if start and end:
                        extracted[key] = {"start": start, "end": end}
                    elif start:
                        extracted[key] = start
            elif prop_type == "people":
                people = prop.get("people", [])
                extracted[key] = [person.get("name") or person.get("id") for person in people]
            elif prop_type == "checkbox":
                extracted[key] = prop.get("checkbox")
            elif prop_type == "url":
                extracted[key] = prop.get("url")
            elif prop_type == "email":
                extracted[key] = prop.get("email")
            elif prop_type == "phone_number":
                extracted[key] = prop.get("phone_number")
            elif prop_type == "formula":
                formula = prop.get("formula", {})
                formula_type = formula.get("type")
                if formula_type:
                    extracted[key] = formula.get(formula_type)
            elif prop_type == "relation":
                relations = prop.get("relation", [])
                extracted[key] = [rel.get("id") for rel in relations]
            elif prop_type == "rollup":
                rollup = prop.get("rollup", {})
                rollup_type = rollup.get("type")
                if rollup_type:
                    extracted[key] = rollup.get(rollup_type)
            elif prop_type == "created_time":
                extracted[key] = prop.get("created_time")
            elif prop_type == "created_by":
                created_by = prop.get("created_by", {})
                extracted[key] = created_by.get("name") or created_by.get("id")
            elif prop_type == "last_edited_time":
                extracted[key] = prop.get("last_edited_time")
            elif prop_type == "last_edited_by":
                last_edited_by = prop.get("last_edited_by", {})
                extracted[key] = last_edited_by.get("name") or last_edited_by.get("id")
            else:
                # For other property types, store the raw value
                extracted[key] = f"[{prop_type} property]"
        
        return extracted
    
    async def close(self) -> None:
        """Close the Notion connector."""
        self.client = None
        await super().close()
        logger.info("Notion connector closed")