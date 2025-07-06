"""Edge case tests for DOCX converter."""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from email_parser.converters.docx_converter import DocxConverter
from email_parser.core.config import ProcessingConfig
from email_parser.exceptions.converter_exceptions import ConversionError


class TestDocxEdgeCases:
    """Test edge cases and error scenarios for DOCX converter."""
    
    @pytest.fixture
    def converter(self, temp_dir):
        """Create a DOCX converter instance."""
        config = ProcessingConfig(output_directory=str(temp_dir))
        config.docx_conversion.enabled = True
        config.docx_conversion.max_file_size = 10 * 1024 * 1024  # 10MB
        return DocxConverter(config)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_empty_file(self, converter, temp_dir):
        """Test handling of empty DOCX file."""
        empty_file = temp_dir / "empty.docx"
        empty_file.write_bytes(b"")
        
        with pytest.raises(ConversionError, match="File appears to be empty"):
            converter.convert(empty_file)
    
    def test_non_docx_file(self, converter, temp_dir):
        """Test handling of non-DOCX file with DOCX extension."""
        fake_docx = temp_dir / "fake.docx"
        fake_docx.write_text("This is not a DOCX file")
        
        with pytest.raises(ConversionError):
            converter.convert(fake_docx)
    
    def test_corrupted_docx_file(self, converter, temp_dir):
        """Test handling of corrupted DOCX file."""
        corrupted_file = temp_dir / "corrupted.docx"
        # Create a file that looks like a ZIP but is corrupted
        corrupted_file.write_bytes(b"PK\x03\x04" + b"corrupted_data" * 100)
        
        with pytest.raises(ConversionError):
            converter.convert(corrupted_file)
    
    def test_file_too_large(self, converter, temp_dir):
        """Test handling of files exceeding size limit."""
        large_file = temp_dir / "large.docx"
        # Create a file larger than the limit
        large_content = b"x" * (15 * 1024 * 1024)  # 15MB
        large_file.write_bytes(large_content)
        
        with pytest.raises(ConversionError, match="File size.*exceeds maximum"):
            converter.convert(large_file)
    
    def test_permission_denied(self, converter, temp_dir):
        """Test handling of permission denied errors."""
        restricted_file = temp_dir / "restricted.docx"
        restricted_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        with patch('pathlib.Path.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConversionError, match="Permission denied"):
                converter.convert(restricted_file)
    
    @patch('email_parser.converters.docx_converter.mammoth')
    def test_mammoth_conversion_error(self, mock_mammoth, converter, temp_dir):
        """Test handling of mammoth conversion errors."""
        test_file = temp_dir / "test.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        # Mock mammoth to raise an exception
        mock_mammoth.convert_to_markdown.side_effect = Exception("Mammoth conversion failed")
        
        with pytest.raises(ConversionError, match="Document conversion failed"):
            converter.convert(test_file)
    
    @patch('email_parser.converters.docx_converter.mammoth')
    def test_mammoth_with_severe_warnings(self, mock_mammoth, converter, temp_dir):
        """Test handling of severe mammoth warnings."""
        test_file = temp_dir / "test.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        # Mock mammoth to return result with severe warnings
        mock_result = Mock()
        mock_result.value = "# Test Document\nConverted content"
        mock_result.messages = [
            Mock(type="error", message="Severe error in document"),
            Mock(type="warning", message="Document structure issue")
        ]
        mock_mammoth.convert_to_markdown.return_value = mock_result
        
        # Should still succeed but log warnings
        result = converter.convert(test_file)
        assert result is not None
    
    def test_output_directory_creation_failure(self, converter, temp_dir):
        """Test handling of output directory creation failure."""
        test_file = temp_dir / "test.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        # Mock os.makedirs to fail
        with patch('email_parser.converters.docx_converter.os.makedirs', 
                  side_effect=OSError("Cannot create directory")):
            with pytest.raises(ConversionError):
                converter.convert(test_file)
    
    def test_memory_pressure_during_conversion(self, converter, temp_dir):
        """Test handling of memory pressure during conversion."""
        test_file = temp_dir / "test.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        with patch('email_parser.converters.docx_converter.mammoth') as mock_mammoth:
            # Mock mammoth to raise MemoryError
            mock_mammoth.convert_to_markdown.side_effect = MemoryError("Out of memory")
            
            with pytest.raises(ConversionError, match="Out of memory"):
                converter.convert(test_file)
    
    def test_unicode_handling_in_filename(self, converter, temp_dir):
        """Test handling of Unicode characters in filenames."""
        unicode_file = temp_dir / "тест_файл_中文.docx"
        unicode_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        with patch('email_parser.converters.docx_converter.mammoth') as mock_mammoth:
            mock_result = Mock()
            mock_result.value = "# Test Document\nUnicode content: тест 中文"
            mock_result.messages = []
            mock_mammoth.convert_to_markdown.return_value = mock_result
            
            result = converter.convert(unicode_file)
            assert result is not None
            
            # Check that output file has proper name handling
            assert "test" in result.name.lower()
    
    def test_very_long_filename(self, converter, temp_dir):
        """Test handling of very long filenames."""
        long_name = "a" * 200 + ".docx"
        long_file = temp_dir / long_name
        long_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        with patch('email_parser.converters.docx_converter.mammoth') as mock_mammoth:
            mock_result = Mock()
            mock_result.value = "# Test Document\nLong filename test"
            mock_result.messages = []
            mock_mammoth.convert_to_markdown.return_value = mock_result
            
            result = converter.convert(long_file)
            assert result is not None
            # Should truncate filename appropriately
            assert len(result.name) < 255
    
    def test_zero_byte_docx_file(self, converter, temp_dir):
        """Test handling of zero-byte DOCX file."""
        zero_file = temp_dir / "zero.docx"
        zero_file.touch()  # Create empty file
        
        with pytest.raises(ConversionError, match="File appears to be empty"):
            converter.convert(zero_file)
    
    def test_invalid_zip_structure(self, converter, temp_dir):
        """Test handling of DOCX with invalid ZIP structure."""
        invalid_zip = temp_dir / "invalid.docx"
        # Write data that looks like ZIP but isn't valid
        invalid_zip.write_bytes(b"PK\x03\x04\x00\x00invalid_zip_data")
        
        with pytest.raises(ConversionError):
            converter.convert(invalid_zip)
    
    def test_missing_document_xml(self, converter, temp_dir):
        """Test handling of DOCX missing document.xml."""
        # This would require creating a valid ZIP with missing document.xml
        # For now, mock the scenario
        test_file = temp_dir / "missing_doc.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        with patch('email_parser.converters.docx_converter.mammoth') as mock_mammoth:
            mock_mammoth.convert_to_markdown.side_effect = Exception("document.xml not found")
            
            with pytest.raises(ConversionError):
                converter.convert(test_file)
    
    def test_concurrent_file_access(self, converter, temp_dir):
        """Test handling of concurrent file access."""
        test_file = temp_dir / "concurrent.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        with patch('pathlib.Path.open', side_effect=FileNotFoundError("File in use")):
            with pytest.raises(ConversionError):
                converter.convert(test_file)
    
    def test_disk_space_exhaustion(self, converter, temp_dir):
        """Test handling of disk space exhaustion during output."""
        test_file = temp_dir / "test.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        with patch('email_parser.converters.docx_converter.mammoth') as mock_mammoth:
            mock_result = Mock()
            mock_result.value = "# Test Document\nContent"
            mock_result.messages = []
            mock_mammoth.convert_to_markdown.return_value = mock_result
            
            # Mock file writing to fail with disk full
            with patch('builtins.open', side_effect=OSError("No space left on device")):
                with pytest.raises(ConversionError):
                    converter.convert(test_file)
    
    def test_network_drive_timeout(self, converter, temp_dir):
        """Test handling of network drive timeouts."""
        # Simulate network drive path
        network_file = temp_dir / "network_file.docx"
        network_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        with patch('pathlib.Path.stat', side_effect=TimeoutError("Network timeout")):
            with pytest.raises(ConversionError):
                converter.convert(network_file)


class TestDocxGracefulDegradation:
    """Test graceful degradation scenarios."""
    
    @pytest.fixture
    def converter(self):
        """Create a DOCX converter instance."""
        config = ProcessingConfig()
        config.docx_conversion.enabled = True
        config.docx_conversion.extract_metadata = True
        config.docx_conversion.extract_styles = True
        config.docx_conversion.extract_images = True
        return DocxConverter(config)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @patch('email_parser.converters.docx.metadata_extractor.MetadataExtractor.extract')
    @patch('email_parser.converters.docx_converter.mammoth')
    def test_metadata_extraction_failure_graceful(self, mock_mammoth, mock_metadata, 
                                                   converter, temp_dir):
        """Test graceful handling when metadata extraction fails."""
        test_file = temp_dir / "test.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        # Mock successful mammoth conversion
        mock_result = Mock()
        mock_result.value = "# Test Document\nContent"
        mock_result.messages = []
        mock_mammoth.convert_to_markdown.return_value = mock_result
        
        # Mock metadata extraction to fail
        mock_metadata.side_effect = Exception("Metadata extraction failed")
        
        # Should still succeed without metadata
        result = converter.convert(test_file)
        assert result is not None
    
    @patch('email_parser.converters.docx.style_extractor.StyleExtractor.extract_styles')
    @patch('email_parser.converters.docx_converter.mammoth')
    def test_style_extraction_failure_graceful(self, mock_mammoth, mock_styles, 
                                                converter, temp_dir):
        """Test graceful handling when style extraction fails."""
        test_file = temp_dir / "test.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        # Mock successful mammoth conversion
        mock_result = Mock()
        mock_result.value = "# Test Document\nContent"
        mock_result.messages = []
        mock_mammoth.convert_to_markdown.return_value = mock_result
        
        # Mock style extraction to fail
        mock_styles.side_effect = Exception("Style extraction failed")
        
        # Should still succeed without styles
        result = converter.convert(test_file)
        assert result is not None
    
    @patch('email_parser.converters.docx.image_handler.ImageHandler.extract_images')
    @patch('email_parser.converters.docx_converter.mammoth')
    def test_image_extraction_failure_graceful(self, mock_mammoth, mock_images, 
                                                converter, temp_dir):
        """Test graceful handling when image extraction fails."""
        test_file = temp_dir / "test.docx"
        test_file.write_bytes(b"PK\x03\x04")  # Minimal ZIP header
        
        # Mock successful mammoth conversion
        mock_result = Mock()
        mock_result.value = "# Test Document\nContent"
        mock_result.messages = []
        mock_mammoth.convert_to_markdown.return_value = mock_result
        
        # Mock image extraction to fail
        mock_images.side_effect = Exception("Image extraction failed")
        
        # Should still succeed without images
        result = converter.convert(test_file)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])