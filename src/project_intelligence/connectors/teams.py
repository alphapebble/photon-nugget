"""
Teams connector for the Project Intelligence System.

This module provides a connector for fetching and processing messages from
Microsoft Teams channels and chats.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .base import DataSourceConnector

logger = logging.getLogger(__name__)


class TeamsConnector(DataSourceConnector):
    """
    Connector for Microsoft Teams.
    
    This connector fetches messages from Teams channels and chats
    using the Microsoft Graph API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Teams connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - client_id: Microsoft app client ID (required)
                - client_secret: Microsoft app client secret (required)
                - tenant_id: Microsoft tenant ID (required)
                - teams: List of team IDs to monitor (default: [])
                - channels: List of channel IDs to monitor (default: [])
                - chats: List of chat IDs to monitor (default: [])
                - max_messages: Maximum number of messages to fetch per channel (default: 100)
                - oldest_timestamp: Oldest timestamp to fetch messages from (default: 24 hours ago)
        """
        super().__init__(config)
        self.client_id = self.config.get("client_id")
        self.client_secret = self.config.get("client_secret")
        self.tenant_id = self.config.get("tenant_id")
        
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("Microsoft Graph API credentials (client_id, client_secret, tenant_id) are required")
        
        self.teams = self.config.get("teams", [])
        self.channels = self.config.get("channels", [])
        self.chats = self.config.get("chats", [])
        self.max_messages = self.config.get("max_messages", 100)
        self.oldest_timestamp = self.config.get("oldest_timestamp")
        
        self.access_token = None
        self.token_expiry = None
    
    async def initialize(self) -> None:
        """Initialize the Teams connector."""
        await super().initialize()
        
        try:
            # Import required libraries
            try:
                import msal
                import requests
            except ImportError:
                logger.error("Required libraries for Teams connector not installed. "
                             "Please install with: pip install msal requests")
                raise
            
            # Get initial access token
            await self._get_access_token()
            
            logger.info("Teams connector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Teams connector: {str(e)}")
            raise
    
    async def _get_access_token(self) -> None:
        """Get an access token for the Microsoft Graph API."""
        try:
            # Import here to avoid dependency if not using Teams
            import msal
            
            # Create an MSAL app
            app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}"
            )
            
            # Get token
            scopes = ["https://graph.microsoft.com/.default"]
            result = await asyncio.to_thread(
                app.acquire_token_for_client,
                scopes=scopes
            )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                # Token expires in result["expires_in"] seconds
                self.token_expiry = datetime.now().timestamp() + result["expires_in"] - 300  # 5 min buffer
                logger.info("Got new access token for Microsoft Graph API")
            else:
                logger.error(f"Failed to get access token: {result.get('error')}")
                logger.error(f"Error description: {result.get('error_description')}")
                raise Exception(f"Failed to get access token: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            raise
    
    async def _ensure_token_valid(self) -> None:
        """Ensure that the access token is valid, refreshing if necessary."""
        if not self.access_token or datetime.now().timestamp() > self.token_expiry:
            await self._get_access_token()
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch messages from Microsoft Teams.
        
        Returns:
            List of message data items
        """
        await self._check_initialization()
        await self._ensure_token_valid()
        
        messages = []
        
        # Fetch team channel messages
        for team_id in self.teams:
            team_channels = await self._fetch_team_channels(team_id)
            for channel in team_channels:
                channel_messages = await self._fetch_channel_messages(team_id, channel["id"])
                messages.extend(channel_messages)
        
        # Fetch specific channel messages
        for channel_id in self.channels:
            # Format: team_id|channel_id
            if "|" in channel_id:
                team_id, channel_id = channel_id.split("|")
                channel_messages = await self._fetch_channel_messages(team_id, channel_id)
                messages.extend(channel_messages)
        
        # Fetch chat messages
        for chat_id in self.chats:
            chat_messages = await self._fetch_chat_messages(chat_id)
            messages.extend(chat_messages)
        
        return messages
    
    async def _fetch_team_channels(self, team_id: str) -> List[Dict[str, Any]]:
        """
        Fetch channels in a team.
        
        Args:
            team_id: The ID of the team
            
        Returns:
            List of channel data
        """
        # This is a stub - in a real implementation, this would call the Microsoft Graph API
        logger.info(f"Fetching channels for team {team_id} (STUB)")
        return []
    
    async def _fetch_channel_messages(self, team_id: str, channel_id: str) -> List[Dict[str, Any]]:
        """
        Fetch messages from a channel.
        
        Args:
            team_id: The ID of the team
            channel_id: The ID of the channel
            
        Returns:
            List of message data
        """
        # This is a stub - in a real implementation, this would call the Microsoft Graph API
        logger.info(f"Fetching messages for channel {channel_id} in team {team_id} (STUB)")
        return []
    
    async def _fetch_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        Fetch messages from a chat.
        
        Args:
            chat_id: The ID of the chat
            
        Returns:
            List of message data
        """
        # This is a stub - in a real implementation, this would call the Microsoft Graph API
        logger.info(f"Fetching messages for chat {chat_id} (STUB)")
        return []
    
    async def close(self) -> None:
        """Close the Teams connector."""
        self.access_token = None
        self.token_expiry = None
        await super().close()
        logger.info("Teams connector closed")