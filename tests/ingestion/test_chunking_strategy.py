"""
Tests for the chunking strategy pattern.
"""
import unittest
from ingestion.chunking_strategy import (
    ChunkingStrategy,
    WordCountChunking,
    SemanticChunking,
    SlidingWindowChunking,
    DocumentChunker,
    ChunkingStrategyFactory
)


class TestChunkingStrategy(unittest.TestCase):
    """Test cases for chunking strategies."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_text = """
        This is a sample document for testing chunking strategies.
        It contains multiple paragraphs that can be used to test different approaches.
        
        This is the second paragraph with some additional text.
        We want to make sure that semantic chunking respects paragraph boundaries.
        
        Here is a third paragraph that adds more content to test with.
        The more content we have, the better we can test the chunking strategies.
        This should give us enough text to create multiple chunks.
        """
        
        self.sample_metadata = {
            "source": "test_document.pdf",
            "author": "Test Author",
            "date": "2023-01-01"
        }
    
    def test_word_count_chunking(self):
        """Test word count chunking strategy."""
        # Create strategy with small chunk size for testing
        strategy = WordCountChunking(chunk_size=10, overlap=0)
        
        # Chunk document
        chunks = strategy.chunk_document(self.sample_text, self.sample_metadata)
        
        # Verify results
        self.assertGreater(len(chunks), 1, "Should create multiple chunks")
        
        # Check chunk size
        for chunk in chunks:
            words = chunk["text"].split()
            self.assertLessEqual(len(words), 10, "Chunk should not exceed max size")
            
        # Check metadata
        for chunk in chunks:
            self.assertEqual(chunk["metadata"]["doc_source"], "test_document.pdf")
            self.assertEqual(chunk["metadata"]["chunk_type"], "word_count")
    
    def test_word_count_with_overlap(self):
        """Test word count chunking with overlap."""
        strategy = WordCountChunking(chunk_size=10, overlap=3)
        chunks = strategy.chunk_document(self.sample_text, self.sample_metadata)
        
        # With overlap, we should have more chunks than without
        no_overlap_strategy = WordCountChunking(chunk_size=10, overlap=0)
        no_overlap_chunks = no_overlap_strategy.chunk_document(self.sample_text, self.sample_metadata)
        
        self.assertGreater(len(chunks), len(no_overlap_chunks), 
                          "Overlapping chunks should create more chunks")
    
    def test_semantic_chunking(self):
        """Test semantic chunking strategy."""
        strategy = SemanticChunking(max_chunk_size=50, min_chunk_size=10)
        chunks = strategy.chunk_document(self.sample_text, self.sample_metadata)
        
        # Verify results
        self.assertGreater(len(chunks), 0, "Should create at least one chunk")
        
        # Check metadata
        for chunk in chunks:
            self.assertEqual(chunk["metadata"]["doc_source"], "test_document.pdf")
            self.assertEqual(chunk["metadata"]["chunk_type"], "semantic")
    
    def test_sliding_window_chunking(self):
        """Test sliding window chunking strategy."""
        strategy = SlidingWindowChunking(window_size=15, stride=5)
        chunks = strategy.chunk_document(self.sample_text, self.sample_metadata)
        
        # Verify results
        self.assertGreater(len(chunks), 1, "Should create multiple chunks")
        
        # Check window size
        for chunk in chunks:
            words = chunk["text"].split()
            self.assertLessEqual(len(words), 15, "Chunk should not exceed window size")
            
        # Check metadata
        for chunk in chunks:
            self.assertEqual(chunk["metadata"]["doc_source"], "test_document.pdf")
            self.assertEqual(chunk["metadata"]["chunk_type"], "sliding_window")
    
    def test_document_chunker(self):
        """Test document chunker context class."""
        strategy1 = WordCountChunking(chunk_size=10)
        strategy2 = SemanticChunking(max_chunk_size=50)
        
        chunker = DocumentChunker(strategy1)
        chunks1 = chunker.chunk_document(self.sample_text, self.sample_metadata)
        
        chunker.set_strategy(strategy2)
        chunks2 = chunker.chunk_document(self.sample_text, self.sample_metadata)
        
        # Verify that different strategies produce different results
        self.assertNotEqual(len(chunks1), len(chunks2), 
                           "Different strategies should produce different chunking")
    
    def test_strategy_factory(self):
        """Test chunking strategy factory."""
        # Register default strategies
        ChunkingStrategyFactory.register_defaults()
        
        # Get strategies
        strategy1 = ChunkingStrategyFactory.get_strategy("word_count_300_0")
        strategy2 = ChunkingStrategyFactory.get_strategy("semantic_100_500")
        
        self.assertIsInstance(strategy1, WordCountChunking)
        self.assertIsInstance(strategy2, SemanticChunking)
        
        # List strategies
        strategies = ChunkingStrategyFactory.list_strategies()
        self.assertGreater(len(strategies), 0, "Should have registered strategies")
        
        # Register custom strategy
        custom = ChunkingStrategyFactory.register_strategy(
            WordCountChunking, 
            chunk_size=42, 
            overlap=7
        )
        
        self.assertEqual(custom.name, "word_count_42_7")
        self.assertIn(custom.name, ChunkingStrategyFactory.list_strategies())


if __name__ == "__main__":
    unittest.main()
