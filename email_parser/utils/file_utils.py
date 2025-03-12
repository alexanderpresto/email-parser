"""
File utility functions for the email parser.
"""
import hashlib
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from email_parser.exceptions.parsing_exceptions import SecurityError

logger = logging.getLogger(__name__)


def ensure_directory(directory_path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Raises:
        SecurityError: If directory creation fails due to security concerns
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
    except PermissionError:
        raise SecurityError(
            f"Permission denied creating directory: {directory_path}",
            "permission_denied"
        )
    except OSError as e:
        raise SecurityError(
            f"Failed to create directory {directory_path}: {str(e)}",
            "directory_creation_failed"
        )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove potential security issues.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and control characters
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    
    # Trim leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Ensure filename isn't empty after sanitization
    if not filename:
        filename = "unnamed_file"
        
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        base, ext = os.path.splitext(filename)
        filename = base[:max_length - len(ext)] + ext
        
    return filename


def generate_unique_filename(
    filename_base: str,
    extension: str,
    identifier: str,
    counter: int = 0,
    timestamp: Optional[str] = None
) -> str:
    """
    Generate a unique filename for saving extracted content.
    
    Args:
        filename_base: Base part of the filename
        extension: File extension including the dot
        identifier: Unique identifier (e.g., email ID)
        counter: Optional counter for multiple files
        timestamp: Optional timestamp string
        
    Returns:
        Unique, sanitized filename
    """
    # Sanitize the base filename
    safe_base = sanitize_filename(filename_base)
    
    # Generate timestamp if not provided
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
    # Generate a hash of the identifier for short uniqueness
    short_hash = hashlib.md5(identifier.encode()).hexdigest()[:8]
    
    # Construct unique filename
    if counter > 0:
        unique_name = f"{safe_base}_{timestamp}_{short_hash}_{counter}{extension}"
    else:
        unique_name = f"{safe_base}_{timestamp}_{short_hash}{extension}"
        
    return unique_name


def get_file_type_from_content(file_content: bytes) -> Optional[str]:
    """
    Try to determine file type from content.
    
    Args:
        file_content: Content of the file as bytes
        
    Returns:
        MIME type string or None if unknown
    """
    try:
        import filetype
        kind = filetype.guess(file_content)
        if kind:
            return kind.mime
        return None
    except:
        return None


def calculate_file_hash(file_content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content.
    
    Args:
        file_content: Content of the file as bytes
        
    Returns:
        Hex digest of SHA-256 hash
    """
    return hashlib.sha256(file_content).hexdigest()