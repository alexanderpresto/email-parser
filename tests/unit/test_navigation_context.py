"""
Unit tests for navigation context system.

Phase 4.5: Interactive File Conversion - Day 7+ Testing
Tests the navigation breadcrumb system and context management.
"""

import pytest
from pathlib import Path

from email_parser.cli.interactive import (
    NavigationContext,
    EmailPathValidator,
    InteractiveConfig,
)


class TestNavigationContext:
    """Test NavigationContext class for breadcrumb navigation."""

    def test_initialization(self):
        """Test NavigationContext initialization."""
        context = NavigationContext()
        
        assert context.breadcrumbs == ["Main Menu"]
        assert context.previous_mode is None
        assert context.get_path() == "Main Menu"

    def test_push_location(self):
        """Test pushing locations to navigation stack."""
        context = NavigationContext()
        
        context.push("Email Processing")
        assert context.breadcrumbs == ["Main Menu", "Email Processing"]
        assert context.get_path() == "Main Menu > Email Processing"
        
        context.push("Scan Results")
        assert context.breadcrumbs == ["Main Menu", "Email Processing", "Scan Results"]
        assert context.get_path() == "Main Menu > Email Processing > Scan Results"

    def test_pop_location(self):
        """Test popping locations from navigation stack."""
        context = NavigationContext()
        
        # Add some locations
        context.push("Email Processing")
        context.push("Profile Selection")
        
        # Pop last location
        popped = context.pop()
        assert popped == "Profile Selection"
        assert context.breadcrumbs == ["Main Menu", "Email Processing"]
        
        # Pop another
        popped = context.pop()
        assert popped == "Email Processing"
        assert context.breadcrumbs == ["Main Menu"]
        
        # Try to pop from root (should stay at Main Menu)
        popped = context.pop()
        assert popped == "Main Menu"
        assert context.breadcrumbs == ["Main Menu"]

    def test_clear_navigation(self):
        """Test clearing navigation history."""
        context = NavigationContext()
        
        # Build up some history
        context.push("Email Processing")
        context.push("Batch Mode")
        context.push("Results")
        
        # Clear it
        context.clear()
        
        assert context.breadcrumbs == ["Main Menu"]
        assert context.get_path() == "Main Menu"

    def test_complex_navigation_flow(self):
        """Test complex navigation flow typical of user interaction."""
        context = NavigationContext()
        
        # User starts email processing
        context.push("Email Processing")
        assert context.get_path() == "Main Menu > Email Processing"
        
        # Goes to scan results
        context.push("Scan Results")
        assert context.get_path() == "Main Menu > Email Processing > Scan Results"
        
        # Back to email processing
        context.pop()
        assert context.get_path() == "Main Menu > Email Processing"
        
        # Switch to file conversion
        context.pop()  # Back to main
        context.push("Convert Documents")
        assert context.get_path() == "Main Menu > Convert Documents"
        
        # Into profile selection
        context.push("Profile Selection")
        assert context.get_path() == "Main Menu > Convert Documents > Profile Selection"

    def test_previous_mode_tracking(self):
        """Test tracking of previous mode."""
        context = NavigationContext()
        
        # Set previous mode
        context.previous_mode = "email_processing"
        assert context.previous_mode == "email_processing"
        
        # Change it
        context.previous_mode = "file_conversion"
        assert context.previous_mode == "file_conversion"
        
        # Clear navigation should not affect previous_mode
        context.clear()
        assert context.previous_mode == "file_conversion"

    def test_navigation_depth_limit(self):
        """Test behavior with deep navigation stacks."""
        context = NavigationContext()
        
        # Push many levels
        for i in range(10):
            context.push(f"Level {i}")
        
        # Should be able to handle deep stacks
        expected_path = "Main Menu > " + " > ".join(f"Level {i}" for i in range(10))
        assert context.get_path() == expected_path
        
        # Should be able to pop all the way back
        for _ in range(10):
            context.pop()
        
        assert context.breadcrumbs == ["Main Menu"]

    def test_unicode_handling(self):
        """Test navigation with unicode characters."""
        context = NavigationContext()
        
        # Test with unicode locations
        context.push("📧 Email Processing")
        context.push("🔍 Scan Results")
        context.push("✅ Complete")
        
        assert context.get_path() == "Main Menu > 📧 Email Processing > 🔍 Scan Results > ✅ Complete"
        
        # Pop should work with unicode
        popped = context.pop()
        assert popped == "✅ Complete"

    def test_empty_location_handling(self):
        """Test handling of empty or None locations."""
        context = NavigationContext()
        
        # Push empty string (should still be added)
        context.push("")
        assert context.breadcrumbs == ["Main Menu", ""]
        
        # The path should handle empty segments
        assert context.get_path() == "Main Menu > "


