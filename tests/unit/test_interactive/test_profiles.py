"""Unit tests for the ProfileManager and processing profiles."""

import pytest
import tempfile
import json
from pathlib import Path

from email_parser.config.profiles import (
    ProfileManager,
    ProcessingProfile,
    BUILTIN_PROFILES
)


class TestProcessingProfile:
    """Test the ProcessingProfile class."""

    def test_profile_creation(self):
        """Test creating a processing profile."""
        settings = {
            "processing": {"convert_pdf": True},
            "performance": {"max_workers": 4}
        }
        
        profile = ProcessingProfile(
            name="test_profile",
            display_name="Test Profile",
            description="A test profile",
            settings=settings,
            priority=50,
            is_builtin=False
        )
        
        assert profile.name == "test_profile"
        assert profile.display_name == "Test Profile"
        assert profile.description == "A test profile"
        assert profile.settings == settings
        assert profile.priority == 50
        assert not profile.is_builtin
        assert not profile.is_default

    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        settings = {"processing": {"convert_pdf": True}}
        
        profile = ProcessingProfile(
            name="test",
            display_name="Test",
            description="Test profile",
            settings=settings
        )
        
        profile_dict = profile.to_dict()
        
        assert profile_dict["name"] == "test"
        assert profile_dict["display_name"] == "Test"
        assert profile_dict["description"] == "Test profile"
        assert profile_dict["settings"] == settings
        assert profile_dict["is_builtin"] is True
        assert profile_dict["is_default"] is False

    def test_profile_from_dict(self):
        """Test creating profile from dictionary."""
        profile_data = {
            "name": "test",
            "display_name": "Test Profile",
            "description": "A test profile",
            "settings": {"processing": {"convert_pdf": True}},
            "priority": 25,
            "is_builtin": False,
            "is_default": True
        }
        
        profile = ProcessingProfile.from_dict(profile_data)
        
        assert profile.name == "test"
        assert profile.display_name == "Test Profile"
        assert profile.description == "A test profile"
        assert profile.settings == {"processing": {"convert_pdf": True}}
        assert profile.priority == 25
        assert not profile.is_builtin
        assert profile.is_default


class TestBuiltinProfiles:
    """Test built-in profiles."""

    def test_builtin_profiles_exist(self):
        """Test that all expected built-in profiles exist."""
        expected_profiles = ["quick", "comprehensive", "ai_ready", "archive", "dev"]
        
        for profile_name in expected_profiles:
            assert profile_name in BUILTIN_PROFILES
            profile = BUILTIN_PROFILES[profile_name]
            assert isinstance(profile, ProcessingProfile)
            assert profile.is_builtin

    def test_quick_profile_settings(self):
        """Test quick profile has appropriate settings."""
        quick = BUILTIN_PROFILES["quick"]
        
        assert quick.name == "quick"
        assert quick.is_default  # Quick should be default
        assert not quick.settings["processing"]["convert_pdf"]
        assert not quick.settings["processing"]["convert_docx"]
        assert quick.settings["processing"]["convert_excel"]

    def test_comprehensive_profile_settings(self):
        """Test comprehensive profile has all conversions enabled."""
        comprehensive = BUILTIN_PROFILES["comprehensive"]
        
        assert comprehensive.name == "comprehensive"
        assert comprehensive.settings["processing"]["convert_pdf"]
        assert comprehensive.settings["processing"]["convert_docx"]
        assert comprehensive.settings["processing"]["convert_excel"]
        assert comprehensive.settings["pdf_conversion"]["enabled"]
        assert comprehensive.settings["docx_conversion"]["enabled"]

    def test_ai_ready_profile_settings(self):
        """Test AI-ready profile has appropriate settings for LLM processing."""
        ai_ready = BUILTIN_PROFILES["ai_ready"]
        
        assert ai_ready.name == "ai_ready"
        assert ai_ready.settings["docx_conversion"]["enable_chunking"]
        assert ai_ready.settings["docx_conversion"]["chunk_strategy"] == "semantic"
        assert ai_ready.settings["docx_conversion"]["output_format"] == "markdown"
        assert ai_ready.settings["performance"]["memory_limit_mb"] == 1024

    def test_archive_profile_settings(self):
        """Test archive profile has maximum quality settings."""
        archive = BUILTIN_PROFILES["archive"]
        
        assert archive.name == "archive"
        assert archive.settings["pdf_conversion"]["image_quality"] == 100
        assert archive.settings["docx_conversion"]["preserve_styles"]
        assert archive.settings["performance"]["quality_over_speed"]

    def test_dev_profile_settings(self):
        """Test development profile has debug features enabled."""
        dev = BUILTIN_PROFILES["dev"]
        
        assert dev.name == "dev"
        assert dev.settings["processing"]["debug_mode"]
        assert dev.settings["performance"]["enable_profiling"]
        assert dev.settings["logging"]["level"] == "DEBUG"


