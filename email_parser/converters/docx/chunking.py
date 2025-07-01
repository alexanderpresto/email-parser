"""AI-ready document chunking for DOCX files with performance optimizations."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from functools import lru_cache
import re

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
    
    @lru_cache(maxsize=1024)
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken or approximation with caching."""
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
    """Optimized token-based chunking with sliding window approach."""
    
    def __init__(self, max_tokens: int = 2000, overlap_tokens: int = 200):
        super().__init__(max_tokens, overlap_tokens)
        # Pre-compile regex for word splitting
        self.word_splitter = re.compile(r'\s+')
    
    def _create_sliding_windows(self, tokens: List[Tuple[str, int]], 
                               token_counts: List[int]) -> List[Tuple[int, int, int]]:
        """Create sliding windows with pre-computed boundaries.
        Returns list of (start_idx, end_idx, token_count) tuples."""
        windows = []
        n = len(tokens)
        
        i = 0
        while i < n:
            # Find window end
            current_tokens = 0
            j = i
            
            while j < n and current_tokens + token_counts[j] <= self.max_tokens:
                current_tokens += token_counts[j]
                j += 1
            
            # If no progress made, include at least one token
            if j == i and j < n:
                j = i + 1
                current_tokens = token_counts[i]
            
            windows.append((i, j, current_tokens))
            
            # Calculate overlap start for next window
            overlap_tokens = 0
            overlap_start = j
            
            # Prevent infinite loop - ensure we make progress
            for k in range(j - 1, i, -1):
                if overlap_tokens + token_counts[k] <= self.overlap_tokens:
                    overlap_start = k
                    overlap_tokens += token_counts[k]
                else:
                    break
            
            # Ensure we advance to avoid infinite loop
            i = max(overlap_start, i + 1) if overlap_start < j else j
        
        return windows
    
    def chunk(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Split content into token-based chunks with optimized sliding window."""
        if not content:
            return []
        
        chunks = []
        
        # Handle single-line content differently
        if '\n' not in content:
            # Split by words for single-line content
            words = self.word_splitter.split(content.strip())
            if not words:
                return []
            
            # Pre-compute token counts
            token_counts = [self.count_tokens(word + ' ') for word in words]
            tokens = list(zip(words, token_counts))
            
            # Create sliding windows
            windows = self._create_sliding_windows(tokens, token_counts)
            
            # Create chunks from windows
            for chunk_id, (start, end, token_count) in enumerate(windows):
                chunk_words = [tokens[i][0] for i in range(start, end)]
                chunk_content = ' '.join(chunk_words)
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    token_count=token_count,
                    start_index=start,
                    end_index=end - 1,
                    metadata=metadata or {},
                    overlap_with_previous=0 if chunk_id == 0 else self.overlap_tokens,
                    overlap_with_next=self.overlap_tokens if chunk_id < len(windows) - 1 else 0
                )
                chunks.append(chunk)
        else:
            # Multi-line content - use similar sliding window approach
            lines = content.split('\n')
            if not lines:
                return []
            
            # Pre-compute token counts for all lines
            token_counts = [self.count_tokens(line + '\n') for line in lines]
            tokens = list(zip(lines, token_counts))
            
            # Create sliding windows
            windows = self._create_sliding_windows(tokens, token_counts)
            
            # Create chunks from windows
            for chunk_id, (start, end, token_count) in enumerate(windows):
                chunk_lines = [tokens[i][0] for i in range(start, end)]
                chunk_content = '\n'.join(chunk_lines)
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    token_count=token_count,
                    start_index=start,
                    end_index=end - 1,
                    metadata=metadata or {},
                    overlap_with_previous=0 if chunk_id == 0 else self.overlap_tokens,
                    overlap_with_next=self.overlap_tokens if chunk_id < len(windows) - 1 else 0
                )
                chunks.append(chunk)
        
        return chunks


class SemanticChunker(BaseChunker):
    """Optimized semantic chunking with paragraph-level caching."""
    
    def __init__(self, max_tokens: int = 2000, overlap_tokens: int = 200):
        super().__init__(max_tokens, overlap_tokens)
        self.section_markers = ['#', '##', '###', '####', '#####', '######']
        # Pre-compile regex for heading detection
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        # Cache for section content tokens
        self._section_token_cache = {}
    
    def _identify_sections(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Identify document sections with optimized heading detection."""
        sections = []
        current_section = {'start': 0, 'end': 0, 'level': 0, 'title': '', 'content': [], 'tokens': 0}
        
        for i, line in enumerate(lines):
            # Use regex for faster heading detection
            match = self.heading_pattern.match(line.strip())
            
            if match:
                # Save previous section
                if current_section['content']:
                    current_section['end'] = i - 1
                    # Cache token count
                    section_key = (current_section['start'], current_section['end'])
                    if section_key not in self._section_token_cache:
                        content = '\n'.join(current_section['content'])
                        self._section_token_cache[section_key] = self.count_tokens(content)
                    current_section['tokens'] = self._section_token_cache[section_key]
                    sections.append(current_section)
                
                # Start new section
                marker, title = match.groups()
                current_section = {
                    'start': i,
                    'end': i,
                    'level': len(marker),
                    'title': title,
                    'content': [line],
                    'tokens': 0
                }
            else:
                current_section['content'].append(line)
        
        # Save last section
        if current_section['content']:
            current_section['end'] = len(lines) - 1
            section_key = (current_section['start'], current_section['end'])
            if section_key not in self._section_token_cache:
                content = '\n'.join(current_section['content'])
                self._section_token_cache[section_key] = self.count_tokens(content)
            current_section['tokens'] = self._section_token_cache[section_key]
            sections.append(current_section)
        
        return sections
    
    def chunk(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Split content into semantic chunks with optimized section handling."""
        if not content:
            return []
        
        lines = content.split('\n')
        sections = self._identify_sections(lines)
        chunks = []
        chunk_id = 0
        
        # Use cached token counts from sections
        current_chunk_sections = []
        current_tokens = 0
        
        # Create token-based chunker once for reuse
        token_chunker = TokenBasedChunker(self.max_tokens, self.overlap_tokens)
        
        for section in sections:
            section_tokens = section['tokens']  # Use pre-computed token count
            
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
                section_content = '\n'.join(section['content'])
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