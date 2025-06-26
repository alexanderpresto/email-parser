"""
Integration tests for PDF converter with email processing pipeline.

These tests verify the integration of PDF conversion within the 
email processing workflow.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from email_parser.core.config import ProcessingConfig
from email_parser.core.email_processor import EmailProcessor
from email_parser.exceptions.converter_exceptions import PDFConversionError


class TestPDFEmailIntegration:
    """Test PDF conversion integration with email processing."""
    
    @pytest.fixture
    def email_with_pdf(self, tmp_path):
        """Create a test email with PDF attachment."""
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email with PDF
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain

This email contains a PDF attachment.

--boundary123
Content-Type: application/pdf; name="document.pdf"
Content-Disposition: attachment; filename="document.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQKJdPr6eEKMSAwIG9iago8PC9UeXBlL0NhdGFsb2c+PgplbmRvYmoKMiAwIG9iago8
PC9UeXBlL1BhZ2VzPj4KZW5kb2JqCnhyZWYKMCA0CjAwMDAwMDAwMDAgNjU1MzUgZgowMDAwMDAw
MDEwIDAwMDAwIG4KMDAwMDAwMDA1MyAwMDAwMCBuCnRyYWlsZXIKPDwvU2l6ZSA0Pj4Kc3RhcnR4
cmVmCjE5MAolJUVPRgo=

--boundary123--
"""
        email_file = tmp_path / "test_email.eml"
        email_file.write_text(email_content)
        return str(email_file)    
    @pytest.fixture
    def processing_config(self, tmp_path):
        """Create processing configuration with PDF conversion enabled."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        config = ProcessingConfig(
            output_directory=str(output_dir),
            convert_pdf=True,
            convert_excel=True,
            pdf_extraction_mode='all'
        )
        return config
    
    @patch('email_parser.converters.pdf_converter.MistralClient')
    def test_email_with_pdf_conversion(self, mock_client_class, email_with_pdf, processing_config):
        """Test processing email with PDF attachment and conversion enabled."""
        # Mock successful API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.parsed.text = "# Converted PDF Content\n\nThis is the converted document."
        mock_client.chat.complete.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Process email
        processor = EmailProcessor(processing_config)
        
        with patch.dict(os.environ, {'MISTRALAI_API_KEY': 'test-key'}):
            result = processor.process_email(email_with_pdf)
        
        # Verify PDF was processed
        assert len(result['attachments']) == 1
        assert result['attachments'][0]['filename'] == 'document.pdf'
        
        # Check for converted markdown
        converted_dir = Path(processing_config.output_directory) / "converted_pdf"
        assert converted_dir.exists()
        
        # Find the converted markdown file
        md_files = list(converted_dir.glob("*.md"))
        assert len(md_files) == 1        
        # Verify content
        with open(md_files[0], 'r') as f:
            content = f.read()
        assert "Converted PDF Content" in content
    
    def test_email_without_pdf(self, processing_config):
        """Test processing email without PDF attachments."""
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Simple Text Email

This is a simple text email without attachments.
"""
        processor = EmailProcessor(processing_config)
        
        # This should process without errors even with PDF conversion enabled
        # Just won't create any PDF conversions
        result = processor.process_email_from_string(email_content)
        
        assert len(result['attachments']) == 0
        
        # Check that converted_pdf directory exists but is empty
        converted_dir = Path(processing_config.output_directory) / "converted_pdf"
        if converted_dir.exists():
            assert len(list(converted_dir.glob("*.md"))) == 0
    
    @patch.dict(os.environ, {}, clear=True)
    def test_pdf_conversion_without_api_key(self, email_with_pdf, processing_config):
        """Test graceful handling when API key is missing."""
        processor = EmailProcessor(processing_config)
        
        # Should process email but skip PDF conversion
        result = processor.process_email(email_with_pdf)
        
        # Email should still be processed
        assert len(result['attachments']) == 1
        
        # But no markdown conversion should occur
        converted_dir = Path(processing_config.output_directory) / "converted_pdf"        if converted_dir.exists():
            assert len(list(converted_dir.glob("*.md"))) == 0
    
    def test_pdf_conversion_disabled(self, email_with_pdf, tmp_path):
        """Test email processing with PDF conversion disabled."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        config = ProcessingConfig(
            output_directory=str(output_dir),
            convert_pdf=False,  # Disabled
            convert_excel=True
        )
        
        processor = EmailProcessor(config)
        result = processor.process_email(email_with_pdf)
        
        # PDF should be extracted but not converted
        assert len(result['attachments']) == 1
        assert result['attachments'][0]['filename'] == 'document.pdf'
        
        # No converted_pdf directory should be created
        converted_dir = Path(config.output_directory) / "converted_pdf"
        assert not converted_dir.exists() or len(list(converted_dir.glob("*.md"))) == 0