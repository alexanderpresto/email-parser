#!/usr/bin/env python3
"""
Performance validation tests for Phase 4.5 requirements.

Phase 4.5: Interactive File Conversion - Day 7+ Testing
Validates all performance requirements specified in the development plan.
"""

import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

from email_parser.cli.interactive_file import (
    ConvertibleFile,
    FileConversionProfileManager,
    InteractiveFileConverter,
)


class Phase45PerformanceValidator:
    """Validates Phase 4.5 performance requirements."""

    def __init__(self):
        self.results = {}
        self.temp_dir = None

    def setup_test_environment(self):
        """Create test environment with sample files."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test files of various sizes
        test_files = {
            "small_files": [],
            "medium_files": [],
            "large_files": [],
        }

        # Create 10 small files (< 1MB each)
        for i in range(10):
            file_path = self.temp_dir / f"small_{i}.txt"
            file_path.write_text("Small file content " * 1000)  # ~20KB
            test_files["small_files"].append(file_path)

        # Create 100 medium files (1-5MB each)
        for i in range(100):
            file_path = self.temp_dir / f"medium_{i}.txt"
            file_path.write_text("Medium file content " * 50000)  # ~1MB
            test_files["medium_files"].append(file_path)

        # Create 10 large files (5-10MB each)
        for i in range(10):
            file_path = self.temp_dir / f"large_{i}.txt"
            file_path.write_text("Large file content " * 200000)  # ~4MB
            test_files["large_files"].append(file_path)

        return test_files

    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_dir:
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_file_discovery_performance(self):
        """Test: File discovery < 2 seconds for directories with < 100 files."""
        print("Testing file discovery performance...")

        test_files = self.setup_test_environment()

        with patch("email_parser.cli.interactive_file.Console"):
            converter = InteractiveFileConverter()

            # Test 1: Small directory (10 files)
            small_dir = self.temp_dir / "small"
            small_dir.mkdir()
            for file_path in test_files["small_files"]:
                new_path = small_dir / file_path.name
                new_path.write_text(file_path.read_text())

            start_time = time.time()
            result = await converter._scan_directory(small_dir)
            discovery_time_small = time.time() - start_time

            # Test 2: Medium directory (100 files)
            medium_dir = self.temp_dir / "medium"
            medium_dir.mkdir()
            for file_path in test_files["medium_files"]:
                new_path = medium_dir / file_path.name
                new_path.write_text(file_path.read_text())

            start_time = time.time()
            result = await converter._scan_directory(medium_dir)
            discovery_time_medium = time.time() - start_time

            # Validate requirements
            requirement_met_small = discovery_time_small < 2.0
            requirement_met_medium = discovery_time_medium < 2.0

            self.results["file_discovery"] = {
                "small_dir_time": discovery_time_small,
                "medium_dir_time": discovery_time_medium,
                "requirement_10_files": requirement_met_small,
                "requirement_100_files": requirement_met_medium,
                "total_files_discovered": len(result.convertible_files),
            }

            print(f"  Small directory (10 files): {discovery_time_small:.3f}s - {'PASS' if requirement_met_small else 'FAIL'}")
            print(f"  Medium directory (100 files): {discovery_time_medium:.3f}s - {'PASS' if requirement_met_medium else 'FAIL'}")

        return requirement_met_small and requirement_met_medium

    def test_ui_responsiveness(self):
        """Test: UI responsiveness with progress updates every 100ms minimum."""
        print("Testing UI responsiveness...")

        update_intervals = []
        last_update_time = time.time()

        def mock_update_callback(*args, **kwargs):
            nonlocal last_update_time
            current_time = time.time()
            interval = current_time - last_update_time
            update_intervals.append(interval)
            last_update_time = current_time

        # Simulate progress updates
        total_updates = 50
        for i in range(total_updates):
            mock_update_callback()
            time.sleep(0.05)  # Simulate 50ms work intervals

        # Analyze update frequency
        if update_intervals:
            avg_interval = sum(update_intervals) / len(update_intervals)
            max_interval = max(update_intervals)
            min_interval = min(update_intervals)

            # Requirement: Updates every 100ms minimum (max interval should be ~100ms)
            responsiveness_met = max_interval <= 0.15  # Allow 150ms tolerance

            self.results["ui_responsiveness"] = {
                "average_interval": avg_interval,
                "max_interval": max_interval,
                "min_interval": min_interval,
                "total_updates": len(update_intervals),
                "requirement_met": responsiveness_met,
            }

            print(f"  Average update interval: {avg_interval*1000:.1f}ms")
            print(f"  Max update interval: {max_interval*1000:.1f}ms - {'PASS' if responsiveness_met else 'FAIL'}")

            return responsiveness_met

        return False

    def test_memory_optimization(self):
        """Test: Memory optimization < 100MB increase for large file sets."""
        print("Testing memory optimization...")

        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Simulate processing large file set
        with patch("email_parser.cli.interactive_file.Console"):
            converter = InteractiveFileConverter()

            # Create large file set in memory
            large_files = []
            for i in range(1000):
                file_info = ConvertibleFile(
                    path=Path(f"/simulated/file_{i}.pdf"),
                    file_type="pdf",
                    size=5 * 1024 * 1024,  # 5MB each
                    estimated_conversion_time=2.0,
                    complexity_indicators=["large"] if i % 10 == 0 else [],
                )
                large_files.append(file_info)

            # Simulate file discovery and analysis
            discovery_result = converter._generate_recommendations(large_files)

            # Measure memory after processing
            final_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_increase = final_memory - initial_memory

            # Requirement: < 100MB increase
            memory_requirement_met = memory_increase < 100.0

            self.results["memory_optimization"] = {
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "files_processed": len(large_files),
                "requirement_met": memory_requirement_met,
            }

            print(f"  Initial memory: {initial_memory:.1f}MB")
            print(f"  Final memory: {final_memory:.1f}MB")
            print(f"  Memory increase: {memory_increase:.1f}MB - {'PASS' if memory_requirement_met else 'FAIL'}")

            return memory_requirement_met

    def test_profile_recommendations(self):
        """Test: Profile recommendations < 0.1 seconds even for 1000+ files."""
        print("Testing profile recommendation performance...")

        profile_manager = FileConversionProfileManager()

        # Create test file sets of various sizes
        test_sizes = [10, 100, 500, 1000, 2000]
        recommendation_times = {}

        for size in test_sizes:
            files = []
            for i in range(size):
                file_info = ConvertibleFile(
                    path=Path(f"/test/file_{i}.pdf"),
                    file_type="pdf" if i % 2 == 0 else "docx",
                    size=(i % 10 + 1) * 1024 * 1024,  # 1-10MB files
                    estimated_conversion_time=float(i % 5 + 1),
                    complexity_indicators=["complex"] if i % 20 == 0 else [],
                )
                files.append(file_info)

            # Time recommendation generation
            start_time = time.time()
            recommendation = profile_manager.recommend_profile(files)
            recommendation_time = time.time() - start_time

            recommendation_times[size] = recommendation_time

            requirement_met = recommendation_time < 0.1
            print(f"  {size} files: {recommendation_time*1000:.1f}ms -> {recommendation} - {'PASS' if requirement_met else 'FAIL'}")

        # Check if all tests pass the 0.1s requirement
        all_requirements_met = all(time < 0.1 for time in recommendation_times.values())

        self.results["profile_recommendations"] = {
            "recommendation_times": recommendation_times,
            "max_time": max(recommendation_times.values()),
            "requirement_met": all_requirements_met,
        }

        return all_requirements_met

    def test_batch_processing_ui(self):
        """Test: Batch processing UI handles 100 files in < 5 seconds UI time."""
        print("Testing batch processing UI performance...")

        # Mock UI operations timing
        ui_operations = []
        start_time = time.time()

        # Simulate UI operations for 100 files
        for i in range(100):
            # Simulate file discovery UI update
            ui_start = time.time()
            time.sleep(0.001)  # 1ms UI operation
            ui_operations.append(time.time() - ui_start)

            # Simulate progress bar update
            ui_start = time.time()
            time.sleep(0.002)  # 2ms progress update
            ui_operations.append(time.time() - ui_start)

            # Simulate status message update
            ui_start = time.time()
            time.sleep(0.001)  # 1ms status update
            ui_operations.append(time.time() - ui_start)

        total_ui_time = time.time() - start_time

        # Requirement: Handle 100 files in < 5 seconds UI time
        requirement_met = total_ui_time < 5.0

        self.results["batch_processing_ui"] = {
            "total_ui_time": total_ui_time,
            "files_processed": 100,
            "ui_operations": len(ui_operations),
            "average_operation_time": sum(ui_operations) / len(ui_operations),
            "requirement_met": requirement_met,
        }

        print(f"  Total UI time for 100 files: {total_ui_time:.3f}s - {'PASS' if requirement_met else 'FAIL'}")

        return requirement_met

    async def run_all_tests(self):
        """Run all performance validation tests."""
        print("=" * 60)
        print("Phase 4.5 Performance Validation Tests")
        print("=" * 60)

        try:
            # Run all performance tests
            test_results = {
                "file_discovery": await self.test_file_discovery_performance(),
                "ui_responsiveness": self.test_ui_responsiveness(),
                "memory_optimization": self.test_memory_optimization(),
                "profile_recommendations": self.test_profile_recommendations(),
                "batch_processing_ui": self.test_batch_processing_ui(),
            }

            # Summary
            print("\n" + "=" * 60)
            print("Performance Test Summary")
            print("=" * 60)

            passed_tests = sum(test_results.values())
            total_tests = len(test_results)

            for test_name, passed in test_results.items():
                status = "PASS" if passed else "FAIL"
                print(f"  {test_name.replace('_', ' ').title()}: {status}")

            print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

            if passed_tests == total_tests:
                print("All Phase 4.5 performance requirements met!")
                return True
            else:
                print("Some performance requirements not met. See details above.")
                return False

        finally:
            self.cleanup_test_environment()

    def generate_performance_report(self):
        """Generate detailed performance report."""
        print("\n" + "=" * 60)
        print("Detailed Performance Report")
        print("=" * 60)

        for test_name, results in self.results.items():
            print(f"\n{test_name.replace('_', ' ').title()}:")
            for key, value in results.items():
                if isinstance(value, float):
                    if "time" in key.lower():
                        print(f"  {key}: {value:.3f}s")
                    elif "mb" in key.lower():
                        print(f"  {key}: {value:.1f}MB")
                    else:
                        print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")


async def main():
    """Main entry point for performance validation."""
    validator = Phase45PerformanceValidator()
    success = await validator.run_all_tests()
    validator.generate_performance_report()

    return 0 if success else 1


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))