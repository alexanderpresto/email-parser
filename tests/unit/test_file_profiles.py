"""
Unit tests for file conversion profiles system.

Phase 4.5: Interactive File Conversion - Day 7+ Testing
Tests the file conversion profile management and configuration mapping.
"""

import pytest

from email_parser.cli.interactive_file import (
    ConversionProfile,
    ConvertibleFile,
    FileConversionProfileManager,
)
from email_parser.core.config import ProcessingConfig


class TestConversionProfile:
    """Test ConversionProfile dataclass."""

    def test_profile_creation(self):
        """Test creating a ConversionProfile instance."""
        profile = ConversionProfile(
            name="Test Profile",
            description="A test conversion profile",
            settings={
                "convert_pdf": True,
                "pdf_mode": "all",
                "convert_docx": True,
                "docx_chunking": True,
            },
            recommended_for=["testing", "development"],
        )

        assert profile.name == "Test Profile"
        assert profile.description == "A test conversion profile"
        assert profile.settings["convert_pdf"] is True
        assert profile.settings["pdf_mode"] == "all"
        assert profile.recommended_for == ["testing", "development"]

    def test_profile_settings_access(self):
        """Test accessing profile settings."""
        profile = ConversionProfile(
            name="Custom",
            description="Custom profile",
            settings={
                "convert_excel": True,
                "max_workers": 4,
                "docx_images": False,
            },
            recommended_for=[],
        )

        assert profile.settings.get("convert_excel") is True
        assert profile.settings.get("max_workers") == 4
        assert profile.settings.get("docx_images") is False
        assert profile.settings.get("non_existent", "default") == "default"


class TestFileConversionProfileManagerProfiles:
    """Test individual profiles in FileConversionProfileManager."""

    @pytest.fixture
    def manager(self):
        """Create a FileConversionProfileManager instance."""
        return FileConversionProfileManager()

    def test_ai_processing_profile(self, manager):
        """Test AI Processing profile configuration."""
        profile = manager.get_profile("ai_processing")

        assert profile is not None
        assert profile.name == "AI Processing"
        assert "LLM consumption" in profile.description

        # Check settings
        settings = profile.settings
        assert settings["convert_pdf"] is True
        assert settings["convert_docx"] is True
        assert settings["convert_excel"] is True
        assert settings["pdf_mode"] == "all"
        assert settings["docx_chunking"] is True
        assert settings["docx_metadata"] is True
        assert settings["docx_images"] is True
        assert settings["docx_chunk_size"] == 2000
        assert settings["docx_chunk_overlap"] == 200

        # Check recommendations
        assert "research" in profile.recommended_for
        assert "analysis" in profile.recommended_for
        assert "ai_training" in profile.recommended_for

    def test_document_archive_profile(self, manager):
        """Test Document Archive profile configuration."""
        profile = manager.get_profile("document_archive")

        assert profile is not None
        assert profile.name == "Document Archive"
        assert "archival" in profile.description

        # Check settings - should preserve everything
        settings = profile.settings
        assert settings["convert_pdf"] is True
        assert settings["convert_docx"] is True
        assert settings["convert_excel"] is True
        assert settings["pdf_mode"] == "all"
        assert settings["docx_chunking"] is False  # No chunking for archival
        assert settings["docx_metadata"] is True
        assert settings["docx_images"] is True
        assert settings["docx_styles"] is True
        assert settings["docx_comments"] is True

        # Check recommendations
        assert "archival" in profile.recommended_for
        assert "preservation" in profile.recommended_for
        assert "backup" in profile.recommended_for

    def test_quick_conversion_profile(self, manager):
        """Test Quick Conversion profile configuration."""
        profile = manager.get_profile("quick_conversion")

        assert profile is not None
        assert profile.name == "Quick Conversion"
        assert "Fast" in profile.description

        # Check settings - minimal features for speed
        settings = profile.settings
        assert settings["convert_pdf"] is True
        assert settings["convert_docx"] is True
        assert settings["convert_excel"] is True
        assert settings["pdf_mode"] == "text"  # Text only for speed
        assert settings["docx_chunking"] is False
        assert settings["docx_metadata"] is False
        assert settings["docx_images"] is False

        # Check recommendations
        assert "preview" in profile.recommended_for
        assert "testing" in profile.recommended_for
        assert "quick_review" in profile.recommended_for

    def test_research_mode_profile(self, manager):
        """Test Research Mode profile configuration."""
        profile = manager.get_profile("research_mode")

        assert profile is not None
        assert profile.name == "Research Mode"
        assert "research" in profile.description.lower()

        # Check settings - comprehensive extraction
        settings = profile.settings
        assert settings["convert_pdf"] is True
        assert settings["convert_docx"] is True
        assert settings["convert_excel"] is True
        assert settings["pdf_mode"] == "all"
        assert settings["docx_chunking"] is True
        assert settings["docx_metadata"] is True
        assert settings["docx_images"] is True
        assert settings["docx_styles"] is True
        assert settings["docx_comments"] is True
        assert settings["docx_chunk_strategy"] == "semantic"

        # Check recommendations
        assert "research" in profile.recommended_for
        assert "academic" in profile.recommended_for
        assert "detailed_analysis" in profile.recommended_for

    def test_batch_optimization_profile(self, manager):
        """Test Batch Optimization profile configuration."""
        profile = manager.get_profile("batch_optimization")

        assert profile is not None
        assert profile.name == "Batch Optimization"
        assert "high-throughput" in profile.description

        # Check settings - optimized for performance
        settings = profile.settings
        assert settings["convert_pdf"] is True
        assert settings["convert_docx"] is True
        assert settings["convert_excel"] is True
        assert settings["pdf_mode"] == "text"  # Text only for speed
        assert settings["docx_chunking"] is False
        assert settings["docx_metadata"] is False
        assert settings["docx_images"] is False
        assert settings["max_workers"] == 8  # Parallel processing

        # Check recommendations
        assert "bulk_processing" in profile.recommended_for
        assert "automation" in profile.recommended_for
        assert "high_volume" in profile.recommended_for


