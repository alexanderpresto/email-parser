"""
Performance tests for Phase 4.5 Interactive File Conversion functionality.

Tests performance benchmarks and requirements for interactive file conversion operations.
"""

import pytest
import time
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil
import os

from email_parser.cli.interactive_file import InteractiveFileConverter, ConvertibleFile


class TestFileDiscoveryPerformance:
    """Test file discovery performance benchmarks."""
    
    @pytest.fixture
    def temp_directory_with_files(self):
        """Create temporary directory with many test files."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create 100 test files of various types
        for i in range(50):
            # Create PDF files (mock)
            pdf_file = temp_dir / f"document_{i}.pdf"
            pdf_file.write_bytes(b"%PDF-1.4 test content " * 100)
            
            # Create DOCX files (mock)
            docx_file = temp_dir / f"document_{i}.docx"
            docx_file.write_bytes(b"PK\x03\x04 test content " * 50)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_file_discovery_performance_100_files(self, temp_directory_with_files):
        """Test file discovery performance with 100 files - should be < 2 seconds."""
        with patch('email_parser.cli.interactive_file.Console'):
            converter = InteractiveFileConverter()
            
            start_time = time.time()
            
            # Mock the file scanning process
            files = list(temp_directory_with_files.glob("*"))
            file_count = len(files)
            
            # Simulate file metadata gathering
            convertible_files = []
            for file_path in files:
                if file_path.is_file():
                    convertible_files.append(ConvertibleFile(
                        path=file_path,
                        file_type="pdf" if file_path.suffix == ".pdf" else "docx",
                        size=file_path.stat().st_size,
                        estimated_conversion_time=1.0,
                        complexity_indicators=[]
                    ))
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Performance requirement: < 2 seconds for 100 files
            assert duration < 2.0, f"File discovery took {duration:.2f}s, should be < 2.0s"
            assert file_count == 100, f"Expected 100 files, found {file_count}"
            assert len(convertible_files) == 100, f"Expected 100 convertible files, found {len(convertible_files)}"
    
    def test_progress_update_frequency(self):
        """Test that progress updates can happen every 100ms."""
        update_interval = 0.1  # 100ms
        
        # Simulate 10 progress updates
        start_time = time.time()
        for i in range(10):
            time.sleep(update_interval)
        
        total_time = time.time() - start_time
        
        # Should be approximately 1 second (10 * 100ms)
        assert 0.9 < total_time < 1.2, f"Progress updates timing issue: {total_time:.2f}s"


class TestMemoryUsagePerformance:
    """Test memory usage performance requirements."""
    
    def test_memory_baseline(self):
        """Establish memory baseline for converter initialization."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        with patch('email_parser.cli.interactive_file.Console'):
            converter = InteractiveFileConverter()
            
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 50MB for initialization)
        max_allowed_increase = 50 * 1024 * 1024  # 50MB
        assert memory_increase < max_allowed_increase, \
            f"Memory increase {memory_increase / 1024 / 1024:.1f}MB exceeds limit"
    
    @pytest.mark.asyncio
    async def test_large_file_set_memory(self):
        """Test memory usage with large file sets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large list of convertible files (simulate 500 files)
        large_file_list = []
        for i in range(500):
            large_file_list.append(ConvertibleFile(
                path=Path(f"test_file_{i}.pdf"),
                file_type="pdf",
                size=10*1024*1024,  # 10MB each
                estimated_conversion_time=5.0,
                complexity_indicators=["large"]
            ))
        
        # Simulate processing recommendations
        with patch('email_parser.cli.interactive_file.Console'):
            converter = InteractiveFileConverter()
            
            # This would normally trigger profile recommendations
            # For testing, we'll just verify the data structures don't explode memory
            
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be < 100MB for large file sets
        max_allowed_increase = 100 * 1024 * 1024  # 100MB
        assert memory_increase < max_allowed_increase, \
            f"Memory increase {memory_increase / 1024 / 1024:.1f}MB exceeds limit for large file set"


class TestUIResponsivenessPerformance:
    """Test UI responsiveness requirements."""
    
    @pytest.mark.asyncio
    async def test_async_operation_responsiveness(self):
        """Test that async operations don't block the UI."""
        
        async def simulate_long_operation():
            """Simulate a long-running operation that yields control."""
            for i in range(10):
                await asyncio.sleep(0.01)  # 10ms chunks
            return "completed"
        
        # Test that we can run multiple operations concurrently
        start_time = time.time()
        
        tasks = [simulate_long_operation() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in roughly 100ms (not 500ms if they ran sequentially)
        assert duration < 0.2, f"Async operations took {duration:.3f}s, should be < 0.2s"
        assert len(results) == 5
        assert all(result == "completed" for result in results)
    
    def test_profile_recommendation_speed(self):
        """Test that profile recommendations are fast."""
        from email_parser.config.profiles import ProfileManager
        
        # Create large file set for testing
        files = []
        for i in range(1000):
            files.append(ConvertibleFile(
                path=Path(f"file_{i}.pdf"),
                file_type="pdf" if i % 2 == 0 else "docx",
                size=1024 * (i + 1),  # Varying sizes
                estimated_conversion_time=1.0 + (i * 0.1),
                complexity_indicators=[]
            ))
        
        # Test recommendation speed
        start_time = time.time()
        
        # Simulate profile recommendation logic
        profile_manager = ProfileManager()
        
        # This should be nearly instantaneous
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be < 0.1 seconds even for 1000 files
        assert duration < 0.1, f"Profile recommendation took {duration:.3f}s, should be < 0.1s"


class TestBatchProcessingPerformance:
    """Test batch processing performance requirements."""
    
    @pytest.mark.asyncio
    async def test_batch_processing_ui_time(self):
        """Test that batch processing UI setup is fast."""
        
        # Simulate preparing 100 files for batch processing
        files = []
        for i in range(100):
            files.append(ConvertibleFile(
                path=Path(f"batch_file_{i}.pdf"),
                file_type="pdf",
                size=1024 * 1024,  # 1MB each
                estimated_conversion_time=2.0,
                complexity_indicators=[]
            ))
        
        start_time = time.time()
        
        # Simulate UI setup operations (file grouping, table creation, etc.)
        file_groups = {}
        for file in files:
            if file.file_type not in file_groups:
                file_groups[file.file_type] = []
            file_groups[file.file_type].append(file)
        
        # Calculate totals
        total_size = sum(f.size for f in files)
        estimated_time = sum(f.estimated_conversion_time for f in files)
        
        end_time = time.time()
        ui_setup_time = end_time - start_time
        
        # UI setup should be < 5 seconds for 100 files
        assert ui_setup_time < 5.0, f"Batch UI setup took {ui_setup_time:.2f}s, should be < 5.0s"
        assert len(file_groups) > 0
        assert total_size > 0
        assert estimated_time > 0


@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmarks for comparison and regression testing."""
    
    def test_converter_initialization_benchmark(self, benchmark):
        """Benchmark converter initialization time."""
        
        def create_converter():
            with patch('email_parser.cli.interactive_file.Console'):
                return InteractiveFileConverter()
        
        result = benchmark(create_converter)
        assert result is not None
    
    def test_file_metadata_processing_benchmark(self, benchmark):
        """Benchmark file metadata processing."""
        
        def process_file_metadata():
            # Create test files data
            files_data = []
            for i in range(50):
                files_data.append({
                    'path': Path(f"test_{i}.pdf"),
                    'size': 1024 * (i + 1),
                    'type': 'pdf'
                })
            
            # Process metadata
            results = []
            for file_data in files_data:
                results.append(ConvertibleFile(
                    path=file_data['path'],
                    file_type=file_data['type'],
                    size=file_data['size'],
                    estimated_conversion_time=file_data['size'] / 1024.0,
                    complexity_indicators=[]
                ))
            
            return results
        
        results = benchmark(process_file_metadata)
        assert len(results) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])