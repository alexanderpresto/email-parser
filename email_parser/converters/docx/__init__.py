"""
DOCX processing modules for advanced document conversion.

This package provides comprehensive DOCX document processing capabilities including:
- AI-ready chunking for LLM processing
- Enhanced metadata extraction and analysis  
- Style preservation and conversion
- Advanced image extraction and handling

Week 2 Integration Complete - All features enabled by default.
"""

from .chunking import (
    ChunkingStrategy,
    DocumentChunk,
    TokenBasedChunker,
    SemanticChunker,
    HybridChunker,
    create_chunker
)

from .metadata_extractor import (
    DocumentMetadata,
    MetadataExtractor,
    PropertyAnalyzer
)

from .style_extractor import (
    StyleType,
    FontStyle,
    ParagraphStyle,
    StyleDefinition,
    DocumentStyles,
    StyleExtractor,
    StyleConverter
)

from .image_handler import (
    ImageInfo,
    ExtractedImage,
    ImageHandler,
    ImageManifest
)

__all__ = [
    # Chunking components
    "ChunkingStrategy",
    "DocumentChunk", 
    "TokenBasedChunker",
    "SemanticChunker",
    "HybridChunker",
    "create_chunker",
    
    # Metadata components
    "DocumentMetadata",
    "MetadataExtractor", 
    "PropertyAnalyzer",
    
    # Style components
    "StyleType",
    "FontStyle",
    "ParagraphStyle", 
    "StyleDefinition",
    "DocumentStyles",
    "StyleExtractor",
    "StyleConverter",
    
    # Image components
    "ImageInfo",
    "ExtractedImage",
    "ImageHandler",
    "ImageManifest"
]