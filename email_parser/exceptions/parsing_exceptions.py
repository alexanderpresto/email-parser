"""
Custom exception hierarchy for email processing errors.
"""

from typing import Optional, Dict, Any


class EmailParsingError(Exception):
    """Base exception for all email parsing related errors."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.error_code = error_code
        super().__init__(message)


class MIMEParsingError(EmailParsingError):
    """Exception raised when MIME parsing fails."""

    def __init__(
        self, message: str, part_id: Optional[str] = None, error_code: Optional[str] = None
    ):
        self.part_id = part_id
        super().__init__(f"MIME parsing error: {message}", error_code)


class SecurityError(EmailParsingError):
    """Exception raised when a security violation is detected."""

    def __init__(self, message: str, violation_type: str, error_code: Optional[str] = None):
        self.violation_type = violation_type
        super().__init__(f"Security violation ({violation_type}): {message}", error_code)


class EncodingError(EmailParsingError):
    """Exception raised when an encoding issue is encountered."""

    def __init__(self, message: str, encoding: str, error_code: Optional[str] = None):
        self.encoding = encoding
        super().__init__(f"Encoding error ({encoding}): {message}", error_code)


class ExcelConversionError(EmailParsingError):
    """Exception raised when Excel to CSV conversion fails."""

    def __init__(
        self,
        message: str,
        file_path: str,
        sheet_name: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        self.file_path = file_path
        self.sheet_name = sheet_name
        sheet_info = f", sheet: {sheet_name}" if sheet_name else ""
        super().__init__(
            f"Excel conversion error for {file_path}{sheet_info}: {message}", error_code
        )


class PDFConversionError(EmailParsingError):
    """Exception raised when PDF to Markdown conversion fails."""

    def __init__(
        self,
        message: str,
        file_path: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        self.file_path = file_path
        self.details = details or {}
        super().__init__(
            f"PDF conversion error for {file_path}: {message}", error_code
        )


class OCRError(PDFConversionError):
    """Exception raised when OCR processing fails."""

    def __init__(
        self,
        message: str,
        file_path: str,
        page_number: Optional[int] = None,
        api_error: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        self.page_number = page_number
        self.api_error = api_error
        details = {
            "page_number": page_number,
            "api_error": api_error
        }
        page_info = f", page {page_number}" if page_number else ""
        super().__init__(
            f"OCR processing failed{page_info}: {message}",
            file_path,
            details,
            error_code
        )


class DocxConversionError(EmailParsingError):
    """Exception raised when DOCX to Markdown conversion fails."""

    def __init__(
        self,
        message: str,
        file_path: str,
        component: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        self.file_path = file_path
        self.component = component  # chunking, metadata, styles, images
        self.details = details or {}
        
        component_info = f" ({component})" if component else ""
        super().__init__(
            f"DOCX conversion error for {file_path}{component_info}: {message}", 
            error_code
        )