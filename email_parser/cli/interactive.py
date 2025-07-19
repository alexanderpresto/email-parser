"""
Interactive CLI mode for email processing with smart recommendations.

This module provides an intuitive, guided interface for processing emails
with features like content scanning, processing recommendations, and
real-time progress tracking.
"""

import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    # Try to set console to UTF-8 mode
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        pass
    # Try to set console code page
    try:
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    except:
        pass

# Add prompt toolkit for interactive prompts
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import PathCompleter
    from prompt_toolkit.shortcuts import radiolist_dialog, yes_no_dialog
    from prompt_toolkit.validation import ValidationError, Validator

    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from email_parser.config.profiles import ProcessingProfile, ProfileManager
from email_parser.core.config import ProcessingConfig
from email_parser.core.email_processor import EmailProcessor

# Internal imports
from email_parser.core.scanner import EmailScanner, ScanResult
from email_parser.utils.progress import ProgressStyle, create_progress_tracker

# Try to import unified progress tracker
try:
    from .components.unified_progress import UnifiedProgressTracker

    UNIFIED_PROGRESS_AVAILABLE = True
except ImportError:
    UNIFIED_PROGRESS_AVAILABLE = False

logger = logging.getLogger(__name__)


class NavigationContext:
    """Track user navigation through the CLI."""

    def __init__(self):
        self.breadcrumbs = ["Main Menu"]
        self.previous_mode = None

    def push(self, location: str):
        """Add location to navigation stack."""
        self.breadcrumbs.append(location)

    def pop(self) -> str:
        """Remove and return last location."""
        if len(self.breadcrumbs) > 1:
            return self.breadcrumbs.pop()
        return "Main Menu"

    def get_path(self) -> str:
        """Get current navigation path."""
        return " > ".join(self.breadcrumbs)

    def clear(self):
        """Clear navigation history."""
        self.breadcrumbs = ["Main Menu"]


class EmailPathValidator(Validator):
    """Validator for email file paths."""

    def validate(self, document):
        """Validate that the path points to a valid email file."""
        text = document.text

        if not text:
            raise ValidationError(message="Please enter a file path")

        path = Path(text).expanduser()

        if not path.exists():
            raise ValidationError(message=f"File not found: {text}")

        if not path.is_file():
            raise ValidationError(message=f"Not a file: {text}")

        # Check for common email extensions
        if path.suffix.lower() not in [".eml", ".msg", ".mbox"]:
            # Allow but warn
            pass

        return True


