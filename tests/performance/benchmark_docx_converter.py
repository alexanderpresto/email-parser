"""Performance benchmarks for DOCX converter.

This module tests the performance characteristics of the DOCX converter
across various file sizes and complexity levels.
"""

import json
import logging
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest
from python_docx import Document
from python_docx.shared import Inches, Pt

from email_parser.converters.docx_converter import DocxConverter
from email_parser.core.config import ProcessingConfig
from email_parser.utils.performance_profiler import profiler, profile_performance

logger = logging.getLogger(__name__)


class DocxBenchmarkFixtures:
    """Generate benchmark test documents of various sizes and complexities."""
    
    @staticmethod
    def create_simple_document(size_mb: float, output_path: Path) -> Path:
        """Create a simple text-only document of approximate size."""
        doc = Document()
        
        # Calculate content needed (rough approximation)
        target_chars = int(size_mb * 1024 * 1024 * 0.5)  # Assume ~50% overhead
        paragraph_size = 1000
        num_paragraphs = target_chars // paragraph_size
        
        # Add metadata
        doc.core_properties.title = f"Benchmark Document {size_mb}MB"
        doc.core_properties.author = "Performance Test Suite"
        doc.core_properties.created = datetime.now()
        
        # Generate content
        for i in range(num_paragraphs):
            p = doc.add_paragraph(
                f"This is paragraph {i+1} of the benchmark document. " * 20
            )
            if i % 10 == 0:
                doc.add_heading(f"Section {i//10 + 1}", level=1)
        
        doc.save(output_path)
        return output_path
    
    @staticmethod
    def create_complex_document(output_path: Path, 
                              num_images: int = 10,
                              num_tables: int = 5,
                              num_styles: int = 10) -> Path:
        """Create a complex document with various elements."""
        doc = Document()
        
        # Add metadata
        doc.core_properties.title = "Complex Benchmark Document"
        doc.core_properties.author = "Performance Test Suite"
        doc.core_properties.subject = "Benchmarking"
        doc.core_properties.keywords = "test, performance, benchmark"
        doc.core_properties.comments = "Document for testing performance"
        
        # Add styled content
        for i in range(num_styles):
            heading = doc.add_heading(f'Styled Section {i+1}', level=1)
            
            # Add paragraph with various styles
            p = doc.add_paragraph()
            p.add_run('Bold text. ').bold = True
            p.add_run('Italic text. ').italic = True
            p.add_run('Underlined text. ').underline = True
            
            # Different font sizes
            run = p.add_run('Large text. ')
            run.font.size = Pt(16)
            
            run = p.add_run('Small text. ')
            run.font.size = Pt(8)
        
        # Add tables
        for i in range(num_tables):
            doc.add_heading(f'Table {i+1}', level=2)
            table = doc.add_table(rows=10, cols=5)
            table.style = 'Light List Accent 1'
            
            # Populate table
            for row in table.rows:
                for cell in row.cells:
                    cell.text = f'Cell {cell._element.index}'
        
        # Add list items
        doc.add_heading('Lists', level=1)
        for i in range(20):
            doc.add_paragraph(f'List item {i+1}', style='List Bullet')
        
        # Note: Real images would require actual image files
        # For benchmarking, we're focusing on text/table complexity
        
        doc.save(output_path)
        return output_path
    
    @staticmethod
    def create_large_document(output_path: Path, num_pages: int = 1000) -> Path:
        """Create a very large document with many pages."""
        doc = Document()
        
        # Add metadata
        doc.core_properties.title = f"Large Document - {num_pages} pages"
        doc.core_properties.author = "Performance Test Suite"
        
        # Generate pages (approximate)
        for page in range(num_pages):
            if page > 0:
                doc.add_page_break()
            
            doc.add_heading(f'Page {page + 1}', level=1)
            
            # Add ~40 lines per page
            for line in range(40):
                doc.add_paragraph(
                    f"Line {line + 1} on page {page + 1}. " + 
                    "This is sample text for benchmarking. " * 5
                )
        
        doc.save(output_path)
        return output_path


