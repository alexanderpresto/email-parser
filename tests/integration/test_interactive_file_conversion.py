"""
Integration tests for Phase 4.5 Interactive File Conversion functionality.

Tests the complete integration of DirectFileConverter with Interactive CLI components
including error handling, file selection, and quality analysis.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import shutil

from email_parser.cli.interactive_file import (
    InteractiveFileConverter, 
    ConvertibleFile, 
    ConversionProfile,
    FileConversionProfileManager
)
from email_parser.cli.components.error_handler import ConversionErrorHandler, ErrorType
from email_parser.cli.components.file_selector import CustomFileSelector
from email_parser.cli.components.quality_analyzer import ConversionQualityAnalyzer


class TestInteractiveFileConversion:
    """Test suite for interactive file conversion integration."""
    
    @pytest.fixture
    def mock_console(self):
        """Mock console for testing."""
        return Mock()
    
    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_files(self, temp_directory):
        """Create sample files for testing."""
        files = []
        
        # Create sample PDF file
        pdf_file = temp_directory / "sample.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 sample content")
        files.append(pdf_file)
        
        # Create sample DOCX file
        docx_file = temp_directory / "sample.docx"
        docx_file.write_bytes(b"PK\x03\x04 sample docx content")
        files.append(docx_file)
        
        # Create sample Excel file
        xlsx_file = temp_directory / "sample.xlsx"
        xlsx_file.write_bytes(b"PK\x03\x04 sample xlsx content")
        files.append(xlsx_file)
        
        return files
    
    @pytest.fixture
    def converter(self, mock_console):
        """Create InteractiveFileConverter instance."""
        with patch('email_parser.cli.interactive_file.Console') as mock_console_class:
            mock_console_class.return_value = mock_console
            converter = InteractiveFileConverter()
            return converter
    
    def test_converter_initialization(self, converter):
        """Test that InteractiveFileConverter initializes all components."""
        assert converter.console is not None
        assert converter.file_detector is not None
        assert converter.progress_tracker is not None
        assert converter.profile_manager is not None
        assert converter.direct_converter is not None
        assert converter.error_handler is not None
        assert converter.file_selector is not None
        assert converter.quality_analyzer is not None
    
    def test_profile_to_config_mapping(self, converter):
        """Test profile settings mapping to ProcessingConfig."""
        profile_manager = FileConversionProfileManager()
        ai_profile = profile_manager.profiles["ai_processing"]
        
        config = converter._map_profile_to_config(ai_profile.settings, "output")
        
        assert config.convert_pdf == True
        assert config.convert_docx == True
        assert config.convert_excel == True
        assert config.docx_conversion.enable_chunking == True
        assert config.docx_conversion.max_chunk_tokens == 2000
        assert config.docx_conversion.chunk_overlap == 200
    
    @pytest.mark.asyncio
    async def test_convert_with_profile_success(self, converter, temp_directory):
        """Test successful file conversion with profile."""
        # Create test file
        test_file = temp_directory / "test.txt"
        test_file.write_text("Test content")
        
        # Create test profile
        test_profile = ConversionProfile(
            name="test",
            description="Test profile",
            settings={
                "convert_pdf": False,
                "convert_docx": False,
                "convert_excel": False
            },
            recommended_for=[]
        )
        
        # Mock DirectFileConverter
        with patch.object(converter, 'direct_converter') as mock_converter:
            mock_result = Mock()
            mock_result.success = True
            mock_result.output_path = temp_directory / "output.txt"
            mock_result.duration_seconds = 1.5
            mock_result.error_message = None
            mock_result.metadata = {}
            
            mock_converter.convert_file.return_value = mock_result
            
            result = await converter._convert_with_profile(
                test_file, test_profile, temp_directory
            )
            
            assert result['success'] == True
            assert result['duration'] == 1.5
            assert 'output.txt' in result['output_path']
    
    @pytest.mark.asyncio
    async def test_convert_with_profile_failure(self, converter, temp_directory):
        """Test file conversion failure handling."""
        test_file = temp_directory / "test.txt"
        test_file.write_text("Test content")
        
        test_profile = ConversionProfile(
            name="test",
            description="Test profile",
            settings={},
            recommended_for=[]
        )
        
        # Mock DirectFileConverter to raise exception
        with patch.object(converter, 'direct_converter') as mock_converter:
            mock_converter.convert_file.side_effect = Exception("Conversion failed")
            
            result = await converter._convert_with_profile(
                test_file, test_profile, temp_directory
            )
            
            assert result['success'] == False
            assert "Conversion failed" in result['error']
    
    def test_find_converted_file(self, converter, temp_directory):
        """Test finding converted files."""
        # Create output directory structure
        pdf_dir = temp_directory / "converted_pdf"
        pdf_dir.mkdir()
        
        # Create converted file
        converted_file = pdf_dir / "sample.md"
        converted_file.write_text("Converted content")
        
        # Test finding the file
        original_file = temp_directory / "sample.pdf"
        found_file = converter._find_converted_file(
            original_file, temp_directory, "pdf"
        )
        
        assert found_file == converted_file
    
    def test_find_converted_file_not_found(self, converter, temp_directory):
        """Test behavior when converted file is not found."""
        original_file = temp_directory / "nonexistent.pdf"
        found_file = converter._find_converted_file(
            original_file, temp_directory, "pdf"
        )
        
        assert found_file is None


class TestErrorHandler:
    """Test suite for ConversionErrorHandler."""
    
    @pytest.fixture
    def mock_console(self):
        return Mock()
    
    @pytest.fixture
    def error_handler(self, mock_console):
        return ConversionErrorHandler(mock_console)
    
    def test_error_classification(self, error_handler):
        """Test error classification."""
        # Test API error
        from email_parser.exceptions.converter_exceptions import APIError
        api_error = APIError("API key missing")
        assert error_handler._classify_error(api_error) == ErrorType.API_ERROR
        
        # Test permission error
        perm_error = PermissionError("Access denied")
        assert error_handler._classify_error(perm_error) == ErrorType.FILE_ACCESS
        
        # Test memory error
        mem_error = MemoryError("Out of memory")
        assert error_handler._classify_error(mem_error) == ErrorType.MEMORY_ERROR
        
        # Test unknown error
        unknown_error = ValueError("Something went wrong")
        assert error_handler._classify_error(unknown_error) == ErrorType.UNKNOWN
    
    def test_recovery_strategies_initialization(self, error_handler):
        """Test that recovery strategies are properly initialized."""
        assert ErrorType.API_ERROR in error_handler.recovery_strategies
        assert ErrorType.FILE_ACCESS in error_handler.recovery_strategies
        assert ErrorType.MEMORY_ERROR in error_handler.recovery_strategies
        assert ErrorType.DISK_SPACE in error_handler.recovery_strategies
        
        # Check that each error type has recovery actions
        for error_type, actions in error_handler.recovery_strategies.items():
            assert len(actions) > 0
            for action in actions:
                assert action.action_type
                assert action.description


class TestFileSelector:
    """Test suite for CustomFileSelector."""
    
    @pytest.fixture
    def mock_console(self):
        return Mock()
    
    @pytest.fixture
    def file_selector(self, mock_console):
        return CustomFileSelector(mock_console)
    
    @pytest.fixture
    def sample_files(self, tmp_path):
        """Create sample files for testing."""
        files = []
        
        # Create files of different types and sizes
        for i in range(5):
            file_path = tmp_path / f"file_{i}.txt"
            file_path.write_text(f"Content {i} " * (i + 1) * 100)
            files.append(file_path)
        
        # Create a PDF file
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 content")
        files.append(pdf_file)
        
        return files
    
    @pytest.mark.asyncio
    async def test_gather_file_metadata(self, file_selector, sample_files):
        """Test file metadata gathering."""
        await file_selector._gather_file_metadata(sample_files)
        
        assert len(file_selector._file_metadata) == len(sample_files)
        
        for file_path in sample_files:
            assert file_path in file_selector._file_metadata
            metadata = file_selector._file_metadata[file_path]
            assert metadata.path == file_path
            assert metadata.size > 0
            assert metadata.file_type is not None
    
    def test_complexity_calculation(self, file_selector, tmp_path):
        """Test file complexity calculation."""
        # Create files of different sizes
        small_file = tmp_path / "small.txt"
        small_file.write_text("small content")
        
        large_file = tmp_path / "large.txt"
        large_file.write_text("content " * 10000)  # Large file
        
        small_complexity = file_selector._calculate_complexity(
            small_file, small_file.stat().st_size, "txt"
        )
        large_complexity = file_selector._calculate_complexity(
            large_file, large_file.stat().st_size, "txt"
        )
        
        assert 0 <= small_complexity <= 1
        assert 0 <= large_complexity <= 1
        assert large_complexity >= small_complexity
    
    def test_time_estimation(self, file_selector):
        """Test conversion time estimation."""
        # Test different file types
        pdf_time = file_selector._estimate_conversion_time(1024*1024, "pdf", 0.5)  # 1MB PDF
        docx_time = file_selector._estimate_conversion_time(1024*1024, "docx", 0.5)  # 1MB DOCX
        
        assert pdf_time > 0
        assert docx_time > 0
        assert pdf_time > docx_time  # PDF should take longer due to OCR


class TestQualityAnalyzer:
    """Test suite for ConversionQualityAnalyzer."""
    
    @pytest.fixture
    def mock_console(self):
        return Mock()
    
    @pytest.fixture
    def quality_analyzer(self, mock_console):
        return ConversionQualityAnalyzer(mock_console)
    
    def test_text_quality_assessment(self, quality_analyzer):
        """Test text quality assessment."""
        # Test high quality text
        good_text = "This is a well-formed document with proper sentences and varied vocabulary."
        good_quality = quality_analyzer._assess_text_quality(good_text)
        
        # Test low quality text
        bad_text = "aaaaaaaaaa bbbbbbbbb ccccccccc"  # Repetitive text
        bad_quality = quality_analyzer._assess_text_quality(bad_text)
        
        # Test empty text
        empty_quality = quality_analyzer._assess_text_quality("")
        
        assert 0 <= good_quality <= 1
        assert 0 <= bad_quality <= 1
        assert empty_quality == 0
        assert good_quality > bad_quality
    
    @pytest.mark.asyncio
    async def test_analyze_conversion_pdf(self, quality_analyzer, tmp_path):
        """Test PDF conversion analysis."""
        # Create original and converted files
        original = tmp_path / "document.pdf"
        original.write_bytes(b"%PDF-1.4 content")
        
        converted = tmp_path / "document.md"
        converted.write_text("# Document Title\n\nThis is the converted content.")
        
        # Mock metadata
        metadata = {
            'ocr_confidence': 95,
            'pages_processed': 10,
            'total_pages': 10,
            'images_extracted': 2,
            'total_images': 3
        }
        
        report = await quality_analyzer.analyze_conversion(
            original, converted, "pdf", metadata
        )
        
        assert report.file_path == original
        assert report.converter_type == "pdf"
        assert 0 <= report.overall_score <= 1
        assert len(report.metrics) > 0
        assert any(m.name == "Text Quality" for m in report.metrics)
        assert any(m.name == "OCR Confidence" for m in report.metrics)
    
    @pytest.mark.asyncio
    async def test_analyze_conversion_file_not_found(self, quality_analyzer, tmp_path):
        """Test behavior when converted file doesn't exist."""
        original = tmp_path / "document.pdf"
        original.write_bytes(b"%PDF-1.4 content")
        
        nonexistent = tmp_path / "nonexistent.md"
        
        report = await quality_analyzer.analyze_conversion(
            original, nonexistent, "pdf", {}
        )
        
        assert report.overall_score == 0.0
        assert len(report.errors) > 0
        assert "not found" in report.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_batch_quality_analysis(self, quality_analyzer, tmp_path):
        """Test batch quality analysis."""
        # Create sample conversion results
        conversion_results = []
        
        for i in range(3):
            original = tmp_path / f"doc_{i}.pdf"
            original.write_bytes(b"%PDF-1.4 content")
            
            converted = tmp_path / f"doc_{i}.md"
            converted.write_text(f"Document {i} content " * 20)
            
            conversion_results.append({
                'success': True,
                'input_path': str(original),
                'output_path': str(converted),
                'converter_type': 'pdf',
                'metadata': {}
            })
        
        batch_analysis = await quality_analyzer.analyze_batch_quality(conversion_results)
        
        assert batch_analysis['total_files'] == 3
        assert batch_analysis['analyzed_files'] <= 3
        assert 'average_quality' in batch_analysis
        assert 'quality_by_type' in batch_analysis


