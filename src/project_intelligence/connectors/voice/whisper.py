"""
Voice-to-text connector using OpenAI's Whisper for the Project Intelligence System.

This module provides a connector for transcribing voice recordings to text
using OpenAI's Whisper model, enabling field calls to be included in project intelligence.
"""

import asyncio
import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import aiofiles
import aiohttp

from ..base import DataSourceConnector

logger = logging.getLogger(__name__)


class WhisperConnector(DataSourceConnector):
    """
    Connector for voice-to-text transcription using OpenAI's Whisper.
    
    This connector monitors directories for audio files, transcribes them using
    Whisper, and provides the transcriptions for project intelligence extraction.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Whisper connector.
        
        Args:
            config: Configuration dictionary with the following keys:
                - api_key: OpenAI API key (required for OpenAI API mode)
                - mode: "local" or "api" (default: "api")
                - local_model: Model name for local mode (default: "base")
                - watch_directories: List of directories to monitor for audio files (default: [])
                - processed_directory: Directory to move processed files to (default: "processed")
                - supported_formats: List of supported audio formats (default: [".mp3", ".wav", ".m4a", ".ogg"])
                - language: Language code for transcription (default: "en")
                - include_metadata: Whether to include audio metadata in output (default: True)
                - max_files: Maximum number of files to process per cycle (default: 10)
                - poll_interval: How often to check for new files in seconds (default: 300)
        """
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        self.mode = self.config.get("mode", "api")
        
        if self.mode == "api" and not self.api_key:
            raise ValueError("OpenAI API key is required for API mode")
        
        self.local_model = self.config.get("local_model", "base")
        self.watch_directories = self.config.get("watch_directories", [])
        self.processed_directory = self.config.get("processed_directory", "processed")
        self.supported_formats = self.config.get("supported_formats", [".mp3", ".wav", ".m4a", ".ogg"])
        self.language = self.config.get("language", "en")
        self.include_metadata = self.config.get("include_metadata", True)
        self.max_files = self.config.get("max_files", 10)
        
        self.session = None
        self.model = None
        self.last_check_times = {}
    
    async def initialize(self) -> None:
        """Initialize the Whisper connector."""
        await super().initialize()
        
        try:
            # Initialize HTTP session for API mode
            if self.mode == "api":
                self.session = aiohttp.ClientSession()
            else:
                # Import and load Whisper for local mode
                try:
                    import whisper
                    self.model = await asyncio.to_thread(whisper.load_model, self.local_model)
                    logger.info(f"Loaded Whisper model: {self.local_model}")
                except ImportError:
                    logger.error("Whisper not installed. Please install with: pip install openai-whisper")
                    raise
            
            # Initialize last check times for directories
            for directory in self.watch_directories:
                self.last_check_times[directory] = datetime.now().timestamp()
                
                # Create processed directory if it doesn't exist
                processed_dir = os.path.join(directory, self.processed_directory)
                os.makedirs(processed_dir, exist_ok=True)
            
            logger.info(f"Whisper connector initialized successfully in {self.mode} mode")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper connector: {str(e)}")
            raise
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch and transcribe audio files.
        
        Returns:
            List of transcription data
        """
        await self._check_initialization()
        
        all_transcriptions = []
        
        for directory in self.watch_directories:
            try:
                # Find audio files modified since last check
                audio_files = await self._find_new_audio_files(directory)
                
                # Process up to max_files
                for file_path in audio_files[:self.max_files]:
                    transcription = await self._transcribe_audio(file_path)
                    if transcription:
                        all_transcriptions.append(transcription)
                        
                        # Move to processed directory
                        await self._move_to_processed(file_path, directory)
            except Exception as e:
                logger.error(f"Error processing audio files in directory {directory}: {str(e)}")
        
        return all_transcriptions
    
    async def _find_new_audio_files(self, directory: str) -> List[str]:
        """
        Find audio files modified since the last check.
        
        Args:
            directory: Directory to check
            
        Returns:
            List of audio file paths
        """
        last_check_time = self.last_check_times.get(directory, 0)
        self.last_check_times[directory] = datetime.now().timestamp()
        
        audio_files = []
        
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                # Skip the processed directory
                if os.path.basename(file_path) == self.processed_directory:
                    continue
                
                # Check if it's a file with supported extension
                if (os.path.isfile(file_path) and 
                    any(filename.lower().endswith(ext) for ext in self.supported_formats)):
                    
                    # Check if modified since last check
                    mod_time = os.path.getmtime(file_path)
                    if mod_time > last_check_time:
                        audio_files.append(file_path)
            
            # Sort by modification time (oldest first)
            audio_files.sort(key=lambda f: os.path.getmtime(f))
        except Exception as e:
            logger.error(f"Error finding audio files in {directory}: {str(e)}")
        
        return audio_files
    
    async def _transcribe_audio(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Transcribe an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Transcription data or None if error
        """
        try:
            # Get file metadata
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # Transcribe based on mode
            if self.mode == "api":
                transcription = await self._transcribe_with_api(file_path)
            else:
                transcription = await self._transcribe_locally(file_path)
            
            if not transcription:
                return None
            
            # Build result
            result = {
                "source_type": "voice",
                "content_type": "transcription",
                "file_path": file_path,
                "file_name": file_name,
                "transcription": transcription,
                "transcription_time": datetime.now().isoformat()
            }
            
            # Add metadata if requested
            if self.include_metadata:
                result["metadata"] = {
                    "file_size": file_size,
                    "modification_time": modification_time.isoformat(),
                    "file_extension": os.path.splitext(file_name)[1].lower()
                }
            
            return result
        except Exception as e:
            logger.error(f"Error transcribing audio file {file_path}: {str(e)}")
            return None
    
    async def _transcribe_with_api(self, file_path: str) -> Optional[str]:
        """
        Transcribe audio using OpenAI's API.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Transcription text or None if error
        """
        if not self.session:
            return None
        
        try:
            url = "https://api.openai.com/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Prepare file for upload
            data = aiohttp.FormData()
            data.add_field("file", open(file_path, "rb"), filename=os.path.basename(file_path))
            data.add_field("model", "whisper-1")
            data.add_field("language", self.language)
            
            # Make API request
            async with self.session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("text")
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Error using OpenAI API for transcription: {str(e)}")
            return None
    
    async def _transcribe_locally(self, file_path: str) -> Optional[str]:
        """
        Transcribe audio using local Whisper model.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Transcription text or None if error
        """
        if not self.model:
            return None
        
        try:
            # Run transcription in a thread pool to avoid blocking
            result = await asyncio.to_thread(
                self.model.transcribe,
                file_path,
                language=self.language
            )
            
            return result.get("text")
        except Exception as e:
            logger.error(f"Error using local Whisper model for transcription: {str(e)}")
            return None
    
    async def _move_to_processed(self, file_path: str, directory: str) -> None:
        """
        Move a processed file to the processed directory.
        
        Args:
            file_path: Path to the file
            directory: Base directory
        """
        try:
            processed_dir = os.path.join(directory, self.processed_directory)
            filename = os.path.basename(file_path)
            
            # Add timestamp to avoid name conflicts
            base, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{base}_{timestamp}{ext}"
            
            destination = os.path.join(processed_dir, new_filename)
            
            # Move the file
            os.rename(file_path, destination)
            logger.info(f"Moved processed file {file_path} to {destination}")
        except Exception as e:
            logger.error(f"Error moving processed file {file_path}: {str(e)}")
    
    async def close(self) -> None:
        """Close the Whisper connector."""
        if self.session:
            await self.session.close()
            self.session = None
        
        # Release model resources
        self.model = None
        
        await super().close()
        logger.info("Whisper connector closed")