"""
Progress tracking and display utilities for interactive CLI.

This module provides real-time progress tracking with support for both
rich terminal UI (if available) and simple fallback display.
"""

import time
import sys
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
from pathlib import Path

# Try to import rich for enhanced UI
try:
    from rich.console import Console
    from rich.progress import (
        Progress, 
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeRemainingColumn,
        TimeElapsedColumn,
        MofNCompleteColumn
    )
    from rich.table import Table
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ProgressStyle(Enum):
    """Progress display styles."""
    RICH = "rich"      # Rich terminal UI
    SIMPLE = "simple"  # Simple text progress
    QUIET = "quiet"    # Minimal output
    NONE = "none"      # No progress display


@dataclass
class TaskInfo:
    """Information about a progress task."""
    name: str
    total: int
    completed: int = 0
    description: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    subtasks: List['TaskInfo'] = field(default_factory=list)
    status: str = "pending"
    error_message: Optional[str] = None
    
    @property
    def elapsed_time(self) -> timedelta:
        """Get elapsed time for this task."""
        return datetime.now() - self.start_time
    
    @property
    def percentage(self) -> float:
        """Get completion percentage."""
        if self.total == 0:
            return 100.0
        return (self.completed / self.total) * 100
    
    @property
    def remaining_time(self) -> Optional[timedelta]:
        """Estimate remaining time."""
        if self.completed == 0 or self.completed >= self.total:
            return None
            
        elapsed = self.elapsed_time.total_seconds()
        rate = self.completed / elapsed
        remaining_items = self.total - self.completed
        remaining_seconds = remaining_items / rate
        
        return timedelta(seconds=int(remaining_seconds))
    
    @property
    def is_complete(self) -> bool:
        """Check if task is complete."""
        return self.completed >= self.total or self.status == "complete"


class ProgressTracker:
    """Real-time progress tracking for email processing."""
    
    def __init__(self, style: ProgressStyle = ProgressStyle.RICH):
        """
        Initialize progress tracker.
        
        Args:
            style: Progress display style
        """
        self.style = style
        if style == ProgressStyle.RICH and not RICH_AVAILABLE:
            self.style = ProgressStyle.SIMPLE
            
        self.tasks: Dict[str, TaskInfo] = {}
        self.current_task: Optional[str] = None
        self.callbacks: List[Callable] = []
        self._lock = threading.Lock()
        
        # Rich console setup
        if self.style == ProgressStyle.RICH:
            self.console = Console()
            self.progress = None
            self.rich_tasks = {}
            
        # Simple progress state
        self.last_update_time = time.time()
        self.update_interval = 0.1  # Update every 100ms
        
    def start_task(
        self, 
        task_id: str,
        name: str, 
        total: int,
        description: str = "",
        parent_id: Optional[str] = None
    ) -> None:
        """
        Start tracking a new task.
        
        Args:
            task_id: Unique task identifier
            name: Task name
            total: Total units of work
            description: Optional task description
            parent_id: Parent task ID for subtasks
        """
        with self._lock:
            task = TaskInfo(
                name=name,
                total=total,
                description=description,
                status="running"
            )
            
            if parent_id and parent_id in self.tasks:
                self.tasks[parent_id].subtasks.append(task)
            else:
                self.tasks[task_id] = task
                self.current_task = task_id
                
            self._update_display()
            
    def update(
        self, 
        task_id: Optional[str] = None,
        completed: Optional[int] = None,
        increment: int = 0,
        message: str = ""
    ) -> None:
        """
        Update task progress.
        
        Args:
            task_id: Task ID (uses current if None)
            completed: Absolute completed count
            increment: Increment completed by this amount
            message: Optional status message
        """
        with self._lock:
            task_id = task_id or self.current_task
            if not task_id or task_id not in self.tasks:
                return
                
            task = self.tasks[task_id]
            
            if completed is not None:
                task.completed = min(completed, task.total)
            elif increment > 0:
                task.completed = min(task.completed + increment, task.total)
                
            if message:
                task.description = message
                
            # Check if complete
            if task.completed >= task.total:
                task.status = "complete"
                
            self._update_display()
            
    def complete_task(self, task_id: Optional[str] = None):
        """Mark a task as complete."""
        with self._lock:
            task_id = task_id or self.current_task
            if task_id and task_id in self.tasks:
                task = self.tasks[task_id]
                task.completed = task.total
                task.status = "complete"
                self._update_display()
                
    def fail_task(self, task_id: Optional[str] = None, error: str = ""):
        """Mark a task as failed."""
        with self._lock:
            task_id = task_id or self.current_task
            if task_id and task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = "failed"
                task.error_message = error
                self._update_display()
                
    def add_callback(self, callback: Callable):
        """Add a progress update callback."""
        self.callbacks.append(callback)
        
    def get_summary(self) -> Dict[str, Any]:
        """Get progress summary."""
        with self._lock:
            total_tasks = len(self.tasks)
            completed_tasks = sum(1 for t in self.tasks.values() if t.is_complete)
            failed_tasks = sum(1 for t in self.tasks.values() if t.status == "failed")
            
            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "active_tasks": total_tasks - completed_tasks - failed_tasks,
                "overall_progress": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
            
    def _update_display(self):
        """Update progress display based on style."""
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return
            
        self.last_update_time = current_time
        
        if self.style == ProgressStyle.RICH:
            self._update_rich_display()
        elif self.style == ProgressStyle.SIMPLE:
            self._update_simple_display()
        elif self.style == ProgressStyle.QUIET:
            self._update_quiet_display()
            
        # Call callbacks
        for callback in self.callbacks:
            callback(self.get_summary())
            
    def _update_rich_display(self):
        """Update rich terminal display."""
        if not self.progress:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console
            )
            self.progress.start()
            
        # Update or create tasks
        for task_id, task in self.tasks.items():
            if task_id not in self.rich_tasks:
                self.rich_tasks[task_id] = self.progress.add_task(
                    task.description or task.name,
                    total=task.total
                )
            
            self.progress.update(
                self.rich_tasks[task_id],
                completed=task.completed,
                description=task.description or task.name
            )
            
    def _update_simple_display(self):
        """Update simple text display."""
        # Clear line and return to start
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        
        if self.current_task and self.current_task in self.tasks:
            task = self.tasks[self.current_task]
            
            # Build progress bar
            bar_width = 20
            filled = int(bar_width * task.percentage / 100)
            bar = '█' * filled + '░' * (bar_width - filled)
            
            # Build status line
            status = f"[{bar}] {task.percentage:.0f}% | {task.name}"
            
            if task.description:
                status += f" | {task.description}"
                
            # Add time estimate
            if task.remaining_time:
                remaining = str(task.remaining_time).split('.')[0]
                status += f" | ETA: {remaining}"
                
            # Truncate if too long
            max_width = 78
            if len(status) > max_width:
                status = status[:max_width-3] + "..."
                
            sys.stdout.write(status)
            sys.stdout.flush()
            
    def _update_quiet_display(self):
        """Update quiet mode (minimal output)."""
        # Only show completion messages
        for task_id, task in list(self.tasks.items()):
            if task.is_complete and task.status == "complete":
                print(f"✓ {task.name} complete")
                del self.tasks[task_id]
            elif task.status == "failed":
                print(f"✗ {task.name} failed: {task.error_message}")
                del self.tasks[task_id]
                
    def cleanup(self):
        """Clean up progress display."""
        if self.style == ProgressStyle.RICH and self.progress:
            self.progress.stop()
        elif self.style == ProgressStyle.SIMPLE:
            sys.stdout.write('\n')
            sys.stdout.flush()


