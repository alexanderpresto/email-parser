"""Performance profiling utilities for email parser components.

This module provides decorators and utilities for measuring performance metrics
including execution time, memory usage, and resource utilization.
"""

import functools
import logging
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""
    
    function_name: str
    start_time: datetime
    end_time: datetime
    execution_time: float  # seconds
    peak_memory_mb: float
    memory_delta_mb: float
    cpu_percent: float
    io_reads: int
    io_writes: int
    file_size_mb: Optional[float] = None
    result_size_mb: Optional[float] = None
    extra_metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def throughput_mbps(self) -> Optional[float]:
        """Calculate throughput in MB/s if applicable."""
        if self.file_size_mb and self.execution_time > 0:
            return self.file_size_mb / self.execution_time
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'function_name': self.function_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'execution_time': self.execution_time,
            'peak_memory_mb': self.peak_memory_mb,
            'memory_delta_mb': self.memory_delta_mb,
            'cpu_percent': self.cpu_percent,
            'io_reads': self.io_reads,
            'io_writes': self.io_writes,
            'file_size_mb': self.file_size_mb,
            'result_size_mb': self.result_size_mb,
            'throughput_mbps': self.throughput_mbps,
            **self.extra_metrics
        }


class PerformanceProfiler:
    """Centralized performance profiling manager."""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.process = psutil.Process()
    
    def time_function(self, include_memory: bool = True, include_io: bool = True):
        """Decorator for timing function execution with optional metrics.
        
        Args:
            include_memory: Whether to track memory usage
            include_io: Whether to track I/O operations
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Start tracking
                start_time = datetime.now()
                start_wall = time.perf_counter()
                
                # Memory tracking
                if include_memory:
                    tracemalloc.start()
                    start_memory = self.process.memory_info().rss / 1024 / 1024
                
                # I/O tracking
                if include_io:
                    start_io = self.process.io_counters()
                
                # CPU tracking
                self.process.cpu_percent(interval=None)  # Initialize
                
                try:
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # End tracking
                    end_time = datetime.now()
                    end_wall = time.perf_counter()
                    execution_time = end_wall - start_wall
                    
                    # Collect metrics
                    peak_memory = 0
                    memory_delta = 0
                    if include_memory:
                        current_memory = self.process.memory_info().rss / 1024 / 1024
                        memory_delta = current_memory - start_memory
                        current, peak = tracemalloc.get_traced_memory()
                        peak_memory = peak / 1024 / 1024
                        tracemalloc.stop()
                    
                    io_reads = 0
                    io_writes = 0
                    if include_io:
                        end_io = self.process.io_counters()
                        io_reads = end_io.read_count - start_io.read_count
                        io_writes = end_io.write_count - start_io.write_count
                    
                    cpu_percent = self.process.cpu_percent(interval=None)
                    
                    # Extract file size if applicable
                    file_size_mb = None
                    if args and isinstance(args[0], Path):
                        try:
                            file_size_mb = args[0].stat().st_size / 1024 / 1024
                        except:
                            pass
                    
                    # Create metrics
                    metrics = PerformanceMetrics(
                        function_name=func.__name__,
                        start_time=start_time,
                        end_time=end_time,
                        execution_time=execution_time,
                        peak_memory_mb=peak_memory,
                        memory_delta_mb=memory_delta,
                        cpu_percent=cpu_percent,
                        io_reads=io_reads,
                        io_writes=io_writes,
                        file_size_mb=file_size_mb
                    )
                    
                    self.metrics_history.append(metrics)
                    logger.debug(f"Performance metrics for {func.__name__}: {metrics.to_dict()}")
                    
                    return result
                    
                except Exception as e:
                    if include_memory and tracemalloc.is_tracing():
                        tracemalloc.stop()
                    raise
                    
            return wrapper
        return decorator
    
    @contextmanager
    def profile_block(self, block_name: str, **extra_metrics):
        """Context manager for profiling code blocks.
        
        Args:
            block_name: Name to identify the code block
            **extra_metrics: Additional metrics to record
        """
        start_time = datetime.now()
        start_wall = time.perf_counter()
        
        # Start tracking
        tracemalloc.start()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_io = self.process.io_counters()
        self.process.cpu_percent(interval=None)
        
        try:
            yield self
            
        finally:
            # End tracking
            end_time = datetime.now()
            end_wall = time.perf_counter()
            execution_time = end_wall - start_wall
            
            # Collect metrics
            current_memory = self.process.memory_info().rss / 1024 / 1024
            memory_delta = current_memory - start_memory
            current, peak = tracemalloc.get_traced_memory()
            peak_memory = peak / 1024 / 1024
            tracemalloc.stop()
            
            end_io = self.process.io_counters()
            io_reads = end_io.read_count - start_io.read_count
            io_writes = end_io.write_count - start_io.write_count
            
            cpu_percent = self.process.cpu_percent(interval=None)
            
            # Create metrics
            metrics = PerformanceMetrics(
                function_name=block_name,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                peak_memory_mb=peak_memory,
                memory_delta_mb=memory_delta,
                cpu_percent=cpu_percent,
                io_reads=io_reads,
                io_writes=io_writes,
                extra_metrics=extra_metrics
            )
            
            self.metrics_history.append(metrics)
            logger.info(f"Block '{block_name}' completed in {execution_time:.3f}s, "
                       f"peak memory: {peak_memory:.1f}MB")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all collected metrics."""
        if not self.metrics_history:
            return {}
        
        total_time = sum(m.execution_time for m in self.metrics_history)
        peak_memory = max(m.peak_memory_mb for m in self.metrics_history)
        total_io_reads = sum(m.io_reads for m in self.metrics_history)
        total_io_writes = sum(m.io_writes for m in self.metrics_history)
        
        return {
            'total_execution_time': total_time,
            'peak_memory_mb': peak_memory,
            'total_io_reads': total_io_reads,
            'total_io_writes': total_io_writes,
            'function_count': len(self.metrics_history),
            'metrics': [m.to_dict() for m in self.metrics_history]
        }
    
    def clear_history(self):
        """Clear metrics history."""
        self.metrics_history.clear()


# Global profiler instance
profiler = PerformanceProfiler()


# Convenience decorators
def profile_performance(include_memory: bool = True, include_io: bool = True):
    """Convenience decorator using global profiler instance."""
    return profiler.time_function(include_memory=include_memory, include_io=include_io)


def profile_method(include_memory: bool = True, include_io: bool = True):
    """Decorator for profiling class methods."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Use class name in function identification
            original_name = func.__name__
            func.__name__ = f"{self.__class__.__name__}.{original_name}"
            
            try:
                decorated = profile_performance(include_memory, include_io)(func)
                result = decorated(self, *args, **kwargs)
                return result
            finally:
                func.__name__ = original_name
                
        return wrapper
    return decorator


def measure_file_operation(operation: str):
    """Decorator specifically for file operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(file_path: Union[str, Path], *args, **kwargs) -> Any:
            file_path = Path(file_path)
            
            with profiler.profile_block(
                f"{operation}_{func.__name__}",
                file_path=str(file_path),
                file_size_mb=file_path.stat().st_size / 1024 / 1024 if file_path.exists() else 0
            ):
                result = func(file_path, *args, **kwargs)
                
                # Measure result size if applicable
                if hasattr(result, '__len__'):
                    result_size_mb = len(str(result)) / 1024 / 1024
                    profiler.metrics_history[-1].result_size_mb = result_size_mb
                
                return result
                
        return wrapper
    return decorator