"""
File converters for email attachments.

This module provides converters for various attachment types:
- Excel to CSV conversion
- PDF to Markdown conversion (with MistralAI OCR)
"""

from email_parser.converters.excel_converter import ExcelConverter
# PDF converter will be imported once implemented
# from email_parser.converters.pdf_converter import PDFConverter

__all__ = [
    "ExcelConverter",
    # "PDFConverter",  # Uncomment when implemented
]