"""
Unit tests for InteractiveFileConverter class.

Phase 4.5: Interactive File Conversion - Day 7+ Testing
Tests the interactive file conversion interface and all its methods.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from rich.console import Console

from email_parser.cli.interactive_file import (
    ConversionProfile,
    ConvertibleFile,
    FileConversionProfileManager,
    FileDiscoveryResult,
    InteractiveFileConverter,
)
from email_parser.cli.file_converter import DirectFileConverter
from email_parser.utils.file_detector import FileTypeDetector


class TestConvertibleFile:
    """Test ConvertibleFile dataclass."""

    def test_convertible_file_creation(self):
        """Test creating a ConvertibleFile instance."""
        file = ConvertibleFile(
            path=Path("/test/document.pdf"),
            file_type="pdf",
            size=1024 * 1024,  # 1MB
            estimated_conversion_time=2.5,
            complexity_indicators=["large", "complex"],
        )

        assert file.path == Path("/test/document.pdf")
        assert file.file_type == "pdf"
        assert file.size == 1024 * 1024
        assert file.estimated_conversion_time == 2.5
        assert file.complexity_indicators == ["large", "complex"]
        assert file.size_mb == 1.0

    def test_size_mb_calculation(self):
        """Test size_mb property calculation."""
        file = ConvertibleFile(
            path=Path("/test/file.docx"),
            file_type="docx",
            size=5 * 1024 * 1024,  # 5MB
            estimated_conversion_time=1.0,
            complexity_indicators=[],
        )

        assert file.size_mb == 5.0


class TestFileDiscoveryResult:
    """Test FileDiscoveryResult dataclass."""

    def test_file_discovery_result_creation(self):
        """Test creating a FileDiscoveryResult instance."""
        files = [
            ConvertibleFile(
                path=Path("/test/doc1.pdf"),
                file_type="pdf",
                size=1024 * 1024,
                estimated_conversion_time=2.0,
                complexity_indicators=[],
            ),
            ConvertibleFile(
                path=Path("/test/doc2.docx"),
                file_type="docx",
                size=2 * 1024 * 1024,
                estimated_conversion_time=1.5,
                complexity_indicators=["complex"],
            ),
        ]

        result = FileDiscoveryResult(
            total_files=10,
            convertible_files=files,
            total_size=3 * 1024 * 1024,
            estimated_total_time=3.5,
            recommendations=["Use AI Processing profile"],
        )

        assert result.total_files == 10
        assert len(result.convertible_files) == 2
        assert result.total_size == 3 * 1024 * 1024
        assert result.total_size_mb == 3.0
        assert result.estimated_total_time == 3.5
        assert result.recommendations == ["Use AI Processing profile"]


class TestFileConversionProfileManager:
    """Test FileConversionProfileManager class."""

    def test_initialization(self):
        """Test profile manager initialization with default profiles."""
        manager = FileConversionProfileManager()

        assert len(manager.profiles) == 5
        assert "ai_processing" in manager.profiles
        assert "document_archive" in manager.profiles
        assert "quick_conversion" in manager.profiles
        assert "research_mode" in manager.profiles
        assert "batch_optimization" in manager.profiles

    def test_get_profiles(self):
        """Test getting all profiles."""
        manager = FileConversionProfileManager()
        profiles = manager.get_profiles()

        assert isinstance(profiles, dict)
        assert len(profiles) == 5
        for key, profile in profiles.items():
            assert isinstance(profile, ConversionProfile)
            assert profile.name
            assert profile.description
            assert isinstance(profile.settings, dict)
            assert isinstance(profile.recommended_for, list)

    def test_get_profile(self):
        """Test getting a specific profile."""
        manager = FileConversionProfileManager()

        # Test existing profile
        profile = manager.get_profile("ai_processing")
        assert profile is not None
        assert profile.name == "AI Processing"
        assert profile.settings["docx_chunking"] is True

        # Test non-existent profile
        profile = manager.get_profile("non_existent")
        assert profile is None

    def test_recommend_profile_batch_files(self):
        """Test profile recommendation for many files."""
        manager = FileConversionProfileManager()

        # Create many small files
        files = [
            ConvertibleFile(
                path=Path(f"/test/doc{i}.pdf"),
                file_type="pdf",
                size=1024 * 1024,  # 1MB each
                estimated_conversion_time=1.0,
                complexity_indicators=[],
            )
            for i in range(60)
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "batch_optimization"

    def test_recommend_profile_large_size(self):
        """Test profile recommendation for large total size."""
        manager = FileConversionProfileManager()

        # Create files with large total size
        files = [
            ConvertibleFile(
                path=Path("/test/large.pdf"),
                file_type="pdf",
                size=150 * 1024 * 1024,  # 150MB
                estimated_conversion_time=10.0,
                complexity_indicators=[],
            )
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "quick_conversion"

    def test_recommend_profile_complex_pdf(self):
        """Test profile recommendation for complex PDFs."""
        manager = FileConversionProfileManager()

        files = [
            ConvertibleFile(
                path=Path("/test/complex.pdf"),
                file_type="pdf",
                size=10 * 1024 * 1024,
                estimated_conversion_time=5.0,
                complexity_indicators=["complex"],
            )
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "research_mode"

    def test_recommend_profile_default(self):
        """Test default profile recommendation."""
        manager = FileConversionProfileManager()

        files = [
            ConvertibleFile(
                path=Path("/test/normal.docx"),
                file_type="docx",
                size=2 * 1024 * 1024,
                estimated_conversion_time=1.5,
                complexity_indicators=[],
            )
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "ai_processing"


class TestInteractiveFileConverter:
    """Test InteractiveFileConverter class."""

    @pytest.fixture
    def converter(self):
        """Create InteractiveFileConverter instance with mocked dependencies."""
        with patch("email_parser.cli.interactive_file.Console"):
            with patch("email_parser.cli.interactive_file.FileTypeDetector"):
                with patch("email_parser.cli.interactive_file.ProgressTracker"):
                    with patch("email_parser.cli.interactive_file.DirectFileConverter"):
                        converter = InteractiveFileConverter()
                        return converter

    def test_initialization(self, converter):
        """Test InteractiveFileConverter initialization."""
        assert converter.console is not None
        assert converter.file_detector is not None
        assert converter.progress_tracker is not None
        assert converter.profile_manager is not None
        assert converter.direct_converter is not None
        assert converter.error_handler is not None
        assert converter.file_selector is not None
        assert converter.quality_analyzer is not None

    def test_estimate_conversion_time_pdf(self, converter):
        """Test conversion time estimation for PDF files."""
        file_path = Path("/test/document.pdf")
        file_path.stat = Mock(return_value=Mock(st_size=5 * 1024 * 1024))  # 5MB

        converter.file_detector.detect_type.return_value = ("application/pdf", "pdf")

        time_estimate = converter._estimate_conversion_time(file_path)

        # Base time for PDF (2.0) + size factor (5MB * 0.3 = 1.5) = 3.5
        assert time_estimate == pytest.approx(3.5, rel=0.01)

    def test_estimate_conversion_time_docx(self, converter):
        """Test conversion time estimation for DOCX files."""
        file_path = Path("/test/document.docx")
        file_path.stat = Mock(return_value=Mock(st_size=2 * 1024 * 1024))  # 2MB

        converter.file_detector.detect_type.return_value = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "docx",
        )

        time_estimate = converter._estimate_conversion_time(file_path)

        # Base time for DOCX (1.5) + size factor (2MB * 0.3 = 0.6) = 2.1
        assert time_estimate == pytest.approx(2.1, rel=0.01)

    def test_analyze_complexity_large_pdf(self, converter):
        """Test complexity analysis for large PDF files."""
        file_path = Path("/test/large.pdf")
        file_path.stat = Mock(return_value=Mock(st_size=15 * 1024 * 1024))  # 15MB

        converter.file_detector.detect_type.return_value = ("application/pdf", "pdf")

        indicators = converter._analyze_complexity(file_path)

        assert "large" in indicators
        assert "complex" in indicators

    def test_analyze_complexity_small_file(self, converter):
        """Test complexity analysis for small files."""
        file_path = Path("/test/small.docx")
        file_path.stat = Mock(return_value=Mock(st_size=500 * 1024))  # 500KB

        converter.file_detector.detect_type.return_value = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "docx",
        )

        indicators = converter._analyze_complexity(file_path)

        assert len(indicators) == 0

    def test_generate_recommendations_large_set(self, converter):
        """Test recommendation generation for large file sets."""
        files = [
            ConvertibleFile(
                path=Path("/test/large.pdf"),
                file_type="pdf",
                size=120 * 1024 * 1024,  # 120MB
                estimated_conversion_time=10.0,
                complexity_indicators=[],
            )
        ]

        recommendations = converter._generate_recommendations(files)

        assert any("Large file set" in rec for rec in recommendations)
        assert any("Quick Conversion" in rec for rec in recommendations)

    def test_generate_recommendations_complex_docx(self, converter):
        """Test recommendation generation for complex DOCX files."""
        files = [
            ConvertibleFile(
                path=Path("/test/complex.docx"),
                file_type="docx",
                size=5 * 1024 * 1024,
                estimated_conversion_time=3.0,
                complexity_indicators=["complex"],
            )
        ]

        recommendations = converter._generate_recommendations(files)

        assert any("Complex DOCX" in rec for rec in recommendations)
        assert any("Research Mode" in rec for rec in recommendations)

    def test_generate_recommendations_batch(self, converter):
        """Test recommendation generation for batch processing."""
        files = [
            ConvertibleFile(
                path=Path(f"/test/doc{i}.pdf"),
                file_type="pdf",
                size=1 * 1024 * 1024,
                estimated_conversion_time=1.0,
                complexity_indicators=[],
            )
            for i in range(25)
        ]

        recommendations = converter._generate_recommendations(files)

        assert any("Large batch" in rec for rec in recommendations)
        assert any("Batch Optimization" in rec for rec in recommendations)

    @pytest.mark.asyncio
    async def test_scan_directory(self, converter):
        """Test directory scanning functionality."""
        test_dir = Path("/test/directory")

        # Mock file discovery
        mock_files = [
            Path("/test/directory/doc1.pdf"),
            Path("/test/directory/doc2.docx"),
            Path("/test/directory/image.jpg"),  # Not supported
            Path("/test/directory/data.xlsx"),
        ]

        # Mock rglob to return our test files
        test_dir.rglob = Mock(return_value=mock_files)

        # Mock file stats
        for file_path in mock_files:
            file_path.is_file = Mock(return_value=True)
            file_path.stat = Mock(return_value=Mock(st_size=2 * 1024 * 1024))  # 2MB each

        # Mock file type detection
        def mock_is_supported(path):
            return path.suffix in [".pdf", ".docx", ".xlsx"]

        def mock_detect_type(path):
            if path.suffix == ".pdf":
                return ("application/pdf", "pdf")
            elif path.suffix == ".docx":
                return (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "docx",
                )
            elif path.suffix == ".xlsx":
                return (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "excel",
                )
            else:
                return ("unknown", "unknown")

        converter.file_detector.is_supported.side_effect = mock_is_supported
        converter.file_detector.detect_type.side_effect = mock_detect_type

        result = await converter._scan_directory(test_dir)

        assert result.total_files == 4
        assert len(result.convertible_files) == 3  # PDF, DOCX, XLSX
        assert result.total_size == 6 * 1024 * 1024  # 3 files * 2MB
        assert result.total_size_mb == 6.0

    def test_map_profile_to_config(self, converter):
        """Test mapping conversion profile to ProcessingConfig."""
        profile_settings = {
            "convert_pdf": True,
            "pdf_mode": "all",
            "convert_docx": True,
            "docx_chunking": True,
            "docx_metadata": True,
            "docx_images": True,
            "docx_chunk_size": 2000,
            "docx_chunk_overlap": 200,
            "docx_chunk_strategy": "semantic",
            "convert_excel": True,
        }

        config = converter._map_profile_to_config(profile_settings, "/output")

        assert config.output_directory == "/output"
        assert config.convert_pdf is True
        assert config.pdf_extraction_mode == "all"
        assert config.convert_docx is True
        assert config.docx_conversion.enabled is True
        assert config.docx_conversion.enable_chunking is True
        assert config.docx_conversion.extract_metadata is True
        assert config.docx_conversion.extract_images is True
        assert config.docx_conversion.max_chunk_tokens == 2000
        assert config.docx_conversion.chunk_overlap == 200
        assert config.docx_conversion.chunk_strategy == "semantic"
        assert config.convert_excel is True

    def test_find_converted_file_pdf(self, converter):
        """Test finding converted PDF files."""
        original_path = Path("/test/document.pdf")
        output_dir = Path("/output")

        # Create mock directory structure
        pdf_dir = output_dir / "converted_pdf"
        pdf_dir.exists = Mock(return_value=True)

        # Mock converted file
        converted_file = pdf_dir / "document.md"
        converted_file.exists = Mock(return_value=True)

        # Mock iterdir to return our converted file
        pdf_dir.iterdir = Mock(return_value=[converted_file])

        result = converter._find_converted_file(original_path, output_dir, "pdf")

        assert result == converted_file

    def test_find_converted_file_not_found(self, converter):
        """Test finding converted file when it doesn't exist."""
        original_path = Path("/test/document.pdf")
        output_dir = Path("/output")

        # Mock directory doesn't exist
        pdf_dir = output_dir / "converted_pdf"
        pdf_dir.exists = Mock(return_value=False)

        result = converter._find_converted_file(original_path, output_dir, "pdf")

        assert result is None

    @pytest.mark.asyncio
    async def test_convert_with_profile_success(self, converter):
        """Test successful file conversion with profile."""
        file_path = Path("/test/document.pdf")
        profile = ConversionProfile(
            name="Test Profile",
            description="Test",
            settings={"convert_pdf": True, "pdf_mode": "all"},
            recommended_for=[],
        )
        output_dir = Path("/output")

        # Mock DirectFileConverter result
        mock_result = Mock(
            success=True,
            output_path=Path("/output/converted_pdf/document.md"),
            duration_seconds=2.5,
            error_message=None,
            metadata={"pages": 10},
        )

        converter.direct_converter.convert_file.return_value = mock_result

        result = await converter._convert_with_profile(file_path, profile, output_dir)

        assert result["success"] is True
        assert result["output_path"] == "/output/converted_pdf/document.md"
        assert result["duration"] == 2.5
        assert result["error"] is None
        assert result["metadata"]["pages"] == 10

    @pytest.mark.asyncio
    async def test_convert_with_profile_failure(self, converter):
        """Test failed file conversion with profile."""
        file_path = Path("/test/document.pdf")
        profile = ConversionProfile(
            name="Test Profile",
            description="Test",
            settings={"convert_pdf": True},
            recommended_for=[],
        )
        output_dir = Path("/output")

        # Mock DirectFileConverter to raise exception
        converter.direct_converter.convert_file.side_effect = Exception("Conversion failed")

        result = await converter._convert_with_profile(file_path, profile, output_dir)

        assert result["success"] is False
        assert result["error"] == "Conversion failed"
        assert result["duration"] == 0.0

    @pytest.mark.asyncio
    async def test_perform_conversion_with_retries(self, converter):
        """Test file conversion with retry logic."""
        files = [
            ConvertibleFile(
                path=Path("/test/doc.pdf"),
                file_type="pdf",
                size=1024 * 1024,
                estimated_conversion_time=2.0,
                complexity_indicators=[],
            )
        ]

        profile = ConversionProfile(
            name="Test", description="Test", settings={"convert_pdf": True}, recommended_for=[]
        )

        output_dir = Path("/output")
        output_dir.mkdir = Mock()

        # Mock conversion to fail once then succeed
        converter._convert_with_profile = AsyncMock()
        converter._convert_with_profile.side_effect = [
            {"success": False, "error": "Temporary failure"},
            {"success": True, "output_path": "/output/doc.md", "duration": 2.0},
        ]

        # Mock error handler to return recovery action
        converter.error_handler.handle_error = AsyncMock(return_value=True)

        # Mock console methods
        converter.console.print = Mock()

        # Mock Confirm.ask to skip quality analysis
        with patch("email_parser.cli.interactive_file.Confirm.ask", return_value=False):
            await converter._perform_conversion(files, profile, output_dir)

        # Verify retry happened
        assert converter._convert_with_profile.call_count == 2
        assert converter.error_handler.handle_error.called

    def test_display_file_info_single_file(self, converter):
        """Test displaying single file information."""
        file = ConvertibleFile(
            path=Path("/test/document.pdf"),
            file_type="pdf",
            size=5.5 * 1024 * 1024,
            estimated_conversion_time=3.2,
            complexity_indicators=["large", "complex"],
        )

        # Mock console print
        converter.console.print = Mock()

        converter._display_file_info([file])

        # Verify Panel was printed
        converter.console.print.assert_called_once()
        call_args = converter.console.print.call_args[0][0]
        # Verify it's a Panel (can't easily check exact content due to rich formatting)
        assert hasattr(call_args, "title")

    def test_display_recommendations(self, converter):
        """Test displaying recommendations."""
        recommendations = [
            "Use AI Processing profile for optimal results",
            "Consider batch processing for better performance",
        ]

        converter.console.print = Mock()

        converter._display_recommendations(recommendations)

        converter.console.print.assert_called_once()

    def test_display_discovery_results(self, converter):
        """Test displaying file discovery results."""
        files = [
            ConvertibleFile(
                path=Path("/test/doc1.pdf"),
                file_type="pdf",
                size=5 * 1024 * 1024,
                estimated_conversion_time=3.0,
                complexity_indicators=[],
            ),
            ConvertibleFile(
                path=Path("/test/doc2.pdf"),
                file_type="pdf",
                size=3 * 1024 * 1024,
                estimated_conversion_time=2.0,
                complexity_indicators=[],
            ),
            ConvertibleFile(
                path=Path("/test/doc3.docx"),
                file_type="docx",
                size=2 * 1024 * 1024,
                estimated_conversion_time=1.5,
                complexity_indicators=[],
            ),
        ]

        result = FileDiscoveryResult(
            total_files=5,
            convertible_files=files,
            total_size=10 * 1024 * 1024,
            estimated_total_time=6.5,
            recommendations=[],
        )

        converter.console.print = Mock()

        converter._display_discovery_results(result)

        # Should print table and summary
        assert converter.console.print.call_count >= 2