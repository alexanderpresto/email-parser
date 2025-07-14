"""
Enterprise-grade email processing system with MIME parsing, PDF/DOCX to Markdown conversion, 
security features, and performance optimization.

This package provides a robust, secure, and efficient email parsing system for enterprise environments
with high volume email processing requirements. Now includes advanced PDF to Markdown conversion
using MistralAI OCR technology and DOCX to Markdown conversion using mammoth library.
"""

__version__ = "2.3.0"

from email_parser.core.config import ProcessingConfig
from email_parser.core.email_processor import EmailProcessor
from email_parser.exceptions.parsing_exceptions import (
    EmailParsingError,
    EncodingError,
    ExcelConversionError,
    MIMEParsingError,
    SecurityError,
    PDFConversionError,
    OCRError,
    DocxConversionError,
)

__all__ = [
    "EmailProcessor",
    "ProcessingConfig",
    "EmailParsingError",
    "MIMEParsingError",
    "SecurityError",
    "EncodingError",
    "ExcelConversionError",
    "PDFConversionError",
    "OCRError",
    "DocxConversionError",
]