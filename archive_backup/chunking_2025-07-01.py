"""AI-ready document chunking for DOCX files."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

try:
    import tiktoken
except ImportError:
    tiktoken = None
    logging.warning("tiktoken not installed. Token counting will use approximation.")


class ChunkingStrategy(Enum):
    """Available chunking strategies."""
    TOKEN = "token"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass
class DocumentChunk:
    """Represents a single chunk of document content."""
    chunk_id: int
    content: str
    token_count: int
    start_index: int
    end_index: int
    metadata: Dict[str, Any]
    overlap_with_previous: int = 0
    overlap_with_next: int = 0


class BaseChunker(ABC):
    """Abstract base class for document chunking strategies."""
    
    def __init__(self, max_tokens: int = 2000, overlap_tokens: int = 200):
        """Initialize chunker with configuration."""
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.logger = logging.getLogger(__name__)
        
        # Initialize tokenizer
        self.encoding = None
        if tiktoken:
            try:
                self.encoding = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                self.logger.warning(f"Failed to initialize tiktoken: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken or approximation."""
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                self.logger.warning(f"Token counting failed: {e}")
        
        # Fallback: approximate 1 token per 4 characters
        return len(text) // 4
    
    @abstractmethod
    def chunk(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Split content into chunks."""
        pass


class TokenBasedChunker(BaseChunker):
    """Simple token-based chunking with overlap."""
    
    def chunk(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Split content into token-based chunks."""
        if not content:
            return []
        
        chunks = []
        # Handle single-line content differently
        if '\n' not in content:
            # Split by words for single-line content
            words = content.split()
            current_chunk = []
            current_tokens = 0
            chunk_start_index = 0
            chunk_id = 0
            
            for i, word in enumerate(words):
                word_tokens = self.count_tokens(word + ' ')
                
                if current_tokens + word_tokens > self.max_tokens and current_chunk:
                    # Create chunk
                    chunk_content = ' '.join(current_chunk)
                    chunk = DocumentChunk(
                        chunk_id=chunk_id,
                        content=chunk_content,
                        token_count=current_tokens,
                        start_index=chunk_start_index,
                        end_index=i - 1,
                        metadata=metadata or {}
                    )
                    chunks.append(chunk)
                    
                    # Calculate overlap
                    overlap_words = []
                    overlap_tokens = 0
                    for j in range(len(current_chunk) - 1, -1, -1):
                        word_token_count = self.count_tokens(current_chunk[j] + ' ')
                        if overlap_tokens + word_token_count <= self.overlap_tokens:
                            overlap_words.insert(0, current_chunk[j])
                            overlap_tokens += word_token_count
                        else:
                            break
                    
                    # Update overlap info
                    if chunks and overlap_tokens > 0:
                        chunks[-1].overlap_with_next = overlap_tokens
                    
                    # Start new chunk with overlap
                    current_chunk = overlap_words + [word]
                    current_tokens = overlap_tokens + word_tokens
                    chunk_start_index = i - len(overlap_words)
                    chunk_id += 1
                else:
                    current_chunk.append(word)
                    current_tokens += word_tokens
            
            # Handle remaining content
            if current_chunk:
                chunk_content = ' '.join(current_chunk)
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    token_count=current_tokens,
                    start_index=chunk_start_index,
                    end_index=len(words) - 1,
                    metadata=metadata or {}
                )
                chunks.append(chunk)
        else:
            # Multi-line content
            lines = content.split('\n')
            current_chunk = []
            current_tokens = 0
            chunk_start_index = 0
            chunk_id = 0
            
            for i, line in enumerate(lines):
                line_tokens = self.count_tokens(line + '\n')
                
                # Check if adding this line would exceed max tokens
                if current_tokens + line_tokens > self.max_tokens and current_chunk:
                    # Create chunk
                    chunk_content = '\n'.join(current_chunk)
                    chunk = DocumentChunk(
                        chunk_id=chunk_id,
                        content=chunk_content,
                        token_count=current_tokens,
                        start_index=chunk_start_index,
                        end_index=i - 1,
                        metadata=metadata or {}
                    )
                    chunks.append(chunk)
                    
                    # Calculate overlap
                    overlap_lines = []
                    overlap_tokens = 0
                    for j in range(len(current_chunk) - 1, -1, -1):
                        line_token_count = self.count_tokens(current_chunk[j] + '\n')
                        if overlap_tokens + line_token_count <= self.overlap_tokens:
                            overlap_lines.insert(0, current_chunk[j])
                            overlap_tokens += line_token_count
                        else:
                            break
                    
                    # Update overlap info
                    if chunks and overlap_tokens > 0:
                        chunks[-1].overlap_with_next = overlap_tokens
                    
                    # Start new chunk with overlap
                    current_chunk = overlap_lines + [line]
                    current_tokens = overlap_tokens + line_tokens
                    chunk_start_index = i - len(overlap_lines)
                    chunk_id += 1
                else:
                    current_chunk.append(line)
                    current_tokens += line_tokens
            
            # Handle remaining content
            if current_chunk:
                chunk_content = '\n'.join(current_chunk)
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    token_count=current_tokens,
                    start_index=chunk_start_index,
                    end_index=len(lines) - 1,
                    metadata=metadata or {}
                )
                chunks.append(chunk)
        
        # Update overlap information
        for i in range(1, len(chunks)):
            if i < len(chunks) and chunks[i-1].overlap_with_next > 0:
                chunks[i].overlap_with_previous = chunks[i-1].overlap_with_next
        
        return chunks


