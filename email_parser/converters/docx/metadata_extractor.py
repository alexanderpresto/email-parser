"""Enhanced metadata extraction for DOCX files."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

try:
    from docx import Document
except ImportError:
    Document = None
    logging.warning("python-docx not installed. Advanced metadata extraction will be limited.")


@dataclass
class DocumentMetadata:
    """Structured metadata from DOCX document."""
    # Core properties
    title: Optional[str] = None
    subject: Optional[str] = None
    author: Optional[str] = None
    keywords: Optional[str] = None
    description: Optional[str] = None
    last_modified_by: Optional[str] = None
    revision: Optional[int] = None
    version: Optional[str] = None
    
    # Dates
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    last_printed: Optional[datetime] = None
    
    # Document statistics
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    paragraph_count: Optional[int] = None
    page_count: Optional[int] = None
    line_count: Optional[int] = None
    table_count: Optional[int] = None
    image_count: Optional[int] = None
    
    # Extended properties
    category: Optional[str] = None
    content_status: Optional[str] = None
    language: Optional[str] = None
    company: Optional[str] = None
    manager: Optional[str] = None
    
    # Custom properties
    custom_properties: Optional[Dict[str, Any]] = None
    
    # Document structure
    has_track_changes: bool = False
    has_comments: bool = False
    protection_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling datetime serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


class MetadataExtractor:
    """Extract comprehensive metadata from DOCX files."""
    
    def __init__(self):
        """Initialize metadata extractor."""
        self.logger = logging.getLogger(__name__)
    
    def extract(self, file_path: Path) -> DocumentMetadata:
        """Extract all available metadata from DOCX file."""
        metadata = DocumentMetadata()
        
        if not Document:
            self.logger.warning("python-docx not available, using basic extraction")
            return self._extract_basic_metadata(file_path)
        
        try:
            doc = Document(str(file_path))
            
            # Extract core properties
            self._extract_core_properties(doc, metadata)
            
            # Extract document statistics
            self._extract_statistics(doc, metadata)
            
            # Extract extended properties
            self._extract_extended_properties(doc, metadata)
            
            # Extract custom properties
            self._extract_custom_properties(doc, metadata)
            
            # Check for track changes and comments
            self._check_document_features(doc, metadata)
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {e}")
            # Return partial metadata on error
        
        return metadata
    
    def _extract_basic_metadata(self, file_path: Path) -> DocumentMetadata:
        """Extract basic metadata without python-docx."""
        metadata = DocumentMetadata()
        
        # Basic file stats
        try:
            stat = file_path.stat()
            metadata.created = datetime.fromtimestamp(stat.st_ctime)
            metadata.modified = datetime.fromtimestamp(stat.st_mtime)
        except Exception as e:
            self.logger.warning(f"Could not get file stats: {e}")
        
        return metadata
    
    def _extract_core_properties(self, doc: Any, metadata: DocumentMetadata) -> None:
        """Extract core document properties."""
        try:
            core_props = doc.core_properties
            
            # Text properties
            metadata.title = core_props.title or None
            metadata.subject = core_props.subject or None
            metadata.author = core_props.author or None
            metadata.keywords = core_props.keywords or None
            metadata.description = core_props.comments or None
            metadata.last_modified_by = core_props.last_modified_by or None
            metadata.category = core_props.category or None
            metadata.content_status = core_props.content_status or None
            metadata.language = core_props.language or None
            metadata.version = core_props.version or None
            
            # Numeric properties
            if hasattr(core_props, 'revision') and core_props.revision:
                try:
                    metadata.revision = int(core_props.revision)
                except (ValueError, TypeError):
                    pass
            
            # Date properties
            metadata.created = core_props.created
            metadata.modified = core_props.modified
            metadata.last_printed = core_props.last_printed
            
        except Exception as e:
            self.logger.warning(f"Error extracting core properties: {e}")
    
    def _extract_statistics(self, doc: Any, metadata: DocumentMetadata) -> None:
        """Extract document statistics."""
        try:
            # Paragraph count
            metadata.paragraph_count = len(doc.paragraphs)
            
            # Table count
            metadata.table_count = len(doc.tables)
            
            # Word and character count (approximate)
            total_words = 0
            total_chars = 0
            
            for paragraph in doc.paragraphs:
                text = paragraph.text
                if text:
                    words = text.split()
                    total_words += len(words)
                    total_chars += len(text)
            
            # Also count text in tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text = cell.text
                        if text:
                            words = text.split()
                            total_words += len(words)
                            total_chars += len(text)
            
            metadata.word_count = total_words
            metadata.character_count = total_chars
            
            # Count inline shapes (images)
            image_count = 0
            for paragraph in doc.paragraphs:
                if hasattr(paragraph, '_element'):
                    # Count inline images
                    inline_shapes = paragraph._element.xpath('.//w:drawing')
                    image_count += len(inline_shapes)
            
            metadata.image_count = image_count
            
        except Exception as e:
            self.logger.warning(f"Error extracting statistics: {e}")
    
    def _extract_extended_properties(self, doc: Any, metadata: DocumentMetadata) -> None:
        """Extract extended properties from document."""
        try:
            # Access extended properties through document part
            if hasattr(doc, 'part') and hasattr(doc.part, 'package'):
                package = doc.part.package
                
                # Try to access app.xml properties
                for rel in package.part.rels.values():
                    if rel.reltype.endswith('extended-properties'):
                        app_part = rel.target_part
                        if hasattr(app_part, 'blob'):
                            # Parse XML to extract extended properties
                            # This is a simplified approach - full implementation would parse XML
                            pass
                        break
            
        except Exception as e:
            self.logger.debug(f"Could not extract extended properties: {e}")
    
    def _extract_custom_properties(self, doc: Any, metadata: DocumentMetadata) -> None:
        """Extract custom document properties."""
        custom_props = {}
        
        try:
            # Access custom properties through document part
            if hasattr(doc, 'part') and hasattr(doc.part, 'package'):
                package = doc.part.package
                
                # Try to find custom properties part
                for rel in package.part.rels.values():
                    if rel.reltype.endswith('custom-properties'):
                        # Found custom properties - would need XML parsing
                        self.logger.debug("Custom properties found but not parsed")
                        break
            
        except Exception as e:
            self.logger.debug(f"Could not extract custom properties: {e}")
        
        if custom_props:
            metadata.custom_properties = custom_props
    
    def _check_document_features(self, doc: Any, metadata: DocumentMetadata) -> None:
        """Check for track changes, comments, and protection."""
        try:
            # Check for comments
            if hasattr(doc, '_element'):
                comments = doc._element.xpath('//w:comment')
                metadata.has_comments = len(comments) > 0
                
                # Check for track changes
                track_changes = doc._element.xpath('//w:del | //w:ins')
                metadata.has_track_changes = len(track_changes) > 0
            
            # Check document protection
            if hasattr(doc, 'settings') and hasattr(doc.settings, 'element'):
                protection = doc.settings.element.find('.//w:documentProtection')
                if protection is not None:
                    metadata.protection_type = protection.get('w:edit', 'unknown')
            
        except Exception as e:
            self.logger.debug(f"Could not check document features: {e}")


class PropertyAnalyzer:
    """Analyze and summarize document properties."""
    
    @staticmethod
    def analyze_metadata(metadata: DocumentMetadata) -> Dict[str, Any]:
        """Analyze metadata and provide insights."""
        analysis = {
            'summary': {},
            'warnings': [],
            'insights': []
        }
        
        # Document age analysis
        if metadata.created and metadata.modified:
            age_days = (datetime.now() - metadata.created).days
            last_modified_days = (datetime.now() - metadata.modified).days
            
            analysis['summary']['document_age_days'] = age_days
            analysis['summary']['last_modified_days'] = last_modified_days
            
            if age_days > 365:
                analysis['insights'].append(f"Document is over {age_days // 365} year(s) old")
            
            if last_modified_days > 180:
                analysis['warnings'].append("Document hasn't been updated in over 6 months")
        
        # Revision analysis
        if metadata.revision and metadata.revision > 50:
            analysis['warnings'].append(f"High revision count ({metadata.revision}) may indicate extensive editing")
        
        # Size analysis
        if metadata.word_count:
            if metadata.word_count > 50000:
                analysis['insights'].append("Large document (>50k words)")
            elif metadata.word_count < 100:
                analysis['insights'].append("Very short document (<100 words)")
        
        # Feature warnings
        if metadata.has_track_changes:
            analysis['warnings'].append("Document contains tracked changes")
        
        if metadata.has_comments:
            analysis['warnings'].append("Document contains comments")
        
        if metadata.protection_type:
            analysis['warnings'].append(f"Document is protected ({metadata.protection_type})")
        
        # Author analysis
        if metadata.author and metadata.last_modified_by:
            if metadata.author != metadata.last_modified_by:
                analysis['insights'].append("Document has been modified by someone other than the original author")
        
        return analysis