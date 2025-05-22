"""
Spreadsheet connector for the Project Intelligence System.

This module provides a connector for fetching and processing data from 
spreadsheets (Excel, Google Sheets, CSV, etc.).
"""

import asyncio
import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple

import pandas as pd
from .base import DataSourceConnector

logger = logging.getLogger(__name__)


class SpreadsheetConnector(DataSourceConnector):
    """
    Connector for spreadsheet sources.
    
    This connector can fetch data from various spreadsheet formats,
    including local files, URLs, and Google Sheets.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the spreadsheet connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - sources: List of spreadsheet sources, each with:
                    - type: "local", "url", or "google_sheets"
                    - path: File path (for local) or URL
                    - sheet_name: Sheet name or index (default: 0)
                    - credentials_file: Path to credentials file (for Google Sheets)
                    - poll_interval: How often to check for changes in seconds (default: 300)
                    - source_id: Unique identifier for this source
        """
        super().__init__(config)
        self.sources = self.config.get("sources", [])
        self.last_modified = {}  # Track when sources were last modified
        self.temp_files = []     # Track temporary files to clean up
    
    async def initialize(self) -> None:
        """Initialize the spreadsheet connector."""
        await super().initialize()
        
        # Check required libraries
        try:
            import pandas as pd
            logger.info("Pandas library available for spreadsheet processing")
        except ImportError:
            logger.error("Pandas library not available. Please install with: pip install pandas")
            raise
        
        # Check if we need gspread for Google Sheets
        has_google_sheets = any(src.get("type") == "google_sheets" for src in self.sources)
        if has_google_sheets:
            try:
                import gspread
                from google.oauth2.service_account import Credentials
                logger.info("Google Sheets libraries available")
            except ImportError:
                logger.error("Google Sheets libraries not available. "
                             "Please install with: pip install gspread google-auth")
                raise
        
        # Initialize last modified times
        for source in self.sources:
            source_id = source.get("source_id") or source.get("path")
            self.last_modified[source_id] = 0
        
        logger.info(f"Spreadsheet connector initialized with {len(self.sources)} sources")
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from configured spreadsheet sources.
        
        Returns:
            List of spreadsheet data items
        """
        await self._check_initialization()
        
        all_data = []
        
        for source in self.sources:
            source_type = source.get("type", "local")
            source_id = source.get("source_id") or source.get("path")
            
            try:
                # Check if we need to update this source
                if not await self._should_update_source(source):
                    logger.debug(f"Skipping source {source_id} - no changes detected")
                    continue
                
                # Fetch data based on source type
                if source_type == "local":
                    data = await self._fetch_local_spreadsheet(source)
                elif source_type == "url":
                    data = await self._fetch_url_spreadsheet(source)
                elif source_type == "google_sheets":
                    data = await self._fetch_google_sheets(source)
                else:
                    logger.warning(f"Unknown spreadsheet source type: {source_type}")
                    continue
                
                if data:
                    all_data.extend(data)
                    
                    # Update last modified time
                    self.last_modified[source_id] = datetime.now().timestamp()
            except Exception as e:
                logger.error(f"Error fetching data from spreadsheet source {source_id}: {str(e)}")
        
        return all_data
    
    async def _should_update_source(self, source: Dict[str, Any]) -> bool:
        """
        Check if a source should be updated based on its last modified time.
        
        Args:
            source: Source configuration
            
        Returns:
            True if the source should be updated, False otherwise
        """
        source_id = source.get("source_id") or source.get("path")
        source_type = source.get("type", "local")
        poll_interval = source.get("poll_interval", 300)  # Default: 5 minutes
        
        # Always update if it's the first time
        if self.last_modified.get(source_id, 0) == 0:
            return True
        
        # Check time elapsed since last update
        time_elapsed = datetime.now().timestamp() - self.last_modified.get(source_id, 0)
        if time_elapsed < poll_interval:
            return False
        
        # For local files, check if file was modified
        if source_type == "local":
            path = source.get("path")
            if not path or not os.path.exists(path):
                return False
            
            try:
                file_mtime = os.path.getmtime(path)
                return file_mtime > self.last_modified.get(source_id, 0)
            except Exception as e:
                logger.error(f"Error checking file modification time: {str(e)}")
                return True
        
        # For other sources, update based on poll interval
        return True
    
    async def _fetch_local_spreadsheet(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch data from a local spreadsheet file.
        
        Args:
            source: Source configuration
            
        Returns:
            List of data items
        """
        path = source.get("path")
        if not path:
            logger.error("Missing path for local spreadsheet source")
            return []
        
        if not os.path.exists(path):
            logger.error(f"Spreadsheet file not found: {path}")
            return []
        
        sheet_name = source.get("sheet_name", 0)
        
        try:
            # Run in thread pool to avoid blocking
            def read_spreadsheet():
                if path.endswith('.csv'):
                    return pd.read_csv(path)
                else:
                    return pd.read_excel(path, sheet_name=sheet_name)
            
            df = await asyncio.to_thread(read_spreadsheet)
            
            # Convert to list of dictionaries
            records = df.to_dict(orient='records')
            
            # Add metadata
            return self._add_metadata_to_records(records, source)
        except Exception as e:
            logger.error(f"Error reading local spreadsheet {path}: {str(e)}")
            return []
    
    async def _fetch_url_spreadsheet(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch data from a spreadsheet URL.
        
        Args:
            source: Source configuration
            
        Returns:
            List of data items
        """
        url = source.get("path")
        if not url:
            logger.error("Missing URL for spreadsheet source")
            return []
        
        sheet_name = source.get("sheet_name", 0)
        
        try:
            # Download file to temporary location
            import requests
            
            # Run in thread pool to avoid blocking
            def download_file():
                response = requests.get(url)
                response.raise_for_status()
                
                # Create temporary file
                suffix = '.csv' if url.endswith('.csv') else '.xlsx'
                fd, temp_path = tempfile.mkstemp(suffix=suffix)
                self.temp_files.append(temp_path)
                
                # Write content to file
                with os.fdopen(fd, 'wb') as f:
                    f.write(response.content)
                
                return temp_path
            
            temp_path = await asyncio.to_thread(download_file)
            
            # Read the downloaded file
            def read_spreadsheet():
                if temp_path.endswith('.csv'):
                    return pd.read_csv(temp_path)
                else:
                    return pd.read_excel(temp_path, sheet_name=sheet_name)
            
            df = await asyncio.to_thread(read_spreadsheet)
            
            # Convert to list of dictionaries
            records = df.to_dict(orient='records')
            
            # Add metadata
            return self._add_metadata_to_records(records, source)
        except Exception as e:
            logger.error(f"Error reading spreadsheet from URL {url}: {str(e)}")
            return []
    
    async def _fetch_google_sheets(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch data from Google Sheets.
        
        Args:
            source: Source configuration
            
        Returns:
            List of data items
        """
        spreadsheet_id = source.get("path")
        credentials_file = source.get("credentials_file")
        sheet_name = source.get("sheet_name", 0)
        
        if not spreadsheet_id:
            logger.error("Missing spreadsheet ID for Google Sheets source")
            return []
        
        if not credentials_file:
            logger.error("Missing credentials file for Google Sheets source")
            return []
        
        try:
            # Import required libraries
            import gspread
            from google.oauth2.service_account import Credentials
            
            # Authenticate and open spreadsheet
            def access_google_sheets():
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets.readonly',
                    'https://www.googleapis.com/auth/drive.readonly'
                ]
                
                credentials = Credentials.from_service_account_file(
                    credentials_file, scopes=scopes
                )
                
                gc = gspread.authorize(credentials)
                spreadsheet = gc.open_by_key(spreadsheet_id)
                
                # Get the specified worksheet
                if isinstance(sheet_name, int):
                    worksheet = spreadsheet.get_worksheet(sheet_name)
                else:
                    worksheet = spreadsheet.worksheet(sheet_name)
                
                # Get all records
                return worksheet.get_all_records()
            
            records = await asyncio.to_thread(access_google_sheets)
            
            # Add metadata
            return self._add_metadata_to_records(records, source)
        except Exception as e:
            logger.error(f"Error reading Google Sheet {spreadsheet_id}: {str(e)}")
            return []
    
    def _add_metadata_to_records(self, records: List[Dict[str, Any]], source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Add metadata to spreadsheet records.
        
        Args:
            records: List of records from the spreadsheet
            source: Source configuration
            
        Returns:
            List of records with metadata
        """
        source_id = source.get("source_id") or source.get("path")
        source_type = source.get("type", "local")
        path = source.get("path", "")
        sheet_name = source.get("sheet_name", 0)
        
        enriched_records = []
        for record in records:
            enriched_record = {
                "source_type": "spreadsheet",
                "source_provider": source_type,
                "source_id": source_id,
                "path": path,
                "sheet_name": sheet_name,
                "fetch_time": datetime.now(),
                "data": record
            }
            enriched_records.append(enriched_record)
        
        return enriched_records
    
    async def close(self) -> None:
        """Close the spreadsheet connector and clean up resources."""
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {temp_file}: {str(e)}")
        
        self.temp_files = []
        await super().close()
        logger.info("Spreadsheet connector closed")