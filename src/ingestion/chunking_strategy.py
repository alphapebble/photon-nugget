"""
Chunking Strategy Pattern for Solar Sage RAG system.

This module implements the Strategy Pattern for document chunking,
allowing flexible and interchangeable chunking algorithms.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import re
import os
from datetime import datetime


class ChunkingStrategy(ABC):
    """Abstract base class for document chunking strategies."""

    @abstractmethod
    def chunk_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Split a document into chunks according to the strategy.

        Args:
            text: The document text to chunk
            metadata: Optional metadata about the document

        Returns:
            List of chunks, each containing text and metadata
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the chunking strategy."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the chunking strategy."""
        pass


class WordCountChunking(ChunkingStrategy):
    """Chunk documents based on word count."""

    def __init__(self, chunk_size: int = 300, overlap: int = 0):
        """
        Initialize word count chunking strategy.

        Args:
            chunk_size: Number of words per chunk
            overlap: Number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split document into chunks of specified word count."""
        # Clean text
        text = re.sub(r"\s+", " ", text).strip()
        words = text.split()

        # Create chunks with overlap
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            if not chunk_words:
                continue

            # Create chunk with text and metadata
            chunk_text = " ".join(chunk_words)
            chunk_metadata = {
                "start_idx": i,
                "end_idx": i + len(chunk_words),
                "chunk_type": "word_count",
                "word_count": len(chunk_words)
            }

            # Add original document metadata
            if metadata:
                chunk_metadata.update({f"doc_{k}": v for k, v in metadata.items()})

            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })

        return chunks

    @property
    def name(self) -> str:
        return f"word_count_{self.chunk_size}_{self.overlap}"

    @property
    def description(self) -> str:
        return f"Word count chunking with {self.chunk_size} words per chunk and {self.overlap} words overlap"


class SemanticChunking(ChunkingStrategy):
    """Chunk documents based on semantic boundaries like paragraphs and sections."""

    def __init__(self, max_chunk_size: int = 500, min_chunk_size: int = 100):
        """
        Initialize semantic chunking strategy.

        Args:
            max_chunk_size: Maximum words per chunk
            min_chunk_size: Minimum words per chunk
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split document into chunks based on semantic boundaries."""
        # Split by paragraphs first
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

        chunks = []
        current_chunk = []
        current_word_count = 0

        for para in paragraphs:
            para_word_count = len(para.split())

            # If adding this paragraph exceeds max size and we already have content,
            # finish the current chunk
            if current_word_count + para_word_count > self.max_chunk_size and current_word_count >= self.min_chunk_size:
                chunk_text = " ".join(current_chunk)
                chunk_metadata = {
                    "chunk_type": "semantic",
                    "word_count": current_word_count
                }

                # Add original document metadata
                if metadata:
                    chunk_metadata.update({f"doc_{k}": v for k, v in metadata.items()})

                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })

                current_chunk = []
                current_word_count = 0

            # Add paragraph to current chunk
            current_chunk.append(para)
            current_word_count += para_word_count

        # Add the last chunk if it has content
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_metadata = {
                "chunk_type": "semantic",
                "word_count": current_word_count
            }

            # Add original document metadata
            if metadata:
                chunk_metadata.update({f"doc_{k}": v for k, v in metadata.items()})

            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })

        return chunks

    @property
    def name(self) -> str:
        return f"semantic_{self.min_chunk_size}_{self.max_chunk_size}"

    @property
    def description(self) -> str:
        return f"Semantic chunking with min {self.min_chunk_size} and max {self.max_chunk_size} words per chunk"


class SlidingWindowChunking(ChunkingStrategy):
    """Chunk documents using a sliding window approach with significant overlap."""

    def __init__(self, window_size: int = 300, stride: int = 150):
        """
        Initialize sliding window chunking strategy.

        Args:
            window_size: Size of the window in words
            stride: Number of words to slide the window
        """
        self.window_size = window_size
        self.stride = stride

    def chunk_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split document using a sliding window approach."""
        # Clean text
        text = re.sub(r"\s+", " ", text).strip()
        words = text.split()

        chunks = []
        for i in range(0, len(words), self.stride):
            window_words = words[i:i + self.window_size]
            if len(window_words) < self.stride:  # Skip very small final chunks
                continue

            # Create chunk with text and metadata
            chunk_text = " ".join(window_words)
            chunk_metadata = {
                "start_idx": i,
                "end_idx": i + len(window_words),
                "chunk_type": "sliding_window",
                "word_count": len(window_words)
            }

            # Add original document metadata
            if metadata:
                chunk_metadata.update({f"doc_{k}": v for k, v in metadata.items()})

            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })

        return chunks

    @property
    def name(self) -> str:
        return f"sliding_window_{self.window_size}_{self.stride}"

    @property
    def description(self) -> str:
        return f"Sliding window chunking with {self.window_size} window size and {self.stride} stride"


class DocumentChunker:
    """Context class that uses a chunking strategy to process documents."""

    def __init__(self, strategy: ChunkingStrategy):
        """
        Initialize with a chunking strategy.

        Args:
            strategy: The chunking strategy to use
        """
        self.strategy = strategy

    def set_strategy(self, strategy: ChunkingStrategy):
        """
        Change the chunking strategy.

        Args:
            strategy: The new chunking strategy to use
        """
        self.strategy = strategy

    def chunk_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process a document using the current strategy.

        Args:
            text: The document text to chunk
            metadata: Optional metadata about the document

        Returns:
            List of chunks according to the current strategy
        """
        return self.strategy.chunk_document(text, metadata)


class ChunkingStrategyFactory:
    """Factory for creating chunking strategies."""

    _strategies = {}

    @classmethod
    def register_strategy(cls, strategy_class, *args, **kwargs):
        """
        Register a chunking strategy.

        Args:
            strategy_class: The strategy class to register
            *args, **kwargs: Arguments to pass to the strategy constructor
        """
        strategy = strategy_class(*args, **kwargs)
        cls._strategies[strategy.name] = strategy
        return strategy

    @classmethod
    def get_strategy(cls, name: str) -> ChunkingStrategy:
        """
        Get a registered strategy by name.

        Args:
            name: Name of the strategy

        Returns:
            The requested strategy

        Raises:
            ValueError: If strategy not found
        """
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not found")
        return cls._strategies[name]

    @classmethod
    def list_strategies(cls) -> List[str]:
        """List all registered strategies."""
        return list(cls._strategies.keys())

    @classmethod
    def register_defaults(cls):
        """Register default chunking strategies."""
        cls.register_strategy(WordCountChunking, chunk_size=300, overlap=0)
        cls.register_strategy(WordCountChunking, chunk_size=500, overlap=50)
        cls.register_strategy(SemanticChunking, max_chunk_size=500, min_chunk_size=100)
        cls.register_strategy(SlidingWindowChunking, window_size=300, stride=150)
