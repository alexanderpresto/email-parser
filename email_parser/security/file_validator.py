"""
File validator module for securely handling potentially malicious content.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Set, Tuple

import filetype  # type: ignore

from email_parser.exceptions.parsing_exceptions import SecurityError

logger = logging.getLogger(__name__)

# Define constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB default max file size


class FileValidator:
    """
    Validates files for security concerns before processing or saving.

    This class implements security measures to prevent common attack vectors
    such as path traversal, malware, and file type spoofing.
    """

    def __init__(
        self, max_file_size: int = MAX_FILE_SIZE, allowed_extensions: Optional[List[str]] = None
    ):
        """Initialize FileValidator with security settings."""
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions or [
            ".txt",
            ".csv",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".zip",
        ]

        # Add blocked extensions attribute
        self.blocked_extensions = [
            ".exe",
            ".bat",
            ".cmd",
            ".sh",
            ".js",
            ".vbs",
            ".ps1",
            ".reg",
            ".msi",
            ".com",
            ".jar",
            ".php",
            ".py",
        ]

        # Map file extensions to allowed MIME types
        self.extension_to_mime = {
            ".txt": ["text/plain", "application/octet-stream"],
            ".csv": ["text/csv", "text/plain"],
            ".pdf": ["application/pdf"],
            ".doc": ["application/msword"],
            ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
            ".xls": ["application/vnd.ms-excel", "application/octet-stream"],
            ".xlsx": [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/octet-stream",
            ],
            ".jpg": ["image/jpeg"],
            ".jpeg": ["image/jpeg"],
            ".png": ["image/png"],
            ".gif": ["image/gif"],
            ".zip": ["application/zip"],
        }

    def validate_file(
        self, file_content: bytes, filename: str, content_type: Optional[str] = None
    ) -> None:
        """
        Validate a file for security concerns.

        Args:
            file_content: Content of the file as bytes
            filename: Name of the file
            content_type: Optional MIME content type

        Raises:
            SecurityError: If the file fails security validation
        """
        # Check file size
        self._validate_file_size(file_content, filename)

        # Check file extension
        file_extension = self._validate_file_extension(filename)

        # Validate MIME type if extension suggests a specific type
        if content_type and file_extension in self.extension_to_mime:
            self._validate_mime_type(file_extension, content_type, filename)

        # Additional validation for content-based detection
        self._validate_content(file_content, filename, file_extension, content_type)

    def validate_path(self, path: str) -> None:
        """
        Validate a file path for security concerns such as path traversal.

        Args:
            path: Path to validate

        Raises:
            SecurityError: If the path fails security validation
        """
        # Check for path traversal attempts
        norm_path = os.path.normpath(path)
        if ".." in norm_path:
            raise SecurityError(f"Path contains path traversal sequences: {path}", "path_traversal")

        # Check for absolute paths
        if os.path.isabs(norm_path):
            raise SecurityError(f"Absolute paths are not allowed: {path}", "absolute_path")

        # Check for suspicious paths
        suspicious_patterns = [
            r"/etc/",
            r"/var/",
            r"/bin/",
            r"/usr/",
            r"/root/",
            r"/home/",
            r"C:\\Windows\\",
            r"C:\\Program Files\\",
            r"C:\\Users\\",
            r"C:\\System",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, norm_path, re.IGNORECASE):
                raise SecurityError(
                    f"Path contains suspicious pattern: {pattern} in {path}", "suspicious_path"
                )

    def _validate_file_size(self, file_content: bytes, filename: str) -> None:
        """
        Validate file size against maximum limit.

        Args:
            file_content: Content of the file as bytes
            filename: Name of the file for logging

        Raises:
            SecurityError: If the file exceeds the maximum size
        """
        size = len(file_content)
        if size > self.max_file_size:
            raise SecurityError(
                f"File exceeds maximum size limit ({size} > {self.max_file_size} bytes): {filename}",
                "file_size_exceeded",
            )

    def _validate_file_extension(self, filename: str) -> str:
        """
        Validate file extension against allowed and blocked lists.

        Args:
            filename: Name of the file

        Returns:
            Validated file extension including the dot

        Raises:
            SecurityError: If the file extension is not allowed or is blocked
        """
        _, extension = os.path.splitext(filename)
        extension = extension.lower()

        # Check if extension is blocked
        if extension in self.blocked_extensions:
            raise SecurityError(f"File extension is blocked: {extension}", "blocked_extension")

        # Check if extension is allowed (if allowed list is specified)
        if self.allowed_extensions is not None and extension not in self.allowed_extensions:
            raise SecurityError(
                f"File extension is not allowed: {extension}", "extension_not_allowed"
            )

        return extension

    def _validate_mime_type(self, file_extension: str, content_type: str, filename: str) -> None:
        """
        Validate that the content type matches expected MIME type for the extension.

        Args:
            file_extension: File extension including the dot
            content_type: MIME content type
            filename: Name of the file for logging

        Raises:
            SecurityError: If the MIME type doesn't match the extension
        """
        expected_mime_types = self.extension_to_mime.get(file_extension, [])

        # Special case for Excel files
        if file_extension in (".xlsx", ".xls") and content_type == "application/octet-stream":
            logger.info(f"Allowing Excel file {filename} with generic MIME type {content_type}")
            return

        # If we have expectations for this extension, validate
        if expected_mime_types and content_type not in expected_mime_types:
            raise SecurityError(
                f"MIME type mismatch for {filename}: got {content_type}, expected one of {expected_mime_types}",
                "mime_type_mismatch",
            )

    def _validate_content(
        self, file_content: bytes, filename: str, file_extension: str, content_type: Optional[str]
    ) -> None:
        """
        Validate file content for potential security issues.

        Args:
            file_content: Content of the file as bytes
            filename: Name of the file
            file_extension: File extension including the dot
            content_type: MIME content type if available

        Raises:
            SecurityError: If the file content fails validation
        """
        try:
            # Use filetype library to detect type from content
            kind = filetype.guess(file_content)

            if kind:
                detected_mime = kind.mime
                detected_extension = f".{kind.extension}"

                # Check if detected type matches extension
                expected_mime_types = self.extension_to_mime.get(file_extension, [])

                if expected_mime_types and detected_mime not in expected_mime_types:
                    logger.warning(
                        f"Content type mismatch for {filename}: detected {detected_mime}, "
                        f"expected one of {expected_mime_types} based on extension {file_extension}"
                    )

                # Check if detected extension matches actual extension
                if (
                    detected_extension != file_extension
                    and detected_extension != ".unknown"
                    and file_extension not in (".txt", ".csv")  # Text files are often undetectable
                ):
                    logger.warning(
                        f"Extension mismatch for {filename}: content suggests {detected_extension}, "
                        f"but filename has {file_extension}"
                    )

        except Exception as e:
            logger.warning(f"Error during content validation for {filename}: {str(e)}")
            # Don't fail on content detection errors, just log
