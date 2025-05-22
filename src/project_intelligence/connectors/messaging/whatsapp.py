"""
WhatsApp connector for the Project Intelligence System.

This module provides a connector for fetching and processing messages from
WhatsApp via the WhatsApp Business API.
"""

import asyncio
import logging
import json
import hmac
import hashlib
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..base import DataSourceConnector

logger = logging.getLogger(__name__)


class WhatsAppConnector(DataSourceConnector):
    """
    Connector for WhatsApp.
    
    This connector fetches messages from WhatsApp using the WhatsApp Business API,
    which is especially useful for field updates in emerging markets.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the WhatsApp connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - phone_number_id: WhatsApp Business API phone number ID (required)
                - access_token: WhatsApp Business API access token (required)
                - webhook_secret: Secret for verifying webhook requests (required for webhook mode)
                - business_account_id: WhatsApp Business account ID (required)
                - mode: "polling" or "webhook" (default: "polling")
                - group_ids: List of WhatsApp group IDs to monitor (default: [])
                - contact_ids: List of contact IDs to monitor (default: [])
                - include_media: Whether to download and process media (default: True)
                - max_messages: Maximum number of messages to fetch per cycle (default: 100)
                - webhook_port: Port to listen for webhooks (default: 8080)
                - webhook_path: Path to listen for webhooks (default: "/webhook")
                - poll_interval: How often to check for new messages in seconds (default: 60)
        """
        super().__init__(config)
        self.phone_number_id = self.config.get("phone_number_id")
        self.access_token = self.config.get("access_token")
        self.webhook_secret = self.config.get("webhook_secret")
        self.business_account_id = self.config.get("business_account_id")
        
        if not self.phone_number_id or not self.access_token or not self.business_account_id:
            raise ValueError("WhatsApp Business API credentials are required")
        
        self.mode = self.config.get("mode", "polling")
        self.group_ids = self.config.get("group_ids", [])
        self.contact_ids = self.config.get("contact_ids", [])
        self.include_media = self.config.get("include_media", True)
        self.max_messages = self.config.get("max_messages", 100)
        self.webhook_port = self.config.get("webhook_port", 8080)
        self.webhook_path = self.config.get("webhook_path", "/webhook")
        
        self.session = None
        self.webhook_server = None
        self.webhook_queue = asyncio.Queue()
        self.last_message_timestamps = {}
    
    async def initialize(self) -> None:
        """Initialize the WhatsApp connector."""
        await super().initialize()
        
        try:
            import aiohttp
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            
            # Initialize last message timestamps
            for group_id in self.group_ids:
                self.last_message_timestamps[f"group_{group_id}"] = datetime.now().timestamp() - 86400  # 24 hours ago
            
            for contact_id in self.contact_ids:
                self.last_message_timestamps[f"contact_{contact_id}"] = datetime.now().timestamp() - 86400  # 24 hours ago
            
            # Set up webhook server if in webhook mode
            if self.mode == "webhook":
                if not self.webhook_secret:
                    logger.warning("Webhook secret not provided. Webhook verification will be disabled.")
                
                await self._setup_webhook_server()
            
            logger.info(f"WhatsApp connector initialized successfully in {self.mode} mode")
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp connector: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from WhatsApp.
        
        Returns:
            List of message data from WhatsApp
        """
        await self._check_initialization()
        
        all_messages = []
        
        if self.mode == "polling":
            # Fetch messages via API polling
            try:
                # Fetch messages from groups
                for group_id in self.group_ids:
                    group_messages = await self._fetch_group_messages(group_id)
                    all_messages.extend(group_messages)
                
                # Fetch messages from contacts
                for contact_id in self.contact_ids:
                    contact_messages = await self._fetch_contact_messages(contact_id)
                    all_messages.extend(contact_messages)
            except Exception as e:
                logger.error(f"Error fetching messages in polling mode: {str(e)}")
        else:
            # Get messages from webhook queue
            try:
                # Get all available messages from the queue (non-blocking)
                while not self.webhook_queue.empty():
                    try:
                        message = self.webhook_queue.get_nowait()
                        processed_message = await self._process_webhook_message(message)
                        if processed_message:
                            all_messages.append(processed_message)
                            
                            # If we've reached the max messages, stop
                            if len(all_messages) >= self.max_messages:
                                break
                    except asyncio.QueueEmpty:
                        break
            except Exception as e:
                logger.error(f"Error processing webhook messages: {str(e)}")
        
        return all_messages
    
    async def _fetch_group_messages(self, group_id: str) -> List[Dict[str, Any]]:
        """
        Fetch messages from a WhatsApp group.
        
        Args:
            group_id: ID of the group
            
        Returns:
            List of message data
        """
        # Note: WhatsApp Business API doesn't directly support group message history
        # This is a placeholder for when/if that functionality becomes available
        logger.warning("WhatsApp Business API does not currently support fetching group message history")
        return []
    
    async def _fetch_contact_messages(self, contact_id: str) -> List[Dict[str, Any]]:
        """
        Fetch messages from a WhatsApp contact.
        
        Args:
            contact_id: ID of the contact
            
        Returns:
            List of message data
        """
        messages = []
        
        try:
            # Get last message timestamp
            last_update = self.last_message_timestamps.get(f"contact_{contact_id}")
            
            # Prepare request parameters
            url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
            params = {
                "recipient_id": contact_id,
                "limit": self.max_messages
            }
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Make request to WhatsApp Business API
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process messages
                    for message in data.get("data", []):
                        # Skip messages older than last update
                        if "timestamp" in message:
                            message_time = int(message["timestamp"])
                            if message_time <= last_update:
                                continue
                        
                        processed_message = await self._process_message(message, contact_id=contact_id)
                        if processed_message:
                            messages.append(processed_message)
                    
                    # Update last message timestamp
                    if messages:
                        self.last_message_timestamps[f"contact_{contact_id}"] = datetime.now().timestamp()
                else:
                    error_text = await response.text()
                    logger.error(f"WhatsApp API error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error fetching messages for contact {contact_id}: {str(e)}")
        
        return messages
    
    async def _process_message(self, message: Dict[str, Any], contact_id: Optional[str] = None, group_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Process a WhatsApp message.
        
        Args:
            message: Raw message data from WhatsApp API
            contact_id: ID of the contact (for direct messages)
            group_id: ID of the group (for group messages)
            
        Returns:
            Processed message data or None if error
        """
        try:
            message_id = message.get("id")
            
            # Get message type and content
            message_type = "unknown"
            content = ""
            media_url = None
            
            if "text" in message:
                message_type = "text"
                content = message.get("text", {}).get("body", "")
            elif "image" in message:
                message_type = "image"
                content = message.get("image", {}).get("caption", "")
                media_url = message.get("image", {}).get("url")
            elif "audio" in message:
                message_type = "audio"
                media_url = message.get("audio", {}).get("url")
            elif "video" in message:
                message_type = "video"
                content = message.get("video", {}).get("caption", "")
                media_url = message.get("video", {}).get("url")
            elif "document" in message:
                message_type = "document"
                content = message.get("document", {}).get("caption", "")
                media_url = message.get("document", {}).get("url")
            elif "location" in message:
                message_type = "location"
                location = message.get("location", {})
                content = f"Location: {location.get('latitude')},{location.get('longitude')}"
                if "name" in location:
                    content += f" - {location.get('name')}"
                if "address" in location:
                    content += f", {location.get('address')}"
            
            # Get media content if needed
            media_content = None
            if self.include_media and media_url:
                media_content = await self._fetch_media(media_url)
            
            # Build processed message
            processed_message = {
                "source_type": "whatsapp",
                "content_type": "message",
                "message_id": message_id,
                "message_type": message_type,
                "content": content,
                "timestamp": message.get("timestamp"),
                "from": message.get("from"),
                "to": message.get("to"),
                "contact_id": contact_id,
                "group_id": group_id,
                "media_url": media_url,
                "media_content": media_content
            }
            
            # Add contact information if available
            if "contacts" in message:
                contacts = message.get("contacts", [])
                if contacts:
                    processed_message["contact_info"] = contacts[0]
            
            return processed_message
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}")
            return None
    
    async def _fetch_media(self, media_url: str) -> Optional[str]:
        """
        Fetch media content from WhatsApp.
        
        Args:
            media_url: URL of the media
            
        Returns:
            Media content as text (if possible) or None
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with self.session.get(media_url, headers=headers) as response:
                if response.status == 200:
                    # Get content type
                    content_type = response.headers.get("Content-Type", "")
                    
                    if content_type.startswith("text/"):
                        # Text content - return as is
                        return await response.text()
                    elif content_type.startswith("image/") or content_type.startswith("video/") or content_type.startswith("audio/"):
                        # Binary content - could be processed further with OCR or speech-to-text
                        # For now, just indicate the type
                        return f"[{content_type} content]"
                    else:
                        return f"[Media content: {content_type}]"
                else:
                    error_text = await response.text()
                    logger.error(f"Error fetching media: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching media from {media_url}: {str(e)}")
            return None
    
    async def _setup_webhook_server(self) -> None:
        """Set up a webhook server for receiving WhatsApp messages."""
        from aiohttp import web
        
        app = web.Application()
        
        # Define webhook handlers
        async def verify_webhook(request):
            # Verify webhook (GET request)
            mode = request.query.get("hub.mode")
            token = request.query.get("hub.verify_token")
            challenge = request.query.get("hub.challenge")
            
            if mode == "subscribe" and token == self.webhook_secret:
                return web.Response(text=challenge)
            else:
                return web.Response(status=403)
        
        async def receive_webhook(request):
            # Process webhook data (POST request)
            try:
                body = await request.json()
                
                # Verify signature if secret is provided
                if self.webhook_secret:
                    signature = request.headers.get("X-Hub-Signature-256", "")
                    if not self._verify_webhook_signature(await request.read(), signature):
                        logger.warning("Invalid webhook signature")
                        return web.Response(status=403)
                
                # Process webhook data
                if "object" in body and body["object"] == "whatsapp_business_account":
                    for entry in body.get("entry", []):
                        if entry.get("id") == self.business_account_id:
                            for change in entry.get("changes", []):
                                if change.get("field") == "messages":
                                    for message in change.get("value", {}).get("messages", []):
                                        # Add message to queue for processing
                                        await self.webhook_queue.put(message)
                
                return web.Response(status=200)
            except Exception as e:
                logger.error(f"Error processing webhook: {str(e)}")
                return web.Response(status=500)
        
        # Set up routes
        app.router.add_get(self.webhook_path, verify_webhook)
        app.router.add_post(self.webhook_path, receive_webhook)
        
        # Start the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.webhook_port)
        await site.start()
        
        self.webhook_server = runner
        logger.info(f"WhatsApp webhook server started on port {self.webhook_port}")
    
    def _verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify the signature of a webhook request.
        
        Args:
            payload: Raw request payload
            signature: Signature from X-Hub-Signature-256 header
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not signature.startswith("sha256="):
            return False
        
        received_hash = signature[7:]
        
        # Calculate expected hash
        hmac_obj = hmac.new(
            self.webhook_secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256
        )
        expected_hash = hmac_obj.hexdigest()
        
        return hmac.compare_digest(received_hash, expected_hash)
    
    async def _process_webhook_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a message received via webhook.
        
        Args:
            message: Message data from webhook
            
        Returns:
            Processed message data or None if error
        """
        try:
            # Determine if this is a group message
            group_id = None
            contact_id = None
            
            if message.get("group_id"):
                group_id = message.get("group_id")
            else:
                contact_id = message.get("from")
            
            # Process the message
            return await self._process_message(message, contact_id=contact_id, group_id=group_id)
        except Exception as e:
            logger.error(f"Error processing webhook message: {str(e)}")
            return None
    
    async def close(self) -> None:
        """Close the WhatsApp connector."""
        if self.session:
            await self.session.close()
            self.session = None
        
        if self.webhook_server:
            await self.webhook_server.cleanup()
            self.webhook_server = None
        
        await super().close()
        logger.info("WhatsApp connector closed")