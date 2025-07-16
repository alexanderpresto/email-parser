"""
Interactive File Conversion Module

Phase 4.5: Interactive File Conversion Integration
Provides interactive interface for direct file conversion operations.

This module bridges Phase 4's direct file conversion capabilities with 
Phase 3.5's interactive CLI experience for a unified user interface.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.file_detector import FileTypeDetector
from ..utils.progress import ProgressTracker
from ..config.profiles import ProfileManager
from ..core.config import ProcessingConfig
from .file_converter import DirectFileConverter
from .components.error_handler import ConversionErrorHandler, ErrorContext
from .components.file_selector import CustomFileSelector
from .components.quality_analyzer import ConversionQualityAnalyzer


@dataclass
class ConvertibleFile:
    """Represents a file that can be converted"""
    path: Path
    file_type: str
    size: int
    estimated_conversion_time: float
    complexity_indicators: List[str]
    
    @property
    def size_mb(self) -> float:
        """File size in megabytes"""
        return self.size / (1024 * 1024)


@dataclass
class FileDiscoveryResult:
    """Results from file discovery and analysis"""
    total_files: int
    convertible_files: List[ConvertibleFile]
    total_size: int
    estimated_total_time: float
    recommendations: List[str]
    
    @property
    def total_size_mb(self) -> float:
        """Total size in megabytes"""
        return self.total_size / (1024 * 1024)


@dataclass
class ConversionProfile:
    """File conversion profile configuration"""
    name: str
    description: str
    settings: Dict[str, Any]
    recommended_for: List[str]


class FileConversionProfileManager:
    """Manages file conversion profiles"""
    
    def __init__(self):
        self.console = Console()
        self._initialize_default_profiles()
    
    def _initialize_default_profiles(self):
        """Initialize built-in conversion profiles"""
        self.profiles = {
            "ai_processing": ConversionProfile(
                name="AI Processing",
                description="Optimized for LLM consumption with chunking and metadata",
                settings={
                    "convert_pdf": True,
                    "convert_docx": True, 
                    "convert_excel": True,
                    "pdf_mode": "all",
                    "docx_chunking": True,
                    "docx_metadata": True,
                    "docx_images": True,
                    "docx_chunk_size": 2000,
                    "docx_chunk_overlap": 200
                },
                recommended_for=["research", "analysis", "ai_training"]
            ),
            
            "document_archive": ConversionProfile(
                name="Document Archive", 
                description="Maximum fidelity preservation for archival purposes",
                settings={
                    "convert_pdf": True,
                    "convert_docx": True,
                    "convert_excel": True,
                    "pdf_mode": "all",
                    "docx_chunking": False,
                    "docx_metadata": True,
                    "docx_images": True,
                    "docx_styles": True,
                    "docx_comments": True
                },
                recommended_for=["archival", "preservation", "backup"]
            ),
            
            "quick_conversion": ConversionProfile(
                name="Quick Conversion",
                description="Fast processing with minimal features for quick results",
                settings={
                    "convert_pdf": True,
                    "convert_docx": True,
                    "convert_excel": True,
                    "pdf_mode": "text",
                    "docx_chunking": False,
                    "docx_metadata": False,
                    "docx_images": False
                },
                recommended_for=["preview", "testing", "quick_review"]
            ),
            
            "research_mode": ConversionProfile(
                name="Research Mode",
                description="Enhanced metadata extraction for research workflows", 
                settings={
                    "convert_pdf": True,
                    "convert_docx": True,
                    "convert_excel": True,
                    "pdf_mode": "all",
                    "docx_chunking": True,
                    "docx_metadata": True,
                    "docx_images": True,
                    "docx_styles": True,
                    "docx_comments": True,
                    "docx_chunk_strategy": "semantic"
                },
                recommended_for=["research", "academic", "detailed_analysis"]
            ),
            
            "batch_optimization": ConversionProfile(
                name="Batch Optimization",
                description="Optimized settings for high-throughput batch processing",
                settings={
                    "convert_pdf": True,
                    "convert_docx": True,
                    "convert_excel": True,
                    "pdf_mode": "text",
                    "docx_chunking": False,
                    "docx_metadata": False,
                    "docx_images": False,
                    "max_workers": 8
                },
                recommended_for=["bulk_processing", "automation", "high_volume"]
            )
        }
    
    def get_profiles(self) -> Dict[str, ConversionProfile]:
        """Get all available profiles"""
        return self.profiles
    
    def get_profile(self, name: str) -> Optional[ConversionProfile]:
        """Get a specific profile by name"""
        return self.profiles.get(name)
    
    def recommend_profile(self, files: List[ConvertibleFile]) -> str:
        """Recommend best profile for given files"""
        total_size = sum(f.size for f in files)
        file_types = set(f.file_type for f in files)
        total_files = len(files)
        
        # Logic for profile recommendation
        if total_files > 50:
            return "batch_optimization"
        elif total_size > 100 * 1024 * 1024:  # > 100MB
            return "quick_conversion"
        elif "pdf" in file_types and any("complex" in f.complexity_indicators for f in files):
            return "research_mode"
        else:
            return "ai_processing"


class InteractiveFileConverter:
    """Interactive interface for direct file conversion"""
    
    def __init__(self):
        self.console = Console()
        self.file_detector = FileTypeDetector()
        self.progress_tracker = ProgressTracker(self.console)
        self.profile_manager = FileConversionProfileManager()
        self.direct_converter = DirectFileConverter()
        self.error_handler = ConversionErrorHandler(self.console)
        self.file_selector = CustomFileSelector(self.console)
        self.quality_analyzer = ConversionQualityAnalyzer(self.console)
    
    async def run_file_mode(self) -> None:
        """Main file conversion workflow"""
        self.console.print("\n[bold blue]📁 Document Conversion Mode[/bold blue]")
        self.console.print("Convert documents directly without email context\n")
        
        while True:
            choice = Prompt.ask(
                "Choose conversion method",
                choices=["single", "directory", "custom", "back"],
                default="directory"
            )
            
            if choice == "back":
                break
            elif choice == "single":
                await self._single_file_conversion()
            elif choice == "directory":
                await self._directory_conversion()
            elif choice == "custom":
                await self._custom_file_selection()
    
    async def _single_file_conversion(self) -> None:
        """Handle single file conversion"""
        file_path = Prompt.ask("Enter file path")
        path = Path(file_path)
        
        if not path.exists():
            self.console.print(f"[red]Error: File '{file_path}' not found[/red]")
            return
        
        if not self.file_detector.is_supported(path):
            self.console.print(f"[red]Error: File type not supported[/red]")
            return
        
        # Create convertible file object
        mime_type, converter_type = self.file_detector.detect_type(path)
        convertible_file = ConvertibleFile(
            path=path,
            file_type=converter_type,
            size=path.stat().st_size,
            estimated_conversion_time=self._estimate_conversion_time(path),
            complexity_indicators=self._analyze_complexity(path)
        )
        
        # Show file info
        self._display_file_info([convertible_file])
        
        # Select profile
        profile_name = self._select_conversion_profile([convertible_file])
        profile = self.profile_manager.get_profile(profile_name)
        
        # Get output directory
        output_dir = Prompt.ask("Output directory", default="converted_output")
        
        # Perform conversion
        if Confirm.ask("Proceed with conversion?"):
            await self._perform_conversion([convertible_file], profile, Path(output_dir))
    
    async def _directory_conversion(self) -> None:
        """Handle directory scanning and conversion"""
        directory_path = Prompt.ask("Enter directory path", default=".")
        path = Path(directory_path)
        
        if not path.exists() or not path.is_dir():
            self.console.print(f"[red]Error: Directory '{directory_path}' not found[/red]")
            return
        
        # Scan directory
        self.console.print(f"\n[blue]🔍 Scanning directory: {path}[/blue]")
        discovery_result = await self._scan_directory(path)
        
        if not discovery_result.convertible_files:
            self.console.print("[yellow]No convertible files found in directory[/yellow]")
            return
        
        # Display results
        self._display_discovery_results(discovery_result)
        
        # Show recommendations
        if discovery_result.recommendations:
            self._display_recommendations(discovery_result.recommendations)
        
        # Select profile
        profile_name = self._select_conversion_profile(discovery_result.convertible_files)
        profile = self.profile_manager.get_profile(profile_name)
        
        # Get output directory  
        output_dir = Prompt.ask("Output directory", default="converted_output")
        
        # Perform conversion
        if Confirm.ask("Proceed with batch conversion?"):
            await self._perform_conversion(discovery_result.convertible_files, profile, Path(output_dir))
    
    async def _custom_file_selection(self) -> None:
        """Handle custom file selection with advanced filtering and sorting"""
        self.console.print("\n[bold green]🎯 Custom File Selection[/bold green]")
        self.console.print("Advanced file selection with filtering, sorting, and preview\n")
        
        # Get directory to scan
        directory_path = Prompt.ask("Enter directory path to scan", default=".")
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            self.console.print(f"[red]Error: Directory '{directory_path}' not found[/red]")
            return
        
        # Scan directory for all files
        self.console.print(f"[cyan]Scanning directory: {directory}[/cyan]")
        all_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Discovering files...", total=None)
            
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    all_files.append(file_path)
                    if len(all_files) % 100 == 0:
                        progress.update(task, description=f"Found {len(all_files)} files...")
        
        if not all_files:
            self.console.print("[yellow]No files found in directory[/yellow]")
            return
        
        self.console.print(f"[green]Found {len(all_files)} files[/green]")
        
        # Use file selector for advanced selection
        selected_files = await self.file_selector.select_files(all_files)
        
        if not selected_files:
            self.console.print("[yellow]No files selected for conversion[/yellow]")
            return
        
        # Convert selected files to ConvertibleFile objects
        convertible_files = []
        for file_path in selected_files:
            if self.file_detector.is_supported(file_path):
                file_size = file_path.stat().st_size
                mime_type, converter_type = self.file_detector.detect_type(file_path)
                convertible_file = ConvertibleFile(
                    path=file_path,
                    file_type=converter_type,
                    size=file_size,
                    estimated_conversion_time=self._estimate_conversion_time(file_path),
                    complexity_indicators=self._analyze_complexity(file_path)
                )
                convertible_files.append(convertible_file)
        
        if not convertible_files:
            self.console.print("[yellow]No supported files selected[/yellow]")
            return
        
        # Proceed with conversion workflow
        await self._convert_files_workflow(convertible_files)
    
    async def _scan_directory(self, path: Path) -> FileDiscoveryResult:
        """Scan directory for convertible files"""
        convertible_files = []
        total_files = 0
        total_size = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Scanning files...", total=None)
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_files += 1
                    
                    if self.file_detector.is_supported(file_path):
                        file_size = file_path.stat().st_size
                        mime_type, converter_type = self.file_detector.detect_type(file_path)
                        convertible_file = ConvertibleFile(
                            path=file_path,
                            file_type=converter_type,
                            size=file_size,
                            estimated_conversion_time=self._estimate_conversion_time(file_path),
                            complexity_indicators=self._analyze_complexity(file_path)
                        )
                        convertible_files.append(convertible_file)
                        total_size += file_size
        
        # Generate recommendations
        recommendations = self._generate_recommendations(convertible_files)
        
        return FileDiscoveryResult(
            total_files=total_files,
            convertible_files=convertible_files,
            total_size=total_size,
            estimated_total_time=sum(f.estimated_conversion_time for f in convertible_files),
            recommendations=recommendations
        )
    
    def _display_discovery_results(self, result: FileDiscoveryResult) -> None:
        """Display file discovery results"""
        table = Table(title="File Discovery Results")
        table.add_column("File Type", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Total Size", justify="right")
        
        # Group by file type
        type_stats = {}
        for file in result.convertible_files:
            if file.file_type not in type_stats:
                type_stats[file.file_type] = {"count": 0, "size": 0}
            type_stats[file.file_type]["count"] += 1
            type_stats[file.file_type]["size"] += file.size
        
        for file_type, stats in type_stats.items():
            size_mb = stats["size"] / (1024 * 1024)
            table.add_row(
                f"📄 {file_type.upper()}",
                str(stats["count"]),
                f"{size_mb:.1f} MB"
            )
        
        self.console.print(table)
        self.console.print(f"\n[bold]Total: {len(result.convertible_files)} convertible files ({result.total_size_mb:.1f} MB)[/bold]")
        self.console.print(f"[dim]Estimated conversion time: {result.estimated_total_time:.1f} seconds[/dim]")
    
    def _display_file_info(self, files: List[ConvertibleFile]) -> None:
        """Display information about selected files"""
        if len(files) == 1:
            file = files[0]
            panel_content = f"""
