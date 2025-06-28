"""Unit tests for DOCX converter."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from email_parser.converters.docx_converter import DocxConverter
from email_parser.exceptions.converter_exceptions import (
    ConversionError,
    ConfigurationError
)


class TestDocxConverter:
    """Test cases for DocxConverter."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        return {
            'max_file_size': 52428800,
            'output_format': 'both',
            'extract_tables': True,
            'extract_metadata': True,
            'extract_images': False,
            'enable_chunking': False
        }
    
    @pytest.fixture
    def converter(self, mock_config):
        """Create DocxConverter instance."""
        return DocxConverter(mock_config)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_initialization_success(self, mock_config):
        """Test successful initialization."""
        converter = DocxConverter(mock_config)
        assert converter.config['max_file_size'] == 52428800
        assert converter.config['output_format'] == 'both'
        assert converter.extract_metadata is True
    
    def test_initialization_default_config(self):
        """Test initialization with default config."""
        converter = DocxConverter()
        assert converter.config['max_file_size'] == 52428800
        assert converter.config['extract_metadata'] is True
    
    def test_supported_extensions(self, converter):
        """Test supported extensions property."""
        assert converter.supported_extensions == ['.docx']
    
    def test_supported_mime_types(self, converter):
        """Test supported MIME types property."""
        mime_types = converter.supported_mime_types
        assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_types
        assert 'application/vnd.ms-word.document.macroEnabled.12' in mime_types
    
    def test_converter_name(self, converter):
        """Test converter name property."""
        assert converter.converter_name == "DOCX to Markdown Converter"
    
    def test_can_convert_docx(self, converter):
        """Test can_convert for DOCX files."""
        assert converter.can_convert(Path("document.docx")) is True
        assert converter.can_convert(Path("document.DOCX")) is True
        assert converter.can_convert(Path("document.pdf")) is False
        assert converter.can_convert(Path("document.txt")) is False
    
    def test_can_convert_with_mime_type(self, converter):
        """Test can_convert with MIME type."""
        docx_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        assert converter.can_convert(Path("document.unknown"), docx_mime) is True
        assert converter.can_convert(Path("document.unknown"), 'text/plain') is False
    
    @patch('email_parser.converters.docx_converter.mammoth')
    @patch('email_parser.converters.docx_converter.Document')
    def test_convert_success(self, mock_document, mock_mammoth, converter, temp_dir):
        """Test successful conversion."""
        # Create test input file
        input_file = temp_dir / "test.docx"
        input_file.write_bytes(b"fake docx content")
        
        # Mock mammoth response
        mock_result = Mock()
        mock_result.value = "# Test Document\n\nThis is test content."
        mock_result.messages = []
        mock_mammoth.convert_to_markdown.return_value = mock_result
        
        # Mock metadata extraction
        mock_doc = Mock()
        mock_props = Mock()
        mock_props.title = "Test Document"
        mock_props.author = "Test Author"
        mock_props.created = None
        mock_props.modified = None
        mock_props.subject = "Test Subject"
        mock_props.keywords = "test, conversion"
        mock_props.category = "Test"
        mock_props.comments = "Test comments"
        mock_props.revision = 1
        mock_doc.core_properties = mock_props
        mock_doc.paragraphs = [Mock(text="Test content")]
        mock_doc.tables = []  # Add empty tables list
        mock_document.return_value = mock_doc
        
        # Convert
        output_file = converter.convert(input_file)
        
        # Verify output file exists
        assert output_file.exists()
        
        # Verify content
        content = output_file.read_text(encoding='utf-8')
        assert "Test Document" in content
        assert "This is test content" in content
        
        # Verify metadata file exists
        metadata_file = output_file.with_suffix('.json')
        assert metadata_file.exists()
    
    def test_convert_file_not_found(self, converter, temp_dir):
        """Test conversion with non-existent file."""
        input_file = temp_dir / "missing.docx"
        
        with pytest.raises(ConversionError, match="File does not exist"):
            converter.convert(input_file)
    
    def test_convert_invalid_file_type(self, converter, temp_dir):
        """Test conversion with invalid file type."""
        input_file = temp_dir / "test.txt"
        input_file.write_text("not a docx")
        
        with pytest.raises(ConversionError, match="Unsupported file format"):
            converter.convert(input_file)
    
    def test_convert_file_too_large(self, converter, temp_dir):
        """Test conversion with oversized file."""
        # Create converter with small file size limit
        small_config = {'max_file_size': 100}
        converter = DocxConverter(small_config)
        
        input_file = temp_dir / "large.docx"
        input_file.write_bytes(b"x" * 200)  # Create file larger than limit
        
        with pytest.raises(ConversionError, match="File too large"):
            converter.convert(input_file)
    
    @patch('email_parser.converters.docx_converter.mammoth')
    def test_mammoth_extraction_with_warnings(self, mock_mammoth, converter, temp_dir):
        """Test mammoth extraction with warnings."""
        input_file = temp_dir / "test.docx"
        input_file.write_bytes(b"fake docx content")
        
        # Mock mammoth with warnings
        mock_result = Mock()
        mock_result.value = "# Test\n\nContent"
        mock_result.messages = ["Warning: Some formatting lost"]
        mock_mammoth.convert_to_markdown.return_value = mock_result
        
        # Should not raise exception
        result = converter._extract_with_mammoth(input_file)
        assert result == "# Test\n\nContent"
    
    @patch('email_parser.converters.docx_converter.mammoth')
    def test_mammoth_extraction_failure(self, mock_mammoth, converter, temp_dir):
        """Test mammoth extraction failure."""
        input_file = temp_dir / "test.docx"
        input_file.write_bytes(b"fake docx content")
        
        # Mock mammoth to raise exception
        mock_mammoth.convert_to_markdown.side_effect = Exception("Mammoth error")
        
        with pytest.raises(ConversionError, match="Mammoth extraction failed"):
            converter._extract_with_mammoth(input_file)
    
    @patch('email_parser.converters.docx_converter.Document')
    def test_metadata_extraction_success(self, mock_document, converter, temp_dir):
        """Test successful metadata extraction."""
        input_file = temp_dir / "test.docx"
        input_file.write_bytes(b"fake docx content")
        
        # Mock document with complete metadata
        mock_doc = Mock()
        mock_props = Mock()
        mock_props.title = "Test Document"
        mock_props.author = "Test Author"
        mock_props.subject = "Test Subject"
        mock_props.keywords = "test, document"
        mock_props.category = "Test"
        mock_props.comments = "Test comments"
        mock_props.revision = 2
        mock_props.created = None
        mock_props.modified = None
        mock_doc.core_properties = mock_props
        mock_doc.paragraphs = [Mock(text="Word one two"), Mock(text="three four")]
        mock_doc.tables = []  # Add empty tables list
        mock_document.return_value = mock_doc
        
        metadata = converter._extract_metadata(input_file)
        
        assert metadata['title'] == "Test Document"
        assert metadata['author'] == "Test Author"
        assert metadata['subject'] == "Test Subject"
        assert metadata['keywords'] == "test, document"
        assert metadata['word_count'] == 5  # "Word one two" (3) + "three four" (2)
        assert metadata['revision'] == 2
    
    @patch('email_parser.converters.docx_converter.Document')
    def test_metadata_extraction_failure(self, mock_document, converter, temp_dir):
        """Test metadata extraction failure."""
        input_file = temp_dir / "test.docx"
        input_file.write_bytes(b"fake docx content")
        
        # Mock document to raise exception
        mock_document.side_effect = Exception("Document error")
        
        # Should return empty dict and not raise exception
        metadata = converter._extract_metadata(input_file)
        assert metadata == {}
    
    def test_word_count_estimation(self, converter):
        """Test word count estimation."""
        # Mock document with paragraphs
        mock_doc = Mock()
        mock_doc.paragraphs = [
            Mock(text="This is a test"),
            Mock(text="Another paragraph with more words"),
            Mock(text="")  # Empty paragraph
        ]
        
        word_count = converter._estimate_word_count(mock_doc)
        assert word_count == 9  # 4 + 5 + 0
    
    def test_word_count_estimation_error(self, converter):
        """Test word count estimation with error."""
        # Mock document that raises exception
        mock_doc = Mock()
        mock_doc.paragraphs = Mock(side_effect=Exception("Error"))
        
        word_count = converter._estimate_word_count(mock_doc)
        assert word_count == 0
    
    @patch('email_parser.converters.docx_converter.mammoth')
    @patch('email_parser.converters.docx_converter.Document')
    def test_convert_with_custom_output_path(self, mock_document, mock_mammoth, converter, temp_dir):
        """Test conversion with custom output path."""
        # Setup mocks
        input_file = temp_dir / "test.docx"
        input_file.write_bytes(b"fake docx content")
        custom_output = temp_dir / "custom_output.md"
        
        mock_result = Mock()
        mock_result.value = "# Test"
        mock_result.messages = []
        mock_mammoth.convert_to_markdown.return_value = mock_result
        
        mock_doc = Mock()
        mock_props = Mock()
        mock_props.title = None
        mock_props.author = None
        mock_props.created = None
        mock_props.modified = None
        mock_props.subject = None
        mock_props.keywords = None
        mock_props.category = None
        mock_props.comments = None
        mock_props.revision = None
        mock_doc.core_properties = mock_props
        mock_doc.paragraphs = []
        mock_document.return_value = mock_doc
        
        # Convert with custom output path
        result_path = converter.convert(input_file, custom_output)
        
        assert result_path == custom_output
        assert custom_output.exists()
    
    def test_repr(self, converter):
        """Test string representation."""
        repr_str = repr(converter)
        assert "DocxConverter" in repr_str
        assert ".docx" in repr_str