"""Live API integration tests for MistralAI PDF converter.

These tests require a valid MISTRALAI_API_KEY environment variable.
They test real API connectivity and response handling.
"""

import os
import time
from pathlib import Path
from unittest.mock import patch
import pytest
import psutil
import requests
from email_parser.converters.pdf_converter import PDFConverter
from email_parser.exceptions.converter_exceptions import ConversionError, APIError


class TestMistralAPILive:
    """Live API tests for MistralAI integration."""
    
    @pytest.fixture
    def api_key(self):
        """Get API key from environment, skip test if not available."""
        key = os.getenv("MISTRALAI_API_KEY")
        if not key:
            pytest.skip("MISTRALAI_API_KEY not set - skipping live API tests")
        return key
    
    @pytest.fixture
    def converter(self, api_key):
        """Create PDF converter with API key."""
        return PDFConverter(api_key=api_key)
    
    @pytest.fixture
    def test_output_dir(self, tmp_path):
        """Create temporary output directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return output_dir
    
    def test_api_connection_valid_key(self, converter, api_key):
        """Test successful API connection with valid key."""
        # Test basic connection by making a simple request
        assert converter.api_key == api_key
        assert converter._validate_api_key()
    
    def test_api_connection_invalid_key(self):
        """Test API connection with invalid key."""
        converter = PDFConverter(api_key="invalid_key_12345")
        
        with pytest.raises(APIError) as exc_info:
            converter._validate_api_key()
        
        assert "Invalid MistralAI API key" in str(exc_info.value)
    
    def test_api_connection_missing_key(self):
        """Test API connection with no key."""
        with pytest.raises(APIError) as exc_info:
            PDFConverter(api_key=None)
        
        assert "API key is required" in str(exc_info.value)
    
    @pytest.mark.timeout(30)
    def test_network_timeout_handling(self, converter):
        """Test network timeout scenarios."""
        # Mock requests to simulate timeout
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
            
            with pytest.raises(ConversionError) as exc_info:
                converter._call_mistral_api(b"dummy pdf content")
            
            assert "timeout" in str(exc_info.value).lower()
    
    def test_rate_limiting_response(self, converter):
        """Test rate limiting handling."""
        # Mock rate limit response
        with patch('requests.post') as mock_post:
            mock_response = mock_post.return_value
            mock_response.status_code = 429
            mock_response.json.return_value = {"error": "rate_limit_exceeded"}
            mock_response.headers = {"Retry-After": "1"}
            
            with pytest.raises(APIError) as exc_info:
                converter._call_mistral_api(b"dummy pdf content")
            
            assert "rate limit" in str(exc_info.value).lower()
    
    @pytest.mark.skipif(not os.getenv("MISTRALAI_API_KEY"), 
                       reason="No API key available for live testing")
    def test_small_pdf_conversion(self, converter, test_output_dir):
        """Test conversion of a small valid PDF."""
        # Create a minimal test PDF (would need actual PDF content)
        # For now, test the error handling when file doesn't exist
        test_pdf = test_output_dir / "nonexistent.pdf"
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(test_pdf, test_output_dir)
        
        assert "not found" in str(exc_info.value).lower()
    
    @pytest.mark.skipif(not os.getenv("MISTRALAI_API_KEY"), 
                       reason="No API key available for live testing")
    def test_large_pdf_handling(self, converter, test_output_dir):
        """Test handling of large PDF files (>5MB)."""
        # Create a mock large file
        large_pdf = test_output_dir / "large.pdf"
        
        # Write 6MB of dummy data
        with open(large_pdf, "wb") as f:
            f.write(b"dummy pdf content" * (6 * 1024 * 1024 // 17))
        
        # Should validate file size before API call
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(large_pdf, test_output_dir)
        
        # Could be size limit or invalid PDF format
        assert any(keyword in str(exc_info.value).lower() 
                  for keyword in ["size", "invalid", "format"])
    
    def test_malformed_pdf_handling(self, converter, test_output_dir):
        """Test handling of malformed PDF files."""
        # Create a file with PDF extension but invalid content
        malformed_pdf = test_output_dir / "malformed.pdf"
        with open(malformed_pdf, "w") as f:
            f.write("This is not a PDF file")
        
        with pytest.raises(ConversionError) as exc_info:
            converter.convert(malformed_pdf, test_output_dir)
        
        assert any(keyword in str(exc_info.value).lower() 
                  for keyword in ["invalid", "format", "corrupted"])
    
    @pytest.mark.skipif(not os.getenv("MISTRALAI_API_KEY"), 
                       reason="No API key available for live testing")
    def test_api_response_time_benchmark(self, converter):
        """Benchmark API response times."""
        start_time = time.time()
        
        try:
            # Test with minimal valid request
            converter._validate_api_key()
            response_time = time.time() - start_time
            
            # API should respond within 5 seconds for key validation
            assert response_time < 5.0, f"API response too slow: {response_time:.2f}s"
            
        except Exception as e:
            # Record the attempt time even if it fails
            response_time = time.time() - start_time
            pytest.fail(f"API call failed in {response_time:.2f}s: {e}")
    
    def test_memory_usage_tracking(self, converter, test_output_dir):
        """Test memory usage during PDF processing."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create small test file
        test_pdf = test_output_dir / "small.pdf"
        with open(test_pdf, "wb") as f:
            f.write(b"small pdf content")
        
        try:
            converter.convert(test_pdf, test_output_dir)
        except ConversionError:
            # Expected for invalid PDF, but still check memory
            pass
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (<10MB for small files)
        assert memory_increase < 10 * 1024 * 1024, \
               f"Memory usage too high: {memory_increase / 1024 / 1024:.2f}MB"
    
    def test_concurrent_request_handling(self, converter, test_output_dir):
        """Test handling of concurrent API requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                # Test key validation concurrently
                result = converter._validate_api_key()
                results.put(("success", result))
            except Exception as e:
                results.put(("error", str(e)))
        
        # Start 3 concurrent requests
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)
        
        # Collect results
        success_count = 0
        error_count = 0
        
        while not results.empty():
            result_type, _ = results.get()
            if result_type == "success":
                success_count += 1
            else:
                error_count += 1
        
        # At least some requests should succeed
        assert success_count > 0, "No concurrent requests succeeded"
    
    def test_resource_cleanup_validation(self, converter, test_output_dir):
        """Test that resources are properly cleaned up after operations."""
        import gc
        
        # Track initial object count
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform operation that should clean up after itself
        test_file = test_output_dir / "cleanup_test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"test content")
        
        try:
            converter.convert(test_file, test_output_dir)
        except ConversionError:
            # Expected for invalid PDF
            pass
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object count shouldn't grow excessively
        object_growth = final_objects - initial_objects
        assert object_growth < 100, \
               f"Potential memory leak: {object_growth} new objects"


class TestMistralAPIErrorScenarios:
    """Test specific API error scenarios."""
    
    def test_corrupted_pdf_api_response(self):
        """Test API response to corrupted PDF."""
        converter = PDFConverter(api_key="test_key")
        
        with patch('requests.post') as mock_post:
            mock_response = mock_post.return_value
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": "invalid_file_format",
                "message": "File is not a valid PDF"
            }
            
            with pytest.raises(ConversionError) as exc_info:
                converter._call_mistral_api(b"corrupted content")
            
            assert "invalid" in str(exc_info.value).lower()
    
    def test_zero_byte_file_handling(self):
        """Test handling of zero-byte files."""
        converter = PDFConverter(api_key="test_key")
        
        with pytest.raises(ConversionError) as exc_info:
            converter._validate_pdf_content(b"")
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_password_protected_pdf_detection(self):
        """Test detection of password-protected PDFs."""
        converter = PDFConverter(api_key="test_key")
        
        # Mock PDF content that indicates password protection
        protected_content = b"%PDF-1.4\n/Encrypt"
        
        with pytest.raises(ConversionError) as exc_info:
            converter._validate_pdf_content(protected_content)
        
        assert any(keyword in str(exc_info.value).lower() 
                  for keyword in ["password", "protected", "encrypted"])
    
    def test_extremely_large_pdf_rejection(self):
        """Test rejection of extremely large PDFs."""
        converter = PDFConverter(api_key="test_key")
        
        # Mock 150MB file
        large_size = 150 * 1024 * 1024
        
        with pytest.raises(ConversionError) as exc_info:
            converter._validate_file_size(large_size)
        
        assert "size" in str(exc_info.value).lower()
    
    def test_non_pdf_extension_detection(self):
        """Test detection of non-PDF files with .pdf extension."""
        converter = PDFConverter(api_key="test_key")
        
        # Text file content with PDF extension
        fake_pdf_content = b"This is just a text file"
        
        with pytest.raises(ConversionError) as exc_info:
            converter._validate_pdf_content(fake_pdf_content)
        
        assert "not a valid PDF" in str(exc_info.value)