[bold]File:[/bold] {file.path.name}
[bold]Type:[/bold] {file.file_type.upper()}
[bold]Size:[/bold] {file.size_mb:.2f} MB
[bold]Estimated time:[/bold] {file.estimated_conversion_time:.1f}s
            """
            if file.complexity_indicators:
                panel_content += f"\n[bold]Complexity:[/bold] {', '.join(file.complexity_indicators)}"
            
            self.console.print(Panel(panel_content.strip(), title="File Information"))
    
    def _display_recommendations(self, recommendations: List[str]) -> None:
        """Display conversion recommendations"""
        if recommendations:
            panel_content = "\n".join(f"• {rec}" for rec in recommendations)
            self.console.print(Panel(panel_content, title="💡 Recommendations", style="yellow"))
    
    def _select_conversion_profile(self, files: List[ConvertibleFile]) -> str:
        """Interactive profile selection"""
        profiles = self.profile_manager.get_profiles()
        recommended = self.profile_manager.recommend_profile(files)
        
        self.console.print(f"\n[bold]Select conversion profile:[/bold]")
        
        choices = []
        for key, profile in profiles.items():
            recommended_text = " (Recommended)" if key == recommended else ""
            self.console.print(f"  [cyan]{key}[/cyan]: {profile.description}{recommended_text}")
            choices.append(key)
        
        return Prompt.ask("Profile", choices=choices, default=recommended)
    
    def _generate_recommendations(self, files: List[ConvertibleFile]) -> List[str]:
        """Generate recommendations based on file analysis"""
        recommendations = []
        
        if not files:
            return recommendations
        
        total_size = sum(f.size for f in files)
        pdf_files = [f for f in files if f.file_type == "pdf"]
        docx_files = [f for f in files if f.file_type == "docx"]
        
        # Size-based recommendations
        if total_size > 100 * 1024 * 1024:  # > 100MB
            recommendations.append("Large file set detected - consider 'Quick Conversion' profile for faster processing")
        
        # PDF-specific recommendations
        if pdf_files:
            large_pdfs = [f for f in pdf_files if f.size > 10 * 1024 * 1024]  # > 10MB
            if large_pdfs:
                recommendations.append("Large PDF files detected - 'AI Processing' profile recommended for chunking")
        
        # DOCX-specific recommendations
        if docx_files:
            complex_docx = [f for f in docx_files if "complex" in f.complexity_indicators]
            if complex_docx:
                recommendations.append("Complex DOCX files detected - 'Research Mode' profile for enhanced extraction")
        
        # Batch processing recommendations
        if len(files) > 20:
            recommendations.append("Large batch detected - 'Batch Optimization' profile for best throughput")
        
        return recommendations
    
    def _estimate_conversion_time(self, file_path: Path) -> float:
        """Estimate conversion time for a file"""
        file_size = file_path.stat().st_size
        mime_type, file_type = self.file_detector.detect_type(file_path)
        
        # Basic time estimation (seconds)
        base_time = {
            "pdf": 2.0,
            "docx": 1.5, 
            "excel": 1.0
        }.get(file_type, 1.0)
        
        # Size factor (per MB)
        size_mb = file_size / (1024 * 1024)
        size_factor = max(0.5, size_mb * 0.3)
        
        return base_time + size_factor
    
    def _analyze_complexity(self, file_path: Path) -> List[str]:
        """Analyze file complexity indicators"""
        indicators = []
        file_size = file_path.stat().st_size
        mime_type, file_type = self.file_detector.detect_type(file_path)
        
        # Size-based indicators
        if file_size > 10 * 1024 * 1024:  # > 10MB
            indicators.append("large")
        
        # Type-specific indicators  
        if file_type == "pdf":
            # Could add PDF-specific analysis here
            if file_size > 5 * 1024 * 1024:  # > 5MB
                indicators.append("complex")
        elif file_type == "docx":
            # Could add DOCX-specific analysis here
            if file_size > 2 * 1024 * 1024:  # > 2MB
                indicators.append("complex")
        
        return indicators
    
    async def _perform_conversion(self, files: List[ConvertibleFile], profile: ConversionProfile, output_dir: Path) -> None:
        """Perform the actual file conversion"""
        self.console.print(f"\n[bold green]Starting conversion with '{profile.name}' profile...[/bold green]")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        failed_files = []
        
        with Progress(console=self.console) as progress:
            task = progress.add_task("Converting files...", total=len(files))
            
            for file in files:
                max_retries = 3
                retry_count = 0
                file_success = False
                
                while retry_count < max_retries and not file_success:
                    try:
                        # Use DirectFileConverter with profile settings
                        self.console.print(f"Converting: {file.path.name}")
                        
                        # Convert file with profile settings
                        result = await self._convert_with_profile(file.path, profile, output_dir)
                        
                        if result['success']:
                            success_count += 1
                            file_success = True
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            
                            # Handle error with recovery options
                            error_context = {
                                'file_path': str(file.path),
                                'operation': 'file_conversion',
                                'profile': profile.name,
                                'retry_count': retry_count
                            }
                            
                            # Create a mock exception for error handling
                            mock_error = Exception(error_msg)
                            recovery_action = await self.error_handler.handle_error(mock_error, error_context)
                            
                            if recovery_action:
                                retry_count += 1
                                self.console.print(f"[cyan]Retrying conversion... (attempt {retry_count}/{max_retries})[/cyan]")
                                continue
                            else:
                                failed_files.append((file.path.name, error_msg))
                                self.console.print(f"[red]Failed to convert {file.path.name}: {error_msg}[/red]")
                                break
                        
                    except Exception as e:
                        # Handle unexpected exceptions
                        error_context = {
                            'file_path': str(file.path),
                            'operation': 'file_conversion',
                            'profile': profile.name,
                            'retry_count': retry_count
                        }
                        
                        recovery_action = await self.error_handler.handle_error(e, error_context)
                        
                        if recovery_action and retry_count < max_retries - 1:
                            retry_count += 1
                            self.console.print(f"[cyan]Retrying conversion... (attempt {retry_count}/{max_retries})[/cyan]")
                            continue
                        else:
                            failed_files.append((file.path.name, str(e)))
                            self.console.print(f"[red]Failed to convert {file.path.name}: {e}[/red]")
                            break
                
                progress.update(task, advance=1)
        
        # Display results
        self.console.print(f"\n[bold]Conversion Complete![/bold]")
        self.console.print(f"✅ Successfully converted: {success_count} files")
        
        if failed_files:
            self.console.print(f"❌ Failed conversions: {len(failed_files)}")
            for filename, error in failed_files:
                self.console.print(f"  • {filename}: {error}")
        
        self.console.print(f"\n📁 Output saved to: {output_dir}")
        
        # Offer quality analysis for successful conversions
        if success_count > 0 and Confirm.ask("\nRun quality analysis on converted files?", default=True):
            await self._run_quality_analysis(files, output_dir, profile)
    
    async def _convert_with_profile(self, file_path: Path, profile: ConversionProfile, output_dir: Path) -> Dict[str, Any]:
        """
        Convert file using DirectFileConverter with profile settings.
        
        Args:
            file_path: Path to file to convert
            profile: ConversionProfile to use for conversion
            output_dir: Output directory for converted files
            
        Returns:
            Dictionary with conversion results including success status and any errors
        """
        try:
            # Map profile settings to ProcessingConfig
            config = self._map_profile_to_config(profile.settings, str(output_dir))
            
            # Create a new DirectFileConverter with the mapped configuration
            converter = DirectFileConverter(config=config, output_directory=str(output_dir))
            
            # Run conversion in thread pool to avoid blocking async loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                converter.convert_file,
                file_path,
                output_dir,
                None  # options
            )
            
            return {
                'success': result.success,
                'output_path': str(result.output_path) if result.output_path else None,
                'duration': result.duration_seconds,
                'error': result.error_message,
                'metadata': result.metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': 0.0
            }
    
    def _map_profile_to_config(self, profile_settings: Dict[str, Any], output_dir: str) -> ProcessingConfig:
        """
        Map ConversionProfile settings to ProcessingConfig format.
        
        Args:
            profile_settings: Settings from the ConversionProfile
            output_dir: Output directory path
            
        Returns:
            ProcessingConfig instance with mapped settings
        """
        # Create base config
        config = ProcessingConfig(output_directory=output_dir)
        
        # Map PDF conversion settings
        if profile_settings.get('convert_pdf', False):
            config.convert_pdf = True
            config.pdf_extraction_mode = profile_settings.get('pdf_mode', 'all')
        else:
            config.convert_pdf = False
            
        # Map DOCX conversion settings
        if profile_settings.get('convert_docx', False):
            config.convert_docx = True
            config.docx_conversion.enabled = True
            config.docx_conversion.enable_chunking = profile_settings.get('docx_chunking', False)
            config.docx_conversion.extract_metadata = profile_settings.get('docx_metadata', True)
            config.docx_conversion.extract_images = profile_settings.get('docx_images', False)
            config.docx_conversion.extract_styles = profile_settings.get('docx_styles', False)
            config.docx_conversion.include_comments = profile_settings.get('docx_comments', False)
            
            # Chunking settings
            if profile_settings.get('docx_chunking', False):
                config.docx_conversion.max_chunk_tokens = profile_settings.get('docx_chunk_size', 2000)
                config.docx_conversion.chunk_overlap = profile_settings.get('docx_chunk_overlap', 200)
                if 'docx_chunk_strategy' in profile_settings:
                    config.docx_conversion.chunk_strategy = profile_settings['docx_chunk_strategy']
        else:
            config.convert_docx = False
            config.docx_conversion.enabled = False
            
        # Map Excel conversion settings
        if profile_settings.get('convert_excel', False):
            config.convert_excel = True
            # Excel converter doesn't have many configurable options in current implementation
        else:
            config.convert_excel = False
            
        # Map performance settings if available
        if 'performance' in profile_settings:
            perf = profile_settings['performance']
            if 'parallel_processing' in perf:
                config.enable_parallel_processing = perf['parallel_processing']
            if 'memory_limit_mb' in perf:
                config.memory_limit_mb = perf['memory_limit_mb']
                
        return config
    
    async def _run_quality_analysis(self, files: List[ConvertibleFile], output_dir: Path, profile: ConversionProfile) -> None:
        """Run quality analysis on converted files."""
        self.console.print("\n[cyan]🔍 Running Quality Analysis...[/cyan]")
        
        conversion_results = []
        
        # Collect conversion results for analysis
        for file in files:
            # Try to find the converted file
            converted_file = self._find_converted_file(file.path, output_dir, file.file_type)
            
            if converted_file and converted_file.exists():
                conversion_results.append({
                    'success': True,
                    'input_path': str(file.path),
                    'output_path': str(converted_file),
                    'converter_type': file.file_type,
                    'metadata': {}  # Could be populated from actual conversion metadata
                })
        
        if not conversion_results:
            self.console.print("[yellow]No converted files found for analysis[/yellow]")
            return
        
        # Run batch quality analysis
        batch_analysis = await self.quality_analyzer.analyze_batch_quality(conversion_results)
        
        # Display batch analysis results
        self._display_batch_quality_results(batch_analysis)
        
        # Offer individual file analysis
        if Confirm.ask("View detailed quality reports for individual files?", default=False):
            await self._show_individual_quality_reports(conversion_results)
    
    def _find_converted_file(self, original_path: Path, output_dir: Path, file_type: str) -> Optional[Path]:
        """Find the converted file for a given original file."""
        base_name = original_path.stem
        
        # Common conversion patterns
        if file_type == 'pdf':
            # PDF usually converts to markdown
            possible_names = [
                f"{base_name}.md",
                f"{base_name}_converted.md",
                f"{base_name}_pdf.md"
            ]
            search_dir = output_dir / "converted_pdf"
        elif file_type == 'docx':
            possible_names = [
                f"{base_name}.md",
                f"{base_name}_converted.md",
                f"{base_name}_docx.md"
            ]
            search_dir = output_dir / "converted_docx"
        elif file_type in ['xlsx', 'xls']:
            possible_names = [
                f"{base_name}.csv",
                f"{base_name}_converted.csv",
                f"{base_name}_excel.csv"
            ]
            search_dir = output_dir / "converted_excel"
        else:
            return None
        
        # Search for the converted file
        if search_dir.exists():
            for name in possible_names:
                candidate = search_dir / name
                if candidate.exists():
                    return candidate
            
            # Fallback: look for any file with similar name
            for file_path in search_dir.iterdir():
                if file_path.is_file() and base_name in file_path.name:
                    return file_path
        
        return None
    
    def _display_batch_quality_results(self, batch_analysis: Dict[str, Any]) -> None:
        """Display batch quality analysis results."""
        if not batch_analysis or "message" in batch_analysis:
            self.console.print("[yellow]No quality analysis available[/yellow]")
            return
        
        # Summary table
        table = Table(title="📊 Batch Quality Summary", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        total_files = batch_analysis.get("total_files", 0)
        analyzed_files = batch_analysis.get("analyzed_files", 0)
        avg_quality = batch_analysis.get("average_quality", 0.0)
        high_quality = batch_analysis.get("high_quality_files", 0)
        medium_quality = batch_analysis.get("medium_quality_files", 0)
        low_quality = batch_analysis.get("low_quality_files", 0)
        
        table.add_row("Total Files", str(total_files))
        table.add_row("Analyzed Files", str(analyzed_files))
        table.add_row("Average Quality", f"{avg_quality:.1%}")
        table.add_row("High Quality (≥80%)", f"{high_quality} files")
        table.add_row("Medium Quality (60-79%)", f"{medium_quality} files")
        table.add_row("Low Quality (<60%)", f"{low_quality} files")
        
        self.console.print(table)
        
        # Quality by type
        quality_by_type = batch_analysis.get("quality_by_type", {})
        if quality_by_type:
            type_table = Table(title="Quality by File Type", show_header=True)
            type_table.add_column("File Type", style="cyan")
            type_table.add_column("Average Quality", justify="right")
            type_table.add_column("Count", justify="right")
            
            for file_type, stats in quality_by_type.items():
                type_table.add_row(
                    file_type.upper(),
                    f"{stats['average']:.1%}",
                    str(stats['count'])
                )
            
            self.console.print(type_table)
        
        # Common issues
        common_issues = batch_analysis.get("common_issues", [])
        if common_issues:
            issues_text = "\n".join(f"• {issue[0]} ({issue[1]} files)" for issue in common_issues[:5])
            panel = Panel(issues_text, title="🔧 Most Common Issues", border_style="yellow")
            self.console.print(panel)
    
    async def _show_individual_quality_reports(self, conversion_results: List[Dict[str, Any]]) -> None:
        """Show individual quality reports."""
        for i, result in enumerate(conversion_results):
            if not result.get('success'):
                continue
            
            try:
                original_path = Path(result['input_path'])
                converted_path = Path(result['output_path'])
                converter_type = result['converter_type']
                
                self.console.print(f"\n[bold]File {i+1}/{len(conversion_results)}[/bold]")
                
                # Generate and display quality report
                quality_report = await self.quality_analyzer.analyze_conversion(
                    original_path, converted_path, converter_type, result.get('metadata')
                )
                
                self.quality_analyzer.display_quality_report(quality_report)
                
                # Ask if user wants to continue to next file
                if i < len(conversion_results) - 1:
                    if not Confirm.ask("Continue to next file?", default=True):
                        break
                        
            except Exception as e:
                self.console.print(f"[red]Error analyzing {result.get('input_path', 'unknown')}: {e}[/red]")
                continue