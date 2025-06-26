"""Unit tests for PDF converter error scenarios.

This module tests specific error handling scenarios for PDF conversion,
including edge cases, malformed files, and various failure modes.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os
from email_parser.converters.pdf_converter import PDFConverter
from email_parser.exceptions.converter_exceptions import ConversionError, APIError


class TestPDFErrorScenarios:
    """Test various error scenarios for PDF conversion."""
    
    @pytest.fixture
    def converter(self):
        """Create PDF converter with test API key."""
        return PDFConverter(api_key="test_api_key")
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_corrupted_pdf_handling(self, converter, temp_dir):
        """Test handling of corrupted PDF files."""
        # Create a corrupted PDF file
        corrupted_pdf = temp_dir / "corrupted.pdf"
        corrupted_pdf.write_bytes(b"%PDF-1.4\n\nCorrupted binary data\x00\x01\x02")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(corrupted_pdf, output_dir)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in [
            "corrupted", "invalid", "malformed", "damaged"
        ])
    
    def test_zero_byte_file_handling(self, converter, temp_dir):
        """Test handling of zero-byte files."""
        empty_pdf = temp_dir / "empty.pdf"
        empty_pdf.write_bytes(b"")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(empty_pdf, output_dir)
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_password_protected_pdf_handling(self, converter, temp_dir):
        """Test handling of password-protected PDFs."""
        # Create a mock password-protected PDF
        protected_pdf = temp_dir / "protected.pdf"
        # PDF header with encryption dictionary
        protected_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/Encrypt 3 0 R
>>
endobj
3 0 obj
<<
/Filter /Standard
/V 1
/R 2
/O (encrypted_owner_password)
/U (encrypted_user_password)
/P -44
>>
endobj
"""
        protected_pdf.write_bytes(protected_content)
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(protected_pdf, output_dir)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in [
            "password", "protected", "encrypted", "permission"
        ])
    
    def test_non_pdf_with_pdf_extension(self, converter, temp_dir):
        """Test handling of non-PDF files with .pdf extension."""
        fake_pdf = temp_dir / "fake.pdf"
        fake_pdf.write_text("This is just a text file, not a PDF!")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(fake_pdf, output_dir)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in [
            "not a pdf", "invalid format", "not a valid pdf"
        ])
    
    def test_extremely_large_pdf_rejection(self, converter, temp_dir):
        """Test rejection of extremely large PDFs."""
        # Create a large file (simulate 200MB)
        large_pdf = temp_dir / "large.pdf"
        
        # Write PDF header then large content
        with open(large_pdf, "wb") as f:
            f.write(b"%PDF-1.4\n")
            # Write 200MB of dummy data
            chunk_size = 1024 * 1024  # 1MB chunks
            chunk = b"x" * chunk_size
            for _ in range(200):  # 200MB total
                f.write(chunk)
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(large_pdf, output_dir)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in [
            "too large", "size limit", "file size", "exceeds"
        ])
    
    def test_invalid_pdf_version_handling(self, converter, temp_dir):
        """Test handling of unsupported PDF versions."""
        # Create PDF with unsupported version
        unsupported_pdf = temp_dir / "unsupported.pdf"
        unsupported_pdf.write_bytes(b"%PDF-2.0\n\nUnsupported version content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(unsupported_pdf, output_dir)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in [
            "version", "unsupported", "not supported"
        ])
    
    def test_missing_input_file(self, converter, temp_dir):
        """Test handling of missing input files."""
        missing_pdf = temp_dir / "nonexistent.pdf"
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(missing_pdf, output_dir)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in [
            "not found", "does not exist", "missing"
        ])
    
    def test_invalid_output_directory(self, converter, temp_dir):
        """Test handling of invalid output directories."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        # Try to use a file as output directory
        invalid_output = temp_dir / "not_a_directory.txt"
        invalid_output.write_text("This is a file, not a directory")
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(test_pdf, invalid_output)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in [
            "output", "directory", "invalid", "not a directory"
        ])
    
    def test_permission_denied_scenarios(self, converter, temp_dir):
        """Test handling of permission denied scenarios."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        # Create output directory with no write permissions
        restricted_output = temp_dir / "restricted"
        restricted_output.mkdir()
        
        # Mock os.access to simulate permission denied
        with patch('os.access', return_value=False):
            with pytest.raises(ConversionError) as exc_info:
                converter.convert(test_pdf, restricted_output)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "permission", "access", "denied", "write"
            ])
    
    def test_disk_space_full_scenario(self, converter, temp_dir):
        """Test handling of disk space full scenarios."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock OSError to simulate disk full
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            with pytest.raises(ConversionError) as exc_info:
                converter.convert(test_pdf, output_dir)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "space", "disk", "full", "storage"
            ])
    
    def test_network_connectivity_errors(self, converter, temp_dir):
        """Test handling of network connectivity issues."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock network errors
        import requests
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Network unreachable")
            
            with pytest.raises(ConversionError) as exc_info:
                converter.convert(test_pdf, output_dir)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "network", "connection", "unreachable", "connectivity"
            ])
    
    def test_api_timeout_handling(self, converter, temp_dir):
        """Test handling of API timeout scenarios."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock timeout
        import requests
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
            
            with pytest.raises(ConversionError) as exc_info:
                converter.convert(test_pdf, output_dir)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "timeout", "timed out", "exceeded"
            ])
    
    def test_api_rate_limit_handling(self, converter, temp_dir):
        """Test handling of API rate limiting."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock rate limit response
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"error": "rate_limit_exceeded"}
            mock_response.headers = {"Retry-After": "60"}
            mock_post.return_value = mock_response
            
            with pytest.raises(APIError) as exc_info:
                converter.convert(test_pdf, output_dir)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "rate limit", "rate limiting", "too many requests"
            ])
    
    def test_api_quota_exceeded_handling(self, converter, temp_dir):
        """Test handling of API quota exceeded."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock quota exceeded response
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.json.return_value = {"error": "quota_exceeded"}
            mock_post.return_value = mock_response
            
            with pytest.raises(APIError) as exc_info:
                converter.convert(test_pdf, output_dir)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "quota", "exceeded", "limit", "usage"
            ])
    
    def test_malformed_api_response_handling(self, converter, temp_dir):
        """Test handling of malformed API responses."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock malformed response
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.text = "Malformed response"
            mock_post.return_value = mock_response
            
            with pytest.raises(ConversionError) as exc_info:
                converter.convert(test_pdf, output_dir)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "malformed", "invalid response", "parse error"
            ])
    
    def test_memory_exhaustion_handling(self, converter, temp_dir):
        """Test handling of memory exhaustion scenarios."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock memory error
        with patch.object(converter, '_process_pdf_content') as mock_process:
            mock_process.side_effect = MemoryError("Out of memory")
            
            with pytest.raises(ConversionError) as exc_info:
                converter.convert(test_pdf, output_dir)
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "memory", "out of memory", "insufficient memory"
            ])
    
    def test_invalid_api_key_scenarios(self):
        """Test various invalid API key scenarios."""
        # Test None API key
        with pytest.raises(APIError) as exc_info:
            PDFConverter(api_key=None)
        assert "required" in str(exc_info.value).lower()
        
        # Test empty API key
        with pytest.raises(APIError) as exc_info:
            PDFConverter(api_key="")
        assert "required" in str(exc_info.value).lower()
        
        # Test whitespace-only API key
        with pytest.raises(APIError) as exc_info:
            PDFConverter(api_key="   ")
        assert "required" in str(exc_info.value).lower()
    
    def test_api_key_validation_with_invalid_format(self):
        """Test API key validation with invalid formats."""
        invalid_keys = [
            "short",  # Too short
            "123",    # Numeric only
            "key with spaces",  # Contains spaces
            "key\nwith\nnewlines",  # Contains newlines
            "key-with-special-chars!@#$%",  # Invalid characters
        ]
        
        for invalid_key in invalid_keys:
            with pytest.raises(APIError) as exc_info:
                converter = PDFConverter(api_key=invalid_key)
                converter._validate_api_key_format()
            
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "invalid", "format", "api key"
            ])
    
    def test_concurrent_conversion_conflicts(self, converter, temp_dir):
        """Test handling of concurrent conversion conflicts."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock file system conflict
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = FileExistsError("Directory already exists")
            
            # Should handle gracefully or provide clear error
            try:
                converter.convert(test_pdf, output_dir)
            except ConversionError as e:
                error_msg = str(e).lower()
                assert any(keyword in error_msg for keyword in [
                    "conflict", "exists", "concurrent", "already"
                ])
    
    def test_cleanup_on_conversion_failure(self, converter, temp_dir):
        """Test that temporary files are cleaned up on conversion failure."""
        test_pdf = temp_dir / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n\nValid PDF content")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock failure after creating temporary files
        with patch.object(converter, '_call_mistral_api') as mock_api:
            mock_api.side_effect = Exception("API call failed")
            
            # Track files before and after
            files_before = list(output_dir.glob("*"))
            
            with pytest.raises(ConversionError):
                converter.convert(test_pdf, output_dir)
            
            files_after = list(output_dir.glob("*"))
            
            # Should not leave temporary files behind
            assert len(files_after) == len(files_before), \
                   "Temporary files not cleaned up after failure"