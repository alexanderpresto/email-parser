"""Performance benchmarking suite for PDF converter.

This module provides comprehensive benchmarking for PDF conversion operations,
measuring time, memory usage, API performance, and resource utilization.
"""

import os
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import json
from datetime import datetime

from email_parser.converters.pdf_converter import PDFConverter
from email_parser.exceptions.converter_exceptions import ConversionError, APIError


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    test_name: str
    duration: float
    memory_peak: int
    memory_initial: int
    memory_final: int
    success: bool
    error_message: Optional[str] = None
    additional_metrics: Optional[Dict[str, Any]] = None


@dataclass
class APIBenchmarkResult:
    """Container for API-specific benchmark results."""
    test_name: str
    response_time: float
    status_code: Optional[int]
    success: bool
    error_message: Optional[str] = None
    retry_count: int = 0


class PDFConverterBenchmark:
    """Main benchmarking class for PDF converter operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize benchmark suite.
        
        Args:
            api_key: MistralAI API key. If None, uses environment variable.
        """
        self.api_key = api_key or os.getenv("MISTRALAI_API_KEY")
        self.results: List[BenchmarkResult] = []
        self.api_results: List[APIBenchmarkResult] = []
        self.process = psutil.Process()
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        return self.process.memory_info().rss
    
    def _create_test_pdf(self, size_mb: float, output_path: Path) -> Path:
        """Create a test PDF file of specified size.
        
        Args:
            size_mb: Target size in megabytes
            output_path: Path to create the file
            
        Returns:
            Path to created file
        """
        # Create dummy PDF content (not valid PDF, for size testing)
        content_size = int(size_mb * 1024 * 1024)
        content = b"dummy pdf content " * (content_size // 18)
        
        output_path.write_bytes(content)
        return output_path
    
    def benchmark_conversion_by_size(self, sizes_mb: List[float], 
                                   output_dir: Path) -> List[BenchmarkResult]:
        """Benchmark conversion performance by file size.
        
        Args:
            sizes_mb: List of file sizes to test in MB
            output_dir: Directory for test files and outputs
            
        Returns:
            List of benchmark results
        """
        results = []
        
        for size in sizes_mb:
            test_name = f"conversion_size_{size}mb"
            test_file = output_dir / f"test_{size}mb.pdf"
            
            # Create test file
            self._create_test_pdf(size, test_file)
            
            # Run benchmark
            result = self._benchmark_single_conversion(
                test_name, test_file, output_dir
            )
            results.append(result)
            
            # Cleanup
            if test_file.exists():
                test_file.unlink()
        
        return results
    
    def _benchmark_single_conversion(self, test_name: str, 
                                   input_file: Path, 
                                   output_dir: Path) -> BenchmarkResult:
        """Benchmark a single conversion operation.
        
        Args:
            test_name: Name of the test
            input_file: Input PDF file
            output_dir: Output directory
            
        Returns:
            Benchmark result
        """
        initial_memory = self._get_memory_usage()
        peak_memory = initial_memory
        
        # Memory monitoring thread
        monitoring = {"running": True}
        
        def monitor_memory():
            nonlocal peak_memory
            while monitoring["running"]:
                current = self._get_memory_usage()
                peak_memory = max(peak_memory, current)
                time.sleep(0.1)
        
        monitor_thread = threading.Thread(target=monitor_memory)
        monitor_thread.start()
        
        try:
            converter = PDFConverter(api_key=self.api_key)
            
            start_time = time.time()
            result = converter.convert(input_file, output_dir)
            duration = time.time() - start_time
            
            monitoring["running"] = False
            monitor_thread.join()
            
            final_memory = self._get_memory_usage()
            
            return BenchmarkResult(
                test_name=test_name,
                duration=duration,
                memory_peak=peak_memory,
                memory_initial=initial_memory,
                memory_final=final_memory,
                success=True,
                additional_metrics={
                    "file_size": input_file.stat().st_size,
                    "pages_processed": result.get("pages", 0),
                    "conversion_quality": result.get("quality", "unknown")
                }
            )
            
        except Exception as e:
            monitoring["running"] = False
            monitor_thread.join()
            
            final_memory = self._get_memory_usage()
            
            return BenchmarkResult(
                test_name=test_name,
                duration=time.time() - start_time if 'start_time' in locals() else 0,
                memory_peak=peak_memory,
                memory_initial=initial_memory,
                memory_final=final_memory,
                success=False,
                error_message=str(e)
            )
    
    def benchmark_api_latency(self, num_requests: int = 10) -> List[APIBenchmarkResult]:
        """Benchmark API response latency.
        
        Args:
            num_requests: Number of API requests to make
            
        Returns:
            List of API benchmark results
        """
        results = []
        
        if not self.api_key:
            return [APIBenchmarkResult(
                test_name="api_latency",
                response_time=0,
                status_code=None,
                success=False,
                error_message="No API key provided"
            )]
        
        converter = PDFConverter(api_key=self.api_key)
        
        for i in range(num_requests):
            start_time = time.time()
            
            try:
                # Test key validation as a lightweight API call
                converter._validate_api_key()
                duration = time.time() - start_time
                
                results.append(APIBenchmarkResult(
                    test_name=f"api_latency_request_{i+1}",
                    response_time=duration,
                    status_code=200,
                    success=True
                ))
                
            except Exception as e:
                duration = time.time() - start_time
                
                results.append(APIBenchmarkResult(
                    test_name=f"api_latency_request_{i+1}",
                    response_time=duration,
                    status_code=None,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def benchmark_concurrent_processing(self, num_threads: int = 5, 
                                      file_size_mb: float = 1.0,
                                      output_dir: Path = None) -> List[BenchmarkResult]:
        """Benchmark concurrent PDF processing.
        
        Args:
            num_threads: Number of concurrent threads
            file_size_mb: Size of test files in MB
            output_dir: Directory for test files
            
        Returns:
            List of benchmark results
        """
        if output_dir is None:
            output_dir = Path("./benchmark_temp")
            output_dir.mkdir(exist_ok=True)
        
        results = []
        
        # Create test files
        test_files = []
        for i in range(num_threads):
            test_file = output_dir / f"concurrent_test_{i}.pdf"
            self._create_test_pdf(file_size_mb, test_file)
            test_files.append(test_file)
        
        def process_file(file_path: Path, thread_id: int) -> BenchmarkResult:
            """Process a single file in a thread."""
            return self._benchmark_single_conversion(
                f"concurrent_thread_{thread_id}",
                file_path,
                output_dir / f"output_{thread_id}"
            )
        
        # Run concurrent processing
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(process_file, file_path, i)
                for i, file_path in enumerate(test_files)
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(BenchmarkResult(
                        test_name="concurrent_processing_error",
                        duration=0,
                        memory_peak=0,
                        memory_initial=0,
                        memory_final=0,
                        success=False,
                        error_message=str(e)
                    ))
        
        total_duration = time.time() - start_time
        
        # Add summary result
        successful_results = [r for r in results if r.success]
        if successful_results:
            avg_duration = statistics.mean([r.duration for r in successful_results])
            results.append(BenchmarkResult(
                test_name="concurrent_processing_summary",
                duration=total_duration,
                memory_peak=max([r.memory_peak for r in successful_results]),
                memory_initial=min([r.memory_initial for r in successful_results]),
                memory_final=max([r.memory_final for r in successful_results]),
                success=True,
                additional_metrics={
                    "num_threads": num_threads,
                    "avg_thread_duration": avg_duration,
                    "success_rate": len(successful_results) / len(results)
                }
            ))
        
        # Cleanup
        for file_path in test_files:
            if file_path.exists():
                file_path.unlink()
        
        return results
    
    def benchmark_error_recovery_overhead(self, output_dir: Path) -> List[BenchmarkResult]:
        """Benchmark error handling and recovery overhead.
        
        Args:
            output_dir: Directory for test files
            
        Returns:
            List of benchmark results
        """
        results = []
        
        # Test scenarios that should fail
        test_scenarios = [
            ("empty_file", b""),
            ("invalid_pdf", b"This is not a PDF file"),
            ("corrupted_pdf", b"%PDF-1.4\nCorrupted content"),
            ("large_invalid", b"x" * (10 * 1024 * 1024))  # 10MB invalid
        ]
        
        for scenario_name, content in test_scenarios:
            test_file = output_dir / f"{scenario_name}.pdf"
            test_file.write_bytes(content)
            
            result = self._benchmark_single_conversion(
                f"error_recovery_{scenario_name}",
                test_file,
                output_dir
            )
            results.append(result)
            
            # Cleanup
            if test_file.exists():
                test_file.unlink()
        
        return results
    
    def generate_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Generate comprehensive benchmark report.
        
        Args:
            output_file: Optional file to save report
            
        Returns:
            Dictionary containing the report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "platform": os.name
            },
            "benchmark_results": [asdict(r) for r in self.results],
            "api_results": [asdict(r) for r in self.api_results],
            "summary": self._generate_summary()
        }
        
        if output_file:
            output_file.write_text(json.dumps(report, indent=2))
        
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from benchmark results."""
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        if not successful_results:
            return {
                "total_tests": len(self.results),
                "success_rate": 0,
                "error": "No successful tests to analyze"
            }
        
        durations = [r.duration for r in successful_results]
        memory_usage = [r.memory_peak - r.memory_initial for r in successful_results]
        
        api_successful = [r for r in self.api_results if r.success]
        api_response_times = [r.response_time for r in api_successful] if api_successful else []
        
        return {
            "total_tests": len(self.results),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "success_rate": len(successful_results) / len(self.results),
            "performance_metrics": {
                "avg_duration": statistics.mean(durations),
                "median_duration": statistics.median(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "avg_memory_usage": statistics.mean(memory_usage),
                "peak_memory_usage": max(memory_usage)
            },
            "api_metrics": {
                "total_api_calls": len(self.api_results),
                "successful_api_calls": len(api_successful),
                "api_success_rate": len(api_successful) / len(self.api_results) if self.api_results else 0,
                "avg_response_time": statistics.mean(api_response_times) if api_response_times else 0,
                "median_response_time": statistics.median(api_response_times) if api_response_times else 0
            },
            "common_errors": self._analyze_common_errors(failed_results)
        }
    
    def _analyze_common_errors(self, failed_results: List[BenchmarkResult]) -> Dict[str, int]:
        """Analyze common error patterns."""
        error_counts = {}
        
        for result in failed_results:
            if result.error_message:
                # Categorize errors
                error_msg = result.error_message.lower()
                if "api" in error_msg:
                    category = "API Error"
                elif "timeout" in error_msg:
                    category = "Timeout Error"
                elif "memory" in error_msg:
                    category = "Memory Error"
                elif "invalid" in error_msg or "format" in error_msg:
                    category = "Format Error"
                else:
                    category = "Other Error"
                
                error_counts[category] = error_counts.get(category, 0) + 1
        
        return error_counts


def main():
    """Run comprehensive benchmark suite."""
    output_dir = Path("./benchmark_output")
    output_dir.mkdir(exist_ok=True)
    
    benchmark = PDFConverterBenchmark()
    
    print("Starting PDF Converter Benchmark Suite...")
    
    # Test different file sizes
    print("Testing conversion by file size...")
    size_results = benchmark.benchmark_conversion_by_size(
        [0.1, 0.5, 1.0, 2.0, 5.0], output_dir
    )
    benchmark.results.extend(size_results)
    
    # Test API latency
    print("Testing API latency...")
    api_results = benchmark.benchmark_api_latency(10)
    benchmark.api_results.extend(api_results)
    
    # Test concurrent processing
    print("Testing concurrent processing...")
    concurrent_results = benchmark.benchmark_concurrent_processing(
        num_threads=3, file_size_mb=1.0, output_dir=output_dir
    )
    benchmark.results.extend(concurrent_results)
    
    # Test error recovery
    print("Testing error recovery overhead...")
    error_results = benchmark.benchmark_error_recovery_overhead(output_dir)
    benchmark.results.extend(error_results)
    
    # Generate report
    print("Generating benchmark report...")
    report_file = output_dir / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = benchmark.generate_report(report_file)
    
    # Print summary
    print("\n=== Benchmark Summary ===")
    summary = report["summary"]
    print(f"Total tests: {summary['total_tests']}")
    print(f"Success rate: {summary['success_rate']:.2%}")
    
    if "performance_metrics" in summary:
        metrics = summary["performance_metrics"]
        print(f"Average duration: {metrics['avg_duration']:.2f}s")
        print(f"Average memory usage: {metrics['avg_memory_usage'] / 1024 / 1024:.2f}MB")
    
    if "api_metrics" in summary:
        api_metrics = summary["api_metrics"]
        print(f"API success rate: {api_metrics['api_success_rate']:.2%}")
        print(f"Average API response time: {api_metrics['avg_response_time']:.2f}s")
    
    print(f"\nDetailed report saved to: {report_file}")


if __name__ == "__main__":
    main()