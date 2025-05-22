"""
Email connector for the Project Intelligence System.

This module provides a connector for fetching and processing emails from
various email providers (IMAP, Gmail API, etc.).
"""

import asyncio
import email
import imaplib
import logging
import re
from datetime import datetime
from email.header import decode_header
from typing import Any, Dict, List, Optional, Union, Tuple

from .base import DataSourceConnector

logger = logging.getLogger(__name__)


class EmailConnector(DataSourceConnector):
    """
    Connector for email sources.
    
    This connector can fetch emails from IMAP servers or via the Gmail API,
    depending on the configuration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the email connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - provider: "imap" or "gmail"
                - server: IMAP server address (for IMAP)
                - username: Email username/address
                - password: Email password or app password
                - port: IMAP port (default: 993)
                - use_ssl: Whether to use SSL (default: True)
                - folders: List of folders to check (default: ["INBOX"])
                - search_criteria: IMAP search criteria (default: "UNSEEN")
                - max_emails: Maximum number of emails to fetch (default: 100)
                - credentials_file: Path to credentials file (for Gmail API)
        """
        super().__init__(config)
        self.provider = self.config.get("provider", "imap").lower()
        self.server = self.config.get("server")
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.port = self.config.get("port", 993)
        self.use_ssl = self.config.get("use_ssl", True)
        self.folders = self.config.get("folders", ["INBOX"])
        self.search_criteria = self.config.get("search_criteria", "UNSEEN")
        self.max_emails = self.config.get("max_emails", 100)
        self.connection = None
        self.gmail_service = None
        
    async def initialize(self) -> None:
        """Initialize the email connector."""
        await super().initialize()
        
        if self.provider == "imap":
            await self._initialize_imap()
        elif self.provider == "gmail":
            await self._initialize_gmail()
        else:
            raise ValueError(f"Unsupported email provider: {self.provider}")
    
    async def _initialize_imap(self) -> None:
        """Initialize connection to IMAP server."""
        try:
            # This is blocking, so we run it in a thread pool
            def connect_imap():
                if self.use_ssl:
                    conn = imaplib.IMAP4_SSL(self.server, self.port)
                else:
                    conn = imaplib.IMAP4(self.server, self.port)
                conn.login(self.username, self.password)
                return conn
            
            self.connection = await asyncio.to_thread(connect_imap)
            logger.info(f"Connected to IMAP server: {self.server}")
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {str(e)}")
            raise
    
    async def _initialize_gmail(self) -> None:
        """Initialize connection to Gmail API."""
        try:
            # Importing here to avoid dependency if not using Gmail
            from googleapiclient.discovery import build
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            import os.path
            
            credentials_file = self.config.get("credentials_file")
            if not credentials_file:
                raise ValueError("credentials_file is required for Gmail API")
            
            token_file = self.config.get("token_file", "token.json")
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            
            creds = None
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            
            # If there are no valid credentials, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    await asyncio.to_thread(creds.refresh, Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                    creds = await asyncio.to_thread(flow.run_local_server, port=0)
                
                # Save the credentials for the next run
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Create Gmail API service
            self.gmail_service = await asyncio.to_thread(build, 'gmail', 'v1', credentials=creds)
            logger.info("Connected to Gmail API")
        except Exception as e:
            logger.error(f"Failed to connect to Gmail API: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch emails from the configured source.
        
        Returns:
            List of email data items
        """
        await self._check_initialization()
        
        if self.provider == "imap":
            return await self._fetch_imap_emails()
        elif self.provider == "gmail":
            return await self._fetch_gmail_emails()
        else:
            logger.error(f"Unsupported email provider: {self.provider}")
            return []
    
    async def _fetch_imap_emails(self) -> List[Dict[str, Any]]:
        """Fetch emails from IMAP server."""
        emails = []
        
        for folder in self.folders:
            try:
                # Select the folder
                status, _ = await asyncio.to_thread(self.connection.select, folder)
                if status != 'OK':
                    logger.error(f"Failed to select folder: {folder}")
                    continue
                
                # Search for emails
                status, data = await asyncio.to_thread(
                    self.connection.search, None, self.search_criteria
                )
                if status != 'OK':
                    logger.error(f"Failed to search emails in folder: {folder}")
                    continue
                
                # Get email IDs
                email_ids = data[0].split()
                if not email_ids:
                    logger.info(f"No emails found in folder: {folder}")
                    continue
                
                # Limit the number of emails
                email_ids = email_ids[-self.max_emails:]
                
                # Fetch emails
                for email_id in email_ids:
                    status, data = await asyncio.to_thread(
                        self.connection.fetch, email_id, '(RFC822)'
                    )
                    if status != 'OK':
                        logger.error(f"Failed to fetch email: {email_id}")
                        continue
                    
                    msg = email.message_from_bytes(data[0][1])
                    email_data = self._parse_email_message(msg, folder)
                    emails.append(email_data)
                    
                    # Mark as seen if needed
                    if 'UNSEEN' in self.search_criteria:
                        await asyncio.to_thread(
                            self.connection.store, email_id, '+FLAGS', '\\Seen'
                        )
            except Exception as e:
                logger.error(f"Error fetching emails from folder {folder}: {str(e)}")
        
        return emails
    
    async def _fetch_gmail_emails(self) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail API."""
        emails = []
        
        try:
            # Convert folder names to Gmail labels
            labels = []
            for folder in self.folders:
                if folder.upper() == "INBOX":
                    labels.append("INBOX")
                else:
                    # Handle custom labels
                    labels.append(folder)
            
            # Create query
            query = ""
            if "UNSEEN" in self.search_criteria:
                query = "is:unread"
            
            # List messages
            for label in labels:
                results = await asyncio.to_thread(
                    self.gmail_service.users().messages().list(
                        userId='me',
                        labelIds=[label],
                        q=query,
                        maxResults=self.max_emails
                    ).execute
                )
                
                messages = results.get('messages', [])
                
                for message in messages:
                    msg = await asyncio.to_thread(
                        self.gmail_service.users().messages().get(
                            userId='me',
                            id=message['id'],
                            format='full'
                        ).execute
                    )
                    
                    email_data = self._parse_gmail_message(msg, label)
                    emails.append(email_data)
                    
                    # Mark as read if needed
                    if "UNSEEN" in self.search_criteria:
                        await asyncio.to_thread(
                            self.gmail_service.users().messages().modify(
                                userId='me',
                                id=message['id'],
                                body={'removeLabelIds': ['UNREAD']}
                            ).execute
                        )
        except Exception as e:
            logger.error(f"Error fetching emails from Gmail API: {str(e)}")
        
        return emails
    
    def _parse_email_message(self, msg, folder: str) -> Dict[str, Any]:
        """
        Parse an email.message.Message object into a dictionary.
        
        Args:
            msg: The email message object
            folder: The folder where the email was found
            
        Returns:
            Dictionary with email data
        """
        # Get email subject
        subject = ""
        if msg["Subject"]:
            subject_parts = decode_header(msg["Subject"])
            subject = "".join(
                part.decode(encoding or "utf-8") if isinstance(part, bytes) else part
                for part, encoding in subject_parts
            )
        
        # Get sender
        sender = ""
        if msg["From"]:
            sender_parts = decode_header(msg["From"])
            sender = "".join(
                part.decode(encoding or "utf-8") if isinstance(part, bytes) else part
                for part, encoding in sender_parts
            )
        
        # Get date
        date_str = msg["Date"]
        date = datetime.now()
        if date_str:
            try:
                from email.utils import parsedate_to_datetime
                date = parsedate_to_datetime(date_str)
            except Exception:
                pass
        
        # Get message body
        body = self._get_email_body(msg)
        
        return {
            "source_type": "email",
            "source_provider": self.provider,
            "folder": folder,
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body,
            "raw_message": str(msg)
        }
    
    def _parse_gmail_message(self, msg, label: str) -> Dict[str, Any]:
        """
        Parse a Gmail API message into a dictionary.
        
        Args:
            msg: The Gmail API message object
            label: The label where the message was found
            
        Returns:
            Dictionary with email data
        """
        headers = msg['payload']['headers']
        
        # Get email subject
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
        
        # Get sender
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
        
        # Get date
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), "")
        date = datetime.now()
        if date_str:
            try:
                from email.utils import parsedate_to_datetime
                date = parsedate_to_datetime(date_str)
            except Exception:
                pass
        
        # Get message body
        body = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    import base64
                    body_bytes = base64.urlsafe_b64decode(part['body']['data'])
                    body = body_bytes.decode('utf-8')
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            import base64
            body_bytes = base64.urlsafe_b64decode(msg['payload']['body']['data'])
            body = body_bytes.decode('utf-8')
        
        return {
            "source_type": "email",
            "source_provider": self.provider,
            "folder": label,
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body,
            "message_id": msg['id']
        }
    
    def _get_email_body(self, msg) -> str:
        """
        Extract the plain text body from an email message.
        
        Args:
            msg: The email.message.Message object
            
        Returns:
            Plain text body of the email
        """
        body = ""
        
        # Check if the message is multipart
        if msg.is_multipart():
            # Iterate through parts to find text/plain
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text/plain parts
                if content_type == "text/plain":
                    try:
                        body_bytes = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body += body_bytes.decode(charset)
                    except Exception as e:
                        logger.warning(f"Failed to decode email part: {str(e)}")
        else:
            # Not multipart, just get the payload
            try:
                body_bytes = msg.get_payload(decode=True)
                charset = msg.get_content_charset() or 'utf-8'
                body = body_bytes.decode(charset)
            except Exception as e:
                logger.warning(f"Failed to decode email: {str(e)}")
        
        return body
    
    async def close(self) -> None:
        """Close the email connector."""
        try:
            if self.provider == "imap" and self.connection:
                await asyncio.to_thread(self.connection.logout)
            
            self.connection = None
            self.gmail_service = None
            await super().close()
            logger.info("Email connector closed")
        except Exception as e:
            logger.error(f"Error closing email connector: {str(e)}")