@dataclass
class InteractiveConfig:
    """Configuration for interactive mode."""

    default_profile: str = "quick"
    show_recommendations: bool = True
    auto_confirm: bool = False
    progress_style: str = "rich"
    scan_timeout: int = 30
    use_colors: bool = True
    save_preferences: bool = True
    preferences_file: Path = Path.home() / ".email_parser" / "interactive_prefs.json"

    def load_preferences(self):
        """Load saved preferences."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, "r") as f:
                    prefs = json.load(f)
                    for key, value in prefs.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception as e:
                logger.warning(f"Failed to load preferences: {e}")

    def save_preferences_to_file(self):
        """Save current preferences to file."""
        if self.save_preferences:  # Now this correctly references the boolean attribute
            try:
                self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
                prefs = {
                    "default_profile": self.default_profile,
                    "show_recommendations": self.show_recommendations,
                    "auto_confirm": self.auto_confirm,
                    "progress_style": self.progress_style,
                    "use_colors": self.use_colors,
                }
                with open(self.preferences_file, "w") as f:
                    json.dump(prefs, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to save preferences: {e}")


class InteractiveCLI:
    """Handles interactive command-line interface for email processing."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize interactive CLI.

        Args:
            config_path: Path to configuration file
        """
        self.config = InteractiveConfig()
        self.config.load_preferences()

        self.scanner = EmailScanner()
        self.profile_manager = ProfileManager()
        self.progress_tracker = None
        self.file_converter = None  # Will be initialized when needed
        self._console = None  # Rich console instance
        self.navigation = NavigationContext()  # Navigation tracking

        # Initialize unified progress tracker if available
        if UNIFIED_PROGRESS_AVAILABLE:
            self.unified_progress = UnifiedProgressTracker(self.get_console())
        else:
            self.unified_progress = None

        # Load processing config with temporary output directory
        temp_output = Path.cwd() / "temp_output"
        self.processing_config = ProcessingConfig(output_directory=str(temp_output))

        # Check for first time use
        self.is_first_time = not self.config.preferences_file.exists()

    def get_console(self):
        """Get or create Rich console instance."""
        if self._console is None:
            try:
                from rich.console import Console

                self._console = Console()
            except ImportError:
                # Return None if rich is not available
                self._console = None
        return self._console

    def run(self) -> int:
        """
        Main interactive loop.

        Returns:
            Exit code (0 for success)
        """
        try:
            # Show welcome
            self._show_welcome()

            # Main loop
            while True:
                action = self._show_main_menu()

                if action == "exit":
                    break
                elif action == "process_single":
                    self._process_single_email()
                elif action == "process_batch":
                    self._process_batch()
                elif action == "convert_documents":
                    self._convert_documents()
                elif action == "quick_scan":
                    self._quick_scan()
                elif action == "settings":
                    self._show_settings()
                elif action == "help":
                    self._show_help()

            # Save preferences on exit
            self.config.save_preferences_to_file()

            print("\nThank you for using Email Parser! Goodbye.")
            return 0

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            return 1
        except Exception as e:
            logger.error(f"Interactive mode error: {e}", exc_info=True)
            try:
                print(f"\n❌ An error occurred: {e}")
            except UnicodeEncodeError:
                print(f"\n[ERROR] An error occurred: {e}")
            return 1

    def _show_welcome(self):
        """Display welcome screen."""
        self._clear_screen()

        width = 70
        try:
            # Try Unicode box-drawing characters
            print("╔" + "═" * width + "╗")
            print("║" + " " * width + "║")
            print("║" + "Email Parser v2.4.0".center(width) + "║")
            print("║" + "Interactive Mode".center(width) + "║")
            print("║" + " " * width + "║")
            print("╚" + "═" * width + "╝")
        except UnicodeEncodeError:
            # Fallback to ASCII characters
            print("+" + "-" * width + "+")
            print("|" + " " * width + "|")
            print("|" + "Email Parser v2.4.0".center(width) + "|")
            print("|" + "Interactive Mode".center(width) + "|")
            print("|" + " " * width + "|")
            print("+" + "-" * width + "+")
        print()

        if self.is_first_time:
            try:
                print("👋 Welcome! This appears to be your first time using Email Parser.")
                print()
                print("This tool helps you:")
                print("  ✓ Extract content from email attachments")
                print("  ✓ Convert PDFs, Word docs, and Excel files")
                print("  ✓ Prepare content for AI/LLM processing")
            except UnicodeEncodeError:
                print("Welcome! This appears to be your first time using Email Parser.")
                print()
                print("This tool helps you:")
                print("  - Extract content from email attachments")
                print("  - Convert PDFs, Word docs, and Excel files")
                print("  - Prepare content for AI/LLM processing")
            print()

            if self._confirm("Would you like to see a quick demo?"):
                self._show_demo()

    def _show_main_menu(self) -> str:
        """
        Display main menu and get user choice.

        Returns:
            Selected action
        """
        # Show navigation breadcrumbs
        print(f"\n📍 {self.navigation.get_path()}")
        print("-" * 50)

        print("\nWhat would you like to do?")
        print()
        print("  [1] Process a single email")
        print("  [2] Batch process multiple emails")
        print("  [3] Convert documents (NEW)")
        print("  [4] Quick scan (preview without processing)")
        print("  [5] Configure settings")
        print("  [6] Help")
        print("  [7] Exit")
        print()

        while True:
            choice = input("Select option [1-7]: ").strip()

            if choice == "1":
                return "process_single"
            elif choice == "2":
                return "process_batch"
            elif choice == "3":
                return "convert_documents"
            elif choice == "4":
                return "quick_scan"
            elif choice == "5":
                return "settings"
            elif choice == "6":
                return "help"
            elif choice == "7":
                return "exit"
            else:
                print("Invalid choice. Please select 1-7.")

    def _process_single_email(self):
        """Process a single email interactively."""
        self.navigation.push("Process Single Email")

        print("\n📧 Process Single Email")
        print("=" * 50)

        # Get email path
        email_path = self._get_email_path()
        if not email_path:
            return

        # Scan email
        print(f"\nScanning: {email_path.name}")
        scan_result = self._scan_email(email_path)

        if not scan_result:
            return

        # Display results
        self._display_scan_results(scan_result)

        # Show recommendations
        if self.config.show_recommendations:
            self._show_recommendations(scan_result)

        # Get processing decision
        if not self._confirm("\nProceed with processing?"):
            return

        # Select profile
        profile = self._select_profile(scan_result)

        # Set output directory
        output_dir = self._get_output_directory(email_path)

        # Process email
        self._process_email_with_profile(email_path, profile, output_dir)

        # Return to main menu
        self.navigation.pop()

    def _get_email_path(self) -> Optional[Path]:
        """Get email file path from user."""
        if PROMPT_TOOLKIT_AVAILABLE:
            try:
                path_str = prompt(
                    "Enter email file path: ",
                    completer=PathCompleter(),
                    validator=EmailPathValidator(),
                )
                return Path(path_str).expanduser().resolve()
            except (EOFError, KeyboardInterrupt):
                return None
        else:
            # Fallback to simple input
            while True:
                path_str = input("Enter email file path: ").strip()
                if not path_str:
                    return None

                path = Path(path_str).expanduser().resolve()

                if not path.exists():
                    print(f"❌ File not found: {path}")
                    if not self._confirm("Try again?"):
                        return None
                elif not path.is_file():
                    print(f"❌ Not a file: {path}")
                    if not self._confirm("Try again?"):
                        return None
                else:
                    return path

    def _scan_email(self, email_path: Path) -> Optional[ScanResult]:
        """Scan email and show progress."""
        try:
            # Create progress tracker
            self.progress_tracker = create_progress_tracker(style=self.config.progress_style)

            self.progress_tracker.start_task("scan", "Scanning email", 100)

            # Perform scan
            self.progress_tracker.update("scan", completed=50, message="Analyzing attachments...")
            scan_result = self.scanner.scan(email_path)

            self.progress_tracker.complete_task("scan")

            return scan_result

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            print(f"\n❌ Scan failed: {e}")
            return None
        finally:
            if self.progress_tracker:
                self.progress_tracker.cleanup()

    def _display_scan_results(self, scan_result: ScanResult):
        """Display scan results in a formatted way."""
        print("\n📊 Email Analysis Complete")
        print("─" * 50)

        print(f"Subject: {scan_result.subject}")
        print(f"From:    {scan_result.sender}")
        print(f"Date:    {scan_result.date or 'Unknown'}")
        print(f"Size:    {scan_result.total_size_mb:.1f} MB")

        if scan_result.attachments:
            print(f"\n📎 Attachments Found: {len(scan_result.attachments)}")

            for i, att in enumerate(scan_result.attachments, 1):
                print(f"\n  {i}. {att.filename} ({att.size_display})")
                print(f"     Type: {att.file_type.value.upper()}")

                if att.features:
                    features_str = ", ".join(sorted(att.features))
                    print(f"     Features: {features_str}")

                if att.warnings:
                    for warning in att.warnings:
                        print(f"     ⚠️  {warning}")

        else:
            print("\n  No attachments found")

        # Time estimate
        print(f"\n⏱️  Estimated processing time: {scan_result.estimated_time}")

        # Warnings
        if scan_result.warnings:
            print("\n⚠️  Warnings:")
            for warning in scan_result.warnings:
                print(f"  • {warning}")

    def _show_recommendations(self, scan_result: ScanResult):
        """Display processing recommendations."""
        print("\n🤖 Processing Recommendations")
        print("─" * 50)

        if scan_result.recommendations:
            print("\nBased on the email content, we recommend:")
            print()

            for rec in scan_result.recommendations:
                print(f"  ✓ {rec}")

        # Suggest profile based on complexity
        if scan_result.complexity_score < 3:
            suggested = "quick"
        elif scan_result.complexity_score < 6:
            suggested = "comprehensive"
        else:
            suggested = "ai_ready"

        print(f"\n📋 Suggested Profile: '{suggested}'")

    def _select_profile(self, scan_result: Optional[ScanResult]) -> ProcessingProfile:
        """Let user select a processing profile."""
        profiles = self.profile_manager.list_profiles()

        print("\n📋 Select Processing Profile")
        print("─" * 50)

        for i, profile in enumerate(profiles, 1):
            marker = (
                " (recommended)"
                if profile.name == self._get_recommended_profile(scan_result)
                else ""
            )
            print(f"  [{i}] {profile.display_name}{marker}")
            print(f"      {profile.description}")

        while True:
            choice = input(f"\nSelect profile [1-{len(profiles)}]: ").strip()

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(profiles):
                    selected = profiles[idx]
                    print(f"\n✓ Selected: {selected.display_name}")
                    return selected
            except ValueError:
                pass

            print("Invalid choice. Please try again.")

    def _get_recommended_profile(self, scan_result: Optional[ScanResult]) -> str:
        """Get recommended profile based on scan results."""
        if scan_result is None:
            return "comprehensive"  # Default for batch processing

        if scan_result.complexity_score < 3:
            return "quick"
        elif scan_result.complexity_score < 6:
            return "comprehensive"
        else:
            return "ai_ready"

    def _get_output_directory(self, email_path: Path) -> Path:
        """Get output directory from user."""
        default_name = f"{email_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        default_path = Path.cwd() / "output" / default_name

        print(f"\nOutput directory (default: {default_path}):")

        user_input = input("> ").strip()

        if user_input:
            output_dir = Path(user_input).expanduser().resolve()
        else:
            output_dir = default_path

        # Create directory
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"✓ Output directory: {output_dir}")

        return output_dir

    def _process_email_with_profile(
        self, email_path: Path, profile: ProcessingProfile, output_dir: Path
    ):
        """Process email with selected profile."""
        print(f"\n🚀 Processing with '{profile.display_name}' profile...")

        try:
            # Create progress tracker
            self.progress_tracker = create_progress_tracker(style=self.config.progress_style)

            # Apply profile to config
            config_dict = self.processing_config.to_dict()
            config_dict = self.profile_manager.apply_profile(profile.name, config_dict)

            # Update output directory in config
            config_dict["output_directory"] = str(output_dir)

            # Create processor with updated config
            processor = EmailProcessor(ProcessingConfig.from_dict(config_dict))

            # Process email (EmailProcessor.process_email only takes email_path)
            result = processor.process_email(str(email_path))

            print("\n✅ Processing complete!")
            print(f"📁 Output saved to: {output_dir}")

            # Show summary with processing result
            self._show_processing_summary(output_dir, result)

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            print(f"\n❌ Processing failed: {e}")
        finally:
            if self.progress_tracker:
                self.progress_tracker.cleanup()

    def _show_processing_summary(self, output_dir: Path, result: Optional[Dict[str, Any]] = None):
        """Show summary of processed files."""
        print("\n📊 Processing Summary")
        print("─" * 50)

        # Show processing result info if available
        if result:
            attachments = result.get("attachments", [])
            print(f"Email processed successfully")
            print(f"Attachments found: {len(attachments)}")

            if attachments:
                print("\nAttachments processed:")
                for i, att in enumerate(attachments, 1):
                    print(f"  {i}. {att.get('filename', 'Unknown')}")

        # Count files in output directory
        file_counts = {}
        total_size = 0

        for file in output_dir.rglob("*"):
            if file.is_file():
                ext = file.suffix.lower()
                file_counts[ext] = file_counts.get(ext, 0) + 1
                total_size += file.stat().st_size

        print(f"\nOutput files created: {sum(file_counts.values())}")
        print(f"Total size: {total_size / (1024*1024):.1f} MB")

        if file_counts:
            print("\nFile types:")
            for ext, count in sorted(file_counts.items()):
                print(f"  {ext or 'no extension'}: {count}")

    def _process_batch(self):
        """Process multiple emails in batch mode."""
        print("\n📦 Batch Processing")
        print("=" * 50)

        # Get input directory
        input_dir = self._get_directory("Enter directory containing emails: ")
        if not input_dir:
            return

        # Find email files
        email_files = list(input_dir.glob("*.eml")) + list(input_dir.glob("*.msg"))

        if not email_files:
            print(f"\n❌ No email files found in {input_dir}")
            return

        print(f"\nFound {len(email_files)} email files")

        # Select profile
        profile = self._select_profile_for_batch()

        # Get output directory
        output_base = self._get_directory("Enter output directory: ", create=True)
        if not output_base:
            return

        # Confirm
        if not self._confirm(
            f"\nProcess {len(email_files)} emails with '{profile.display_name}' profile?"
        ):
            return

        # Process emails
        self._process_batch_emails(email_files, profile, output_base)

    def _convert_documents(self):
        """Convert documents directly without email context."""
        self.navigation.push("Document Conversion")

        print("\n📁 Document Conversion Mode")
        print("=" * 50)
        print("Convert documents directly without email processing")
        print()

        try:
            # Initialize file converter with shared configuration
            if not hasattr(self, "file_converter") or self.file_converter is None:
                from .interactive_file import InteractiveFileConverter

                self.file_converter = InteractiveFileConverter(
                    config=self.processing_config, profile_manager=self.profile_manager
                )

            # Share navigation context and progress tracking
            self.file_converter.console = self.get_console()
            self.file_converter.parent_cli = self
            if self.unified_progress:
                self.file_converter.unified_progress = self.unified_progress

            # Use asyncio to run the file converter
            import asyncio

            asyncio.run(self.file_converter.run_file_mode())

            # Return to main menu
            if self.get_console():
                self.get_console().print("\n[green]Returning to main menu...[/green]")
            else:
                print("\nReturning to main menu...")

        except ImportError as e:
            logger.error(f"File conversion module not available: {e}")
            print(f"\n❌ Error: File conversion module not available: {e}")
        except Exception as e:
            logger.error(f"Document conversion error: {e}", exc_info=True)
            print(f"\n❌ Document conversion failed: {e}")
            print("Please check your file paths and try again.")
        finally:
            self.navigation.pop()  # Remove from navigation stack

    def _quick_scan(self):
        """Quick scan without processing."""
        print("\n🔍 Quick Scan")
        print("=" * 50)

        email_path = self._get_email_path()
        if not email_path:
            return

        scan_result = self._scan_email(email_path)

        if scan_result:
            self._display_scan_results(scan_result)

            if scan_result.recommendations:
                self._show_recommendations(scan_result)

    def _show_settings(self):
        """Show settings menu."""
        print("\n⚙️  Settings")
        print("=" * 50)

        while True:
            print("\n[1] Processing Profiles")
            print("[2] Display Preferences")
            print("[3] API Configuration")
            print("[4] Back to main menu")

            choice = input("\nSelect option [1-4]: ").strip()

            if choice == "1":
                self._manage_profiles()
            elif choice == "2":
                self._configure_display()
            elif choice == "3":
                self._configure_api()
            elif choice == "4":
                break
            else:
                print("Invalid choice.")

    def _show_help(self):
        """Display help information."""
        print("\n📚 Help")
        print("=" * 50)

        print("\nEmail Parser Interactive Mode")
        print("\nThis tool helps you process emails and extract content from attachments.")
        print("\nKey Features:")
        print("  • Automatic attachment detection")
        print("  • Smart processing recommendations")
        print("  • Multiple processing profiles")
        print("  • Real-time progress tracking")
        print("  • Batch processing support")
        print("  • NEW: Direct document conversion (Phase 4.5)")

        print("\nSupported Attachments:")
        print("  • PDF files (with MistralAI OCR)")
        print("  • Word documents (DOCX)")
        print("  • Excel spreadsheets (XLSX)")
        print("  • Images (PNG, JPG, etc.)")

        print("\nFor more information, visit:")
        print("  https://github.com/yourusername/email-parser")

        input("\nPress Enter to continue...")

    def _show_demo(self):
        """Show interactive demo."""
        print("\n🎬 Interactive Demo")
        print("=" * 50)

        print("\nEmail Parser can help you with:")
        print("\n1. Extract text from PDF attachments using AI-powered OCR")
        print("2. Convert Word documents to markdown format")
        print("3. Transform Excel spreadsheets into CSV files")
        print("4. Prepare content for AI/LLM processing")

        print("\nThe interactive mode guides you through:")
        print("  • Selecting emails to process")
        print("  • Scanning for attachments")
        print("  • Choosing the right processing profile")
        print("  • Monitoring progress in real-time")

        input("\nPress Enter to continue...")

    def _confirm(self, message: str) -> bool:
        """Get yes/no confirmation from user."""
        if PROMPT_TOOLKIT_AVAILABLE:
            try:
                return yes_no_dialog(title="Confirm", text=message).run()
            except:
                pass

        # Fallback
        while True:
            response = input(f"{message} [y/N]: ").strip().lower()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no", ""]:
                return False
            else:
                print("Please enter 'y' or 'n'")

    def _clear_screen(self):
        """Clear terminal screen."""
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")

    def _get_directory(self, prompt_text: str, create: bool = False) -> Optional[Path]:
        """Get directory path from user."""
        while True:
            path_str = input(prompt_text).strip()
            if not path_str:
                return None

            path = Path(path_str).expanduser().resolve()

            if not path.exists():
                if create and self._confirm(f"Directory doesn't exist. Create it?"):
                    path.mkdir(parents=True, exist_ok=True)
                    return path
                else:
                    print(f"❌ Directory not found: {path}")
                    if not self._confirm("Try again?"):
                        return None
            elif not path.is_dir():
                print(f"❌ Not a directory: {path}")
                if not self._confirm("Try again?"):
                    return None
            else:
                return path

    def _select_profile_for_batch(self) -> ProcessingProfile:
        """Select profile for batch processing."""
        print("\nFor batch processing, consider:")
        print("  • 'quick' - Fast processing, minimal conversions")
        print("  • 'comprehensive' - Full features, balanced speed")
        print("  • 'ai_ready' - Optimized for AI/LLM processing")

        return self._select_profile(None)

    def _process_batch_emails(
        self, email_files: List[Path], profile: ProcessingProfile, output_base: Path
    ):
        """Process multiple emails in batch."""
        from email_parser.utils.progress import BatchProgressTracker

        # Create batch progress tracker
        tracker = BatchProgressTracker(ProgressStyle(self.config.progress_style))
        tracker.start_batch(len(email_files))

        successful = 0
        failed = 0

        try:
            for i, email_path in enumerate(email_files):
                tracker.start_file(str(email_path), i)

                try:
                    # Create output directory for this email
                    output_dir = output_base / email_path.stem
                    output_dir.mkdir(exist_ok=True)

                    # Apply profile to config
                    config_dict = self.processing_config.to_dict()
                    config_dict = self.profile_manager.apply_profile(profile.name, config_dict)

                    # Update output directory in config
                    config_dict["output_directory"] = str(output_dir)

                    # Process email
                    processor = EmailProcessor(ProcessingConfig.from_dict(config_dict))
                    result = processor.process_email(str(email_path))

                    tracker.complete_file(i, success=True)
                    successful += 1

                except Exception as e:
                    logger.error(f"Failed to process {email_path}: {e}")
                    tracker.complete_file(i, success=False)
                    failed += 1

        finally:
            tracker.cleanup()

        # Show summary
        print(f"\n✅ Batch processing complete!")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

    def _manage_profiles(self):
        """Manage processing profiles."""
        print("\n📋 Processing Profiles")

        profiles = self.profile_manager.list_profiles()

        for i, profile in enumerate(profiles, 1):
            builtin = " (built-in)" if profile.is_builtin else ""
            print(f"  [{i}] {profile.display_name}{builtin}")

        print(f"\n[C]reate new profile")
        print(f"[E]dit custom profile")
        print(f"[D]elete custom profile")
        print(f"[B]ack")

        choice = input("\nSelect option: ").strip().upper()

        if choice == "C":
            self._create_profile()
        elif choice == "E":
            self._edit_profile()
        elif choice == "D":
            self._delete_profile()

    def _configure_display(self):
        """Configure display preferences."""
        print("\n🎨 Display Preferences")

        print(f"\nProgress style: {self.config.progress_style}")
        print(f"Use colors: {self.config.use_colors}")
        print(f"Show recommendations: {self.config.show_recommendations}")

        if self._confirm("\nChange settings?"):
            # Progress style
            styles = ["rich", "simple", "quiet"]
            print("\nProgress style:")
            for i, style in enumerate(styles, 1):
                current = " (current)" if style == self.config.progress_style else ""
                print(f"  [{i}] {style}{current}")

            choice = input("Select [1-3]: ").strip()
            if choice in ["1", "2", "3"]:
                self.config.progress_style = styles[int(choice) - 1]

            # Other settings
            self.config.use_colors = self._confirm("Use colors?")
            self.config.show_recommendations = self._confirm("Show recommendations?")

            print("\n✓ Settings updated")

    def _configure_api(self):
        """Configure API settings."""
        print("\n🔑 API Configuration")

        print("\nPDF conversion requires a MistralAI API key.")

        # Check if key is set
        api_key_env = os.environ.get("MISTRALAI_API_KEY")

        if api_key_env:
            print("✓ API key is configured")

            if self._confirm("\nUpdate API key?"):
                self._set_api_key()
        else:
            print("❌ API key not found")

            if self._confirm("\nSet API key now?"):
                self._set_api_key()

    def _set_api_key(self):
        """Set MistralAI API key."""
        print("\nEnter your MistralAI API key:")
        print("(It will be saved to your environment)")

        import getpass

        api_key = getpass.getpass("API Key: ")

        if api_key:
            # Save to .env file
            env_file = Path.home() / ".email_parser" / ".env"
            env_file.parent.mkdir(exist_ok=True)

            with open(env_file, "a") as f:
                f.write(f"\nMISTRALAI_API_KEY={api_key}\n")

            print("✓ API key saved")
            print("\nNote: Restart the application for changes to take effect")

    def _create_profile(self):
        """Create a new profile."""
        print("\n✨ Create New Profile")

        name = input("Profile name (lowercase, no spaces): ").strip().lower()
        if not name or " " in name:
            print("❌ Invalid name")
            return

        display_name = input("Display name: ").strip()
        description = input("Description: ").strip()

        # Select base profile
        print("\nBase profile to inherit from:")
        profiles = self.profile_manager.list_profiles()

        for i, profile in enumerate(profiles, 1):
            print(f"  [{i}] {profile.display_name}")

        choice = input("Select [1-{}]: ".format(len(profiles))).strip()

        try:
            base_idx = int(choice) - 1
            if 0 <= base_idx < len(profiles):
                base_profile = profiles[base_idx].name

                # Create profile
                self.profile_manager.create_profile(
                    name=name,
                    display_name=display_name,
                    description=description,
                    settings={},  # Will inherit from base
                    base_profile=base_profile,
                )

                print(f"\n✓ Profile '{name}' created")
        except Exception as e:
            print(f"❌ Failed to create profile: {e}")

    def _edit_profile(self):
        """Edit a custom profile."""
        # Get custom profiles only
        all_profiles = self.profile_manager.list_profiles()
        custom_profiles = [p for p in all_profiles if not p.is_builtin]

        if not custom_profiles:
            print("\nNo custom profiles to edit")
            return

        print("\nSelect profile to edit:")
        for i, profile in enumerate(custom_profiles, 1):
            print(f"  [{i}] {profile.display_name}")

        # Implementation would continue here...
        print("\n(Profile editing not fully implemented in this demo)")

    def _delete_profile(self):
        """Delete a custom profile."""
        # Get custom profiles only
        all_profiles = self.profile_manager.list_profiles()
        custom_profiles = [p for p in all_profiles if not p.is_builtin]

        if not custom_profiles:
            print("\nNo custom profiles to delete")
            return

        print("\nSelect profile to delete:")
        for i, profile in enumerate(custom_profiles, 1):
            print(f"  [{i}] {profile.display_name}")

        choice = input("Select profile: ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(custom_profiles):
                profile = custom_profiles[idx]

                if self._confirm(f"Delete profile '{profile.name}'?"):
                    self.profile_manager.delete_profile(profile.name)
                    print("✓ Profile deleted")
        except Exception as e:
            print(f"❌ Failed to delete profile: {e}")


def main():
    """Main entry point for interactive mode."""
    cli = InteractiveCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
