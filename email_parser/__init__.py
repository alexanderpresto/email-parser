"""
Enterprise-grade email processing system with MIME parsing, security features, and performance optimization.

This package provides a robust, secure, and efficient email parsing system for enterprise environments
with high volume email processing requirements.
"""

__version__ = "1.0.0"

from email_parser.core.email_processor import EmailProcessor
from email_parser.exceptions.parsing_exceptions import (
    EmailParsingError,
    MIMEParsingError,
    SecurityError,
    EncodingError,
    ExcelConversionError,
)

__all__ = [
    "EmailProcessor",
    "EmailParsingError",
    "MIMEParsingError",
    "SecurityError",
    "EncodingError",
    "ExcelConversionError",
]