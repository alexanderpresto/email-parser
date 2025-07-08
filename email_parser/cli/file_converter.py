"""
Direct file conversion interface for standalone document processing.

This module provides a unified interface for converting documents
without requiring email context.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from email_parser.converters.pdf_converter import PDFConverter
from email_parser.converters.docx_converter import DocxConverter
from email_parser.converters.excel_converter import ExcelConverter
from email_parser.utils.file_detector import FileTypeDetector
from email_parser.core.config import ProcessingConfig
from email_parser.exceptions.converter_exceptions import (
    ConversionError, 
    UnsupportedFormatError,
    FileSizeError
)

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of a file conversion operation."""
    success: bool
    input_path: Path
    output_path: Optional[Path] = None
    converter_type: Optional[str] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DirectFileConverter:
    """Handles direct file conversion without email context."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None, output_directory: str = "output"):
        """
        Initialize the DirectFileConverter.
        
        Args:
            config: Processing configuration. If None, default config is used.
            output_directory: Default output directory for conversions.
        """
        if config is None:
            self.config = ProcessingConfig(output_directory=output_directory)
        else:
            self.config = config
            
        self.console = Console()
        self.file_detector = FileTypeDetector()
        
        # Initialize converters with appropriate configurations
        # Convert ProcessingConfig to dict format expected by converters
        pdf_config = self._get_pdf_config()
        docx_config = self._get_docx_config()
        excel_output_dir = f"{self.config.output_directory}/converted_excel"
        
        self.converters = {
            'pdf': PDFConverter(config=pdf_config),
            'docx': DocxConverter(config=docx_config),
            'xlsx': ExcelConverter(output_dir=excel_output_dir),
            'xls': ExcelConverter(output_dir=excel_output_dir)  # Use same converter for both Excel formats
        }
        
        logger.debug("DirectFileConverter initialized with converters: %s", list(self.converters.keys()))
    
    def _get_pdf_config(self) -> Dict[str, Any]:
        """Convert ProcessingConfig to PDF converter config format."""
        return {
            'api_key_env': self.config.pdf_conversion.api_key_env,
            'extraction_mode': self.config.pdf_extraction_mode,
            'max_file_size': self.config.max_attachment_size,
            'output_dir': f"{self.config.output_directory}/converted_pdf",
            'image_settings': {
                'limit': self.config.pdf_image_limit,
                'min_size': self.config.pdf_image_min_size,
                'save_images': True,
                'image_dir': 'images'
            },
            'pagination': {
                'enabled': self.config.pdf_paginate,
                'page_separator': '\\n\\n---\\n\\n'
            }
        }
    
    def _get_docx_config(self) -> Dict[str, Any]:
        """Convert ProcessingConfig to DOCX converter config format."""
        return {
            'max_file_size': self.config.docx_conversion.max_file_size,
            'output_format': self.config.docx_conversion.output_format,
            'extract_tables': self.config.docx_conversion.extract_tables,
            'enable_chunking': self.config.docx_enable_chunking,
            'chunking_strategy': self.config.docx_chunk_strategy,
            'max_chunk_tokens': self.config.docx_chunk_size,
            'chunk_overlap': self.config.docx_chunk_overlap,
            'extract_metadata': self.config.docx_extract_metadata,
            'extract_styles': self.config.docx_extract_styles,
            'extract_images': self.config.docx_extract_images,
            'include_comments': self.config.docx_extract_comments,
            'output_dir': f"{self.config.output_directory}/converted_docx"
        }
    
    def convert_file(self, file_path: Path, output_dir: Path, 
                    options: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """
        Convert a single file.
        
        Args:
            file_path: Path to the file to convert
            output_dir: Directory where output files should be saved
            options: Optional conversion options
            
        Returns:
            ConversionResult with details about the conversion
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not file_path.exists():
                return ConversionResult(
                    success=False,
                    input_path=file_path,
                    error_message=f"File not found: {file_path}"
                )
            
            # Detect file type
            try:
                mime_type, converter_type = self.file_detector.detect_type(file_path)
            except ValueError as e:
                return ConversionResult(
                    success=False,
                    input_path=file_path,
                    error_message=str(e)
                )
            
            # Get appropriate converter
            if converter_type not in self.converters:
                return ConversionResult(
                    success=False,
                    input_path=file_path,
                    converter_type=converter_type,
                    error_message=f"No converter available for type: {converter_type}"
                )
            
            converter = self.converters[converter_type]
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Perform conversion using standalone method if available, otherwise adapt existing method
            if hasattr(converter, 'convert_standalone'):
                output_path = converter.convert_standalone(file_path, output_dir, options)
            else:
                # Fallback to existing convert method
                output_path = self._convert_with_fallback(converter, file_path, output_dir, options)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Get conversion metadata
            metadata = self._get_conversion_metadata(file_path, output_path, converter_type, duration)
            
            logger.info(f"Successfully converted {file_path.name} to {output_path.name} in {duration:.2f}s")
            
            return ConversionResult(
                success=True,
                input_path=file_path,
                output_path=output_path,
                converter_type=converter_type,
                duration_seconds=duration,
                metadata=metadata
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = f"Conversion failed: {type(e).__name__}: {e}"
            
            logger.error(f"Failed to convert {file_path.name}: {error_msg}")
            
            return ConversionResult(
                success=False,
                input_path=file_path,
                converter_type=getattr(self, '_last_converter_type', None),
                duration_seconds=duration,
                error_message=error_msg
            )
    
    def _convert_with_fallback(self, converter, file_path: Path, output_dir: Path, 
                              options: Optional[Dict[str, Any]] = None) -> Path:
        """
        Convert file using existing converter interface with adaptations.
        
        Args:
            converter: The converter instance to use
            file_path: Path to input file
            output_dir: Output directory
            options: Conversion options
            
        Returns:
            Path to converted file
        """
        # Generate output path in the specified directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = file_path.stem
        output_name = f"{base_name}_{timestamp}.md"
        output_path = output_dir / output_name
        
        # Use the converter's existing convert method
        # Most converters auto-generate output paths, so we might need to move the result
        result_path = converter.convert(file_path, output_path)
        
        return result_path
    
    def convert_batch(self, files: List[Path], output_dir: Path,
                     options: Optional[Dict[str, Any]] = None,
                     show_progress: bool = True) -> List[ConversionResult]:
        """
        Convert multiple files with progress tracking.
        
        Args:
            files: List of file paths to convert
            output_dir: Directory where output files should be saved
            options: Optional conversion options
            show_progress: Whether to show progress indicators
            
        Returns:
            List of ConversionResult objects, one for each file
        """
        results = []
        
        if not files:
            return results
        
        logger.info(f"Starting batch conversion of {len(files)} files")
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task_id = progress.add_task("Converting files...", total=len(files))
                
                for i, file_path in enumerate(files):
                    progress.update(task_id, description=f"Converting {file_path.name}")
                    
                    result = self.convert_file(file_path, output_dir, options)
                    results.append(result)
                    
                    progress.advance(task_id)
        else:
            # Convert without progress display
            for file_path in files:
                result = self.convert_file(file_path, output_dir, options)
                results.append(result)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(f"Batch conversion completed: {successful} successful, {failed} failed")
        
        return results
    
    def scan_directory(self, directory: Path, pattern: str = "*", 
                      recursive: bool = False) -> List[Path]:
        """
        Scan a directory for supported files.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match (e.g., "*.pdf", "*")
            recursive: Whether to search subdirectories
            
        Returns:
            List of supported file paths found
        """
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Directory not found or not a directory: {directory}")
        
        # Get all files matching the pattern
        if recursive:
            all_files = list(directory.rglob(pattern))
        else:
            all_files = list(directory.glob(pattern))
        
        # Filter to only supported files
        supported_files = []
        for file_path in all_files:
            if file_path.is_file() and self.file_detector.is_supported(file_path):
                supported_files.append(file_path)
        
        logger.debug(f"Found {len(supported_files)} supported files in {directory}")
        return supported_files
    
    def get_conversion_preview(self, files: List[Path]) -> Dict[str, Any]:
        """
        Get a preview of what would be converted without actually converting.
        
        Args:
            files: List of file paths to analyze
            
        Returns:
            Dictionary with conversion preview information
        """
        preview = {
            'total_files': len(files),
            'supported_files': 0,
            'unsupported_files': 0,
            'by_type': {},
            'estimated_time': 0.0,
            'total_size': 0,
            'file_details': []
        }
        
        for file_path in files:
            file_info = self.file_detector.get_file_info(file_path)
            preview['file_details'].append(file_info)
            
            if file_info.get('supported', False):
                preview['supported_files'] += 1
                converter_type = file_info.get('converter_type', 'unknown')
                preview['by_type'][converter_type] = preview['by_type'].get(converter_type, 0) + 1
                
                # Add to size calculation
                file_size = file_info.get('size', 0)
                preview['total_size'] += file_size
                
                # Rough time estimation (very approximate)
                if converter_type == 'pdf':
                    preview['estimated_time'] += max(5.0, file_size / (1024 * 1024) * 2)  # 2s per MB
                elif converter_type in ['docx', 'xlsx', 'xls']:
                    preview['estimated_time'] += max(2.0, file_size / (1024 * 1024) * 1)  # 1s per MB
                else:
                    preview['estimated_time'] += 3.0  # Default estimate
            else:
                preview['unsupported_files'] += 1
        
        return preview
    
    def _get_conversion_metadata(self, input_path: Path, output_path: Path, 
                               converter_type: str, duration: float) -> Dict[str, Any]:
        """
        Generate metadata for a conversion operation.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            converter_type: Type of converter used
            duration: Conversion duration in seconds
            
        Returns:
            Metadata dictionary
        """
        input_stat = input_path.stat()
        output_stat = output_path.stat() if output_path and output_path.exists() else None
        
        return {
            'converter_type': converter_type,
            'conversion_time': datetime.now().isoformat(),
            'duration_seconds': duration,
            'input_file': {
                'name': input_path.name,
                'size': input_stat.st_size,
                'modified': datetime.fromtimestamp(input_stat.st_mtime).isoformat()
            },
            'output_file': {
                'name': output_path.name if output_path else None,
                'size': output_stat.st_size if output_stat else None,
                'path': str(output_path) if output_path else None
            } if output_path else None,
            'config_used': {
                'profile': getattr(self.config, 'profile_name', 'default'),
                'version': '2.3.0-dev'
            }
        }