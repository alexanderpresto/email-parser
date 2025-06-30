"""Tests for DOCX metadata extraction."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from email_parser.converters.docx.metadata_extractor import (
    DocumentMetadata,
    MetadataExtractor,
    PropertyAnalyzer
)


class TestDocumentMetadata:
    """Test DocumentMetadata dataclass."""
    
    def test_default_values(self):
        """Test default metadata values."""
        metadata = DocumentMetadata()
        
        assert metadata.title is None
        assert metadata.author is None
        assert metadata.word_count is None
        assert metadata.has_track_changes is False
        assert metadata.has_comments is False
        assert metadata.custom_properties is None
    
    def test_to_dict_basic(self):
        """Test conversion to dictionary."""
        metadata = DocumentMetadata(
            title="Test Document",
            author="Test Author",
            word_count=100
        )
        
        data = metadata.to_dict()
        
        assert data['title'] == "Test Document"
        assert data['author'] == "Test Author"
        assert data['word_count'] == 100
    
    def test_to_dict_with_datetime(self):
        """Test datetime serialization."""
        now = datetime.now()
        metadata = DocumentMetadata(
            created=now,
            modified=now
        )
        
        data = metadata.to_dict()
        
        assert isinstance(data['created'], str)
        assert isinstance(data['modified'], str)
        assert data['created'] == now.isoformat()


class TestMetadataExtractor:
    """Test metadata extraction functionality."""
    
    def test_initialization(self):
        """Test extractor initialization."""
        extractor = MetadataExtractor()
        assert hasattr(extractor, 'logger')
    
    @patch('email_parser.converters.docx.metadata_extractor.Document', None)
    def test_extract_without_python_docx(self, tmp_path):
        """Test extraction when python-docx is not available."""
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"fake docx content")
        
        extractor = MetadataExtractor()
        metadata = extractor.extract(test_file)
        
        assert isinstance(metadata, DocumentMetadata)
        # Should have basic file stats
        assert metadata.created is not None
        assert metadata.modified is not None
    
    @patch('email_parser.converters.docx.metadata_extractor.Document')
    def test_extract_core_properties(self, mock_document_class, tmp_path):
        """Test extraction of core properties."""
        # Create mock document
        mock_doc = Mock()
        mock_core_props = Mock()
        
        # Set core properties
        mock_core_props.title = "Test Title"
        mock_core_props.subject = "Test Subject"
        mock_core_props.author = "Test Author"
        mock_core_props.keywords = "test, keywords"
        mock_core_props.comments = "Test description"
        mock_core_props.last_modified_by = "Another Author"
        mock_core_props.category = "Test Category"
        mock_core_props.content_status = "Final"
        mock_core_props.language = "en-US"
        mock_core_props.version = "1.0"
        mock_core_props.revision = "5"
        mock_core_props.created = datetime(2023, 1, 1)
        mock_core_props.modified = datetime(2023, 6, 1)
        mock_core_props.last_printed = datetime(2023, 5, 1)
        
        mock_doc.core_properties = mock_core_props
        mock_doc.paragraphs = []
        mock_doc.tables = []
        mock_doc._element = Mock()
        mock_doc._element.xpath.return_value = []
        
        mock_document_class.return_value = mock_doc
        
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"fake content")
        
        extractor = MetadataExtractor()
        metadata = extractor.extract(test_file)
        
        assert metadata.title == "Test Title"
        assert metadata.subject == "Test Subject"
        assert metadata.author == "Test Author"
        assert metadata.keywords == "test, keywords"
        assert metadata.description == "Test description"
        assert metadata.last_modified_by == "Another Author"
        assert metadata.revision == 5
        assert metadata.created == datetime(2023, 1, 1)
    
    @patch('email_parser.converters.docx.metadata_extractor.Document')
    def test_extract_statistics(self, mock_document_class, tmp_path):
        """Test extraction of document statistics."""
        # Create mock document with content
        mock_doc = Mock()
        
        # Mock paragraphs
        mock_para1 = Mock()
        mock_para1.text = "This is the first paragraph with some text."
        mock_para2 = Mock()
        mock_para2.text = "This is the second paragraph."
        mock_doc.paragraphs = [mock_para1, mock_para2]
        
        # Mock tables
        mock_cell = Mock()
        mock_cell.text = "Table cell content"
        mock_row = Mock()
        mock_row.cells = [mock_cell]
        mock_table = Mock()
        mock_table.rows = [mock_row]
        mock_doc.tables = [mock_table]
        
        # Mock core properties (minimal)
        mock_core_props = Mock()
        for attr in ['title', 'subject', 'author', 'keywords', 'comments', 
                     'last_modified_by', 'category', 'content_status', 
                     'language', 'version', 'revision', 'created', 
                     'modified', 'last_printed']:
            setattr(mock_core_props, attr, None)
        mock_doc.core_properties = mock_core_props
        
        # Mock inline shapes
        mock_doc._element = Mock()
        mock_doc._element.xpath.return_value = []
        
        # Set up paragraph elements
        for para in mock_doc.paragraphs:
            para._element = Mock()
            para._element.xpath.return_value = []
        
        mock_document_class.return_value = mock_doc
        
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"fake content")
        
        extractor = MetadataExtractor()
        metadata = extractor.extract(test_file)
        
        assert metadata.paragraph_count == 2
        assert metadata.table_count == 1
        assert metadata.word_count > 0  # Should count words from paragraphs and tables
        assert metadata.character_count > 0
    
    @patch('email_parser.converters.docx.metadata_extractor.Document')
    def test_check_document_features(self, mock_document_class, tmp_path):
        """Test checking for track changes and comments."""
        mock_doc = Mock()
        
        # Set up basic structure
        mock_doc.paragraphs = []
        mock_doc.tables = []
        mock_doc.core_properties = Mock()
        for attr in ['title', 'subject', 'author', 'keywords', 'comments', 
                     'last_modified_by', 'category', 'content_status', 
                     'language', 'version', 'revision', 'created', 
                     'modified', 'last_printed']:
            setattr(mock_doc.core_properties, attr, None)
        
        # Mock document element with comments and track changes
        mock_element = Mock()
        mock_doc._element = mock_element
        
        # Mock xpath calls
        def xpath_side_effect(query):
            if '//w:comment' in query:
                return ['comment1', 'comment2']  # Has comments
            elif '//w:del | //w:ins' in query:
                return ['change1']  # Has track changes
            else:
                return []
        
        mock_element.xpath = Mock(side_effect=xpath_side_effect)
        
        mock_document_class.return_value = mock_doc
        
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"fake content")
        
        extractor = MetadataExtractor()
        metadata = extractor.extract(test_file)
        
        assert metadata.has_comments is True
        assert metadata.has_track_changes is True
    
    @patch('email_parser.converters.docx.metadata_extractor.Document')
    def test_extract_with_error(self, mock_document_class, tmp_path):
        """Test extraction handles errors gracefully."""
        # Make Document constructor raise an error
        mock_document_class.side_effect = Exception("Failed to open document")
        
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"fake content")
        
        extractor = MetadataExtractor()
        metadata = extractor.extract(test_file)
        
        # Should return empty metadata on error
        assert isinstance(metadata, DocumentMetadata)


class TestPropertyAnalyzer:
    """Test metadata analysis functionality."""
    
    def test_analyze_old_document(self):
        """Test analysis of old document."""
        metadata = DocumentMetadata(
            created=datetime(2020, 1, 1),
            modified=datetime(2020, 6, 1)
        )
        
        analysis = PropertyAnalyzer.analyze_metadata(metadata)
        
        assert 'document_age_days' in analysis['summary']
        assert analysis['summary']['document_age_days'] > 1000  # Over 3 years old
        assert any("year(s) old" in insight for insight in analysis['insights'])
        assert any("hasn't been updated" in warning for warning in analysis['warnings'])
    
    def test_analyze_high_revision_count(self):
        """Test analysis of high revision count."""
        metadata = DocumentMetadata(revision=75)
        
        analysis = PropertyAnalyzer.analyze_metadata(metadata)
        
        assert any("High revision count" in warning for warning in analysis['warnings'])
    
    def test_analyze_document_size(self):
        """Test analysis of document size."""
        # Large document
        metadata_large = DocumentMetadata(word_count=60000)
        analysis_large = PropertyAnalyzer.analyze_metadata(metadata_large)
        assert any("Large document" in insight for insight in analysis_large['insights'])
        
        # Small document
        metadata_small = DocumentMetadata(word_count=50)
        analysis_small = PropertyAnalyzer.analyze_metadata(metadata_small)
        assert any("Very short document" in insight for insight in analysis_small['insights'])
    
    def test_analyze_document_features(self):
        """Test analysis of document features."""
        metadata = DocumentMetadata(
            has_track_changes=True,
            has_comments=True,
            protection_type="readOnly"
        )
        
        analysis = PropertyAnalyzer.analyze_metadata(metadata)
        
        assert any("tracked changes" in warning for warning in analysis['warnings'])
        assert any("comments" in warning for warning in analysis['warnings'])
        assert any("protected" in warning for warning in analysis['warnings'])
    
    def test_analyze_author_changes(self):
        """Test analysis of author changes."""
        metadata = DocumentMetadata(
            author="Original Author",
            last_modified_by="Different Author"
        )
        
        analysis = PropertyAnalyzer.analyze_metadata(metadata)
        
        assert any("modified by someone other" in insight for insight in analysis['insights'])