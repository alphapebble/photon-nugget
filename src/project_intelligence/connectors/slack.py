"""
Slack connector for the Project Intelligence System.

This module provides a connector for fetching and processing messages from
Slack channels and direct messages.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .base import DataSourceConnector

logger = logging.getLogger(__name__)


class SlackConnector(DataSourceConnector):
    """
    Connector for Slack.
    
    This connector fetches messages from Slack channels and direct messages
    using the Slack API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Slack connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - token: Slack API token (required)
                - channels: List of channel IDs or names to monitor (default: [])
                - dm_users: List of user IDs to monitor DMs with (default: [])
                - max_messages: Maximum number of messages to fetch per channel (default: 100)
                - oldest_timestamp: Oldest timestamp to fetch messages from (default: 24 hours ago)
                - include_replies: Whether to include thread replies (default: True)
        """
        super().__init__(config)
        self.token = self.config.get("token")
        if not self.token:
            raise ValueError("Slack API token is required")
        
        self.channels = self.config.get("channels", [])
        self.dm_users = self.config.get("dm_users", [])
        self.max_messages = self.config.get("max_messages", 100)
        self.oldest_timestamp = self.config.get("oldest_timestamp")
        self.include_replies = self.config.get("include_replies", True)
        
        self.client = None
        self.bot_user_id = None
        self.channel_ids = {}  # Map of channel names to IDs
        self.user_ids = {}     # Map of user names to IDs
    
    async def initialize(self) -> None:
        """Initialize the Slack connector."""
        await super().initialize()
        
        try:
            # Initialize Slack client
            self.client = WebClient(token=self.token)
            
            # Get bot user ID
            bot_info = await asyncio.to_thread(self.client.auth_test)
            self.bot_user_id = bot_info["user_id"]
            
            # Resolve channel names to IDs
            await self._resolve_channel_names()
            
            # Resolve user names to IDs
            await self._resolve_user_names()
            
            logger.info("Slack connector initialized successfully")
        except SlackApiError as e:
            logger.error(f"Failed to initialize Slack connector: {str(e)}")
            raise
    
    async def _resolve_channel_names(self) -> None:
        """Resolve channel names to IDs."""
        channels_to_resolve = []
        for channel in self.channels:
            if not channel.startswith("C"):  # Not a channel ID
                channels_to_resolve.append(channel)
        
        if not channels_to_resolve:
            return
        
        try:
            # Get all channels
            response = await asyncio.to_thread(
                self.client.conversations_list,
                types="public_channel,private_channel"
            )
            
            # Map channel names to IDs
            for channel in response["channels"]:
                if channel["name"] in channels_to_resolve:
                    self.channel_ids[channel["name"]] = channel["id"]
            
            # Update channels list with resolved IDs
            resolved_channels = []
            for channel in self.channels:
                if channel.startswith("C"):  # Already an ID
                    resolved_channels.append(channel)
                elif channel in self.channel_ids:
                    resolved_channels.append(self.channel_ids[channel])
                else:
                    logger.warning(f"Could not resolve Slack channel name: {channel}")
            
            self.channels = resolved_channels
        except SlackApiError as e:
            logger.error(f"Failed to resolve Slack channel names: {str(e)}")
    
    async def _resolve_user_names(self) -> None:
        """Resolve user names to IDs."""
        users_to_resolve = []
        for user in self.dm_users:
            if not user.startswith("U"):  # Not a user ID
                users_to_resolve.append(user)
        
        if not users_to_resolve:
            return
        
        try:
            # Get all users
            response = await asyncio.to_thread(self.client.users_list)
            
            # Map user names to IDs
            for user in response["members"]:
                if user["name"] in users_to_resolve or user.get("real_name") in users_to_resolve:
                    self.user_ids[user["name"]] = user["id"]
                    if user.get("real_name"):
                        self.user_ids[user["real_name"]] = user["id"]
            
            # Update users list with resolved IDs
            resolved_users = []
            for user in self.dm_users:
                if user.startswith("U"):  # Already an ID
                    resolved_users.append(user)
                elif user in self.user_ids:
                    resolved_users.append(self.user_ids[user])
                else:
                    logger.warning(f"Could not resolve Slack user name: {user}")
            
            self.dm_users = resolved_users
        except SlackApiError as e:
            logger.error(f"Failed to resolve Slack user names: {str(e)}")
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch messages from Slack.
        
        Returns:
            List of message data items
        """
        await self._check_initialization()
        
        messages = []
        
        # Fetch messages from channels
        for channel_id in self.channels:
            channel_messages = await self._fetch_channel_messages(channel_id)
            messages.extend(channel_messages)
        
        # Fetch direct messages
        for user_id in self.dm_users:
            dm_messages = await self._fetch_dm_messages(user_id)
            messages.extend(dm_messages)
        
        return messages
    
    async def _fetch_channel_messages(self, channel_id: str) -> List[Dict[str, Any]]:
        """
        Fetch messages from a Slack channel.
        
        Args:
            channel_id: The ID of the channel
            
        Returns:
            List of message data items
        """
        messages = []
        
        try:
            # Determine the oldest timestamp to fetch messages from
            oldest = self.oldest_timestamp
            if not oldest:
                # Default to 24 hours ago
                oldest = str(datetime.now().timestamp() - 86400)
            
            # Fetch messages
            response = await asyncio.to_thread(
                self.client.conversations_history,
                channel=channel_id,
                limit=self.max_messages,
                oldest=oldest
            )
            
            # Process messages
            for msg in response["messages"]:
                message_data = await self._process_message(msg, channel_id)
                messages.append(message_data)
                
                # Fetch thread replies if needed
                if self.include_replies and "thread_ts" in msg and msg["thread_ts"] == msg["ts"]:
                    replies = await self._fetch_thread_replies(channel_id, msg["ts"])
                    messages.extend(replies)
        except SlackApiError as e:
            logger.error(f"Failed to fetch messages from Slack channel {channel_id}: {str(e)}")
        
        return messages
    
    async def _fetch_dm_messages(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetch direct messages with a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of message data items
        """
        messages = []
        
        try:
            # Open DM channel
            response = await asyncio.to_thread(
                self.client.conversations_open,
                users=user_id
            )
            
            channel_id = response["channel"]["id"]
            
            # Fetch messages
            oldest = self.oldest_timestamp
            if not oldest:
                # Default to 24 hours ago
                oldest = str(datetime.now().timestamp() - 86400)
            
            response = await asyncio.to_thread(
                self.client.conversations_history,
                channel=channel_id,
                limit=self.max_messages,
                oldest=oldest
            )
            
            # Process messages
            for msg in response["messages"]:
                message_data = await self._process_message(msg, channel_id, is_dm=True)
                messages.append(message_data)
                
                # Fetch thread replies if needed
                if self.include_replies and "thread_ts" in msg and msg["thread_ts"] == msg["ts"]:
                    replies = await self._fetch_thread_replies(channel_id, msg["ts"])
                    messages.extend(replies)
        except SlackApiError as e:
            logger.error(f"Failed to fetch direct messages with user {user_id}: {str(e)}")
        
        return messages
    
    async def _fetch_thread_replies(self, channel_id: str, thread_ts: str) -> List[Dict[str, Any]]:
        """
        Fetch replies in a thread.
        
        Args:
            channel_id: The ID of the channel
            thread_ts: The timestamp of the parent message
            
        Returns:
            List of message data items
        """
        replies = []
        
        try:
            response = await asyncio.to_thread(
                self.client.conversations_replies,
                channel=channel_id,
                ts=thread_ts
            )
            
            # Skip the parent message
            for msg in response["messages"][1:]:
                message_data = await self._process_message(msg, channel_id, is_reply=True)
                replies.append(message_data)
        except SlackApiError as e:
            logger.error(f"Failed to fetch thread replies in channel {channel_id}: {str(e)}")
        
        return replies
    
    async def _process_message(self, msg: Dict[str, Any], channel_id: str, is_dm: bool = False, is_reply: bool = False) -> Dict[str, Any]:
        """
        Process a Slack message.
        
        Args:
            msg: The message data from the Slack API
            channel_id: The ID of the channel
            is_dm: Whether the message is a direct message
            is_reply: Whether the message is a thread reply
            
        Returns:
            Processed message data
        """
        # Get user info
        user_id = msg.get("user")
        user_info = {"name": "Unknown", "real_name": "Unknown", "email": None}
        
        if user_id:
            try:
                user_response = await asyncio.to_thread(
                    self.client.users_info,
                    user=user_id
                )
                user = user_response["user"]
                user_info = {
                    "name": user.get("name", "Unknown"),
                    "real_name": user.get("real_name", "Unknown"),
                    "email": user.get("profile", {}).get("email")
                }
            except SlackApiError as e:
                logger.warning(f"Failed to get user info for {user_id}: {str(e)}")
        
        # Get channel info
        channel_info = {"name": "Unknown"}
        if not is_dm:
            try:
                channel_response = await asyncio.to_thread(
                    self.client.conversations_info,
                    channel=channel_id
                )
                channel_info = {
                    "name": channel_response["channel"]["name"]
                }
            except SlackApiError as e:
                logger.warning(f"Failed to get channel info for {channel_id}: {str(e)}")
        
        # Convert timestamp to datetime
        timestamp = float(msg["ts"])
        date = datetime.fromtimestamp(timestamp)
        
        # Process message text
        text = msg.get("text", "")
        
        # Handle message blocks (rich text)
        if "blocks" in msg:
            for block in msg["blocks"]:
                if block["type"] == "rich_text":
                    for element in block.get("elements", []):
                        if element["type"] == "rich_text_section":
                            for item in element.get("elements", []):
                                if item["type"] == "text":
                                    text += item.get("text", "")
                                elif item["type"] == "link":
                                    text += item.get("url", "")
        
        # Process message data
        message_data = {
            "source_type": "slack",
            "channel_id": channel_id,
            "channel_name": channel_info["name"] if not is_dm else "DM",
            "is_dm": is_dm,
            "is_reply": is_reply,
            "user_id": user_id,
            "user_name": user_info["name"],
            "user_real_name": user_info["real_name"],
            "user_email": user_info["email"],
            "text": text,
            "timestamp": timestamp,
            "date": date,
            "thread_ts": msg.get("thread_ts"),
            "reactions": msg.get("reactions", []),
            "attachments": msg.get("attachments", []),
            "files": msg.get("files", [])
        }
        
        return message_data
    
    async def close(self) -> None:
        """Close the Slack connector."""
        self.client = None
        await super().close()
        logger.info("Slack connector closed")