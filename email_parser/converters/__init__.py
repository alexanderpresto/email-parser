"""
File converters for email attachments.

This module provides converters for various attachment types:
- Excel to CSV conversion
- PDF to Markdown conversion (with MistralAI OCR)
- DOCX to Markdown conversion (with mammoth)
"""

from email_parser.converters.base_converter import BaseConverter
from email_parser.converters.excel_converter import ExcelConverter
from email_parser.converters.pdf_converter import PDFConverter
from email_parser.converters.docx_converter import DocxConverter

__all__ = [
    "BaseConverter",
    "ExcelConverter",
    "PDFConverter",
    "DocxConverter",
]
