"""
Google Drive connector for the Project Intelligence System.

This module provides a connector for fetching and processing data from
Google Drive files and folders.
"""

import asyncio
import logging
import io
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..base import DataSourceConnector

logger = logging.getLogger(__name__)


class GoogleDriveConnector(DataSourceConnector):
    """
    Connector for Google Drive.
    
    This connector fetches data from Google Drive files and folders
    using the Google Drive API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Google Drive connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - credentials_file: Path to the Google API credentials file (required)
                - token_file: Path to save the token (default: token.json)
                - folders: List of folder IDs to monitor (default: [])
                - file_types: List of file types to include (default: all)
                - include_file_content: Whether to include file content (default: True)
                - max_files: Maximum number of files to fetch (default: 1000)
                - query: Custom query for files (default: None)
                - poll_interval: How often to check for changes in seconds (default: 300)
        """
        super().__init__(config)
        self.credentials_file = self.config.get("credentials_file")
        if not self.credentials_file:
            raise ValueError("Google Drive credentials file is required")
        
        self.token_file = self.config.get("token_file", "token.json")
        self.folders = self.config.get("folders", [])
        self.file_types = self.config.get("file_types", [])
        self.include_file_content = self.config.get("include_file_content", True)
        self.max_files = self.config.get("max_files", 1000)
        self.query = self.config.get("query")
        
        self.drive_service = None
        self.last_update_timestamps = {}
        self.temp_files = []
    
    async def initialize(self) -> None:
        """Initialize the Google Drive connector."""
        await super().initialize()
        
        try:
            # Import Google API libraries
            try:
                from googleapiclient.discovery import build
                from google_auth_oauthlib.flow import InstalledAppFlow
                from google.auth.transport.requests import Request
                from google.oauth2.credentials import Credentials
            except ImportError:
                logger.error("Google API libraries not installed. Please install with: "
                             "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
                raise
            
            # Define the scopes
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            
            # Authenticate and build service
            def auth_and_build():
                creds = None
                
                # Load existing token if it exists
                if os.path.exists(self.token_file):
                    creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
                
                # If no valid credentials are available, authenticate
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for the next run
                    with open(self.token_file, 'w') as token:
                        token.write(creds.to_json())
                
                # Build the Drive service
                return build('drive', 'v3', credentials=creds)
            
            # Run authentication in a thread pool
            self.drive_service = await asyncio.to_thread(auth_and_build)
            
            # Initialize last update timestamps
            current_time = datetime.now().timestamp() - 86400  # 24 hours ago
            
            for folder in self.folders:
                self.last_update_timestamps[folder] = current_time
            
            # If no specific folders, track root folder
            if not self.folders:
                self.last_update_timestamps["root"] = current_time
            
            logger.info("Google Drive connector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive connector: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from Google Drive.
        
        Returns:
            List of data items from Google Drive
        """
        await self._check_initialization()
        
        all_items = []
        
        # If specific folders are configured, fetch files from each folder
        if self.folders:
            for folder_id in self.folders:
                try:
                    folder_files = await self._fetch_folder_files(folder_id)
                    all_items.extend(folder_files)
                except Exception as e:
                    logger.error(f"Error fetching files from folder {folder_id}: {str(e)}")
        else:
            # If no specific folders, fetch recent files from the root
            try:
                root_files = await self._fetch_recent_files()
                all_items.extend(root_files)
            except Exception as e:
                logger.error(f"Error fetching recent files: {str(e)}")
        
        return all_items
    
    async def _fetch_folder_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        Fetch files from a Google Drive folder.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            List of file data
        """
        # Construct query for files in this folder
        query = f"'{folder_id}' in parents and trashed = false"
        
        # Add file type filter if specified
        if self.file_types:
            mime_types = []
            for file_type in self.file_types:
                if file_type == "document":
                    mime_types.append("application/vnd.google-apps.document")
                elif file_type == "spreadsheet":
                    mime_types.append("application/vnd.google-apps.spreadsheet")
                elif file_type == "presentation":
                    mime_types.append("application/vnd.google-apps.presentation")
                elif file_type == "pdf":
                    mime_types.append("application/pdf")
                elif file_type == "text":
                    mime_types.append("text/plain")
                else:
                    mime_types.append(file_type)  # Allow custom MIME types
            
            if mime_types:
                mime_query = " or ".join([f"mimeType = '{mime}'" for mime in mime_types])
                query += f" and ({mime_query})"
        
        # Add modification time filter
        last_update = self.last_update_timestamps.get(folder_id)
        last_update_date = datetime.fromtimestamp(last_update).isoformat()
        query += f" and modifiedTime > '{last_update_date}'"
        
        # Get files from the folder
        files = await self._list_files(query)
        
        # Update last update timestamp
        self.last_update_timestamps[folder_id] = datetime.now().timestamp()
        
        return await self._process_files(files)
    
    async def _fetch_recent_files(self) -> List[Dict[str, Any]]:
        """
        Fetch recent files from Google Drive.
        
        Returns:
            List of file data
        """
        # Get last update timestamp for root
        last_update = self.last_update_timestamps.get("root")
        last_update_date = datetime.fromtimestamp(last_update).isoformat()
        
        # Construct query for recently modified files
        query = f"trashed = false and modifiedTime > '{last_update_date}'"
        
        # Add file type filter if specified
        if self.file_types:
            mime_types = []
            for file_type in self.file_types:
                if file_type == "document":
                    mime_types.append("application/vnd.google-apps.document")
                elif file_type == "spreadsheet":
                    mime_types.append("application/vnd.google-apps.spreadsheet")
                elif file_type == "presentation":
                    mime_types.append("application/vnd.google-apps.presentation")
                elif file_type == "pdf":
                    mime_types.append("application/pdf")
                elif file_type == "text":
                    mime_types.append("text/plain")
                else:
                    mime_types.append(file_type)  # Allow custom MIME types
            
            if mime_types:
                mime_query = " or ".join([f"mimeType = '{mime}'" for mime in mime_types])
                query += f" and ({mime_query})"
        
        # Add custom query if specified
        if self.query:
            query += f" and ({self.query})"
        
        # Get recent files
        files = await self._list_files(query)
        
        # Update last update timestamp
        self.last_update_timestamps["root"] = datetime.now().timestamp()
        
        return await self._process_files(files)
    
    async def _list_files(self, query: str) -> List[Dict[str, Any]]:
        """
        List files from Google Drive using a query.
        
        Args:
            query: Query string for files
            
        Returns:
            List of file metadata
        """
        try:
            # Fields to retrieve
            fields = "files(id, name, mimeType, description, createdTime, modifiedTime, size, webViewLink, parents, properties)"
            
            # Execute the query
            response = await asyncio.to_thread(
                self.drive_service.files().list,
                q=query,
                spaces='drive',
                fields=fields,
                pageSize=min(100, self.max_files)  # API typically limits to 100 per request
            )
            
            result = await asyncio.to_thread(response.execute)
            
            files = result.get('files', [])
            
            # Handle pagination if needed
            next_page_token = result.get('nextPageToken')
            while next_page_token and len(files) < self.max_files:
                response = await asyncio.to_thread(
                    self.drive_service.files().list,
                    q=query,
                    spaces='drive',
                    fields=fields,
                    pageToken=next_page_token,
                    pageSize=min(100, self.max_files - len(files))
                )
                
                result = await asyncio.to_thread(response.execute)
                files.extend(result.get('files', []))
                next_page_token = result.get('nextPageToken')
            
            return files[:self.max_files]  # Limit to max_files
        except Exception as e:
            logger.error(f"Error listing files from Google Drive: {str(e)}")
            return []
    
    async def _process_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process Google Drive files.
        
        Args:
            files: List of file metadata
            
        Returns:
            List of processed file data
        """
        processed_files = []
        
        for file in files:
            try:
                file_id = file.get('id')
                mime_type = file.get('mimeType')
                
                processed_file = {
                    "source_type": "google_drive",
                    "content_type": "file",
                    "file_id": file_id,
                    "name": file.get('name'),
                    "mime_type": mime_type,
                    "description": file.get('description'),
                    "created_time": file.get('createdTime'),
                    "modified_time": file.get('modifiedTime'),
                    "size": file.get('size'),
                    "web_view_link": file.get('webViewLink'),
                    "parents": file.get('parents', []),
                    "properties": file.get('properties', {})
                }
                
                # Add file content if requested
                if self.include_file_content:
                    content = await self._get_file_content(file_id, mime_type)
                    processed_file["content"] = content
                
                processed_files.append(processed_file)
            except Exception as e:
                logger.error(f"Error processing file {file.get('id')}: {str(e)}")
        
        return processed_files
    
    async def _get_file_content(self, file_id: str, mime_type: str) -> Optional[str]:
        """
        Get the content of a Google Drive file.
        
        Args:
            file_id: ID of the file
            mime_type: MIME type of the file
            
        Returns:
            File content as text or None if not available
        """
        try:
            from googleapiclient.http import MediaIoBaseDownload
            import io
            
            content = None
            
            # Handle Google Docs formats
            if mime_type == 'application/vnd.google-apps.document':
                # Export as plain text
                request = self.drive_service.files().export_media(fileId=file_id, mimeType='text/plain')
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = await asyncio.to_thread(downloader.next_chunk)
                content = fh.getvalue().decode('utf-8')
            
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                # Export as CSV
                request = self.drive_service.files().export_media(fileId=file_id, mimeType='text/csv')
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = await asyncio.to_thread(downloader.next_chunk)
                content = fh.getvalue().decode('utf-8')
            
            # Handle normal files (PDFs, text files, etc.)
            elif mime_type.startswith('text/') or mime_type == 'application/pdf':
                request = self.drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = await asyncio.to_thread(downloader.next_chunk)
                
                # For PDF files, extract text using PyPDF2 if available
                if mime_type == 'application/pdf':
                    try:
                        from PyPDF2 import PdfReader
                        
                        # Create a temporary file
                        fd, temp_path = tempfile.mkstemp(suffix='.pdf')
                        self.temp_files.append(temp_path)
                        
                        with os.fdopen(fd, 'wb') as temp_file:
                            temp_file.write(fh.getvalue())
                        
                        # Extract text from PDF
                        pdf_text = []
                        with open(temp_path, 'rb') as f:
                            reader = PdfReader(f)
                            for page in reader.pages:
                                pdf_text.append(page.extract_text())
                        
                        content = "\n\n".join(pdf_text)
                    except ImportError:
                        logger.warning("PyPDF2 not installed. Cannot extract text from PDF.")
                        content = "[PDF content - text extraction not available]"
                else:
                    # For text files, decode directly
                    content = fh.getvalue().decode('utf-8', errors='replace')
            
            return content
        except Exception as e:
            logger.error(f"Error getting content for file {file_id}: {str(e)}")
            return None
    
    async def close(self) -> None:
        """Close the Google Drive connector."""
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {temp_file}: {str(e)}")
        
        self.temp_files = []
        self.drive_service = None
        
        await super().close()
        logger.info("Google Drive connector closed")