class TestProfileManager:
    """Test the ProfileManager class."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.profile_manager = ProfileManager(self.temp_dir)

    def teardown_method(self):
        """Clean up after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_profile_manager_initialization(self):
        """Test ProfileManager initialization."""
        # Should load all built-in profiles
        assert len(self.profile_manager.profiles) >= 5  # At least 5 built-in profiles
        
        # Check that built-in profiles are loaded
        for profile_name in BUILTIN_PROFILES:
            assert profile_name in self.profile_manager.profiles

    def test_get_profile(self):
        """Test getting a profile by name."""
        # Get built-in profile
        quick_profile = self.profile_manager.get_profile("quick")
        assert quick_profile is not None
        assert quick_profile.name == "quick"
        
        # Get non-existent profile
        nonexistent = self.profile_manager.get_profile("nonexistent")
        assert nonexistent is None

    def test_get_default_profile(self):
        """Test getting the default profile."""
        default_profile = self.profile_manager.get_default_profile()
        assert default_profile is not None
        assert default_profile.name == "quick"  # Quick should be default

    def test_list_profiles(self):
        """Test listing profiles."""
        # List all profiles
        all_profiles = self.profile_manager.list_profiles()
        assert len(all_profiles) >= 5
        
        # Should be sorted by priority
        priorities = [p.priority for p in all_profiles]
        assert priorities == sorted(priorities)
        
        # List only built-in profiles
        builtin_profiles = self.profile_manager.list_profiles(include_custom=False)
        assert all(p.is_builtin for p in builtin_profiles)

    def test_create_custom_profile(self):
        """Test creating a custom profile."""
        settings = {"processing": {"convert_pdf": True, "convert_docx": False}}
        
        profile = self.profile_manager.create_profile(
            name="custom_test",
            display_name="Custom Test Profile",
            description="A custom test profile",
            settings=settings
        )
        
        assert profile.name == "custom_test"
        assert profile.display_name == "Custom Test Profile"
        assert not profile.is_builtin
        assert profile.settings == settings
        
        # Should be in manager's profiles
        assert "custom_test" in self.profile_manager.profiles

    def test_create_profile_with_base(self):
        """Test creating a profile based on an existing one."""
        custom_settings = {"performance": {"max_workers": 8}}
        
        profile = self.profile_manager.create_profile(
            name="custom_comprehensive",
            display_name="Custom Comprehensive",
            description="Based on comprehensive profile",
            settings=custom_settings,
            base_profile="comprehensive"
        )
        
        # Should inherit comprehensive settings
        assert profile.settings["processing"]["convert_pdf"]
        assert profile.settings["processing"]["convert_docx"]
        
        # Should have custom override
        assert profile.settings["performance"]["max_workers"] == 8

    def test_create_duplicate_profile_fails(self):
        """Test that creating a duplicate profile name fails."""
        settings = {"processing": {"convert_pdf": True}}
        
        # Create first profile
        self.profile_manager.create_profile(
            name="duplicate_test",
            display_name="First Profile",
            description="First profile",
            settings=settings
        )
        
        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            self.profile_manager.create_profile(
                name="duplicate_test",
                display_name="Second Profile",
                description="Duplicate profile",
                settings=settings
            )

    def test_update_custom_profile(self):
        """Test updating a custom profile."""
        # Create custom profile
        settings = {"processing": {"convert_pdf": True}}
        
        profile = self.profile_manager.create_profile(
            name="update_test",
            display_name="Update Test",
            description="Test profile for updating",
            settings=settings
        )
        
        # Update the profile
        new_settings = {"performance": {"max_workers": 6}}
        updated_profile = self.profile_manager.update_profile(
            name="update_test",
            settings=new_settings,
            display_name="Updated Test Profile"
        )
        
        assert updated_profile.display_name == "Updated Test Profile"
        assert updated_profile.settings["performance"]["max_workers"] == 6
        # Original settings should be preserved and merged
        assert updated_profile.settings["processing"]["convert_pdf"]

    def test_update_builtin_profile_fails(self):
        """Test that updating a built-in profile fails."""
        with pytest.raises(ValueError, match="Cannot modify built-in profile"):
            self.profile_manager.update_profile(
                name="quick",
                settings={"processing": {"convert_pdf": True}}
            )

    def test_delete_custom_profile(self):
        """Test deleting a custom profile."""
        # Create custom profile
        settings = {"processing": {"convert_pdf": True}}
        
        self.profile_manager.create_profile(
            name="delete_test",
            display_name="Delete Test",
            description="Test profile for deletion",
            settings=settings
        )
        
        # Verify it exists
        assert "delete_test" in self.profile_manager.profiles
        
        # Delete it
        self.profile_manager.delete_profile("delete_test")
        
        # Verify it's gone
        assert "delete_test" not in self.profile_manager.profiles

    def test_delete_builtin_profile_fails(self):
        """Test that deleting a built-in profile fails."""
        with pytest.raises(ValueError, match="Cannot delete built-in profile"):
            self.profile_manager.delete_profile("quick")

    def test_delete_nonexistent_profile_fails(self):
        """Test that deleting a non-existent profile fails."""
        with pytest.raises(ValueError, match="not found"):
            self.profile_manager.delete_profile("nonexistent")

    def test_export_profile(self):
        """Test exporting a profile to file."""
        export_path = self.temp_dir / "exported_profile.json"
        
        self.profile_manager.export_profile("quick", export_path)
        
        assert export_path.exists()
        
        # Verify exported content
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
            
        assert exported_data["name"] == "quick"
        assert exported_data["display_name"] == "🚀 Quick Processing"

    def test_export_nonexistent_profile_fails(self):
        """Test that exporting a non-existent profile fails."""
        export_path = self.temp_dir / "nonexistent.json"
        
        with pytest.raises(ValueError, match="not found"):
            self.profile_manager.export_profile("nonexistent", export_path)

    def test_import_profile(self):
        """Test importing a profile from file."""
        # Create profile data to import
        profile_data = {
            "name": "imported_test",
            "display_name": "Imported Test Profile",
            "description": "An imported test profile",
            "settings": {"processing": {"convert_pdf": True}},
            "priority": 75,
            "is_builtin": False,
            "is_default": False
        }
        
        import_path = self.temp_dir / "import_test.json"
        with open(import_path, 'w') as f:
            json.dump(profile_data, f)
        
        # Import the profile
        imported_profile = self.profile_manager.import_profile(import_path)
        
        assert imported_profile.name == "imported_test"
        assert imported_profile.display_name == "Imported Test Profile"
        assert not imported_profile.is_builtin
        
        # Should be in manager's profiles
        assert "imported_test" in self.profile_manager.profiles

    def test_import_existing_profile_fails_without_overwrite(self):
        """Test that importing an existing profile fails without overwrite flag."""
        # Export existing profile
        export_path = self.temp_dir / "existing.json"
        self.profile_manager.export_profile("quick", export_path)
        
        # Try to import without overwrite
        with pytest.raises(ValueError, match="already exists"):
            self.profile_manager.import_profile(export_path, overwrite=False)

    def test_import_existing_profile_succeeds_with_overwrite(self):
        """Test that importing an existing profile succeeds with overwrite flag."""
        # Create custom profile first
        self.profile_manager.create_profile(
            name="overwrite_test",
            display_name="Original Profile",
            description="Original description",
            settings={"processing": {"convert_pdf": False}}
        )
        
        # Create new profile data to import
        profile_data = {
            "name": "overwrite_test",
            "display_name": "Overwritten Profile",
            "description": "New description",
            "settings": {"processing": {"convert_pdf": True}},
            "priority": 75,
            "is_builtin": False,
            "is_default": False
        }
        
        import_path = self.temp_dir / "overwrite_test.json"
        with open(import_path, 'w') as f:
            json.dump(profile_data, f)
        
        # Import with overwrite
        imported_profile = self.profile_manager.import_profile(import_path, overwrite=True)
        
        assert imported_profile.display_name == "Overwritten Profile"
        assert imported_profile.settings["processing"]["convert_pdf"]

    def test_apply_profile(self):
        """Test applying a profile to a configuration."""
        base_config = {
            "output_directory": "/tmp/output",
            "processing": {"convert_pdf": False}
        }
        
        # Apply comprehensive profile
        updated_config = self.profile_manager.apply_profile("comprehensive", base_config)
        
        # Should merge profile settings
        assert updated_config["output_directory"] == "/tmp/output"  # Preserved
        assert updated_config["processing"]["convert_pdf"]  # From profile
        assert updated_config["pdf_conversion"]["enabled"]  # From profile

    def test_apply_nonexistent_profile_fails(self):
        """Test that applying a non-existent profile fails."""
        config = {"processing": {"convert_pdf": False}}
        
        with pytest.raises(ValueError, match="not found"):
            self.profile_manager.apply_profile("nonexistent", config)

    def test_save_and_load_custom_profiles(self):
        """Test saving and loading custom profiles to/from disk."""
        # Create some custom profiles
        self.profile_manager.create_profile(
            name="save_test_1",
            display_name="Save Test 1",
            description="First save test",
            settings={"processing": {"convert_pdf": True}}
        )
        
        self.profile_manager.create_profile(
            name="save_test_2",
            display_name="Save Test 2",
            description="Second save test",
            settings={"processing": {"convert_docx": True}}
        )
        
        # Manually save
        self.profile_manager.save_custom_profiles()
        
        # Create new manager instance to test loading
        new_manager = ProfileManager(self.temp_dir)
        
        # Should have loaded custom profiles
        assert "save_test_1" in new_manager.profiles
        assert "save_test_2" in new_manager.profiles
        
        # Verify profile content
        profile_1 = new_manager.get_profile("save_test_1")
        assert profile_1.display_name == "Save Test 1"
        assert profile_1.settings["processing"]["convert_pdf"]

    def test_deep_merge_functionality(self):
        """Test the deep merge functionality used in profile management."""
        # Test through profile creation with base
        base_settings = {
            "processing": {"convert_pdf": True, "convert_docx": False},
            "performance": {"max_workers": 2}
        }
        
        override_settings = {
            "processing": {"convert_docx": True},  # Should override
            "output": {"format": "markdown"}  # Should add new section
        }
        
        # Create profile that should merge these
        profile = self.profile_manager.create_profile(
            name="merge_test",
            display_name="Merge Test",
            description="Test deep merge",
            settings=override_settings,
            base_profile="comprehensive"  # Has complex nested settings
        )
        
        # Should have merged settings
        assert profile.settings["processing"]["convert_pdf"]  # From base
        assert profile.settings["processing"]["convert_docx"]  # From override
        assert "pdf_conversion" in profile.settings  # From comprehensive base