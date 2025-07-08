"""
File type detection utilities for automatic converter selection.

This module provides functionality to detect file types and select the appropriate
converter for direct file conversion without email context.
"""

import mimetypes
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FileTypeDetector:
    """Detects file types for automatic converter selection."""
    
    # Mapping of MIME types to converter types
    SUPPORTED_TYPES = {
        'application/pdf': 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'application/vnd.ms-excel': 'xls',
        'application/msword': 'doc',  # Legacy support if needed later
    }
    
    # File extension fallback mapping
    EXTENSION_MAPPING = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.xlsx': 'xlsx',
        '.xls': 'xls',
        '.doc': 'doc',
    }
    
    def __init__(self):
        """Initialize the file type detector."""
        # Initialize mimetypes
        mimetypes.init()
        
    def detect_type(self, file_path: Path) -> Tuple[str, str]:
        """
        Detect file type using MIME type detection and file extension fallback.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Tuple of (mime_type, converter_type)
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.debug(f"Detecting file type for: {file_path}")
        
        # Try MIME type detection first
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        if mime_type and mime_type in self.SUPPORTED_TYPES:
            converter_type = self.SUPPORTED_TYPES[mime_type]
            logger.debug(f"Detected via MIME type: {mime_type} -> {converter_type}")
            return mime_type, converter_type
            
        # Fallback to file extension
        extension = file_path.suffix.lower()
        if extension in self.EXTENSION_MAPPING:
            converter_type = self.EXTENSION_MAPPING[extension]
            # Set a default MIME type for the extension
            mime_type = self._get_mime_type_for_extension(extension)
            logger.debug(f"Detected via extension: {extension} -> {converter_type}")
            return mime_type, converter_type
            
        # If we get here, the file type is not supported
        detected_mime = mime_type or "unknown"
        raise ValueError(
            f"Unsupported file type: {file_path.name} "
            f"(detected MIME type: {detected_mime}, extension: {extension})"
        )
    
    def _get_mime_type_for_extension(self, extension: str) -> str:
        """
        Get the appropriate MIME type for a file extension.
        
        Args:
            extension: File extension (with dot)
            
        Returns:
            MIME type string
        """
        extension_to_mime = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.doc': 'application/msword',
        }
        return extension_to_mime.get(extension, 'application/octet-stream')
    
    def is_supported(self, file_path: Path) -> bool:
        """
        Check if a file type is supported for conversion.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file type is supported, False otherwise
        """
        try:
            self.detect_type(file_path)
            return True
        except (ValueError, FileNotFoundError):
            return False
    
    def get_supported_extensions(self) -> list[str]:
        """
        Get a list of all supported file extensions.
        
        Returns:
            List of supported file extensions (with dots)
        """
        return list(self.EXTENSION_MAPPING.keys())
    
    def get_supported_mime_types(self) -> list[str]:
        """
        Get a list of all supported MIME types.
        
        Returns:
            List of supported MIME types
        """
        return list(self.SUPPORTED_TYPES.keys())
    
    def get_converter_for_file(self, file_path: Path) -> str:
        """
        Get the converter type needed for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Converter type string ('pdf', 'docx', 'xlsx', etc.)
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
        """
        _, converter_type = self.detect_type(file_path)
        return converter_type
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get comprehensive file information including type detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            mime_type, converter_type = self.detect_type(file_path)
            file_stat = file_path.stat()
            
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size': file_stat.st_size,
                'extension': file_path.suffix.lower(),
                'mime_type': mime_type,
                'converter_type': converter_type,
                'supported': True,
                'exists': True
            }
        except FileNotFoundError:
            return {
                'path': str(file_path),
                'name': file_path.name,
                'exists': False,
                'supported': False,
                'error': 'File not found'
            }
        except ValueError as e:
            file_stat = file_path.stat() if file_path.exists() else None
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size': file_stat.st_size if file_stat else None,
                'extension': file_path.suffix.lower(),
                'exists': file_path.exists(),
                'supported': False,
                'error': str(e)
            }