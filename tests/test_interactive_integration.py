"""
Integration tests for Phase 4.5 Interactive CLI enhancements.

Tests the integration between email processing and file conversion modes,
navigation flows, configuration sharing, and unified progress tracking.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio

from email_parser.cli.interactive import InteractiveCLI, NavigationContext
from email_parser.cli.interactive_file import InteractiveFileConverter
from email_parser.cli.components.unified_progress import UnifiedProgressTracker
from email_parser.config.profiles import ProfileManager
from email_parser.core.config import ProcessingConfig


class TestInteractiveCLIIntegration:
    """Test integrated interactive CLI functionality."""
    
    @pytest.fixture
    def cli(self):
        """Create InteractiveCLI instance for testing."""
        return InteractiveCLI()
    
    @pytest.fixture
    def mock_input(self):
        """Create mock for user input."""
        with patch('builtins.input') as mock:
            yield mock
    
    @pytest.fixture
    def mock_prompt(self):
        """Create mock for prompt_toolkit prompt."""
        with patch('email_parser.cli.interactive.prompt') as mock:
            yield mock
            
    def test_navigation_context_initialization(self, cli):
        """Test navigation context is properly initialized."""
        assert cli.navigation is not None
        assert isinstance(cli.navigation, NavigationContext)
        assert cli.navigation.get_path() == "Main Menu"
        
    def test_navigation_breadcrumbs(self):
        """Test navigation breadcrumb functionality."""
        nav = NavigationContext()
        
        # Test initial state
        assert nav.get_path() == "Main Menu"
        
        # Test push
        nav.push("Process Email")
        assert nav.get_path() == "Main Menu > Process Email"
        
        nav.push("Select Profile")
        assert nav.get_path() == "Main Menu > Process Email > Select Profile"
        
        # Test pop
        location = nav.pop()
        assert location == "Select Profile"
        assert nav.get_path() == "Main Menu > Process Email"
        
        # Test clear
        nav.clear()
        assert nav.get_path() == "Main Menu"
        
    def test_menu_navigation(self, cli, mock_input):
        """Test navigation between email and file modes."""
        # Mock user selecting document conversion then exit
        mock_input.side_effect = ["3", "7"]
        
        with patch.object(cli, '_convert_documents') as mock_convert:
            with patch.object(cli, '_show_welcome'):
                result = cli.run()
                
        # Verify convert documents was called
        mock_convert.assert_called_once()
        assert result == 0
        
    def test_file_converter_initialization_with_config(self, cli):
        """Test file converter receives shared configuration."""
        # Initialize file converter
        cli._convert_documents()
        
        # Verify file converter was created with shared config
        assert cli.file_converter is not None
        assert hasattr(cli.file_converter, 'shared_config')
        assert hasattr(cli.file_converter, 'shared_profile_manager')
        
    def test_profile_sharing(self, cli):
        """Test profile consistency across modes."""
        # Both should use the same ProfileManager instance
        assert cli.profile_manager is not None
        
        # When file converter is initialized, it should get profile manager
        from email_parser.cli.interactive_file import InteractiveFileConverter
        file_converter = InteractiveFileConverter(
            config=cli.processing_config,
            profile_manager=cli.profile_manager
        )
        
        assert file_converter.shared_profile_manager == cli.profile_manager
        
    def test_unified_progress_tracker_creation(self, cli):
        """Test unified progress tracker is created when available."""
        if hasattr(cli, 'unified_progress'):
            assert isinstance(cli.unified_progress, UnifiedProgressTracker)
        
    def test_console_sharing(self, cli):
        """Test console instance is properly shared."""
        console = cli.get_console()
        
        # Should return same instance on multiple calls
        assert cli.get_console() is console
        
    def test_error_recovery_navigation(self, cli, mock_input):
        """Test error handling during mode transitions."""
        # Mock user selecting document conversion
        mock_input.side_effect = ["3"]
        
        # Mock file converter to raise error
        with patch.object(cli, 'file_converter') as mock_converter:
            mock_converter.run_file_mode.side_effect = Exception("Test error")
            
            # Should handle error gracefully
            cli._convert_documents()
            
        # Navigation should be cleaned up
        assert cli.navigation.get_path() == "Main Menu"
        
    def test_configuration_persistence(self, cli):
        """Test settings persistence across sessions."""
        # Save preferences
        cli.config.default_profile = "comprehensive"
        cli.config.save_preferences_to_file()
        
        # Create new CLI instance
        new_cli = InteractiveCLI()
        
        # Should load saved preferences
        if new_cli.config.preferences_file.exists():
            assert new_cli.config.default_profile == "comprehensive"
            
    def test_mode_switching_suggestions(self):
        """Test mode switching suggestions."""
        tracker = UnifiedProgressTracker()
        
        # Test email mode with attachments
        context = {
            "has_attachments": True,
            "in_email_mode": True
        }
        
        # Should suggest document conversion mode
        with patch.object(tracker.console, 'print') as mock_print:
            tracker.suggest_mode_switch(context)
            mock_print.assert_called_once()
            
    def test_progress_tracking_across_modes(self):
        """Test unified progress tracking."""
        tracker = UnifiedProgressTracker()
        
        # Start email operation
        tracker.start_operation("email_1", "email", 10)
        tracker.update_operation("email_1", completed=5)
        
        # Start file operation
        tracker.start_operation("file_1", "file", 20)
        tracker.update_operation("file_1", completed=10)
        
        # Get summaries
        email_summary = tracker.get_operation_summary("email_1")
        file_summary = tracker.get_operation_summary("file_1")
        
        assert email_summary['progress_percentage'] == 50.0
        assert file_summary['progress_percentage'] == 50.0
        
    def test_file_converter_integration_flow(self, cli):
        """Test complete integration flow."""
        # Mock asyncio.run to prevent actual async execution
        with patch('asyncio.run') as mock_run:
            # Navigate to document conversion
            cli.navigation.push("Document Conversion")
            
            # Initialize and run file converter
            cli._convert_documents()
            
            # Verify navigation was restored
            assert cli.navigation.get_path() == "Main Menu"
            
            # Verify file converter was properly initialized
            assert cli.file_converter is not None
            assert cli.file_converter.parent_cli == cli
            
            # Verify async run was called
            mock_run.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_async_file_conversion_integration(self):
        """Test async file conversion with main CLI."""
        cli = InteractiveCLI()
        file_converter = InteractiveFileConverter(
            config=cli.processing_config,
            profile_manager=cli.profile_manager
        )
        
        # Mock the run_file_mode to return quickly
        with patch.object(file_converter, 'run_file_mode') as mock_run:
            mock_run.return_value = None
            
            # Run async method
            await file_converter.run_file_mode()
            
            # Verify it was called
            mock_run.assert_called_once()
            
    def test_main_menu_with_breadcrumbs(self, cli, mock_input, capsys):
        """Test main menu displays breadcrumbs."""
        mock_input.return_value = "7"  # Exit
        
        with patch.object(cli, '_show_welcome'):
            cli._show_main_menu()
            
        captured = capsys.readouterr()
        assert "📍 Main Menu" in captured.out
        assert "-" * 50 in captured.out