class BatchProgressTracker(ProgressTracker):
    """Extended progress tracker for batch operations."""
    
    def __init__(self, style: ProgressStyle = ProgressStyle.RICH):
        super().__init__(style)
        self.batch_info = {
            "total_files": 0,
            "processed_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "warnings": 0,
            "start_time": datetime.now()
        }
        
    def start_batch(self, total_files: int):
        """Start batch processing tracking."""
        self.batch_info["total_files"] = total_files
        self.batch_info["start_time"] = datetime.now()
        
        self.start_task(
            "batch_overall",
            f"Processing {total_files} emails",
            total_files
        )
        
    def start_file(self, filename: str, file_number: int):
        """Start processing a new file."""
        self.start_task(
            f"file_{file_number}",
            f"Processing: {Path(filename).name}",
            100,  # Percentage based
            parent_id="batch_overall"
        )
        
    def complete_file(self, file_number: int, success: bool = True):
        """Complete file processing."""
        self.complete_task(f"file_{file_number}")
        
        self.batch_info["processed_files"] += 1
        if success:
            self.batch_info["successful_files"] += 1
        else:
            self.batch_info["failed_files"] += 1
            
        self.update("batch_overall", increment=1)
        
    def add_warning(self):
        """Add a warning to batch stats."""
        self.batch_info["warnings"] += 1
        
    def get_batch_summary(self) -> Dict[str, Any]:
        """Get batch processing summary."""
        elapsed = datetime.now() - self.batch_info["start_time"]
        
        return {
            **self.batch_info,
            "elapsed_time": str(elapsed).split('.')[0],
            "success_rate": (
                self.batch_info["successful_files"] / 
                max(1, self.batch_info["processed_files"]) * 100
            ),
            "files_remaining": (
                self.batch_info["total_files"] - 
                self.batch_info["processed_files"]
            )
        }
        
    def display_batch_summary(self):
        """Display final batch summary."""
        summary = self.get_batch_summary()
        
        if self.style == ProgressStyle.RICH:
            table = Table(title="Batch Processing Complete")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Files", str(summary["total_files"]))
            table.add_row("Successful", str(summary["successful_files"]))
            table.add_row("Failed", str(summary["failed_files"]))
            table.add_row("Warnings", str(summary["warnings"]))
            table.add_row("Success Rate", f"{summary['success_rate']:.1f}%")
            table.add_row("Total Time", summary["elapsed_time"])
            
            self.console.print(table)
            
        else:
            print("\n" + "="*50)
            print("Batch Processing Complete")
            print("="*50)
            print(f"Total Files:  {summary['total_files']}")
            print(f"Successful:   {summary['successful_files']}")
            print(f"Failed:       {summary['failed_files']}")
            print(f"Warnings:     {summary['warnings']}")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
            print(f"Total Time:   {summary['elapsed_time']}")
            print("="*50)


def create_progress_tracker(
    style: Optional[str] = None,
    batch_mode: bool = False
) -> ProgressTracker:
    """
    Factory function to create appropriate progress tracker.
    
    Args:
        style: Progress style (rich, simple, quiet, none)
        batch_mode: Whether to create batch progress tracker
        
    Returns:
        ProgressTracker instance
    """
    # Determine style
    if style:
        try:
            progress_style = ProgressStyle(style)
        except ValueError:
            progress_style = ProgressStyle.SIMPLE
    else:
        # Auto-detect best style
        if RICH_AVAILABLE and sys.stdout.isatty():
            progress_style = ProgressStyle.RICH
        else:
            progress_style = ProgressStyle.SIMPLE
            
    # Create tracker
    if batch_mode:
        return BatchProgressTracker(progress_style)
    else:
        return ProgressTracker(progress_style)