class TestDocxConverterPerformance:
    """Performance benchmarks for DOCX converter."""
    
    @pytest.fixture
    def converter(self):
        """Create a DOCX converter instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ProcessingConfig(output_directory=tmpdir)
            config.docx_conversion.enabled = True
            config.docx_conversion.enable_chunking = True
            config.docx_conversion.extract_metadata = True
            config.docx_conversion.extract_styles = True
            config.docx_conversion.extract_images = True
            return DocxConverter(config)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @profile_performance()
    def benchmark_conversion(self, converter: DocxConverter, 
                           file_path: Path, 
                           description: str) -> Dict[str, any]:
        """Run a single benchmark test."""
        logger.info(f"Starting benchmark: {description}")
        
        start_time = time.perf_counter()
        
        try:
            # Convert the document
            output_path = converter.convert(file_path)
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            
            # Gather results
            file_size_mb = file_path.stat().st_size / 1024 / 1024
            output_size_mb = output_path.stat().st_size / 1024 / 1024 if output_path else 0
            
            # Check for additional output files
            additional_files = 0
            if output_path:
                output_dir = output_path.parent / f"{output_path.stem}_docx_output"
                if output_dir.exists():
                    additional_files = len(list(output_dir.rglob("*")))
            
            result = {
                'description': description,
                'status': 'success',
                'file_size_mb': file_size_mb,
                'output_size_mb': output_size_mb,
                'execution_time': execution_time,
                'throughput_mbps': file_size_mb / execution_time if execution_time > 0 else 0,
                'additional_files': additional_files,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Benchmark complete: {description} - {execution_time:.2f}s")
            
        except Exception as e:
            result = {
                'description': description,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"Benchmark failed: {description} - {e}")
        
        return result
    
    def test_small_document_performance(self, converter, temp_dir):
        """Test performance with small documents (<1MB)."""
        # Create test documents
        sizes = [0.1, 0.5, 0.9]  # MB
        results = []
        
        for size in sizes:
            file_path = temp_dir / f"small_{size}mb.docx"
            DocxBenchmarkFixtures.create_simple_document(size, file_path)
            
            result = self.benchmark_conversion(
                converter, 
                file_path, 
                f"Small document {size}MB"
            )
            results.append(result)
            
            # Performance assertion - should be fast
            assert result['status'] == 'success'
            assert result['execution_time'] < 0.5, f"Small file took too long: {result['execution_time']}s"
        
        self._save_results(results, temp_dir / "small_document_results.json")
    
    def test_medium_document_performance(self, converter, temp_dir):
        """Test performance with medium documents (1-10MB)."""
        sizes = [1.0, 5.0, 10.0]  # MB
        results = []
        
        for size in sizes:
            file_path = temp_dir / f"medium_{size}mb.docx"
            DocxBenchmarkFixtures.create_simple_document(size, file_path)
            
            result = self.benchmark_conversion(
                converter, 
                file_path, 
                f"Medium document {size}MB"
            )
            results.append(result)
            
            # Performance assertion
            assert result['status'] == 'success'
            assert result['execution_time'] < 2.0, f"Medium file took too long: {result['execution_time']}s"
        
        self._save_results(results, temp_dir / "medium_document_results.json")
    
    @pytest.mark.slow
    def test_large_document_performance(self, converter, temp_dir):
        """Test performance with large documents (10-50MB)."""
        sizes = [20.0, 35.0, 50.0]  # MB
        results = []
        
        for size in sizes:
            file_path = temp_dir / f"large_{size}mb.docx"
            DocxBenchmarkFixtures.create_simple_document(size, file_path)
            
            result = self.benchmark_conversion(
                converter, 
                file_path, 
                f"Large document {size}MB"
            )
            results.append(result)
            
            # Performance assertion
            assert result['status'] == 'success'
            assert result['execution_time'] < 10.0, f"Large file took too long: {result['execution_time']}s"
        
        self._save_results(results, temp_dir / "large_document_results.json")
    
    def test_complex_document_performance(self, converter, temp_dir):
        """Test performance with complex documents."""
        complexities = [
            {'num_tables': 10, 'num_styles': 20},
            {'num_tables': 50, 'num_styles': 50},
            {'num_tables': 100, 'num_styles': 100}
        ]
        results = []
        
        for i, complexity in enumerate(complexities):
            file_path = temp_dir / f"complex_{i}.docx"
            DocxBenchmarkFixtures.create_complex_document(
                file_path, 
                **complexity
            )
            
            result = self.benchmark_conversion(
                converter, 
                file_path, 
                f"Complex document with {complexity['num_tables']} tables"
            )
            results.append(result)
            
            assert result['status'] == 'success'
        
        self._save_results(results, temp_dir / "complex_document_results.json")
    
    def test_chunking_strategy_comparison(self, converter, temp_dir):
        """Compare performance of different chunking strategies."""
        # Create test document
        file_path = temp_dir / "chunking_test.docx"
        DocxBenchmarkFixtures.create_simple_document(5.0, file_path)
        
        strategies = ['token', 'semantic', 'hybrid']
        results = []
        
        for strategy in strategies:
            # Update config
            converter.config.docx_conversion.chunk_strategy = strategy
            
            result = self.benchmark_conversion(
                converter,
                file_path,
                f"Chunking strategy: {strategy}"
            )
            result['strategy'] = strategy
            results.append(result)
        
        self._save_results(results, temp_dir / "chunking_strategy_results.json")
        
        # All strategies should complete successfully
        assert all(r['status'] == 'success' for r in results)
    
    def test_memory_efficiency(self, converter, temp_dir):
        """Test memory usage patterns."""
        # Clear profiler history
        profiler.clear_history()
        
        # Create documents of increasing size
        sizes = [1.0, 5.0, 10.0, 20.0]
        
        for size in sizes:
            file_path = temp_dir / f"memory_test_{size}mb.docx"
            DocxBenchmarkFixtures.create_simple_document(size, file_path)
            
            # Convert with profiling
            with profiler.profile_block(f"memory_test_{size}mb"):
                converter.convert(file_path)
        
        # Analyze memory usage
        summary = profiler.get_summary()
        
        # Memory usage should be reasonable (< 3x file size)
        for metric in summary['metrics']:
            if 'file_size_mb' in metric.get('extra_metrics', {}):
                file_size = metric['extra_metrics']['file_size_mb']
                peak_memory = metric['peak_memory_mb']
                
                assert peak_memory < file_size * 3, \
                    f"Memory usage too high: {peak_memory}MB for {file_size}MB file"
    
    def test_concurrent_processing(self, converter, temp_dir):
        """Test performance under concurrent load."""
        import concurrent.futures
        
        # Create test documents
        num_docs = 5
        docs = []
        for i in range(num_docs):
            file_path = temp_dir / f"concurrent_{i}.docx"
            DocxBenchmarkFixtures.create_simple_document(1.0, file_path)
            docs.append(file_path)
        
        # Process concurrently
        start_time = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for doc in docs:
                future = executor.submit(converter.convert, doc)
                futures.append(future)
            
            # Wait for completion
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Concurrent processing error: {e}")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        logger.info(f"Processed {num_docs} documents in {total_time:.2f}s")
        
        # Should complete all successfully
        assert len(results) == num_docs
    
    def _save_results(self, results: List[Dict], output_path: Path):
        """Save benchmark results to JSON file."""
        with open(output_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'summary': {
                    'total_tests': len(results),
                    'successful': sum(1 for r in results if r.get('status') == 'success'),
                    'failed': sum(1 for r in results if r.get('status') == 'failed'),
                    'avg_throughput': sum(r.get('throughput_mbps', 0) for r in results) / len(results) if results else 0
                }
            }, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    # Run benchmarks directly
    pytest.main([__file__, "-v", "-s"])