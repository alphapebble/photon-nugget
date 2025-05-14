"""
Enhanced ingestion pipeline with configurable chunking strategies.

This module extends the standard ingestion pipeline with support for
different document chunking strategies using the Strategy Pattern.
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from ingestion.chunking_strategy import (
    ChunkingStrategy,
    ChunkingStrategyFactory,
    DocumentChunker
)
from ingestion.pipeline import (
    extract_text_from_pdf,
    fetch_pdf,
    is_valid_pdf,
    embed_and_store
)


def embed_and_store_with_metadata(
    texts: List[str],
    metadatas: List[Dict[str, Any]],
    db_path: str,
    table_name: str,
    model_name: str
) -> bool:
    """
    Embed texts and store them with metadata in the vector database.
    
    Args:
        texts: List of text chunks to embed
        metadatas: List of metadata dictionaries for each chunk
        db_path: LanceDB storage path
        table_name: LanceDB table name
        model_name: Embedding model name
        
    Returns:
        Success status
    """
    # Convert metadata to strings for storage
    string_metadatas = []
    for metadata in metadatas:
        string_metadata = {}
        for k, v in metadata.items():
            string_metadata[k] = str(v)
        string_metadatas.append(string_metadata)
    
    # Use the existing embed_and_store function with metadata
    return embed_and_store(texts, db_path, table_name, model_name, string_metadatas)


def run_pipeline(
    source: str, 
    db_path: str, 
    table_name: str, 
    model_name: str,
    chunking_strategy: str = "word_count_300_0"  # Default to current behavior
) -> bool:
    """
    Runs the full ingestion pipeline with configurable chunking strategy.
    
    Args:
        source: Source document path or URL
        db_path: LanceDB storage path
        table_name: LanceDB table name
        model_name: Embedding model name
        chunking_strategy: Name of chunking strategy to use
        
    Returns:
        Success status
    """
    # Download if needed
    if source.startswith("http://") or source.startswith("https://"):
        source = fetch_pdf(source)
        if not source:
            return False

    # Validate source
    if not os.path.exists(source) or not is_valid_pdf(source):
        print(f"[ERROR] File not found or not a valid PDF: {source}")
        return False

    # Extract text
    print(f"Extracting text from {source}")
    text = extract_text_from_pdf(source)
    
    # Get document metadata
    metadata = {
        "source": source,
        "filename": os.path.basename(source),
        "ingestion_time": datetime.now().isoformat()
    }
    
    # Initialize chunking strategy
    try:
        # Register defaults if this is the first run
        if not ChunkingStrategyFactory.list_strategies():
            ChunkingStrategyFactory.register_defaults()
            
        strategy = ChunkingStrategyFactory.get_strategy(chunking_strategy)
    except ValueError:
        print(f"[WARNING] Strategy '{chunking_strategy}' not found, using default")
        ChunkingStrategyFactory.register_defaults()
        strategy = ChunkingStrategyFactory.get_strategy("word_count_300_0")
    
    chunker = DocumentChunker(strategy)
    
    # Chunk document
    print(f"Chunking document using strategy: {strategy.description}")
    chunks = chunker.chunk_document(text, metadata)
    
    if not chunks:
        print("[WARNING] No valid text chunks extracted.")
        return False
    
    # Extract text from chunks for embedding
    chunk_texts = [chunk["text"] for chunk in chunks]
    chunk_metadatas = [chunk["metadata"] for chunk in chunks]
    
    # Embed and store
    print(f"Embedding and storing {len(chunk_texts)} chunks")
    success = embed_and_store_with_metadata(
        chunk_texts, 
        chunk_metadatas, 
        db_path, 
        table_name, 
        model_name
    )
    
    if success:
        print(f"Successfully ingested {source} using {strategy.description}")
    else:
        print(f"Failed to ingest {source}")
        
    return success


def list_available_strategies() -> List[str]:
    """
    List all available chunking strategies.
    
    Returns:
        List of strategy names
    """
    # Register defaults if this is the first run
    if not ChunkingStrategyFactory.list_strategies():
        ChunkingStrategyFactory.register_defaults()
        
    return ChunkingStrategyFactory.list_strategies()


def register_custom_strategy(
    strategy_type: str,
    **kwargs
) -> str:
    """
    Register a custom chunking strategy.
    
    Args:
        strategy_type: Type of strategy ("word_count", "semantic", "sliding_window")
        **kwargs: Parameters for the strategy
        
    Returns:
        Name of the registered strategy
        
    Raises:
        ValueError: If strategy type is invalid
    """
    # Register defaults if this is the first run
    if not ChunkingStrategyFactory.list_strategies():
        ChunkingStrategyFactory.register_defaults()
    
    if strategy_type == "word_count":
        from ingestion.chunking_strategy import WordCountChunking
        strategy = ChunkingStrategyFactory.register_strategy(
            WordCountChunking,
            chunk_size=kwargs.get("chunk_size", 300),
            overlap=kwargs.get("overlap", 0)
        )
    elif strategy_type == "semantic":
        from ingestion.chunking_strategy import SemanticChunking
        strategy = ChunkingStrategyFactory.register_strategy(
            SemanticChunking,
            max_chunk_size=kwargs.get("max_chunk_size", 500),
            min_chunk_size=kwargs.get("min_chunk_size", 100)
        )
    elif strategy_type == "sliding_window":
        from ingestion.chunking_strategy import SlidingWindowChunking
        strategy = ChunkingStrategyFactory.register_strategy(
            SlidingWindowChunking,
            window_size=kwargs.get("window_size", 300),
            stride=kwargs.get("stride", 150)
        )
    else:
        raise ValueError(f"Invalid strategy type: {strategy_type}")
    
    return strategy.name
