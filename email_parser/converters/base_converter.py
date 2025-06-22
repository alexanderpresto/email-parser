"""
Base converter class for email attachments.

This module provides the abstract base class for all attachment converters,
defining the common interface and shared functionality.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime

from email_parser.exceptions.converter_exceptions import (
    ConversionError,
    UnsupportedFormatError,
    FileSizeError
)


logger = logging.getLogger(__name__)


class BaseConverter(ABC):
    """
    Abstract base class for all file converters.
    
    This class defines the common interface that all converters must implement
    and provides shared functionality for file handling, validation, and logging.
    """
    
    # Default configuration values
    DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    DEFAULT_OUTPUT_DIR = Path("output")
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise the converter with configuration.
        
        Args:
            config: Configuration dictionary containing converter settings
        """
        self.config = config or {}
        self.max_file_size = self.config.get('max_file_size', self.DEFAULT_MAX_FILE_SIZE)
        self.output_dir = Path(self.config.get('output_dir', self.DEFAULT_OUTPUT_DIR))
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.debug(f"Initialised {self.__class__.__name__} with config: {self.config}")
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """
        Return a list of supported file extensions.
        
        Returns:
            List of supported file extensions (including the dot, e.g., ['.pdf', '.docx'])
        """
        pass
    
    @property
    @abstractmethod
    def supported_mime_types(self) -> List[str]:
        """
        Return a list of supported MIME types.
        
        Returns:
            List of supported MIME types (e.g., ['application/pdf', 'text/plain'])
        """
        pass
    
    @property
    @abstractmethod
    def converter_name(self) -> str:
        """
        Return the human-readable name of this converter.
        
        Returns:
            Name of the converter (e.g., "PDF to Markdown Converter")
        """
        pass
    
    def can_convert(self, file_path: Path, mime_type: Optional[str] = None) -> bool:
        """
        Check if this converter can handle the given file.
        
        Args:
            file_path: Path to the file to check
            mime_type: Optional MIME type of the file
            
        Returns:
            True if this converter can handle the file, False otherwise
        """
        # Check file extension
        if file_path.suffix.lower() in [ext.lower() for ext in self.supported_extensions]:
            return True
            
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
            
        return False
    
    def validate_file(self, file_path: Path) -> None:
        """
        Validate that the file can be processed.
        
        Args:
            file_path: Path to the file to validate
            
        Raises:
            ConversionError: If the file cannot be processed
            FileSizeError: If the file is too large
            UnsupportedFormatError: If the file format is not supported
        """
        if not file_path.exists():
            raise ConversionError(f"File does not exist: {file_path}")
            
        if not file_path.is_file():
            raise ConversionError(f"Path is not a file: {file_path}")
            
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise FileSizeError(
                f"File too large: {file_size} bytes (max: {self.max_file_size} bytes)"
            )
            
        # Check if we can convert this file
        if not self.can_convert(file_path):
            raise UnsupportedFormatError(
                f"Unsupported file format: {file_path.suffix} "
                f"(supported: {self.supported_extensions})"
            )
    
    def generate_output_path(self, input_path: Path, suffix: str = "") -> Path:
        """
        Generate an output file path based on the input file.
        
        Args:
            input_path: Path to the input file
            suffix: Optional suffix to add to the filename
            
        Returns:
            Path for the output file
        """
        base_name = input_path.stem
        if suffix:
            base_name = f"{base_name}_{suffix}"
            
        # Use timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{base_name}_{timestamp}.md"
        
        return self.output_dir / output_name
    
    def log_conversion_start(self, input_path: Path, output_path: Path) -> None:
        """
        Log the start of a conversion operation.
        
        Args:
            input_path: Path to the input file
            output_path: Path to the output file
        """
        self.logger.info(
            f"Starting {self.converter_name} conversion: "
            f"{input_path.name} -> {output_path.name}"
        )
    
    def log_conversion_success(self, input_path: Path, output_path: Path, 
                             duration_seconds: float) -> None:
        """
        Log successful completion of a conversion operation.
        
        Args:
            input_path: Path to the input file
            output_path: Path to the output file
            duration_seconds: Time taken for the conversion
        """
        self.logger.info(
            f"Completed {self.converter_name} conversion: "
            f"{input_path.name} -> {output_path.name} "
            f"({duration_seconds:.2f}s)"
        )
    
    def log_conversion_error(self, input_path: Path, error: Exception) -> None:
        """
        Log a conversion error.
        
        Args:
            input_path: Path to the input file
            error: The exception that occurred
        """
        self.logger.error(
            f"Failed {self.converter_name} conversion: "
            f"{input_path.name} - {type(error).__name__}: {error}"
        )
    
    @abstractmethod
    def convert(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Convert the input file to the target format.
        
        Args:
            input_path: Path to the input file
            output_path: Optional path for the output file (auto-generated if None)
            
        Returns:
            Path to the converted output file
            
        Raises:
            ConversionError: If the conversion fails
        """
        pass
    
    def get_conversion_metadata(self, input_path: Path) -> Dict[str, Any]:
        """
        Get metadata about the conversion process and input file.
        
        Args:
            input_path: Path to the input file
            
        Returns:
            Dictionary containing conversion metadata
        """
        file_stat = input_path.stat()
        return {
            'converter': self.converter_name,
            'input_file': str(input_path),
            'input_size': file_stat.st_size,
            'input_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'conversion_time': datetime.now().isoformat(),
            'config': self.config.copy()
        }
    
    def __repr__(self) -> str:
        """Return a string representation of the converter."""
        return f"{self.__class__.__name__}(supported_extensions={self.supported_extensions})"