class TestProfileRecommendationLogic:
    """Test profile recommendation logic with various scenarios."""

    @pytest.fixture
    def manager(self):
        """Create a FileConversionProfileManager instance."""
        return FileConversionProfileManager()

    def test_recommend_empty_files(self, manager):
        """Test recommendation with empty file list."""
        recommendation = manager.recommend_profile([])
        # Should return default
        assert recommendation == "ai_processing"

    def test_recommend_single_small_file(self, manager):
        """Test recommendation for single small file."""
        files = [
            ConvertibleFile(
                path="/test/small.pdf",
                file_type="pdf",
                size=500 * 1024,  # 500KB
                estimated_conversion_time=1.0,
                complexity_indicators=[],
            )
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "ai_processing"  # Default for normal files

    def test_recommend_many_files(self, manager):
        """Test recommendation for many files (batch scenario)."""
        files = []
        for i in range(75):  # More than 50 files
            files.append(
                ConvertibleFile(
                    path=f"/test/file{i}.pdf",
                    file_type="pdf",
                    size=1 * 1024 * 1024,  # 1MB each
                    estimated_conversion_time=1.0,
                    complexity_indicators=[],
                )
            )

        recommendation = manager.recommend_profile(files)
        assert recommendation == "batch_optimization"

    def test_recommend_large_total_size(self, manager):
        """Test recommendation for large total file size."""
        files = [
            ConvertibleFile(
                path="/test/huge1.pdf",
                file_type="pdf",
                size=60 * 1024 * 1024,  # 60MB
                estimated_conversion_time=10.0,
                complexity_indicators=[],
            ),
            ConvertibleFile(
                path="/test/huge2.pdf",
                file_type="pdf",
                size=50 * 1024 * 1024,  # 50MB
                estimated_conversion_time=8.0,
                complexity_indicators=[],
            ),
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "quick_conversion"  # For files > 100MB total

    def test_recommend_complex_pdf_files(self, manager):
        """Test recommendation for complex PDF files."""
        files = [
            ConvertibleFile(
                path="/test/complex1.pdf",
                file_type="pdf",
                size=8 * 1024 * 1024,
                estimated_conversion_time=5.0,
                complexity_indicators=["complex", "large"],
            ),
            ConvertibleFile(
                path="/test/simple.docx",
                file_type="docx",
                size=1 * 1024 * 1024,
                estimated_conversion_time=1.0,
                complexity_indicators=[],
            ),
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "research_mode"  # Complex PDFs present

    def test_recommend_mixed_file_types(self, manager):
        """Test recommendation for mixed file types."""
        files = [
            ConvertibleFile(
                path="/test/doc.pdf",
                file_type="pdf",
                size=2 * 1024 * 1024,
                estimated_conversion_time=2.0,
                complexity_indicators=[],
            ),
            ConvertibleFile(
                path="/test/sheet.xlsx",
                file_type="excel",
                size=1 * 1024 * 1024,
                estimated_conversion_time=1.0,
                complexity_indicators=[],
            ),
            ConvertibleFile(
                path="/test/report.docx",
                file_type="docx",
                size=3 * 1024 * 1024,
                estimated_conversion_time=1.5,
                complexity_indicators=[],
            ),
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "ai_processing"  # Default for mixed normal files

    def test_recommendation_priority_order(self, manager):
        """Test that recommendation follows priority order."""
        # Priority should be: batch > size > complexity > default

        # Test 1: Many files with large size (batch should win)
        files = []
        for i in range(60):
            files.append(
                ConvertibleFile(
                    path=f"/test/file{i}.pdf",
                    file_type="pdf",
                    size=3 * 1024 * 1024,  # 3MB each = 180MB total
                    estimated_conversion_time=2.0,
                    complexity_indicators=[],
                )
            )

        recommendation = manager.recommend_profile(files)
        assert recommendation == "batch_optimization"  # Batch wins over size

        # Test 2: Few large complex files (size should win over complexity)
        files = [
            ConvertibleFile(
                path="/test/huge_complex.pdf",
                file_type="pdf",
                size=110 * 1024 * 1024,  # 110MB
                estimated_conversion_time=20.0,
                complexity_indicators=["complex"],
            )
        ]

        recommendation = manager.recommend_profile(files)
        assert recommendation == "quick_conversion"  # Size wins over complexity


class TestProfileToConfigMapping:
    """Test mapping profiles to ProcessingConfig."""

    def test_map_minimal_profile(self):
        """Test mapping minimal profile settings."""
        from email_parser.cli.interactive_file import InteractiveFileConverter

        converter = InteractiveFileConverter()

        profile_settings = {
            "convert_pdf": False,
            "convert_docx": False,
            "convert_excel": False,
        }

        config = converter._map_profile_to_config(profile_settings, "/output")

        assert config.output_directory == "/output"
        assert config.convert_pdf is False
        assert config.convert_docx is False
        assert config.convert_excel is False

    def test_map_comprehensive_profile(self):
        """Test mapping comprehensive profile settings."""
        from email_parser.cli.interactive_file import InteractiveFileConverter

        converter = InteractiveFileConverter()

        profile_settings = {
            "convert_pdf": True,
            "pdf_mode": "all",
            "convert_docx": True,
            "docx_chunking": True,
            "docx_metadata": True,
            "docx_images": True,
            "docx_styles": True,
            "docx_comments": True,
            "docx_chunk_size": 1500,
            "docx_chunk_overlap": 150,
            "docx_chunk_strategy": "semantic",
            "convert_excel": True,
            "performance": {
                "parallel_processing": True,
                "memory_limit_mb": 512,
            },
        }

        config = converter._map_profile_to_config(profile_settings, "/output")

        # Check PDF settings
        assert config.convert_pdf is True
        assert config.pdf_extraction_mode == "all"

        # Check DOCX settings
        assert config.convert_docx is True
        assert config.docx_conversion.enabled is True
        assert config.docx_conversion.enable_chunking is True
        assert config.docx_conversion.extract_metadata is True
        assert config.docx_conversion.extract_images is True
        assert config.docx_conversion.extract_styles is True
        assert config.docx_conversion.include_comments is True
        assert config.docx_conversion.max_chunk_tokens == 1500
        assert config.docx_conversion.chunk_overlap == 150
        assert config.docx_conversion.chunk_strategy == "semantic"

        # Check Excel settings
        assert config.convert_excel is True

        # Check performance settings
        assert config.enable_parallel_processing is True
        assert config.memory_limit_mb == 512

    def test_map_profile_with_partial_settings(self):
        """Test mapping profile with partial settings."""
        from email_parser.cli.interactive_file import InteractiveFileConverter

        converter = InteractiveFileConverter()

        profile_settings = {
            "convert_pdf": True,
            # pdf_mode not specified, should use default
            "convert_docx": True,
            "docx_chunking": True,
            # Other DOCX settings not specified
            "convert_excel": False,
        }

        config = converter._map_profile_to_config(profile_settings, "/output")

        # PDF should be enabled with default mode
        assert config.convert_pdf is True
        assert config.pdf_extraction_mode == "all"  # Default

        # DOCX should be enabled with chunking
        assert config.convert_docx is True
        assert config.docx_conversion.enabled is True
        assert config.docx_conversion.enable_chunking is True
        # Other settings should have defaults
        assert config.docx_conversion.extract_metadata is True  # Default
        assert config.docx_conversion.extract_images is False  # Not specified
        assert config.docx_conversion.max_chunk_tokens == 2000  # Default

        # Excel should be disabled
        assert config.convert_excel is False


class TestProfileValidation:
    """Test profile validation and edge cases."""

    def test_get_nonexistent_profile(self):
        """Test getting a profile that doesn't exist."""
        manager = FileConversionProfileManager()

        profile = manager.get_profile("nonexistent_profile")
        assert profile is None

    def test_profile_immutability(self):
        """Test that profiles cannot be modified after creation."""
        manager = FileConversionProfileManager()

        # Get a profile
        profile = manager.get_profile("ai_processing")
        original_name = profile.name

        # Try to modify (this should not affect the stored profile)
        profile.name = "Modified Name"

        # Get the profile again
        profile_again = manager.get_profile("ai_processing")
        assert profile_again.name == original_name

    def test_all_profiles_have_required_fields(self):
        """Test that all default profiles have required fields."""
        manager = FileConversionProfileManager()
        profiles = manager.get_profiles()

        for profile_key, profile in profiles.items():
            # Check required fields
            assert profile.name is not None and profile.name != ""
            assert profile.description is not None and profile.description != ""
            assert isinstance(profile.settings, dict)
            assert isinstance(profile.recommended_for, list)

            # Check converter flags
            assert "convert_pdf" in profile.settings
            assert "convert_docx" in profile.settings
            assert "convert_excel" in profile.settings

            # If PDF is enabled, check mode
            if profile.settings.get("convert_pdf"):
                assert "pdf_mode" in profile.settings
                assert profile.settings["pdf_mode"] in ["text", "all"]

    def test_profile_settings_consistency(self):
        """Test that profile settings are internally consistent."""
        manager = FileConversionProfileManager()
        profiles = manager.get_profiles()

        for profile_key, profile in profiles.items():
            settings = profile.settings

            # If DOCX chunking is enabled, chunk settings should be present
            if settings.get("docx_chunking"):
                if "docx_chunk_size" in settings:
                    assert isinstance(settings["docx_chunk_size"], int)
                    assert settings["docx_chunk_size"] > 0
                if "docx_chunk_overlap" in settings:
                    assert isinstance(settings["docx_chunk_overlap"], int)
                    assert settings["docx_chunk_overlap"] >= 0

            # If performance settings exist, they should be valid
            if "max_workers" in settings:
                assert isinstance(settings["max_workers"], int)
                assert settings["max_workers"] > 0

            # Quick conversion should have minimal features
            if profile_key == "quick_conversion":
                assert not settings.get("docx_chunking", False)
                assert not settings.get("docx_metadata", False)
                assert not settings.get("docx_images", False)

            # Archive profile should preserve everything
            if profile_key == "document_archive":
                assert not settings.get("docx_chunking", False)  # No chunking for archive
                assert settings.get("docx_metadata", False)
                assert settings.get("docx_images", False)
                assert settings.get("docx_styles", False)
                assert settings.get("docx_comments", False)