class SemanticChunker(BaseChunker):
    """Semantic chunking that preserves document structure."""
    
    def __init__(self, max_tokens: int = 2000, overlap_tokens: int = 200):
        super().__init__(max_tokens, overlap_tokens)
        self.section_markers = ['#', '##', '###', '####', '#####', '######']
    
    def _identify_sections(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Identify document sections based on markdown headings."""
        sections = []
        current_section = {'start': 0, 'end': 0, 'level': 0, 'title': '', 'content': []}
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check for markdown heading
            is_heading = False
            for level, marker in enumerate(self.section_markers, 1):
                if stripped.startswith(marker + ' '):
                    is_heading = True
                    
                    # Save previous section
                    if current_section['content']:
                        current_section['end'] = i - 1
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        'start': i,
                        'end': i,
                        'level': level,
                        'title': stripped[len(marker):].strip(),
                        'content': [line]
                    }
                    break
            
            if not is_heading and i > 0:
                current_section['content'].append(line)
        
        # Save last section
        if current_section['content']:
            current_section['end'] = len(lines) - 1
            sections.append(current_section)
        
        return sections
    
    def chunk(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Split content into semantic chunks based on document structure."""
        if not content:
            return []
        
        lines = content.split('\n')
        sections = self._identify_sections(lines)
        chunks = []
        chunk_id = 0
        
        # Group sections into chunks
        current_chunk_sections = []
        current_tokens = 0
        
        for section in sections:
            section_content = '\n'.join(section['content'])
            section_tokens = self.count_tokens(section_content)
            
            # Check if section alone exceeds max tokens
            if section_tokens > self.max_tokens:
                # First, save any accumulated sections
                if current_chunk_sections:
                    chunk_content = '\n'.join(['\n'.join(s['content']) for s in current_chunk_sections])
                    chunk = DocumentChunk(
                        chunk_id=chunk_id,
                        content=chunk_content,
                        token_count=current_tokens,
                        start_index=current_chunk_sections[0]['start'],
                        end_index=current_chunk_sections[-1]['end'],
                        metadata={**(metadata or {}), 'section_count': len(current_chunk_sections)}
                    )
                    chunks.append(chunk)
                    chunk_id += 1
                    current_chunk_sections = []
                    current_tokens = 0
                
                # Split large section using token-based approach
                token_chunker = TokenBasedChunker(self.max_tokens, self.overlap_tokens)
                section_chunks = token_chunker.chunk(section_content, 
                    {**(metadata or {}), 'section_title': section['title'], 'section_level': section['level']})
                
                for sc in section_chunks:
                    sc.chunk_id = chunk_id
                    sc.start_index += section['start']
                    sc.end_index = min(sc.end_index + section['start'], section['end'])
                    chunks.append(sc)
                    chunk_id += 1
            
            elif current_tokens + section_tokens > self.max_tokens and current_chunk_sections:
                # Create chunk from accumulated sections
                chunk_content = '\n'.join(['\n'.join(s['content']) for s in current_chunk_sections])
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    token_count=current_tokens,
                    start_index=current_chunk_sections[0]['start'],
                    end_index=current_chunk_sections[-1]['end'],
                    metadata={**(metadata or {}), 'section_count': len(current_chunk_sections)}
                )
                chunks.append(chunk)
                chunk_id += 1
                
                # Start new chunk with current section
                current_chunk_sections = [section]
                current_tokens = section_tokens
            else:
                # Add section to current chunk
                current_chunk_sections.append(section)
                current_tokens += section_tokens
        
        # Handle remaining sections
        if current_chunk_sections:
            chunk_content = '\n'.join(['\n'.join(s['content']) for s in current_chunk_sections])
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                token_count=current_tokens,
                start_index=current_chunk_sections[0]['start'],
                end_index=current_chunk_sections[-1]['end'],
                metadata={**(metadata or {}), 'section_count': len(current_chunk_sections)}
            )
            chunks.append(chunk)
        
        return chunks


class HybridChunker(BaseChunker):
    """Hybrid chunking combining semantic and token-based approaches."""
    
    def __init__(self, max_tokens: int = 2000, overlap_tokens: int = 200):
        super().__init__(max_tokens, overlap_tokens)
        self.semantic_chunker = SemanticChunker(max_tokens, overlap_tokens)
        self.token_chunker = TokenBasedChunker(max_tokens, overlap_tokens)
    
    def chunk(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Apply hybrid chunking strategy."""
        if not content:
            return []
        
        # First, try semantic chunking
        semantic_chunks = self.semantic_chunker.chunk(content, metadata)
        
        # If semantic chunking produces reasonable results, use it
        if semantic_chunks and len(semantic_chunks) > 1:
            return semantic_chunks
        
        # Otherwise, fall back to token-based chunking
        return self.token_chunker.chunk(content, metadata)


def create_chunker(strategy: ChunkingStrategy, max_tokens: int = 2000, 
                  overlap_tokens: int = 200) -> BaseChunker:
    """Factory function to create appropriate chunker."""
    if strategy == ChunkingStrategy.TOKEN:
        return TokenBasedChunker(max_tokens, overlap_tokens)
    elif strategy == ChunkingStrategy.SEMANTIC:
        return SemanticChunker(max_tokens, overlap_tokens)
    elif strategy == ChunkingStrategy.HYBRID:
        return HybridChunker(max_tokens, overlap_tokens)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")