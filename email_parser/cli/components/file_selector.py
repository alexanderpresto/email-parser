"""
File selection components for interactive file conversion.

Provides advanced file selection with filtering, sorting, and preview capabilities.
"""

from typing import List, Dict, Any, Optional, Set, Callable
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import os

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from email_parser.utils.file_detector import FileTypeDetector


@dataclass
class FileMetadata:
    """Metadata about a file for selection purposes."""
    path: Path
    size: int
    modified: datetime
    file_type: str
    is_supported: bool
    complexity_score: float = 0.0
    estimated_time: float = 0.0
    
    @property
    def size_mb(self) -> float:
        """File size in megabytes."""
        return self.size / (1024 * 1024)
    
    @property
    def age_days(self) -> int:
        """File age in days."""
        return (datetime.now() - self.modified).days


@dataclass
class FilterCriteria:
    """Criteria for filtering files."""
    file_types: Optional[Set[str]] = None
    min_size_mb: Optional[float] = None
    max_size_mb: Optional[float] = None
    max_age_days: Optional[int] = None
    min_age_days: Optional[int] = None
    name_pattern: Optional[str] = None
    supported_only: bool = True


@dataclass
class SortCriteria:
    """Criteria for sorting files."""
    field: str = "name"  # name, size, modified, type
    reverse: bool = False


class CustomFileSelector:
    """Advanced file selection interface with filtering and sorting."""
    
    def __init__(self, console: Console):
        self.console = console
        self.file_detector = FileTypeDetector()
        self._selected_files: Set[Path] = set()
        self._file_metadata: Dict[Path, FileMetadata] = {}
    
    async def select_files(self, initial_files: List[Path]) -> List[Path]:
        """
        Main file selection workflow.
        
        Args:
            initial_files: Initial list of files to consider
            
        Returns:
            List of selected file paths
        """
        # Gather metadata for all files
        self.console.print("\n[cyan]Analyzing files...[/cyan]")
        await self._gather_file_metadata(initial_files)
        
        current_files = list(self._file_metadata.keys())
        
        while True:
            # Display current selection
            self._display_file_list(current_files)
            
            # Show selection menu
            choice = self._show_selection_menu()
            
            if choice == "done":
                break
            elif choice == "filter":
                current_files = await self._filter_files(current_files)
            elif choice == "sort":
                current_files = self._sort_files(current_files)
            elif choice == "select":
                self._interactive_select(current_files)
            elif choice == "select_all":
                self._selected_files.update(current_files)
                self.console.print(f"[green]Selected all {len(current_files)} files[/green]")
            elif choice == "deselect_all":
                self._selected_files.clear()
                self.console.print("[yellow]Deselected all files[/yellow]")
            elif choice == "invert":
                self._invert_selection(current_files)
            elif choice == "preview":
                await self._preview_selection()
        
        return list(self._selected_files)
    
    async def _gather_file_metadata(self, files: List[Path]) -> None:
        """Gather metadata for all files."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing files...", total=len(files))
            
            for file_path in files:
                try:
                    stat = file_path.stat()
                    
                    # Detect file type
                    file_type = self.file_detector.detect_file_type(file_path)
                    is_supported = file_type in ['pdf', 'docx', 'xlsx', 'xls']
                    
                    # Calculate complexity score (simple heuristic)
                    complexity = self._calculate_complexity(file_path, stat.st_size, file_type)
                    
                    # Estimate conversion time
                    estimated_time = self._estimate_conversion_time(stat.st_size, file_type, complexity)
                    
                    metadata = FileMetadata(
                        path=file_path,
                        size=stat.st_size,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        file_type=file_type,
                        is_supported=is_supported,
                        complexity_score=complexity,
                        estimated_time=estimated_time
                    )
                    
                    self._file_metadata[file_path] = metadata
                    
                except Exception as e:
                    # Skip files that can't be analyzed
                    continue
                
                progress.advance(task)
    
    def _calculate_complexity(self, file_path: Path, size: int, file_type: str) -> float:
        """Calculate file complexity score (0-1)."""
        base_score = min(size / (50 * 1024 * 1024), 1.0)  # Size factor
        
        # Type-specific complexity
        type_multipliers = {
            'pdf': 1.0,
            'docx': 0.8,
            'xlsx': 0.6,
            'xls': 0.6
        }
        
        return base_score * type_multipliers.get(file_type, 0.5)
    
    def _estimate_conversion_time(self, size: int, file_type: str, complexity: float) -> float:
        """Estimate conversion time in seconds."""
        # Base time per MB
        base_times = {
            'pdf': 2.0,    # 2 seconds per MB for PDF (API dependent)
            'docx': 0.5,   # 0.5 seconds per MB for DOCX
            'xlsx': 0.3,   # 0.3 seconds per MB for Excel
            'xls': 0.3
        }
        
        size_mb = size / (1024 * 1024)
        base_time = base_times.get(file_type, 1.0) * size_mb
        
        # Apply complexity multiplier
        return base_time * (1 + complexity)
    
    def _display_file_list(self, files: List[Path]) -> None:
        """Display current file list with selection status."""
        if not files:
            self.console.print("[yellow]No files to display[/yellow]")
            return
        
        table = Table(title=f"Files ({len(files)} total, {len(self._selected_files)} selected)")
        table.add_column("Select", width=6)
        table.add_column("Name", style="cyan")
        table.add_column("Type", width=8)
        table.add_column("Size", width=8, justify="right")
        table.add_column("Modified", width=12)
        table.add_column("Est. Time", width=8, justify="right")
        
        # Show only first 20 files to avoid overwhelming display
        display_files = files[:20]
        if len(files) > 20:
            table.add_row("...", f"({len(files) - 20} more files)", "", "", "", "")
        
        for file_path in display_files:
            metadata = self._file_metadata.get(file_path)
            if not metadata:
                continue
            
            selected = "✓" if file_path in self._selected_files else ""
            
            # Format size
            if metadata.size_mb >= 1:
                size_str = f"{metadata.size_mb:.1f}MB"
            else:
                size_str = f"{metadata.size // 1024}KB"
            
            # Format time
            time_str = f"{metadata.estimated_time:.1f}s"
            
            # Format date
            date_str = metadata.modified.strftime("%Y-%m-%d")
            
            # Color coding
            name_style = "green" if metadata.is_supported else "red"
            
            table.add_row(
                selected,
                Text(metadata.path.name, style=name_style),
                metadata.file_type.upper(),
                size_str,
                date_str,
                time_str
            )
        
        self.console.print(table)
        
        # Show summary
        total_size = sum(m.size for m in self._file_metadata.values() if m.path in self._selected_files)
        total_time = sum(m.estimated_time for m in self._file_metadata.values() if m.path in self._selected_files)
        
        if self._selected_files:
            summary = f"Selected: {len(self._selected_files)} files, " \
                     f"{total_size / (1024*1024):.1f}MB, " \
                     f"~{total_time:.1f}s estimated"
            self.console.print(f"\n[bold]{summary}[/bold]")
    
    def _show_selection_menu(self) -> str:
        """Show selection menu and get user choice."""
        choices = {
            "1": "filter",
            "2": "sort", 
            "3": "select",
            "4": "select_all",
            "5": "deselect_all",
            "6": "invert",
            "7": "preview",
            "8": "done"
        }
        
        menu_text = """
