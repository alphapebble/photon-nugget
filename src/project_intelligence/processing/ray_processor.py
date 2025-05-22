"""
Ray distributed processing module for Project Intelligence.

This module provides Ray-based distributed processing capabilities for
the Project Intelligence System.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union, Callable

import ray
from ray.actor import ActorHandle

from ..models.extraction import DocumentContext, ExtractionResult
from ..workflows.extraction_workflow import process_document

logger = logging.getLogger(__name__)


@ray.remote
class DocumentProcessor:
    """
    Ray actor for processing documents in parallel.
    
    This actor processes documents using the extraction workflow and
    returns the results.
    """
    
    def __init__(self, processor_id: str):
        """
        Initialize the document processor.
        
        Args:
            processor_id: Unique identifier for this processor
        """
        self.processor_id = processor_id
        self.documents_processed = 0
        self.errors = 0
        self.loop = None
        self._initialize_asyncio()
    
    def _initialize_asyncio(self):
        """Initialize asyncio event loop for the actor."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def process_document(self, document_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document and extract information.
        
        Args:
            document_dict: Dictionary representation of a DocumentContext
            
        Returns:
            Dictionary representation of an ExtractionResult
        """
        try:
            # Convert dict to DocumentContext
            from pydantic import ValidationError
            
            try:
                document = DocumentContext.model_validate(document_dict)
            except ValidationError as e:
                logger.error(f"Error validating document: {str(e)}")
                return {
                    "document_id": document_dict.get("id", "unknown"),
                    "document_type": document_dict.get("type", "unknown"),
                    "confidence": 0.0,
                    "requires_human_review": True,
                    "errors": [f"Document validation error: {str(e)}"],
                }
            
            # Process document using the event loop
            result_dict = self.loop.run_until_complete(self._process_async(document))
            
            # Update stats
            self.documents_processed += 1
            
            return result_dict
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            self.errors += 1
            return {
                "document_id": document_dict.get("id", "unknown"),
                "document_type": document_dict.get("type", "unknown"),
                "confidence": 0.0,
                "requires_human_review": True,
                "errors": [f"Processing error: {str(e)}"],
            }
    
    async def _process_async(self, document: DocumentContext) -> Dict[str, Any]:
        """
        Process a document asynchronously.
        
        Args:
            document: Document to process
            
        Returns:
            Dictionary representation of the extraction result
        """
        try:
            # Process the document using the extraction workflow
            result = await process_document(document)
            
            # Convert to dict
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in async processing: {str(e)}")
            return {
                "document_id": document.id,
                "document_type": document.type,
                "confidence": 0.0,
                "requires_human_review": True,
                "errors": [f"Async processing error: {str(e)}"],
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get processor statistics.
        
        Returns:
            Dictionary of processor statistics
        """
        return {
            "processor_id": self.processor_id,
            "documents_processed": self.documents_processed,
            "errors": self.errors,
        }


class RayProcessor:
    """
    Ray-based distributed processor for project intelligence extraction.
    
    This class manages a pool of Ray actors for parallel document processing.
    """
    
    def __init__(self, num_processors: int = 4):
        """
        Initialize the Ray processor.
        
        Args:
            num_processors: Number of processor actors to create
        """
        self.num_processors = num_processors
        self.processors: List[ActorHandle] = []
        self.initialized = False
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def initialize(self) -> None:
        """Initialize the Ray cluster and create processor actors."""
        if self.initialized:
            return
        
        # Initialize Ray if not already initialized
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)
        
        # Create processor actors
        self.processors = [
            DocumentProcessor.remote(f"processor-{i}")
            for i in range(self.num_processors)
        ]
        
        self.initialized = True
        logger.info(f"Ray processor initialized with {self.num_processors} processors")
    
    def shutdown(self) -> None:
        """Shutdown the Ray cluster."""
        if not self.initialized:
            return
        
        # Shutdown Ray if it was initialized
        if ray.is_initialized():
            ray.shutdown()
        
        self.processors = []
        self.initialized = False
        logger.info("Ray processor shut down")
    
    async def process_batch(self, documents: List[DocumentContext]) -> List[ExtractionResult]:
        """
        Process a batch of documents in parallel.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of extraction results
        """
        if not self.initialized:
            self.initialize()
        
        if not documents:
            return []
        
        try:
            # Convert documents to dicts
            document_dicts = [doc.model_dump() for doc in documents]
            
            # Distribute documents across processors
            tasks = []
            for i, doc_dict in enumerate(document_dicts):
                processor_idx = i % len(self.processors)
                processor = self.processors[processor_idx]
                tasks.append(processor.process_document.remote(doc_dict))
            
            # Wait for results
            result_dicts = await asyncio.to_thread(ray.get, tasks)
            
            # Convert results back to ExtractionResult objects
            from pydantic import ValidationError
            
            results = []
            for result_dict in result_dicts:
                try:
                    result = ExtractionResult.model_validate(result_dict)
                    results.append(result)
                except ValidationError as e:
                    logger.error(f"Error validating result: {str(e)}")
                    # Create a minimal result with error
                    doc_id = result_dict.get("document_id", "unknown")
                    doc_type = result_dict.get("document_type", "unknown")
                    results.append(
                        ExtractionResult(
                            document_id=doc_id,
                            document_type=doc_type,
                            confidence=0.0,
                            requires_human_review=True,
                            errors=[f"Result validation error: {str(e)}"],
                        )
                    )
            
            return results
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            # Return minimal results with errors
            return [
                ExtractionResult(
                    document_id=doc.id,
                    document_type=doc.type,
                    confidence=0.0,
                    requires_human_review=True,
                    errors=[f"Batch processing error: {str(e)}"],
                )
                for doc in documents
            ]
    
    async def get_processor_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics from all processors.
        
        Returns:
            List of processor statistics
        """
        if not self.initialized:
            return []
        
        stats_refs = [processor.get_stats.remote() for processor in self.processors]
        return await asyncio.to_thread(ray.get, stats_refs)


# Singleton instance for easy access
ray_processor = RayProcessor()