@pytest.mark.integration
class TestFullIntegration:
    """Full integration tests combining all components."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with sample files."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample files
        (temp_dir / "sample.txt").write_text("Sample text content")
        (temp_dir / "document.md").write_text("# Document\n\nMarkdown content")
        
        # Create output directory
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        yield temp_dir, output_dir
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, temp_workspace):
        """Test complete end-to-end workflow simulation."""
        temp_dir, output_dir = temp_workspace
        
        with patch('email_parser.cli.interactive_file.Console'):
            converter = InteractiveFileConverter()
            
            # Test file discovery
            files = list(temp_dir.glob("*"))
            text_files = [f for f in files if f.is_file()]
            
            assert len(text_files) >= 2
            
            # Test profile mapping
            profile_manager = FileConversionProfileManager()
            test_profile = profile_manager.profiles["quick_conversion"]
            
            config = converter._map_profile_to_config(test_profile.settings, str(output_dir))
            
            assert config is not None
            assert config.output_directory == str(output_dir)
            
            # Test error handler initialization
            assert converter.error_handler is not None
            assert len(converter.error_handler.recovery_strategies) > 0
            
            # Test quality analyzer initialization
            assert converter.quality_analyzer is not None
            
            # This test verifies that all components can be initialized and
            # basic operations work without errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])