[bold]File Selection Options:[/bold]
1. Filter files
2. Sort files
3. Select/deselect individual files
4. Select all displayed files
5. Deselect all files
6. Invert selection
7. Preview selection
8. Done (proceed with selected files)
"""
        
        self.console.print(Panel(menu_text, title="Selection Menu"))
        
        choice = Prompt.ask(
            "Choose option",
            choices=list(choices.keys()),
            default="8"
        )
        
        return choices[choice]
    
    async def _filter_files(self, current_files: List[Path]) -> List[Path]:
        """Apply filters to file list."""
        self.console.print("\n[bold]File Filtering[/bold]")
        
        # Get filter criteria
        criteria = FilterCriteria()
        
        # File type filter
        if Confirm.ask("Filter by file type?", default=False):
            available_types = set(self._file_metadata[f].file_type for f in current_files)
            type_list = ", ".join(sorted(available_types))
            self.console.print(f"Available types: {type_list}")
            
            types_input = Prompt.ask("Enter file types (comma-separated)", default="")
            if types_input:
                criteria.file_types = set(t.strip().lower() for t in types_input.split(","))
        
        # Size filter
        if Confirm.ask("Filter by file size?", default=False):
            min_size = Prompt.ask("Minimum size (MB)", default="0")
            max_size = Prompt.ask("Maximum size (MB)", default="")
            
            try:
                if min_size:
                    criteria.min_size_mb = float(min_size)
                if max_size:
                    criteria.max_size_mb = float(max_size)
            except ValueError:
                self.console.print("[red]Invalid size values[/red]")
        
        # Age filter
        if Confirm.ask("Filter by file age?", default=False):
            max_age = Prompt.ask("Maximum age (days)", default="")
            
            try:
                if max_age:
                    criteria.max_age_days = int(max_age)
            except ValueError:
                self.console.print("[red]Invalid age value[/red]")
        
        # Apply filters
        filtered_files = []
        for file_path in current_files:
            metadata = self._file_metadata.get(file_path)
            if not metadata:
                continue
            
            # Check all criteria
            if criteria.file_types and metadata.file_type not in criteria.file_types:
                continue
            
            if criteria.min_size_mb and metadata.size_mb < criteria.min_size_mb:
                continue
            
            if criteria.max_size_mb and metadata.size_mb > criteria.max_size_mb:
                continue
            
            if criteria.max_age_days and metadata.age_days > criteria.max_age_days:
                continue
            
            if criteria.supported_only and not metadata.is_supported:
                continue
            
            filtered_files.append(file_path)
        
        self.console.print(f"[green]Filtered to {len(filtered_files)} files[/green]")
        return filtered_files
    
    def _sort_files(self, current_files: List[Path]) -> List[Path]:
        """Sort files by specified criteria."""
        sort_options = {
            "1": ("name", "File name"),
            "2": ("size", "File size"),
            "3": ("modified", "Date modified"),
            "4": ("type", "File type"),
            "5": ("time", "Estimated conversion time")
        }
        
        self.console.print("\n[bold]Sort Options:[/bold]")
        for key, (field, desc) in sort_options.items():
            self.console.print(f"{key}. {desc}")
        
        choice = Prompt.ask(
            "Sort by",
            choices=list(sort_options.keys()),
            default="1"
        )
        
        reverse = Confirm.ask("Descending order?", default=False)
        
        field = sort_options[choice][0]
        
        # Define sort key functions
        def sort_key(file_path: Path):
            metadata = self._file_metadata.get(file_path)
            if not metadata:
                return 0
            
            if field == "name":
                return metadata.path.name.lower()
            elif field == "size":
                return metadata.size
            elif field == "modified":
                return metadata.modified
            elif field == "type":
                return metadata.file_type
            elif field == "time":
                return metadata.estimated_time
            
            return 0
        
        sorted_files = sorted(current_files, key=sort_key, reverse=reverse)
        
        self.console.print(f"[green]Sorted by {sort_options[choice][1]}[/green]")
        return sorted_files
    
    def _interactive_select(self, current_files: List[Path]) -> None:
        """Interactive file selection interface."""
        self.console.print("\n[bold]Interactive Selection[/bold]")
        self.console.print("Enter file numbers to toggle selection (comma-separated), or 'done' to finish")
        
        # Show numbered file list
        table = Table()
        table.add_column("Num", width=4)
        table.add_column("Select", width=6)
        table.add_column("Name", style="cyan")
        table.add_column("Type", width=8)
        
        for i, file_path in enumerate(current_files[:50], 1):  # Limit to 50 for usability
            metadata = self._file_metadata.get(file_path)
            if not metadata:
                continue
            
            selected = "✓" if file_path in self._selected_files else ""
            
            table.add_row(
                str(i),
                selected,
                metadata.path.name,
                metadata.file_type.upper()
            )
        
        self.console.print(table)
        
        while True:
            selection = Prompt.ask("Select files (numbers)", default="done")
            
            if selection.lower() == "done":
                break
            
            try:
                # Parse selection
                numbers = [int(x.strip()) for x in selection.split(",")]
                
                for num in numbers:
                    if 1 <= num <= len(current_files):
                        file_path = current_files[num - 1]
                        if file_path in self._selected_files:
                            self._selected_files.remove(file_path)
                            self.console.print(f"[yellow]Deselected: {file_path.name}[/yellow]")
                        else:
                            self._selected_files.add(file_path)
                            self.console.print(f"[green]Selected: {file_path.name}[/green]")
                    else:
                        self.console.print(f"[red]Invalid number: {num}[/red]")
                        
            except ValueError:
                self.console.print("[red]Invalid input. Use comma-separated numbers.[/red]")
    
    def _invert_selection(self, current_files: List[Path]) -> None:
        """Invert current selection."""
        new_selection = set(current_files) - self._selected_files
        self._selected_files = new_selection
        self.console.print(f"[green]Inverted selection: {len(self._selected_files)} files selected[/green]")
    
    async def _preview_selection(self) -> None:
        """Preview the current selection."""
        if not self._selected_files:
            self.console.print("[yellow]No files selected[/yellow]")
            return
        
        total_size = sum(self._file_metadata[f].size for f in self._selected_files)
        total_time = sum(self._file_metadata[f].estimated_time for f in self._selected_files)
        
        # Group by file type
        type_counts = {}
        for file_path in self._selected_files:
            file_type = self._file_metadata[file_path].file_type
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        preview_text = f"""
[bold]Selection Preview:[/bold]

📊 [bold]Summary:[/bold]
• Total files: {len(self._selected_files)}
• Total size: {total_size / (1024*1024):.1f} MB
• Estimated time: {total_time:.1f} seconds

📋 [bold]By file type:[/bold]
"""
        
        for file_type, count in sorted(type_counts.items()):
            preview_text += f"• {file_type.upper()}: {count} files\n"
        
        self.console.print(Panel(preview_text, title="Selection Preview"))
        
        # Show detailed list if requested
        if Confirm.ask("Show detailed file list?", default=False):
            table = Table(title="Selected Files")
            table.add_column("Name", style="cyan")
            table.add_column("Type", width=8)
            table.add_column("Size", width=8, justify="right")
            
            for file_path in sorted(self._selected_files, key=lambda x: x.name):
                metadata = self._file_metadata[file_path]
                
                size_str = f"{metadata.size_mb:.1f}MB" if metadata.size_mb >= 1 else f"{metadata.size // 1024}KB"
                
                table.add_row(
                    metadata.path.name,
                    metadata.file_type.upper(),
                    size_str
                )
            
            self.console.print(table)