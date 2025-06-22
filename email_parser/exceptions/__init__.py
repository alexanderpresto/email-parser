"""
Email parser exception classes.

This module provides custom exceptions for various email parsing
and conversion operations.
"""

# Import parsing exceptions
from email_parser.exceptions.parsing_exceptions import *

# Import converter exceptions
from email_parser.exceptions.converter_exceptions import (
    ConversionError,
    UnsupportedFormatError,
    FileSizeError,
    APIError,
    ConfigurationError,
    ProcessingError
)

__all__ = [
    # Converter exceptions
    'ConversionError',
    'UnsupportedFormatError', 
    'FileSizeError',
    'APIError',
    'ConfigurationError',
    'ProcessingError',
    # Parsing exceptions (imported via *)
]
