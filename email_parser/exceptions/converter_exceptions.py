"""
Converter-specific exception classes.

This module defines custom exceptions for file conversion operations,
providing specific error types for different failure scenarios.
"""


class ConversionError(Exception):
    """
    Base exception for conversion operations.
    
    Raised when a file conversion operation fails for any reason.
    """
    pass


class UnsupportedFormatError(ConversionError):
    """
    Raised when attempting to convert an unsupported file format.
    
    This exception is raised when the converter cannot handle the
    provided file type or format.
    """
    pass


class FileSizeError(ConversionError):
    """
    Raised when a file exceeds the maximum allowed size for conversion.
    
    This exception is raised when the input file is too large to
    process safely within the configured limits.
    """
    pass


class APIError(ConversionError):
    """
    Raised when an external API call fails during conversion.
    
    This exception is raised when communication with external services
    (like MistralAI OCR API) fails or returns an error.
    """
    pass


class ConfigurationError(ConversionError):
    """
    Raised when converter configuration is invalid or incomplete.
    
    This exception is raised when required configuration settings
    are missing or invalid, such as API keys or invalid parameters.
    """
    pass


class ProcessingError(ConversionError):
    """
    Raised when file processing operations fail.
    
    This exception is raised when the conversion process encounters
    errors during file processing, such as corrupted data or
    unexpected file structures.
    """
    pass
