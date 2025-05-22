"""
Trello connector for the Project Intelligence System.

This module provides a connector for fetching and processing data from
Trello boards, lists, and cards.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..base import DataSourceConnector

logger = logging.getLogger(__name__)


class TrelloConnector(DataSourceConnector):
    """
    Connector for Trello.
    
    This connector fetches data from Trello boards, lists, and cards
    using the Trello API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Trello connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - api_key: Trello API key (required)
                - token: Trello API token (required)
                - board_ids: List of board IDs to monitor (default: [])
                - filter_by_labels: List of labels to filter cards by (default: [])
                - include_archived: Whether to include archived cards (default: False)
                - include_checklists: Whether to include checklist items (default: True)
                - include_comments: Whether to include card comments (default: True)
                - max_cards_per_board: Maximum number of cards to fetch per board (default: 1000)
                - poll_interval: How often to check for changes in seconds (default: 300)
        """
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        self.token = self.config.get("token")
        
        if not self.api_key or not self.token:
            raise ValueError("Trello API key and token are required")
        
        self.board_ids = self.config.get("board_ids", [])
        self.filter_by_labels = self.config.get("filter_by_labels", [])
        self.include_archived = self.config.get("include_archived", False)
        self.include_checklists = self.config.get("include_checklists", True)
        self.include_comments = self.config.get("include_comments", True)
        self.max_cards_per_board = self.config.get("max_cards_per_board", 1000)
        
        self.last_update_timestamps = {}
        self.session = None
    
    async def initialize(self) -> None:
        """Initialize the Trello connector."""
        await super().initialize()
        
        try:
            import aiohttp
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            
            # Initialize last update timestamps
            for board_id in self.board_ids:
                self.last_update_timestamps[board_id] = datetime.now().timestamp() - 86400  # 24 hours ago
            
            logger.info("Trello connector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Trello connector: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from Trello.
        
        Returns:
            List of data items from Trello
        """
        await self._check_initialization()
        
        all_items = []
        
        # Fetch data from each board
        for board_id in self.board_ids:
            try:
                board_items = await self._fetch_board(board_id)
                all_items.extend(board_items)
            except Exception as e:
                logger.error(f"Error fetching Trello board {board_id}: {str(e)}")
        
        return all_items
    
    async def _fetch_board(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Fetch data from a Trello board.
        
        Args:
            board_id: ID of the board to fetch
            
        Returns:
            List of data items from the board
        """
        items = []
        
        try:
            # Fetch board details
            board = await self._api_get(f"boards/{board_id}", {
                "fields": "name,desc,url,dateLastActivity"
            })
            
            # Check if board was updated since last check
            last_update = self.last_update_timestamps.get(board_id)
            board_update = datetime.fromisoformat(board.get("dateLastActivity").replace("Z", "+00:00")).timestamp()
            
            if board_update <= last_update:
                return []
            
            # Fetch lists on the board
            lists = await self._api_get(f"boards/{board_id}/lists", {
                "cards": "none",
                "filter": "open" if not self.include_archived else "all"
            })
            
            # Create a mapping of list IDs to names
            list_names = {lst["id"]: lst["name"] for lst in lists}
            
            # Fetch cards on the board
            filter_param = "all" if self.include_archived else "open"
            cards = await self._api_get(f"boards/{board_id}/cards/{filter_param}", {
                "limit": self.max_cards_per_board,
                "members": "true",
                "member_fields": "id,fullName,username",
                "checklists": "all" if self.include_checklists else "none",
                "attachments": "true",
                "attachment_fields": "name,url,date",
                "fields": "id,name,desc,idList,labels,due,dueComplete,dateLastActivity,closed,url,shortUrl"
            })
            
            # Filter cards by labels if needed
            if self.filter_by_labels:
                filtered_cards = []
                for card in cards:
                    card_labels = [label["name"] for label in card.get("labels", [])]
                    if any(label in card_labels for label in self.filter_by_labels):
                        filtered_cards.append(card)
                cards = filtered_cards
            
            # Process each card
            for card in cards:
                try:
                    # Get list name
                    list_id = card.get("idList")
                    list_name = list_names.get(list_id, "Unknown List")
                    
                    # Extract card data
                    card_data = {
                        "source_type": "trello",
                        "content_type": "card",
                        "board_id": board_id,
                        "board_name": board.get("name"),
                        "list_id": list_id,
                        "list_name": list_name,
                        "card_id": card.get("id"),
                        "name": card.get("name"),
                        "description": card.get("desc"),
                        "url": card.get("url"),
                        "short_url": card.get("shortUrl"),
                        "due_date": card.get("due"),
                        "is_complete": card.get("dueComplete", False),
                        "is_archived": card.get("closed", False),
                        "last_activity": card.get("dateLastActivity"),
                        "labels": [{"name": label.get("name"), "color": label.get("color")} for label in card.get("labels", [])],
                        "members": [{"id": member.get("id"), "name": member.get("fullName"), "username": member.get("username")} 
                                    for member in card.get("members", [])],
                        "attachments": [{"name": att.get("name"), "url": att.get("url"), "date": att.get("date")}
                                       for att in card.get("attachments", [])]
                    }
                    
                    # Add checklists if included
                    if self.include_checklists:
                        checklists = []
                        for checklist in card.get("checklists", []):
                            checklist_items = []
                            for item in checklist.get("checkItems", []):
                                checklist_items.append({
                                    "name": item.get("name"),
                                    "state": item.get("state"),
                                    "due": item.get("due")
                                })
                            
                            checklists.append({
                                "id": checklist.get("id"),
                                "name": checklist.get("name"),
                                "items": checklist_items
                            })
                        
                        card_data["checklists"] = checklists
                    
                    # Add comments if included
                    if self.include_comments:
                        try:
                            comments = await self._api_get(f"cards/{card.get('id')}/actions", {
                                "filter": "commentCard",
                                "limit": 50
                            })
                            
                            card_data["comments"] = [{
                                "id": comment.get("id"),
                                "text": comment.get("data", {}).get("text"),
                                "date": comment.get("date"),
                                "creator": {
                                    "id": comment.get("idMemberCreator"),
                                    "username": comment.get("memberCreator", {}).get("username"),
                                    "name": comment.get("memberCreator", {}).get("fullName")
                                }
                            } for comment in comments]
                        except Exception as e:
                            logger.error(f"Error fetching comments for card {card.get('id')}: {str(e)}")
                            card_data["comments"] = []
                    
                    items.append(card_data)
                except Exception as e:
                    logger.error(f"Error processing Trello card: {str(e)}")
            
            # Update last update timestamp
            self.last_update_timestamps[board_id] = datetime.now().timestamp()
            
        except Exception as e:
            logger.error(f"Error fetching Trello board {board_id}: {str(e)}")
        
        return items
    
    async def _api_get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """
        Make a GET request to the Trello API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            Response data as JSON
        """
        if not self.session:
            raise RuntimeError("Trello connector session not initialized")
        
        url = f"https://api.trello.com/1/{endpoint}"
        
        # Add authentication parameters
        request_params = {
            "key": self.api_key,
            "token": self.token
        }
        
        # Add additional parameters
        if params:
            request_params.update(params)
        
        try:
            async with self.session.get(url, params=request_params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Trello API error: {response.status} - {error_text}")
                    raise Exception(f"Trello API error: {response.status}")
        except Exception as e:
            logger.error(f"Error in Trello API request to {endpoint}: {str(e)}")
            raise
    
    async def close(self) -> None:
        """Close the Trello connector."""
        if self.session:
            await self.session.close()
            self.session = None
        
        await super().close()
        logger.info("Trello connector closed")