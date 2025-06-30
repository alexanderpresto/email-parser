"""Tests for DOCX document chunking."""

import pytest
from unittest.mock import Mock, patch

from email_parser.converters.docx.chunking import (
    ChunkingStrategy,
    DocumentChunk,
    TokenBasedChunker,
    SemanticChunker,
    HybridChunker,
    create_chunker
)


class TestDocumentChunk:
    """Test DocumentChunk dataclass."""
    
    def test_document_chunk_creation(self):
        """Test creating a document chunk."""
        chunk = DocumentChunk(
            chunk_id=0,
            content="Test content",
            token_count=100,
            start_index=0,
            end_index=10,
            metadata={"test": "value"}
        )
        
        assert chunk.chunk_id == 0
        assert chunk.content == "Test content"
        assert chunk.token_count == 100
        assert chunk.start_index == 0
        assert chunk.end_index == 10
        assert chunk.metadata == {"test": "value"}
        assert chunk.overlap_with_previous == 0
        assert chunk.overlap_with_next == 0


class TestTokenBasedChunker:
    """Test token-based chunking."""
    
    def test_empty_content(self):
        """Test chunking empty content."""
        chunker = TokenBasedChunker(max_tokens=100)
        chunks = chunker.chunk("")
        assert chunks == []
    
    def test_single_small_chunk(self):
        """Test content that fits in a single chunk."""
        chunker = TokenBasedChunker(max_tokens=100)
        content = "This is a small piece of content."
        chunks = chunker.chunk(content)
        
        assert len(chunks) == 1
        assert chunks[0].content == content
        assert chunks[0].chunk_id == 0
    
    def test_multiple_chunks(self):
        """Test content that requires multiple chunks."""
        chunker = TokenBasedChunker(max_tokens=30, overlap_tokens=10)
        
        # Create content with multiple lines - each line should be about 20 tokens
        lines = [f"This is line number {i} with some longer content that will require chunking" for i in range(10)]
        content = "\n".join(lines)
        
        chunks = chunker.chunk(content)
        
        assert len(chunks) > 1
        # Check chunks have unique IDs
        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))
        
        # Verify all content is present
        all_content = ' '.join(c.content for c in chunks)
        assert "This is line number 0" in all_content
        assert "This is line number 9" in all_content
    
    @patch('email_parser.converters.docx.chunking.tiktoken')
    def test_with_tiktoken(self, mock_tiktoken):
        """Test token counting with tiktoken."""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_tiktoken.get_encoding.return_value = mock_encoding
        
        chunker = TokenBasedChunker(max_tokens=10)
        count = chunker.count_tokens("test text")
        
        assert count == 5
        mock_encoding.encode.assert_called_once_with("test text")
    
    def test_without_tiktoken(self):
        """Test token counting fallback without tiktoken."""
        with patch('email_parser.converters.docx.chunking.tiktoken', None):
            chunker = TokenBasedChunker()
            # Fallback uses 1 token per 4 characters
            count = chunker.count_tokens("12345678")  # 8 characters
            assert count == 2


class TestSemanticChunker:
    """Test semantic chunking."""
    
    def test_empty_content(self):
        """Test chunking empty content."""
        chunker = SemanticChunker()
        chunks = chunker.chunk("")
        assert chunks == []
    
    def test_markdown_sections(self):
        """Test chunking with markdown sections."""
        content = """# Section 1
This is section 1 content.

## Subsection 1.1
Content for subsection.

# Section 2
This is section 2 content.

## Subsection 2.1
More content here."""
        
        chunker = SemanticChunker(max_tokens=1000)
        chunks = chunker.chunk(content)
        
        assert len(chunks) >= 1
        # Check that sections are preserved in metadata
        for chunk in chunks:
            assert 'section_count' in chunk.metadata or 'section_title' in chunk.metadata
    
    def test_large_section_splitting(self):
        """Test splitting of sections that exceed max tokens."""
        # Create a large section
        large_content = "# Large Section\n" + ("word " * 1000 + "\n") * 10
        
        chunker = SemanticChunker(max_tokens=100)
        chunks = chunker.chunk(large_content)
        
        assert len(chunks) > 1
        # Check that metadata includes section info
        assert all('section_title' in c.metadata or 'section_count' in c.metadata 
                  for c in chunks)
    
    def test_section_identification(self):
        """Test identification of markdown sections."""
        lines = [
            "# Main Title",
            "Introduction text",
            "## Subsection",
            "Subsection content",
            "### Sub-subsection",
            "More content"
        ]
        
        chunker = SemanticChunker()
        sections = chunker._identify_sections(lines)
        
        assert len(sections) == 3
        assert sections[0]['title'] == "Main Title"
        assert sections[0]['level'] == 1
        assert sections[1]['title'] == "Subsection"
        assert sections[1]['level'] == 2
        assert sections[2]['title'] == "Sub-subsection"
        assert sections[2]['level'] == 3


class TestHybridChunker:
    """Test hybrid chunking strategy."""
    
    def test_uses_semantic_when_appropriate(self):
        """Test that hybrid chunker uses semantic chunking for structured content."""
        content = """# Section 1
Content for section 1.

# Section 2
Content for section 2.

# Section 3
Content for section 3."""
        
        chunker = HybridChunker(max_tokens=100)
        chunks = chunker.chunk(content)
        
        # Should produce multiple chunks if semantic chunking works
        assert len(chunks) >= 1
    
    def test_falls_back_to_token_based(self):
        """Test fallback to token-based chunking for unstructured content."""
        # Content without clear structure
        content = "word " * 500  # Long unstructured text
        
        chunker = HybridChunker(max_tokens=50)
        chunks = chunker.chunk(content)
        
        assert len(chunks) > 1


class TestChunkerFactory:
    """Test chunker factory function."""
    
    def test_create_token_chunker(self):
        """Test creating token-based chunker."""
        chunker = create_chunker(ChunkingStrategy.TOKEN)
        assert isinstance(chunker, TokenBasedChunker)
    
    def test_create_semantic_chunker(self):
        """Test creating semantic chunker."""
        chunker = create_chunker(ChunkingStrategy.SEMANTIC)
        assert isinstance(chunker, SemanticChunker)
    
    def test_create_hybrid_chunker(self):
        """Test creating hybrid chunker."""
        chunker = create_chunker(ChunkingStrategy.HYBRID)
        assert isinstance(chunker, HybridChunker)
    
    def test_custom_parameters(self):
        """Test creating chunker with custom parameters."""
        chunker = create_chunker(
            ChunkingStrategy.TOKEN,
            max_tokens=500,
            overlap_tokens=50
        )
        assert chunker.max_tokens == 500
        assert chunker.overlap_tokens == 50
    
    def test_invalid_strategy(self):
        """Test error handling for invalid strategy."""
        with pytest.raises(ValueError, match="Unknown chunking strategy"):
            create_chunker("invalid_strategy")