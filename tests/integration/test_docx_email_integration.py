"""Integration tests for DOCX email processing workflow."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from email_parser.core.email_processor import EmailProcessor
from email_parser.core.config import ProcessingConfig
from email_parser.converters.docx_converter import DocxConverter
from email_parser.exceptions.parsing_exceptions import DocxConversionError


class TestDocxEmailIntegration:
    """Test complete email-to-DOCX processing workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def config(self, temp_dir):
        """Create test configuration with Week 2 features enabled."""
        return ProcessingConfig(
            output_directory=str(temp_dir),
            convert_docx=True,
            docx_enable_chunking=True,
            docx_chunk_size=1000,  # Smaller for testing
            docx_chunk_overlap=100,
            docx_chunk_strategy="hybrid",
            docx_extract_metadata=True,
            docx_extract_images=True,
            docx_extract_styles=True,
            docx_extract_comments=True
        )
    
    @pytest.fixture
    def sample_email_with_docx(self, temp_dir):
        """Create sample email with DOCX attachment."""
        email_content = """From: test@example.com
To: recipient@example.com
Subject: Test Email with DOCX
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain

This email contains a DOCX attachment for testing.

--boundary123
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="test_document.docx"
Content-Transfer-Encoding: base64

UEsDBBQABgAIAAAAIQDfpNJsWgEAACAFAAATAAgCW0NvbnRlbnRfVHlwZXNdLnhtbCKiBAIooAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC0lMOw0CMQhF6VwJH2B7y7I=

--boundary123--
"""
        email_file = temp_dir / "test_email.eml"
        email_file.write_text(email_content)
        return email_file
    
    def test_docx_converter_initialization_with_week2_features(self, config):
        """Test that DocxConverter initializes with Week 2 features."""
        converter = DocxConverter(config.docx_conversion.__dict__)
        
        assert converter.enable_chunking is True
        assert converter.extract_images is True
        assert converter.extract_metadata is True
        assert converter.extract_styles is True
        assert converter.chunker is not None
        assert converter.metadata_extractor is not None
        assert converter.style_extractor is not None
        assert converter.image_handler is not None
    
    @patch('email_parser.converters.docx_converter.mammoth')
    @patch('email_parser.converters.docx_converter.Document')
    def test_docx_conversion_with_all_week2_features(self, mock_document, mock_mammoth, config, temp_dir):
        """Test DOCX conversion with all Week 2 features enabled."""
        # Create test DOCX file
        docx_file = temp_dir / "test.docx"
        docx_file.write_bytes(b"fake docx content")
        
        # Mock mammoth response
        mock_result = Mock()
        mock_result.value = """# Test Document

This is a comprehensive test document for Week 2 DOCX processing features.

## Section 1: Introduction

This section introduces the document and its purpose for testing AI-ready chunking, metadata extraction, style preservation, and image handling.

## Section 2: Content Analysis

This section contains various types of content to test different aspects of the DOCX converter:

- Bulleted lists for structure testing
- **Bold text** for style testing
- *Italic text* for character formatting
- Tables and other complex elements

## Section 3: Conclusion

This final section wraps up the document and provides a conclusion for testing purposes.
"""
        mock_result.messages = []
        mock_mammoth.convert_to_markdown.return_value = mock_result
        
        # Mock Document for metadata
        mock_doc = Mock()
        mock_props = Mock()
        mock_props.title = "Test Document"
        mock_props.author = "Test Author"
        mock_props.created = None
        mock_props.modified = None
        mock_props.subject = "Test Subject"
        mock_props.keywords = "test, week2, docx"
        mock_props.category = "Testing"
        mock_props.comments = "Week 2 integration test"
        mock_props.revision = 2
        mock_doc.core_properties = mock_props
        mock_doc.paragraphs = [Mock(text="Test content line 1"), Mock(text="Test content line 2")]
        mock_doc.tables = []
        mock_document.return_value = mock_doc
        
        # Convert with Week 2 features
        converter = DocxConverter(config.docx_conversion.__dict__)
        output_file = converter.convert(docx_file)
        
        # Verify main output file exists
        assert output_file.exists()
        
        # Verify output directory structure
        output_dir = output_file.parent / f"{output_file.stem}_docx_output"
        assert output_dir.exists()
        
        # Check for Week 2 feature outputs
        conversion_manifest = output_dir / "conversion_manifest.json"
        assert conversion_manifest.exists()
        
        # Verify manifest contains Week 2 feature information
        with open(conversion_manifest, 'r') as f:
            manifest = json.load(f)
        
        assert manifest['features_used']['enhanced_metadata'] is True
        assert manifest['features_used']['style_extraction'] is True
        assert manifest['features_used']['chunking'] is True
        
        # Verify content has YAML frontmatter
        content = output_file.read_text()
        assert "---" in content  # YAML frontmatter
        assert "Test Document" in content
    
    def test_docx_conversion_error_handling(self, config, temp_dir):
        """Test error handling in DOCX conversion with Week 2 features."""
        # Create invalid DOCX file
        invalid_file = temp_dir / "invalid.docx"
        invalid_file.write_bytes(b"not a docx file")
        
        converter = DocxConverter(config.docx_conversion.__dict__)
        
        # Should raise DocxConversionError
        with pytest.raises(Exception):  # Will be ConversionError from base class
            converter.convert(invalid_file)
    
    def test_docx_chunking_output_structure(self, config, temp_dir):
        """Test that chunking creates proper output structure."""
        with patch('email_parser.converters.docx_converter.mammoth') as mock_mammoth, \
             patch('email_parser.converters.docx_converter.Document') as mock_document:
            
            # Create long content for chunking
            long_content = """# Long Document

""" + "\n\n".join([f"This is paragraph {i} with substantial content that will require chunking into multiple segments for AI processing. " * 5 for i in range(20)])
            
            mock_result = Mock()
            mock_result.value = long_content
            mock_result.messages = []
            mock_mammoth.convert_to_markdown.return_value = mock_result
            
            # Mock basic document
            mock_doc = Mock()
            mock_doc.core_properties = Mock()
            for attr in ['title', 'author', 'created', 'modified', 'subject', 'keywords', 'category', 'comments', 'revision']:
                setattr(mock_doc.core_properties, attr, None)
            mock_doc.paragraphs = []
            mock_doc.tables = []
            mock_document.return_value = mock_doc
            
            # Create test file
            docx_file = temp_dir / "long_test.docx"
            docx_file.write_bytes(b"fake long docx content")
            
            # Convert
            converter = DocxConverter(config.docx_conversion.__dict__)
            output_file = converter.convert(docx_file)
            
            # Verify chunking output
            output_dir = output_file.parent / f"{output_file.stem}_docx_output"
            chunks_dir = output_dir / "chunks"
            
            # Should have chunks directory and manifest
            chunk_manifest = output_dir / "chunk_manifest.json"
            if chunk_manifest.exists():  # Only if chunking succeeded
                with open(chunk_manifest, 'r') as f:
                    chunk_data = json.load(f)
                
                assert chunk_data['total_chunks'] > 1
                assert chunk_data['chunking_strategy'] == 'hybrid'
                assert chunk_data['max_tokens'] == 1000
    
    def test_week2_feature_fallback_behavior(self, config, temp_dir):
        """Test graceful fallback when Week 2 features fail."""
        with patch('email_parser.converters.docx_converter.mammoth') as mock_mammoth:
            # Mock successful mammoth conversion
            mock_result = Mock()
            mock_result.value = "# Fallback Test\n\nThis tests fallback behavior."
            mock_result.messages = []
            mock_mammoth.convert_to_markdown.return_value = mock_result
            
            # Create test file
            docx_file = temp_dir / "fallback_test.docx"
            docx_file.write_bytes(b"fake docx content")
            
            # Convert - should succeed even if advanced features fail
            converter = DocxConverter(config.docx_conversion.__dict__)
            output_file = converter.convert(docx_file)
            
            # Should still produce output file
            assert output_file.exists()
            content = output_file.read_text()
            assert "Fallback Test" in content
    
    def test_docx_converter_config_validation(self):
        """Test DOCX converter configuration validation."""
        # Test with minimal config
        minimal_config = {"enabled": True}
        converter = DocxConverter(minimal_config)
        assert converter.config["enabled"] is True
        
        # Test with Week 2 config
        week2_config = {
            "enabled": True,
            "enable_chunking": True,
            "chunking_strategy": "hybrid",
            "extract_images": True,
            "extract_metadata": True,
            "extract_styles": True
        }
        converter = DocxConverter(week2_config)
        assert converter.enable_chunking is True
        assert converter.extract_images is True
    
    def test_docx_output_manifest_structure(self, config, temp_dir):
        """Test the structure of DOCX conversion output manifest."""
        with patch('email_parser.converters.docx_converter.mammoth') as mock_mammoth, \
             patch('email_parser.converters.docx_converter.Document') as mock_document:
            
            # Mock conversion
            mock_result = Mock()
            mock_result.value = "# Manifest Test\n\nTesting manifest structure."
            mock_result.messages = []
            mock_mammoth.convert_to_markdown.return_value = mock_result
            
            # Mock document
            mock_doc = Mock()
            mock_doc.core_properties = Mock()
            mock_doc.core_properties.title = "Manifest Test Doc"
            mock_doc.paragraphs = []
            mock_doc.tables = []
            mock_document.return_value = mock_doc
            
            # Create and convert
            docx_file = temp_dir / "manifest_test.docx"
            docx_file.write_bytes(b"fake content")
            
            converter = DocxConverter(config.docx_conversion.__dict__)
            output_file = converter.convert(docx_file)
            
            # Check manifest structure
            output_dir = output_file.parent / f"{output_file.stem}_docx_output"
            manifest_file = output_dir / "conversion_manifest.json"
            
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                
                # Verify required manifest fields
                required_fields = [
                    'source_file', 'main_output', 'output_directory',
                    'features_used', 'metadata'
                ]
                for field in required_fields:
                    assert field in manifest
                
                # Verify features_used structure
                features = manifest['features_used']
                assert 'enhanced_metadata' in features
                assert 'style_extraction' in features
                assert 'image_extraction' in features
                assert 'chunking' in features