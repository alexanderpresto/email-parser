"""
File converters for email attachments.

This module provides converters for various attachment types:
- Excel to CSV conversion
- PDF to Markdown conversion (with MistralAI OCR)
"""

from email_parser.converters.base_converter import BaseConverter
from email_parser.converters.excel_converter import ExcelConverter
from email_parser.converters.pdf_converter import PDFConverter

__all__ = [
    "BaseConverter",
    "ExcelConverter",
    "PDFConverter",
]
