"""
Unified progress tracking system for both email and file operations.

Phase 4.5: Day 5-6 Enhanced InteractiveCLI Integration
Provides consistent progress tracking across all interactive operations.
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel


@dataclass
class OperationInfo:
    """Information about an active operation"""
    operation_id: str
    operation_type: str  # 'email', 'file', 'batch'
    total_items: int
    completed_items: int
    start_time: float
    status: str  # 'active', 'completed', 'failed'
    current_item: Optional[str] = None
    error: Optional[str] = None


class UnifiedProgressTracker:
    """Unified progress tracking for all operations."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.active_operations: Dict[str, OperationInfo] = {}
        self.progress = None
        self.current_task_id = None
        
    def start_operation(self, operation_id: str, operation_type: str, total_items: int, description: str = ""):
        """Start tracking any operation (email or file)."""
        self.active_operations[operation_id] = OperationInfo(
            operation_id=operation_id,
            operation_type=operation_type,
            total_items=total_items,
            completed_items=0,
            start_time=time.time(),
            status='active'
        )
        
        # Create progress display
        if not self.progress:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console
            )
            self.progress.start()
            
        # Add task to progress
        task_description = description or f"{operation_type.title()} Processing"
        self.current_task_id = self.progress.add_task(
            task_description,
            total=total_items
        )
        
    def update_operation(self, operation_id: str, completed: int = None, current_item: str = None, increment: int = 1):
        """Update operation progress."""
        if operation_id not in self.active_operations:
            return
            
        operation = self.active_operations[operation_id]
        
        if completed is not None:
            operation.completed_items = completed
        else:
            operation.completed_items += increment
            
        if current_item:
            operation.current_item = current_item
            
        # Update progress display
        if self.progress and self.current_task_id is not None:
            self.progress.update(
                self.current_task_id,
                completed=operation.completed_items,
                description=f"Processing: {current_item}" if current_item else None
            )
            
    def complete_operation(self, operation_id: str, success: bool = True, error: str = None):
        """Mark operation as complete."""
        if operation_id not in self.active_operations:
            return
            
        operation = self.active_operations[operation_id]
        operation.status = 'completed' if success else 'failed'
        operation.error = error
        
        # Complete progress task
        if self.progress and self.current_task_id is not None:
            self.progress.update(
                self.current_task_id,
                completed=operation.total_items if success else operation.completed_items
            )
            
    def get_operation_summary(self, operation_id: str) -> Dict[str, Any]:
        """Get summary of an operation."""
        if operation_id not in self.active_operations:
            return {}
            
        operation = self.active_operations[operation_id]
        elapsed_time = time.time() - operation.start_time
        
        return {
            'operation_type': operation.operation_type,
            'total_items': operation.total_items,
            'completed_items': operation.completed_items,
            'progress_percentage': (operation.completed_items / operation.total_items * 100) if operation.total_items > 0 else 0,
            'elapsed_time': elapsed_time,
            'status': operation.status,
            'items_per_second': operation.completed_items / elapsed_time if elapsed_time > 0 else 0,
            'estimated_remaining': ((operation.total_items - operation.completed_items) / (operation.completed_items / elapsed_time)) if operation.completed_items > 0 and elapsed_time > 0 else 0
        }
        
    def show_all_operations(self):
        """Display summary of all operations."""
        if not self.active_operations:
            self.console.print("No active operations")
            return
            
        table = Table(title="Active Operations", show_header=True)
        table.add_column("Operation", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Progress", justify="right")
        table.add_column("Status", style="green")
        table.add_column("Time", justify="right")
        
        for op_id, operation in self.active_operations.items():
            progress_pct = (operation.completed_items / operation.total_items * 100) if operation.total_items > 0 else 0
            elapsed = time.time() - operation.start_time
            
            table.add_row(
                op_id,
                operation.operation_type,
                f"{operation.completed_items}/{operation.total_items} ({progress_pct:.1f}%)",
                operation.status,
                f"{elapsed:.1f}s"
            )
            
        self.console.print(table)
        
    def cleanup(self):
        """Clean up progress display."""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.current_task_id = None
            
    def suggest_mode_switch(self, context: Dict[str, Any]):
        """Suggest switching modes based on user actions."""
        # Email mode with attachments
        if context.get("has_attachments") and context.get("in_email_mode"):
            panel = Panel(
                "[yellow]💡 Tip: You can also convert these attachments directly using 'Convert Documents' mode from the main menu.[/yellow]",
                title="Did you know?",
                border_style="yellow"
            )
            self.console.print(panel)
            
        # File mode with many files
        elif context.get("file_count", 0) > 10 and context.get("in_file_mode"):
            panel = Panel(
                "[yellow]💡 Tip: For batch processing emails with attachments, try 'Batch process multiple emails' from the main menu.[/yellow]",
                title="Did you know?",
                border_style="yellow"
            )
            self.console.print(panel)