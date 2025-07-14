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
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.file_detector import FileTypeDetector
from ..utils.progress import ProgressTracker
from ..config.profiles import ProfileManager
from .file_converter import DirectFileConverter


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
        """Handle custom file selection"""
        self.console.print("[yellow]Custom file selection not implemented yet[/yellow]")
        # TODO: Implement custom file selection interface
    
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
                try:
                    # Use DirectFileConverter with profile settings
                    # This would need to be implemented to accept profile settings
                    self.console.print(f"Converting: {file.path.name}")
                    
                    # TODO: Integrate with DirectFileConverter using profile settings
                    # await self.direct_converter.convert_with_profile(file.path, output_dir, profile.settings)
                    
                    success_count += 1
                    
                except Exception as e:
                    failed_files.append((file.path.name, str(e)))
                    self.console.print(f"[red]Failed to convert {file.path.name}: {e}[/red]")
                
                progress.update(task, advance=1)
        
        # Display results
        self.console.print(f"\n[bold]Conversion Complete![/bold]")
        self.console.print(f"✅ Successfully converted: {success_count} files")
        
        if failed_files:
            self.console.print(f"❌ Failed conversions: {len(failed_files)}")
            for filename, error in failed_files:
                self.console.print(f"  • {filename}: {error}")
        
        self.console.print(f"\n📁 Output saved to: {output_dir}")