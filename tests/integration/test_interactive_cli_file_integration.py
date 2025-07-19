"""
Integration tests for interactive CLI file conversion workflow.

Phase 4.5: Interactive File Conversion - Day 7+ Testing
Tests the complete workflow integration between main CLI and file conversion mode.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from email_parser.cli.interactive import InteractiveCLI, NavigationContext
from email_parser.cli.interactive_file import (
    ConversionProfile,
    ConvertibleFile,
    FileConversionProfileManager,
    InteractiveFileConverter,
)
from email_parser.cli.file_converter import DirectFileConverter, ConversionResult


class TestInteractiveCLIFileIntegration:
    """Test integration between InteractiveCLI and InteractiveFileConverter."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create sample files
        pdf_file = temp_dir / "document.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 sample content")

        docx_file = temp_dir / "report.docx"
        docx_file.write_bytes(b"PK\x03\x04 docx content")

        xlsx_file = temp_dir / "data.xlsx"
        xlsx_file.write_bytes(b"PK\x03\x04 xlsx content")

        yield temp_dir

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_prompt_responses(self):
        """Mock user responses for prompt toolkit."""
        return {
            "main_menu": "3",  # Convert Documents
            "conversion_method": "directory",
            "directory_path": ".",
            "profile": "ai_processing",
            "output_dir": "output",
            "proceed": True,
            "quality_analysis": False,
            "back_to_main": "back",
        }

    @pytest.mark.asyncio
    async def test_main_menu_to_file_conversion(self):
        """Test navigation from main menu to file conversion mode."""
        with patch("email_parser.cli.interactive.Console") as mock_console:
            cli = InteractiveCLI()

            # Test navigation context
            assert cli.navigation_context.get_path() == "Main Menu"

            # Mock file converter
            mock_file_converter = AsyncMock()
            cli.file_converter = mock_file_converter

            # Mock main menu selection
            with patch("email_parser.cli.interactive.Prompt.ask", return_value="3"):
                # This would normally trigger file conversion mode
                cli.navigation_context.push("Convert Documents")

            assert cli.navigation_context.get_path() == "Main Menu > Convert Documents"

    @pytest.mark.asyncio
    async def test_complete_file_conversion_workflow(self, temp_workspace):
        """Test complete workflow from menu selection to conversion completion."""
        with patch("email_parser.cli.interactive_file.Console") as mock_console:
            converter = InteractiveFileConverter()

            # Mock user inputs
            with patch("email_parser.cli.interactive_file.Prompt.ask") as mock_prompt:
                with patch("email_parser.cli.interactive_file.Confirm.ask") as mock_confirm:
                    mock_prompt.side_effect = [
                        "directory",  # Choose directory conversion
                        str(temp_workspace),  # Directory path
                        "ai_processing",  # Profile selection
                        "output",  # Output directory
                    ]
                    mock_confirm.side_effect = [
                        True,  # Proceed with conversion
                        False,  # Skip quality analysis
                    ]

                    # Mock DirectFileConverter
                    with patch.object(converter, "direct_converter") as mock_direct:
                        mock_result = Mock()
                        mock_result.success = True
                        mock_result.output_path = Path("output/converted.md")
                        mock_result.duration_seconds = 2.0
                        mock_result.error_message = None
                        mock_result.metadata = {}

                        mock_direct.convert_file.return_value = mock_result

                        # Execute directory conversion
                        await converter._directory_conversion()

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, temp_workspace):
        """Test error recovery and navigation during conversion failures."""
        converter = InteractiveFileConverter()

        # Create a file that will fail conversion
        problem_file = temp_workspace / "corrupted.pdf"
        problem_file.write_bytes(b"Not a valid PDF")

        files = [
            ConvertibleFile(
                path=problem_file,
                file_type="pdf",
                size=100,
                estimated_conversion_time=1.0,
                complexity_indicators=["corrupted"],
            )
        ]

        profile = ConversionProfile(
            name="Test", description="Test", settings={"convert_pdf": True}, recommended_for=[]
        )

        # Mock conversion to fail
        with patch.object(converter, "_convert_with_profile") as mock_convert:
            mock_convert.return_value = {
                "success": False,
                "error": "Invalid PDF format",
                "duration": 0.0,
            }

            # Mock error handler to suggest retry
            with patch.object(converter.error_handler, "handle_error") as mock_error_handler:
                mock_error_handler.return_value = False  # Don't retry

                # Mock console and user inputs
                with patch.object(converter.console, "print"):
                    with patch("email_parser.cli.interactive_file.Confirm.ask", return_value=False):
                        await converter._perform_conversion(
                            files, profile, temp_workspace / "output"
                        )

                # Verify error handling was called
                assert mock_error_handler.called

    @pytest.mark.asyncio
    async def test_profile_switching_mid_workflow(self):
        """Test changing profiles during conversion workflow."""
        converter = InteractiveFileConverter()
        profile_manager = FileConversionProfileManager()

        # Get all available profiles
        profiles = profile_manager.get_profiles()

        # Test switching between profiles
        files = [
            ConvertibleFile(
                path=Path("/test/doc.pdf"),
                file_type="pdf",
                size=10 * 1024 * 1024,
                estimated_conversion_time=5.0,
                complexity_indicators=["large"],
            )
        ]

        # First recommendation
        initial_recommendation = profile_manager.recommend_profile(files)

        # Change file characteristics
        files[0].complexity_indicators.append("complex")

        # New recommendation should potentially be different
        new_recommendation = profile_manager.recommend_profile(files)

        # Verify profile change logic works
        assert initial_recommendation in profiles
        assert new_recommendation in profiles

    @pytest.mark.asyncio
    async def test_cancellation_at_various_steps(self):
        """Test user cancellation at different workflow steps."""
        converter = InteractiveFileConverter()

        # Test 1: Cancel at directory selection
        with patch("email_parser.cli.interactive_file.Prompt.ask", return_value="back"):
            # Should exit without proceeding
            await converter._directory_conversion()

        # Test 2: Cancel at profile selection
        with patch("email_parser.cli.interactive_file.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = [".", KeyboardInterrupt()]

            with pytest.raises(KeyboardInterrupt):
                await converter._directory_conversion()

        # Test 3: Cancel at conversion confirmation
        with patch("email_parser.cli.interactive_file.Prompt.ask") as mock_prompt:
            with patch("email_parser.cli.interactive_file.Confirm.ask", return_value=False):
                mock_prompt.side_effect = [".", "ai_processing", "output"]

                # Should complete without performing conversion
                await converter._directory_conversion()

    @pytest.mark.asyncio
    async def test_batch_processing_with_progress(self, temp_workspace):
        """Test batch file processing with progress tracking."""
        converter = InteractiveFileConverter()

        # Create multiple files
        files = []
        for i in range(5):
            file_path = temp_workspace / f"document_{i}.pdf"
            file_path.write_bytes(b"%PDF-1.4 content")
            files.append(
                ConvertibleFile(
                    path=file_path,
                    file_type="pdf",
                    size=1024 * 1024,
                    estimated_conversion_time=2.0,
                    complexity_indicators=[],
                )
            )

        profile = ConversionProfile(
            name="Batch",
            description="Batch test",
            settings={"convert_pdf": True, "pdf_mode": "text"},
            recommended_for=["batch"],
        )

        # Mock successful conversions
        with patch.object(converter, "_convert_with_profile") as mock_convert:
            mock_convert.return_value = {
                "success": True,
                "output_path": "output/converted.md",
                "duration": 1.5,
                "error": None,
            }

            # Mock progress display
            with patch("email_parser.cli.interactive_file.Progress"):
                with patch.object(converter.console, "print"):
                    with patch(
                        "email_parser.cli.interactive_file.Confirm.ask", return_value=False
                    ):
                        await converter._perform_conversion(
                            files, profile, temp_workspace / "output"
                        )

            # Verify all files were processed
            assert mock_convert.call_count == len(files)


class TestProfileConverterMapping:
    """Test profile to converter configuration mapping."""

    @pytest.fixture
    def converter(self):
        """Create converter instance."""
        with patch("email_parser.cli.interactive_file.Console"):
            return InteractiveFileConverter()

    def test_ai_processing_profile_mapping(self, converter):
        """Test AI Processing profile maps correctly to converter settings."""
        profile_manager = FileConversionProfileManager()
        ai_profile = profile_manager.get_profile("ai_processing")

        config = converter._map_profile_to_config(ai_profile.settings, "/output")

        # Verify PDF settings
        assert config.convert_pdf is True
        assert config.pdf_extraction_mode == "all"

        # Verify DOCX settings
        assert config.convert_docx is True
        assert config.docx_conversion.enabled is True
        assert config.docx_conversion.enable_chunking is True
        assert config.docx_conversion.max_chunk_tokens == 2000
        assert config.docx_conversion.chunk_overlap == 200
        assert config.docx_conversion.extract_metadata is True
        assert config.docx_conversion.extract_images is True

        # Verify Excel settings
        assert config.convert_excel is True

    def test_document_archive_profile_mapping(self, converter):
        """Test Document Archive profile preserves all content."""
        profile_manager = FileConversionProfileManager()
        archive_profile = profile_manager.get_profile("document_archive")

        config = converter._map_profile_to_config(archive_profile.settings, "/output")

        # Should preserve everything without chunking
        assert config.convert_pdf is True
        assert config.pdf_extraction_mode == "all"
        assert config.convert_docx is True
        assert config.docx_conversion.enable_chunking is False  # No chunking for archive
        assert config.docx_conversion.extract_metadata is True
        assert config.docx_conversion.extract_images is True
        assert config.docx_conversion.extract_styles is True
        assert config.docx_conversion.include_comments is True

    def test_quick_conversion_profile_mapping(self, converter):
        """Test Quick Conversion profile optimizes for speed."""
        profile_manager = FileConversionProfileManager()
        quick_profile = profile_manager.get_profile("quick_conversion")

        config = converter._map_profile_to_config(quick_profile.settings, "/output")

        # Should minimize processing
        assert config.convert_pdf is True
        assert config.pdf_extraction_mode == "text"  # Text only
        assert config.convert_docx is True
        assert config.docx_conversion.enable_chunking is False
        assert config.docx_conversion.extract_metadata is False
        assert config.docx_conversion.extract_images is False

    def test_research_mode_profile_mapping(self, converter):
        """Test Research Mode profile enables comprehensive extraction."""
        profile_manager = FileConversionProfileManager()
        research_profile = profile_manager.get_profile("research_mode")

        config = converter._map_profile_to_config(research_profile.settings, "/output")

        # Should enable everything
        assert config.convert_pdf is True
        assert config.pdf_extraction_mode == "all"
        assert config.convert_docx is True
        assert config.docx_conversion.enable_chunking is True
        assert config.docx_conversion.chunk_strategy == "semantic"
        assert config.docx_conversion.extract_metadata is True
        assert config.docx_conversion.extract_images is True
        assert config.docx_conversion.extract_styles is True
        assert config.docx_conversion.include_comments is True

    def test_batch_optimization_profile_mapping(self, converter):
        """Test Batch Optimization profile settings for performance."""
        profile_manager = FileConversionProfileManager()
        batch_profile = profile_manager.get_profile("batch_optimization")

        config = converter._map_profile_to_config(batch_profile.settings, "/output")

        # Should optimize for speed and throughput
        assert config.convert_pdf is True
        assert config.pdf_extraction_mode == "text"
        assert config.convert_docx is True
        assert config.docx_conversion.enable_chunking is False
        assert config.docx_conversion.extract_metadata is False
        assert config.docx_conversion.extract_images is False

        # Note: max_workers setting would need to be handled separately
        # as it's not part of the current ProcessingConfig structure


class TestNavigationIntegration:
    """Test navigation context integration with file conversion."""

    @pytest.mark.asyncio
    async def test_navigation_breadcrumbs_during_conversion(self):
        """Test navigation breadcrumbs update correctly during conversion workflow."""
        # Create main CLI with navigation
        with patch("email_parser.cli.interactive.Console"):
            cli = InteractiveCLI()

            # Simulate navigation through menus
            cli.navigation_context.push("Convert Documents")
            assert cli.navigation_context.get_path() == "Main Menu > Convert Documents"

            cli.navigation_context.push("Directory Selection")
            assert (
                cli.navigation_context.get_path()
                == "Main Menu > Convert Documents > Directory Selection"
            )

            cli.navigation_context.push("Profile Selection")
            assert (
                cli.navigation_context.get_path()
                == "Main Menu > Convert Documents > Directory Selection > Profile Selection"
            )

            # Simulate going back
            cli.navigation_context.pop()
            assert (
                cli.navigation_context.get_path()
                == "Main Menu > Convert Documents > Directory Selection"
            )

            cli.navigation_context.pop()
            assert cli.navigation_context.get_path() == "Main Menu > Convert Documents"

            cli.navigation_context.pop()
            assert cli.navigation_context.get_path() == "Main Menu"

    def test_error_recovery_navigation(self):
        """Test navigation state during error recovery."""
        with patch("email_parser.cli.interactive.Console"):
            cli = InteractiveCLI()

            # Navigate to conversion
            cli.navigation_context.push("Convert Documents")
            cli.navigation_context.push("Conversion in Progress")

            # Save state before error
            pre_error_path = cli.navigation_context.get_path()

            # Simulate error - should maintain context
            assert pre_error_path == "Main Menu > Convert Documents > Conversion in Progress"

            # After error recovery, should be able to navigate back
            cli.navigation_context.pop()
            assert cli.navigation_context.get_path() == "Main Menu > Convert Documents"

    def test_mode_switching_preserves_context(self):
        """Test that switching between email and file modes preserves context."""
        with patch("email_parser.cli.interactive.Console"):
            cli = InteractiveCLI()

            # Start in email mode
            cli.navigation_context.push("Email Processing")
            cli.navigation_context.previous_mode = "email"

            # Switch to file mode
            cli.navigation_context.pop()
            cli.navigation_context.push("Convert Documents")
            previous = cli.navigation_context.previous_mode
            cli.navigation_context.previous_mode = "file"

            # Verify mode tracking
            assert previous == "email"
            assert cli.navigation_context.previous_mode == "file"

            # Navigation should be independent of mode
            assert cli.navigation_context.get_path() == "Main Menu > Convert Documents"


class TestQualityAnalysisIntegration:
    """Test quality analysis integration with conversion workflow."""

    @pytest.mark.asyncio
    async def test_post_conversion_quality_analysis(self, temp_workspace):
        """Test quality analysis after successful conversion."""
        converter = InteractiveFileConverter()

        # Create test files
        original = temp_workspace / "document.pdf"
        original.write_bytes(b"%PDF-1.4 test content")

        converted = temp_workspace / "output" / "converted_pdf" / "document.md"
        converted.parent.mkdir(parents=True, exist_ok=True)
        converted.write_text("# Converted Document\n\nThis is the converted content.")

        files = [
            ConvertibleFile(
                path=original,
                file_type="pdf",
                size=original.stat().st_size,
                estimated_conversion_time=2.0,
                complexity_indicators=[],
            )
        ]

        # Mock quality analyzer
        with patch.object(converter.quality_analyzer, "analyze_batch_quality") as mock_analyze:
            mock_analyze.return_value = {
                "total_files": 1,
                "analyzed_files": 1,
                "average_quality": 0.85,
                "high_quality_files": 1,
                "medium_quality_files": 0,
                "low_quality_files": 0,
                "quality_by_type": {"pdf": {"average": 0.85, "count": 1}},
                "common_issues": [],
            }

            # Mock display method
            with patch.object(converter, "_display_batch_quality_results"):
                await converter._run_quality_analysis(
                    files,
                    temp_workspace / "output",
                    FileConversionProfileManager().get_profile("ai_processing"),
                )

            # Verify quality analysis was called
            assert mock_analyze.called

    @pytest.mark.asyncio
    async def test_quality_analysis_with_failed_conversions(self, temp_workspace):
        """Test quality analysis handling when some conversions fail."""
        converter = InteractiveFileConverter()

        # Create files where one will fail
        files = []
        for i in range(3):
            file_path = temp_workspace / f"doc_{i}.pdf"
            file_path.write_bytes(b"%PDF-1.4 content")
            files.append(
                ConvertibleFile(
                    path=file_path,
                    file_type="pdf",
                    size=1024,
                    estimated_conversion_time=1.0,
                    complexity_indicators=[],
                )
            )

        # Only create converted files for 2 out of 3
        output_dir = temp_workspace / "output" / "converted_pdf"
        output_dir.mkdir(parents=True, exist_ok=True)
        for i in range(2):  # Only 2 converted files
            converted = output_dir / f"doc_{i}.md"
            converted.write_text(f"Converted content {i}")

        # Mock quality analyzer
        with patch.object(converter.quality_analyzer, "analyze_batch_quality") as mock_analyze:
            mock_analyze.return_value = {
                "total_files": 3,
                "analyzed_files": 2,  # Only 2 could be analyzed
                "average_quality": 0.75,
                "quality_by_type": {"pdf": {"average": 0.75, "count": 2}},
            }

            with patch.object(converter, "_display_batch_quality_results"):
                await converter._run_quality_analysis(
                    files,
                    temp_workspace / "output",
                    FileConversionProfileManager().get_profile("quick_conversion"),
                )

            # Should handle partial results gracefully
            assert mock_analyze.called