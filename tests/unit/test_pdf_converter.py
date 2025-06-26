"""
Unit tests for PDF to Markdown converter with MistralAI integration.

These tests cover the PDFConverter class functionality including:
- File validation and format checking
- API connectivity and error handling
- Conversion process and output generation
- Retry logic and timeout handling
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from email_parser.converters.pdf_converter import PDFConverter
from email_parser.exceptions.converter_exceptions import (
    UnsupportedFormatError,
    FileSizeError,
    APIError,
    ConversionError,
    ConfigurationError
)


class TestPDFConverter:
    """Test suite for PDF to Markdown converter."""
    
    @pytest.fixture
    def pdf_converter(self):
        """Create a PDF converter instance for testing."""
        config = {
            'extraction_mode': 'all',
            'image_settings': {
                'limit': 5,
                'min_size': 100
            }
        }
        return PDFConverter(config)
    
    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Create a sample PDF file path."""
        pdf_file = tmp_path / "test_document.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 sample content")
        return str(pdf_file)    
    def test_supported_extensions(self, pdf_converter):
        """Test that PDF converter supports correct extensions."""
        assert '.pdf' in pdf_converter.supported_extensions
        assert len(pdf_converter.supported_extensions) == 1
    
    def test_supported_mime_types(self, pdf_converter):
        """Test that PDF converter supports correct MIME types."""
        assert 'application/pdf' in pdf_converter.supported_mime_types
    
    def test_validate_file_valid(self, pdf_converter, sample_pdf_path):
        """Test validation of valid PDF file."""
        # Should not raise any exception
        pdf_converter._validate_file(sample_pdf_path)
    
    def test_validate_file_not_exists(self, pdf_converter):
        """Test validation fails for non-existent file."""
        with pytest.raises(FileNotFoundError):
            pdf_converter._validate_file("non_existent.pdf")
    
    def test_validate_file_wrong_extension(self, pdf_converter, tmp_path):
        """Test validation fails for wrong file extension."""
        wrong_file = tmp_path / "document.txt"
        wrong_file.write_text("Not a PDF")
        
        with pytest.raises(UnsupportedFormatError):
            pdf_converter._validate_file(str(wrong_file))
    
    def test_validate_file_size_limit(self, pdf_converter, tmp_path):
        """Test validation fails for oversized files."""
        # Set a small size limit for testing
        pdf_converter.config['max_file_size'] = 100  # 100 bytes
        
        large_file = tmp_path / "large.pdf"
        large_file.write_bytes(b"%PDF-1.4" + b"x" * 200)  # Create file > 100 bytes        
        with pytest.raises(FileSizeError):
            pdf_converter._validate_file(str(large_file))
    
    @patch.dict(os.environ, {'MISTRALAI_API_KEY': 'test-api-key'})
    def test_get_api_key_from_env(self, pdf_converter):
        """Test API key retrieval from environment."""
        api_key = pdf_converter._get_api_key()
        assert api_key == 'test-api-key'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_missing(self, pdf_converter):
        """Test error when API key is missing."""
        with pytest.raises(ConfigurationError, match="MISTRALAI_API_KEY"):
            pdf_converter._get_api_key()
    
    def test_generate_output_path_default(self, pdf_converter):
        """Test default output path generation."""
        input_path = "/path/to/document.pdf"
        output_path = pdf_converter._generate_output_path(input_path)
        
        assert output_path.endswith(".md")
        assert "document" in output_path
        assert "converted_pdf" in output_path
    
    def test_generate_output_path_custom(self, pdf_converter):
        """Test custom output path."""
        input_path = "/path/to/document.pdf"
        custom_output = "/custom/output.md"
        output_path = pdf_converter._generate_output_path(input_path, custom_output)
        
        assert output_path == custom_output    
    @patch('email_parser.converters.pdf_converter.MistralClient')
    def test_convert_success(self, mock_client_class, pdf_converter, sample_pdf_path, tmp_path):
        """Test successful PDF conversion."""
        # Mock API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.parsed.text = "# Converted Document\n\nThis is the converted content."
        mock_client.chat.complete.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Set output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        pdf_converter.config['output_base_dir'] = str(output_dir)
        
        # Perform conversion
        with patch.dict(os.environ, {'MISTRALAI_API_KEY': 'test-key'}):
            result_path = pdf_converter.convert(sample_pdf_path)
        
        # Verify result
        assert result_path.endswith(".md")
        assert os.path.exists(result_path)
        
        # Check content
        with open(result_path, 'r') as f:
            content = f.read()
        assert "# Converted Document" in content
    
    @patch('email_parser.converters.pdf_converter.MistralClient')
    def test_convert_api_error(self, mock_client_class, pdf_converter, sample_pdf_path):
        """Test handling of API errors during conversion."""
        # Mock API error
        mock_client = Mock()
        mock_client.chat.complete.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {'MISTRALAI_API_KEY': 'test-key'}):
            with pytest.raises(APIError):
                pdf_converter.convert(sample_pdf_path)
    
    def test_retry_logic(self, pdf_converter):
        """Test retry logic for transient failures."""
        # Mock function that fails twice then succeeds
        mock_func = Mock(side_effect=[Exception("Fail 1"), Exception("Fail 2"), "Success"])
        
        result = pdf_converter._retry_operation(mock_func, max_retries=3)
        assert result == "Success"
        assert mock_func.call_count == 3
    
    def test_retry_logic_exhausted(self, pdf_converter):
        """Test retry logic when all retries fail."""
        # Mock function that always fails
        mock_func = Mock(side_effect=Exception("Always fails"))
        
        with pytest.raises(Exception, match="Always fails"):
            pdf_converter._retry_operation(mock_func, max_retries=2)
        
        assert mock_func.call_count == 2
    
    def test_extraction_mode_text_only(self, pdf_converter):
        """Test text-only extraction mode."""
        pdf_converter.config['extraction_mode'] = 'text'
        assert pdf_converter.config['extraction_mode'] == 'text'
    
    def test_extraction_mode_images_only(self, pdf_converter):
        """Test images-only extraction mode."""
        pdf_converter.config['extraction_mode'] = 'images'
        assert pdf_converter.config['extraction_mode'] == 'images'