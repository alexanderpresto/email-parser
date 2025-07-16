"""
Error handling components for interactive file conversion.

Provides comprehensive error handling with recovery strategies for common
conversion failures.
"""

from typing import Optional, Dict, Any, Callable, List
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
import logging
import os

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from email_parser.exceptions.converter_exceptions import (
    ConversionError,
    APIError,
    FileSizeError,
    UnsupportedFormatError
)

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur during conversion."""
    API_ERROR = "api_error"
    FILE_ACCESS = "file_access"
    FILE_CORRUPTED = "file_corrupted"
    MEMORY_ERROR = "memory_error"
    DISK_SPACE = "disk_space"
    NETWORK_TIMEOUT = "network_timeout"
    UNSUPPORTED_FORMAT = "unsupported_format"
    UNKNOWN = "unknown"


@dataclass
class RecoveryAction:
    """Represents a recovery action that can be taken."""
    action_type: str
    description: str
    handler: Optional[Callable] = None
    requires_input: bool = False


@dataclass
class ErrorContext:
    """Context information about an error."""
    error: Exception
    error_type: ErrorType
    file_path: Path
    operation: str
    additional_info: Optional[Dict[str, Any]] = None


class ConversionErrorHandler:
    """Handles conversion errors with recovery options."""
    
    def __init__(self, console: Console):
        self.console = console
        self._initialize_recovery_strategies()
    
    def _initialize_recovery_strategies(self):
        """Initialize recovery strategies for different error types."""
        self.recovery_strategies = {
            ErrorType.API_ERROR: [
                RecoveryAction(
                    action_type="configure_api",
                    description="Configure API key",
                    handler=self._handle_api_configuration,
                    requires_input=True
                ),
                RecoveryAction(
                    action_type="skip_pdf",
                    description="Skip PDF conversion and continue",
                    handler=self._handle_skip_conversion
                ),
                RecoveryAction(
                    action_type="retry",
                    description="Retry conversion",
                    handler=self._handle_retry
                )
            ],
            ErrorType.FILE_ACCESS: [
                RecoveryAction(
                    action_type="check_permissions",
                    description="Check file permissions and retry",
                    handler=self._handle_check_permissions
                ),
                RecoveryAction(
                    action_type="copy_file",
                    description="Copy file to accessible location",
                    handler=self._handle_copy_file,
                    requires_input=True
                ),
                RecoveryAction(
                    action_type="skip",
                    description="Skip this file",
                    handler=self._handle_skip_file
                )
            ],
            ErrorType.MEMORY_ERROR: [
                RecoveryAction(
                    action_type="reduce_batch",
                    description="Reduce batch size and retry",
                    handler=self._handle_reduce_batch_size
                ),
                RecoveryAction(
                    action_type="free_memory",
                    description="Free memory and retry",
                    handler=self._handle_free_memory
                ),
                RecoveryAction(
                    action_type="sequential",
                    description="Process files sequentially",
                    handler=self._handle_sequential_processing
                )
            ],
            ErrorType.DISK_SPACE: [
                RecoveryAction(
                    action_type="change_output",
                    description="Change output directory",
                    handler=self._handle_change_output_dir,
                    requires_input=True
                ),
                RecoveryAction(
                    action_type="cleanup",
                    description="Clean up temporary files and retry",
                    handler=self._handle_cleanup_temp
                )
            ],
            ErrorType.FILE_CORRUPTED: [
                RecoveryAction(
                    action_type="repair",
                    description="Attempt file repair",
                    handler=self._handle_file_repair
                ),
                RecoveryAction(
                    action_type="partial",
                    description="Extract partial content",
                    handler=self._handle_partial_extraction
                ),
                RecoveryAction(
                    action_type="skip",
                    description="Skip corrupted file",
                    handler=self._handle_skip_file
                )
            ]
        }
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Optional[RecoveryAction]:
        """
        Handle conversion error with recovery options.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            Selected recovery action or None
        """
        # Classify the error
        error_type = self._classify_error(error)
        
        # Create error context
        error_context = ErrorContext(
            error=error,
            error_type=error_type,
            file_path=Path(context.get('file_path', '')),
            operation=context.get('operation', 'conversion'),
            additional_info=context
        )
        
        # Display error information
        self._display_error(error_context)
        
        # Get recovery options
        recovery_options = self.recovery_strategies.get(error_type, [])
        
        if not recovery_options:
            self.console.print("[yellow]No recovery options available for this error type.[/yellow]")
            return None
        
        # Present recovery options to user
        return await self._present_recovery_options(recovery_options, error_context)
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error into an ErrorType."""
        if isinstance(error, APIError):
            return ErrorType.API_ERROR
        elif isinstance(error, FileSizeError):
            return ErrorType.MEMORY_ERROR
        elif isinstance(error, UnsupportedFormatError):
            return ErrorType.UNSUPPORTED_FORMAT
        elif isinstance(error, PermissionError):
            return ErrorType.FILE_ACCESS
        elif isinstance(error, MemoryError):
            return ErrorType.MEMORY_ERROR
        elif isinstance(error, OSError) and "No space left" in str(error):
            return ErrorType.DISK_SPACE
        elif "corrupt" in str(error).lower() or "invalid" in str(error).lower():
            return ErrorType.FILE_CORRUPTED
        else:
            return ErrorType.UNKNOWN
    
    def _display_error(self, context: ErrorContext):
        """Display error information to user."""
        error_panel = Panel(
            f"[red bold]Error:[/red bold] {type(context.error).__name__}\n"
            f"[yellow]Message:[/yellow] {str(context.error)}\n"
            f"[blue]File:[/blue] {context.file_path.name if context.file_path else 'Unknown'}\n"
            f"[blue]Operation:[/blue] {context.operation}",
            title="❌ Conversion Error",
            border_style="red"
        )
        self.console.print(error_panel)
    
    async def _present_recovery_options(self, options: List[RecoveryAction], 
                                      context: ErrorContext) -> Optional[RecoveryAction]:
        """Present recovery options to user and get selection."""
        table = Table(title="Recovery Options", show_header=True)
        table.add_column("Option", style="cyan", width=10)
        table.add_column("Description", style="white")
        
        for i, option in enumerate(options, 1):
            table.add_row(str(i), option.description)
        
        table.add_row("0", "Skip and continue")
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "Select recovery option",
            choices=[str(i) for i in range(len(options) + 1)],
            default="0"
        )
        
        if choice == "0":
            return None
        
        selected_option = options[int(choice) - 1]
        
        # Execute the recovery handler if available
        if selected_option.handler:
            success = await selected_option.handler(context)
            if success:
                return selected_option
        
        return None
    
    # Recovery handlers
    async def _handle_api_configuration(self, context: ErrorContext) -> bool:
        """Handle API configuration recovery."""
        self.console.print("\n[yellow]API Key Configuration Required[/yellow]")
        
        api_key = Prompt.ask("Enter your MistralAI API key", password=True)
        
        if api_key:
            # Set environment variable
            os.environ['MISTRALAI_API_KEY'] = api_key
            self.console.print("[green]API key configured successfully![/green]")
            
            # Optionally save to .env file
            if Confirm.ask("Save API key to .env file for future use?", default=True):
                try:
                    with open('.env', 'a') as f:
                        f.write(f"\nMISTRALAI_API_KEY={api_key}\n")
                    self.console.print("[green].env file updated[/green]")
                except Exception as e:
                    self.console.print(f"[yellow]Could not save to .env: {e}[/yellow]")
            
            return True
        
        return False
    
    async def _handle_skip_conversion(self, context: ErrorContext) -> bool:
        """Skip specific conversion type."""
        self.console.print("[yellow]Skipping PDF conversion for remaining files[/yellow]")
        context.additional_info['skip_pdf'] = True
        return True
    
    async def _handle_retry(self, context: ErrorContext) -> bool:
        """Simple retry handler."""
        self.console.print("[cyan]Retrying conversion...[/cyan]")
        return True
    
    async def _handle_check_permissions(self, context: ErrorContext) -> bool:
        """Check and fix file permissions."""
        try:
            # Check if file exists
            if not context.file_path.exists():
                self.console.print(f"[red]File not found: {context.file_path}[/red]")
                return False
            
            # Check read permissions
            if not os.access(context.file_path, os.R_OK):
                self.console.print(f"[yellow]No read permission for: {context.file_path}[/yellow]")
                
                if os.name == 'nt':  # Windows
                    self.console.print("[yellow]Please check file permissions in File Properties[/yellow]")
                else:
                    self.console.print("[yellow]Try running with appropriate permissions[/yellow]")
                
                return False
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Permission check failed: {e}[/red]")
            return False
    
    async def _handle_copy_file(self, context: ErrorContext) -> bool:
        """Copy file to accessible location."""
        try:
            temp_dir = Path("temp_conversion")
            temp_dir.mkdir(exist_ok=True)
            
            new_path = temp_dir / context.file_path.name
            
            self.console.print(f"[cyan]Copying file to: {new_path}[/cyan]")
            
            import shutil
            shutil.copy2(context.file_path, new_path)
            
            # Update context with new path
            context.file_path = new_path
            context.additional_info['temp_file'] = str(new_path)
            
            self.console.print("[green]File copied successfully![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Failed to copy file: {e}[/red]")
            return False
    
    async def _handle_skip_file(self, context: ErrorContext) -> bool:
        """Skip the current file."""
        self.console.print(f"[yellow]Skipping file: {context.file_path.name}[/yellow]")
        return True
    
    async def _handle_reduce_batch_size(self, context: ErrorContext) -> bool:
        """Reduce batch size for memory conservation."""
        self.console.print("[cyan]Reducing batch size to conserve memory...[/cyan]")
        context.additional_info['batch_size'] = 1
        return True
    
    async def _handle_free_memory(self, context: ErrorContext) -> bool:
        """Attempt to free memory."""
        try:
            import gc
            gc.collect()
            self.console.print("[green]Memory cleanup completed[/green]")
            return True
        except Exception:
            return False
    
    async def _handle_sequential_processing(self, context: ErrorContext) -> bool:
        """Switch to sequential processing."""
        self.console.print("[cyan]Switching to sequential processing mode[/cyan]")
        context.additional_info['parallel'] = False
        return True
    
    async def _handle_change_output_dir(self, context: ErrorContext) -> bool:
        """Change output directory."""
        new_dir = Prompt.ask("Enter new output directory path")
        
        try:
            new_path = Path(new_dir)
            new_path.mkdir(parents=True, exist_ok=True)
            
            context.additional_info['output_dir'] = str(new_path)
            self.console.print(f"[green]Output directory changed to: {new_path}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Failed to create directory: {e}[/red]")
            return False
    
    async def _handle_cleanup_temp(self, context: ErrorContext) -> bool:
        """Clean up temporary files."""
        try:
            temp_dirs = ['temp_conversion', 'output/temp', '.cache']
            cleaned = 0
            
            for temp_dir in temp_dirs:
                if Path(temp_dir).exists():
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    cleaned += 1
            
            self.console.print(f"[green]Cleaned {cleaned} temporary directories[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[yellow]Cleanup partially failed: {e}[/yellow]")
            return False
    
    async def _handle_file_repair(self, context: ErrorContext) -> bool:
        """Attempt to repair corrupted file."""
        self.console.print("[yellow]File repair not implemented yet[/yellow]")
        return False
    
    async def _handle_partial_extraction(self, context: ErrorContext) -> bool:
        """Extract partial content from corrupted file."""
        self.console.print("[cyan]Attempting partial content extraction...[/cyan]")
        context.additional_info['partial_extraction'] = True
        return True