class TestEmailPathValidator:
    """Test EmailPathValidator for email file validation."""

    def test_valid_email_file(self, tmp_path):
        """Test validation of valid email file."""
        # Create a test email file
        email_file = tmp_path / "test.eml"
        email_file.write_text("Test email content")
        
        validator = EmailPathValidator()
        
        # Create mock document
        document = type('Document', (), {'text': str(email_file)})()
        
        # Should validate successfully
        assert validator.validate(document) is True

    def test_empty_path(self):
        """Test validation with empty path."""
        validator = EmailPathValidator()
        document = type('Document', (), {'text': ""})()
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(document)
        
        assert "Please enter a file path" in str(exc_info.value)

    def test_nonexistent_file(self):
        """Test validation with nonexistent file."""
        validator = EmailPathValidator()
        document = type('Document', (), {'text': "/nonexistent/file.eml"})()
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(document)
        
        assert "File not found" in str(exc_info.value)

    def test_directory_instead_of_file(self, tmp_path):
        """Test validation with directory path."""
        validator = EmailPathValidator()
        document = type('Document', (), {'text': str(tmp_path)})()
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(document)
        
        assert "Not a file" in str(exc_info.value)

    def test_non_email_extension(self, tmp_path):
        """Test validation with non-email file extension."""
        # Create a non-email file
        text_file = tmp_path / "document.txt"
        text_file.write_text("Not an email")
        
        validator = EmailPathValidator()
        document = type('Document', (), {'text': str(text_file)})()
        
        # Should still validate (allows non-standard extensions)
        assert validator.validate(document) is True

    def test_common_email_extensions(self, tmp_path):
        """Test validation with common email extensions."""
        validator = EmailPathValidator()
        
        # Test various email extensions
        for ext in ['.eml', '.msg', '.mbox', '.EML', '.MSG', '.MBOX']:
            email_file = tmp_path / f"test{ext}"
            email_file.write_text("Email content")
            
            document = type('Document', (), {'text': str(email_file)})()
            assert validator.validate(document) is True

    def test_expanduser_support(self, tmp_path, monkeypatch):
        """Test validation with home directory expansion."""
        # Create test file
        email_file = tmp_path / "test.eml"
        email_file.write_text("Test email")
        
        # Mock home directory to tmp_path
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("USERPROFILE", str(tmp_path))  # Windows
        
        validator = EmailPathValidator()
        document = type('Document', (), {'text': "~/test.eml"})()
        
        # Should validate with expansion
        assert validator.validate(document) is True


class TestInteractiveConfig:
    """Test InteractiveConfig dataclass."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = InteractiveConfig()
        
        assert config.default_profile == "quick"

    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = InteractiveConfig(default_profile="comprehensive")
        
        assert config.default_profile == "comprehensive"

    def test_config_modification(self):
        """Test modifying configuration after creation."""
        config = InteractiveConfig()
        
        # Should be able to modify
        config.default_profile = "ai_ready"
        assert config.default_profile == "ai_ready"


class TestNavigationIntegration:
    """Test navigation integration scenarios."""

    def test_error_recovery_navigation(self):
        """Test navigation context during error recovery."""
        context = NavigationContext()
        
        # Simulate navigation to error state
        context.push("Email Processing")
        context.push("Conversion")
        
        # Save state before error
        error_location = context.get_path()
        
        # Simulate error recovery - going back
        context.pop()
        
        # Should be able to track where error occurred
        assert error_location == "Main Menu > Email Processing > Conversion"
        assert context.get_path() == "Main Menu > Email Processing"

    def test_mode_switching_navigation(self):
        """Test navigation when switching between modes."""
        context = NavigationContext()
        
        # Start in email mode
        context.push("Email Processing")
        context.previous_mode = "email"
        
        # Switch to file mode
        context.pop()
        context.push("Convert Documents")
        old_mode = context.previous_mode
        context.previous_mode = "file"
        
        # Should track mode switches
        assert old_mode == "email"
        assert context.previous_mode == "file"
        assert context.get_path() == "Main Menu > Convert Documents"

    def test_navigation_persistence(self):
        """Test that navigation can be persisted and restored."""
        context = NavigationContext()
        
        # Build up navigation state
        context.push("Email Processing")
        context.push("Batch Mode")
        context.previous_mode = "batch_email"
        
        # Save state
        saved_breadcrumbs = context.breadcrumbs.copy()
        saved_mode = context.previous_mode
        
        # Clear and restore
        context.clear()
        context.breadcrumbs = saved_breadcrumbs
        context.previous_mode = saved_mode
        
        assert context.get_path() == "Main Menu > Email Processing > Batch Mode"
        assert context.previous_mode == "batch_email"

    def test_navigation_with_special_characters(self):
        """Test navigation with special characters in paths."""
        context = NavigationContext()
        
        # Test various special characters
        special_locations = [
            "Email & Attachments",
            "Convert -> PDF",
            "Results (10/25)",
            "Profile: AI-Ready",
            "Status [Complete]",
        ]
        
        for location in special_locations:
            context.push(location)
        
        # Path should handle all special characters
        expected = "Main Menu > " + " > ".join(special_locations)
        assert context.get_path() == expected
        
        # Pop should work correctly
        for expected_location in reversed(special_locations):
            popped = context.pop()
            assert popped == expected_location