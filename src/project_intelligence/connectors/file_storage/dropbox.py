"""
Dropbox connector for the Project Intelligence System.

This module provides a connector for fetching and processing data from
Dropbox files and folders.
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


class DropboxConnector(DataSourceConnector):
    """
    Connector for Dropbox.
    
    This connector fetches data from Dropbox files and folders
    using the Dropbox API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Dropbox connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - access_token: Dropbox access token (required)
                - refresh_token: Dropbox refresh token (optional)
                - app_key: Dropbox app key (required for refresh token flow)
                - app_secret: Dropbox app secret (required for refresh token flow)
                - folders: List of folder paths to monitor (default: [])
                - file_types: List of file extensions to include (default: all)
                - include_file_content: Whether to include file content (default: True)
                - max_files: Maximum number of files to fetch (default: 1000)
                - include_deleted: Whether to include deleted files (default: False)
                - poll_interval: How often to check for changes in seconds (default: 300)
        """
        super().__init__(config)
        self.access_token = self.config.get("access_token")
        self.refresh_token = self.config.get("refresh_token")
        self.app_key = self.config.get("app_key")
        self.app_secret = self.config.get("app_secret")
        
        if not self.access_token and not (self.refresh_token and self.app_key and self.app_secret):
            raise ValueError("Dropbox authentication credentials are required")
        
        self.folders = self.config.get("folders", [])
        self.file_types = self.config.get("file_types", [])
        self.include_file_content = self.config.get("include_file_content", True)
        self.max_files = self.config.get("max_files", 1000)
        self.include_deleted = self.config.get("include_deleted", False)
        
        self.dbx = None
        self.cursor = None
        self.temp_files = []
    
    async def initialize(self) -> None:
        """Initialize the Dropbox connector."""
        await super().initialize()
        
        try:
            # Import Dropbox library
            try:
                import dropbox
                from dropbox import DropboxOAuth2FlowNoRedirect
            except ImportError:
                logger.error("Dropbox library not installed. Please install with: pip install dropbox")
                raise
            
            # Initialize Dropbox client
            if self.access_token:
                self.dbx = dropbox.Dropbox(self.access_token)
            elif self.refresh_token and self.app_key and self.app_secret:
                # Use refresh token flow
                def refresh_access_token():
                    from dropbox import DropboxOAuth2FlowNoRedirect
                    flow = DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
                    token_refresh = flow.refresh_access_token(self.refresh_token)
                    return dropbox.Dropbox(token_refresh.access_token)
                
                self.dbx = await asyncio.to_thread(refresh_access_token)
            
            # Validate the connection
            account = await asyncio.to_thread(self.dbx.users_get_current_account)
            logger.info(f"Dropbox connector initialized successfully for account: {account.name.display_name}")
            
            # Initialize cursor for listing changes
            if not self.folders:
                # If no folders specified, monitor the whole account
                result = await asyncio.to_thread(self.dbx.files_list_folder_get_latest_cursor, "", recursive=True)
                self.cursor = result.cursor
        except Exception as e:
            logger.error(f"Failed to initialize Dropbox connector: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from Dropbox.
        
        Returns:
            List of data items from Dropbox
        """
        await self._check_initialization()
        
        all_items = []
        
        # If specific folders are configured, fetch files from each folder
        if self.folders:
            for folder_path in self.folders:
                try:
                    folder_files = await self._fetch_folder_files(folder_path)
                    all_items.extend(folder_files)
                except Exception as e:
                    logger.error(f"Error fetching files from folder {folder_path}: {str(e)}")
        else:
            # If no specific folders, fetch changes since last check
            try:
                changed_files = await self._fetch_changes()
                all_items.extend(changed_files)
            except Exception as e:
                logger.error(f"Error fetching changes: {str(e)}")
        
        return all_items
    
    async def _fetch_folder_files(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Fetch files from a Dropbox folder.
        
        Args:
            folder_path: Path of the folder
            
        Returns:
            List of file data
        """
        try:
            # List folder contents
            result = await asyncio.to_thread(
                self.dbx.files_list_folder,
                folder_path,
                recursive=True,
                include_deleted=self.include_deleted
            )
            
            files = []
            entries = result.entries
            
            # Handle pagination
            while result.has_more:
                result = await asyncio.to_thread(self.dbx.files_list_folder_continue, result.cursor)
                entries.extend(result.entries)
            
            # Process entries
            for entry in entries:
                if hasattr(entry, 'path_lower'):
                    # Check if this is a file
                    is_file = hasattr(entry, 'size') and not hasattr(entry, 'folder_id')
                    
                    if is_file:
                        # Apply file type filter if specified
                        if self.file_types:
                            file_extension = os.path.splitext(entry.path_lower)[1].lower().lstrip('.')
                            if file_extension not in self.file_types:
                                continue
                        
                        # Process file
                        file_data = await self._process_file_entry(entry)
                        if file_data:
                            files.append(file_data)
                            
                            # Limit number of files
                            if len(files) >= self.max_files:
                                break
            
            return files
        except Exception as e:
            logger.error(f"Error listing files from Dropbox folder {folder_path}: {str(e)}")
            return []
    
    async def _fetch_changes(self) -> List[Dict[str, Any]]:
        """
        Fetch changes from Dropbox since last check.
        
        Returns:
            List of changed file data
        """
        if not self.cursor:
            logger.error("No cursor available for fetching changes")
            return []
        
        try:
            # Get changes since last cursor
            result = await asyncio.to_thread(self.dbx.files_list_folder_continue, self.cursor)
            
            files = []
            entries = result.entries
            
            # Handle pagination
            while result.has_more:
                result = await asyncio.to_thread(self.dbx.files_list_folder_continue, result.cursor)
                entries.extend(result.entries)
            
            # Update cursor for next time
            self.cursor = result.cursor
            
            # Process entries
            for entry in entries:
                if hasattr(entry, 'path_lower'):
                    # Check if this is a file
                    is_file = hasattr(entry, 'size') and not hasattr(entry, 'folder_id')
                    
                    if is_file:
                        # Apply file type filter if specified
                        if self.file_types:
                            file_extension = os.path.splitext(entry.path_lower)[1].lower().lstrip('.')
                            if file_extension not in self.file_types:
                                continue
                        
                        # Process file
                        file_data = await self._process_file_entry(entry)
                        if file_data:
                            files.append(file_data)
                            
                            # Limit number of files
                            if len(files) >= self.max_files:
                                break
            
            return files
        except Exception as e:
            logger.error(f"Error fetching changes from Dropbox: {str(e)}")
            return []
    
    async def _process_file_entry(self, entry: Any) -> Optional[Dict[str, Any]]:
        """
        Process a Dropbox file entry.
        
        Args:
            entry: Dropbox file entry
            
        Returns:
            Processed file data or None if error
        """
        try:
            # Extract file metadata
            file_data = {
                "source_type": "dropbox",
                "content_type": "file",
                "id": entry.id,
                "path": entry.path_lower,
                "name": os.path.basename(entry.path_lower),
                "size": entry.size,
                "client_modified": entry.client_modified.isoformat() if hasattr(entry, 'client_modified') else None,
                "server_modified": entry.server_modified.isoformat() if hasattr(entry, 'server_modified') else None,
                "revision": entry.rev if hasattr(entry, 'rev') else None
            }
            
            # Add sharing info if available
            if hasattr(entry, 'sharing_info'):
                file_data["sharing_info"] = {
                    "read_only": entry.sharing_info.read_only,
                    "parent_shared_folder_id": entry.sharing_info.parent_shared_folder_id
                }
            
            # Add file content if requested
            if self.include_file_content:
                content = await self._get_file_content(entry.path_lower)
                file_data["content"] = content
            
            return file_data
        except Exception as e:
            logger.error(f"Error processing Dropbox file entry: {str(e)}")
            return None
    
    async def _get_file_content(self, path: str) -> Optional[str]:
        """
        Get the content of a Dropbox file.
        
        Args:
            path: Path of the file
            
        Returns:
            File content as text or None if not available
        """
        try:
            # Get file extension
            file_extension = os.path.splitext(path)[1].lower()
            
            # Download file
            metadata, response = await asyncio.to_thread(self.dbx.files_download, path)
            
            # Process based on file type
            if file_extension in ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h', '.sh', '.bat', '.log']:
                # Text file - read directly
                content = response.content.decode('utf-8', errors='replace')
                return content
            elif file_extension in ['.pdf']:
                # PDF file - extract text if PyPDF2 is available
                try:
                    from PyPDF2 import PdfReader
                    
                    # Create a temporary file
                    fd, temp_path = tempfile.mkstemp(suffix='.pdf')
                    self.temp_files.append(temp_path)
                    
                    with os.fdopen(fd, 'wb') as temp_file:
                        temp_file.write(response.content)
                    
                    # Extract text from PDF
                    pdf_text = []
                    with open(temp_path, 'rb') as f:
                        reader = PdfReader(f)
                        for page in reader.pages:
                            pdf_text.append(page.extract_text())
                    
                    return "\n\n".join(pdf_text)
                except ImportError:
                    logger.warning("PyPDF2 not installed. Cannot extract text from PDF.")
                    return "[PDF content - text extraction not available]"
            elif file_extension in ['.doc', '.docx']:
                # Word document - extract text if python-docx is available
                try:
                    import docx
                    
                    # Create a temporary file
                    fd, temp_path = tempfile.mkstemp(suffix=file_extension)
                    self.temp_files.append(temp_path)
                    
                    with os.fdopen(fd, 'wb') as temp_file:
                        temp_file.write(response.content)
                    
                    # Extract text
                    doc = docx.Document(temp_path)
                    content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                    return content
                except ImportError:
                    logger.warning("python-docx not installed. Cannot extract text from Word document.")
                    return "[Word document content - text extraction not available]"
            elif file_extension in ['.xls', '.xlsx']:
                # Excel file - extract text if pandas and openpyxl are available
                try:
                    import pandas as pd
                    
                    # Create a temporary file
                    fd, temp_path = tempfile.mkstemp(suffix=file_extension)
                    self.temp_files.append(temp_path)
                    
                    with os.fdopen(fd, 'wb') as temp_file:
                        temp_file.write(response.content)
                    
                    # Extract data
                    df = pd.read_excel(temp_path)
                    return df.to_string()
                except ImportError:
                    logger.warning("pandas or openpyxl not installed. Cannot extract text from Excel file.")
                    return "[Excel file content - text extraction not available]"
            else:
                # Unknown file type
                return f"[Binary content - {metadata.name}]"
        except Exception as e:
            logger.error(f"Error getting content for file {path}: {str(e)}")
            return None
    
    async def close(self) -> None:
        """Close the Dropbox connector."""
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {temp_file}: {str(e)}")
        
        self.temp_files = []
        self.dbx = None
        
        await super().close()
        logger.info("Dropbox connector closed")