"""
PDF to Markdown converter using MistralAI OCR.

This module provides PDF to Markdown conversion functionality using MistralAI's
OCR API for text extraction and image processing.
"""

import os
import base64
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
import threading
from functools import wraps

try:
    from mistralai import Mistral
    # MistralAI doesn't export a specific exception class in v1.8.2
    MistralException = Exception
except ImportError:
    Mistral = None
    MistralException = Exception

from email_parser.converters.base_converter import BaseConverter
from email_parser.exceptions.converter_exceptions import (
    ConversionError,
    APIError,
    ConfigurationError
)


logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for API calls."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 300, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise APIError("Circuit breaker is OPEN - API calls blocked")
            
            try:
                result = func(*args, **kwargs)
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                    logger.info("Circuit breaker reset to CLOSED")
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                    logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
                
                raise e


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff_multiplier: float = 2.0):
    """Decorator for retrying failed operations with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        sleep_time = delay * (backoff_multiplier ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {sleep_time}s...")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator


class PDFConverter(BaseConverter):
    """
    PDF to Markdown converter using MistralAI OCR API.
    
    This converter processes PDF files using MistralAI's OCR capabilities to extract
    text content and embedded images, converting them to Markdown format with
    properly linked image files.
    """
    
    # Supported extraction modes
    EXTRACTION_MODES = {
        'text': 'Extract text content only',
        'images': 'Extract images only',  
        'all': 'Extract both text and images'
    }
    
    # Default configuration
    DEFAULT_CONFIG = {
        'api_key_env': 'MISTRALAI_API_KEY',
        'extraction_mode': 'all',
        'image_settings': {
            'limit': 0,  # 0 = no limit
            'min_size': 100,  # minimum size in pixels
            'save_images': True,
            'image_dir': 'images'
        },
        'pagination': {
            'enabled': True,
            'page_separator': '\\n\\n---\\n\\n'
        },
        'api_settings': {
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 1.0,
            'circuit_breaker': {
                'failure_threshold': 5,
                'recovery_timeout': 300,  # 5 minutes
                'reset_timeout': 60  # 1 minute
            }
        },
        'validation': {
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'min_file_size': 1,  # 1 byte
            'allowed_pdf_versions': ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7'],
            'validate_pdf_structure': True
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None):
        """
        Initialise the PDF converter.
        
        Args:
            config: Configuration dictionary for the converter
            api_key: Optional API key (overrides config and environment)
            
        Raises:
            ConfigurationError: If MistralAI SDK is not available or API key is missing
            APIError: If API key validation fails
        """
        # Merge with default config
        merged_config = self.DEFAULT_CONFIG.copy()
        if config:
            merged_config.update(config)
            
        super().__init__(merged_config)
        
        # Check if MistralAI SDK is available
        if Mistral is None:
            raise ConfigurationError(
                "MistralAI SDK not available. Install with: pip install mistralai>=1.5.2"
            )
        
        # Get and validate API key
        if api_key:
            self.api_key = api_key
        else:
            api_key_env = self.config['api_key_env']
            self.api_key = os.getenv(api_key_env)
        
        if not self.api_key:
            raise APIError(
                f"MistralAI API key is required. Set {self.config['api_key_env']} environment variable or provide api_key parameter."
            )
        
        self._validate_api_key_format()
        
        # Initialize circuit breaker
        cb_config = self.config['api_settings']['circuit_breaker']
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=cb_config['failure_threshold'],
            recovery_timeout=cb_config['recovery_timeout'],
            reset_timeout=cb_config['reset_timeout']
        )
        
        # Initialise MistralAI client
        try:
            self.client = Mistral(api_key=self.api_key)
            self.logger.info("MistralAI client initialised successfully")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialise MistralAI client: {e}")
        
        # Set up image directory
        self.image_dir = self.output_dir / self.config['image_settings']['image_dir']
        self.image_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def supported_extensions(self) -> List[str]:
        """Return supported PDF file extensions."""
        return ['.pdf']
    
    @property  
    def supported_mime_types(self) -> List[str]:
        """Return supported PDF MIME types."""
        return ['application/pdf', 'application/x-pdf']
    
    @property
    def converter_name(self) -> str:
        """Return the converter name."""
        return "PDF to Markdown Converter"
    
    def _validate_extraction_mode(self, mode: str) -> None:
        """
        Validate the extraction mode.
        
        Args:
            mode: The extraction mode to validate
            
        Raises:
            ConversionError: If the mode is not supported
        """
        if mode not in self.EXTRACTION_MODES:
            raise ConversionError(
                f"Unsupported extraction mode: {mode}. "
                f"Supported modes: {list(self.EXTRACTION_MODES.keys())}"
            )
    
    def _validate_api_key_format(self) -> None:
        """
        Validate API key format.
        
        Raises:
            APIError: If API key format is invalid
        """
        if not self.api_key or not self.api_key.strip():
            raise APIError("API key is required and cannot be empty")
        
        # Basic format validation
        key = self.api_key.strip()
        
        if len(key) < 10:
            raise APIError("API key appears to be too short")
        
        if ' ' in key or '\n' in key or '\t' in key:
            raise APIError("API key contains invalid whitespace characters")
        
        # Check for obvious invalid patterns
        if key.isdigit() or key.lower() in ['none', 'null', 'undefined', 'test']:
            raise APIError("API key format appears to be invalid")
    
    def _validate_api_key(self) -> bool:
        """
        Validate API key by making a test call.
        
        Returns:
            True if API key is valid
            
        Raises:
            APIError: If API key is invalid
        """
        try:
            # Make a minimal test call to validate the key
            test_payload = {
                'model': 'pixtral-12b-2409',
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 1
            }
            
            response = self.client.chat.complete(**test_payload)
            return True
            
        except MistralException as e:
            if "unauthorized" in str(e).lower() or "invalid" in str(e).lower():
                raise APIError("Invalid MistralAI API key. Please check your credentials.")
            raise APIError(f"API key validation failed: {e}")
        except Exception as e:
            raise APIError(f"Unable to validate API key: {e}")
    
    def _validate_file_size(self, file_size: int) -> None:
        """
        Validate PDF file size.
        
        Args:
            file_size: File size in bytes
            
        Raises:
            ConversionError: If file size is invalid
        """
        validation_config = self.config['validation']
        min_size = validation_config['min_file_size']
        max_size = validation_config['max_file_size']
        
        if file_size < min_size:
            raise ConversionError(f"File is too small: {file_size} bytes (minimum: {min_size} bytes)")
        
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            file_mb = file_size / (1024 * 1024)
            raise ConversionError(
                f"File is too large: {file_mb:.1f}MB (maximum: {max_mb:.1f}MB)"
            )
    
    def _validate_pdf_content(self, pdf_data: bytes) -> None:
        """
        Validate PDF file content and structure.
        
        Args:
            pdf_data: Binary PDF data
            
        Raises:
            ConversionError: If PDF content is invalid
        """
        if not pdf_data:
            raise ConversionError("PDF file is empty or contains no data")
        
        # Check PDF header
        if not pdf_data.startswith(b'%PDF-'):
            raise ConversionError("File is not a valid PDF - missing PDF header")
        
        # Extract PDF version
        try:
            header_line = pdf_data[:20].decode('ascii', errors='ignore')
            if '%PDF-' in header_line:
                version_start = header_line.find('%PDF-') + 5
                version_end = version_start + 3
                version = header_line[version_start:version_end]
                
                allowed_versions = self.config['validation']['allowed_pdf_versions']
                if version not in allowed_versions:
                    self.logger.warning(f"PDF version {version} may not be fully supported")
        except Exception:
            self.logger.warning("Could not extract PDF version from header")
        
        # Check for password protection (more specific check)
        # Look for actual encryption dictionary, not just the presence of /Encrypt
        if b'/Encrypt' in pdf_data:
            # More sophisticated check for actual encryption
            encrypt_pattern = pdf_data.find(b'/Encrypt')
            if encrypt_pattern != -1:
                # Look for signs of actual encryption (like /V entries indicating encryption version)
                after_encrypt = pdf_data[encrypt_pattern:encrypt_pattern + 200]
                if b'/V' in after_encrypt and (b'/R' in after_encrypt or b'/P' in after_encrypt):
                    self.logger.warning("PDF may be encrypted, but attempting conversion anyway")
                    # Don't raise error - let the OCR API handle it
        
        # Basic structure validation
        if self.config['validation']['validate_pdf_structure']:
            required_elements = [b'%%EOF', b'endobj']
            missing_elements = [elem for elem in required_elements if elem not in pdf_data]
            
            if missing_elements:
                self.logger.warning(f"PDF may be corrupted - missing elements: {missing_elements}")
    
    def _validate_output_directory(self, output_dir: Path) -> None:
        """
        Validate output directory.
        
        Args:
            output_dir: Output directory path
            
        Raises:
            ConversionError: If output directory is invalid
        """
        if output_dir.exists() and not output_dir.is_dir():
            raise ConversionError(f"Output path exists but is not a directory: {output_dir}")
        
        # Try to create directory if it doesn't exist
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise ConversionError(f"Permission denied: Cannot create output directory {output_dir}")
        except OSError as e:
            raise ConversionError(f"Cannot create output directory {output_dir}: {e}")
        
        # Test write permissions
        test_file = output_dir / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError:
            raise ConversionError(f"Permission denied: Cannot write to output directory {output_dir}")
        except OSError as e:
            raise ConversionError(f"Cannot write to output directory {output_dir}: {e}")
    
    def _validate_input_file(self, input_path: Path) -> None:
        """
        Comprehensive input file validation.
        
        Args:
            input_path: Input file path
            
        Raises:
            ConversionError: If input file is invalid
        """
        if not input_path.exists():
            raise ConversionError(f"Input file not found: {input_path}")
        
        if not input_path.is_file():
            raise ConversionError(f"Input path is not a file: {input_path}")
        
        # Check file extension
        if input_path.suffix.lower() not in self.supported_extensions:
            raise ConversionError(
                f"Unsupported file extension: {input_path.suffix}. "
                f"Supported extensions: {self.supported_extensions}"
            )
        
        # Validate file size
        file_size = input_path.stat().st_size
        self._validate_file_size(file_size)
        
        # Read and validate content
        try:
            pdf_data = input_path.read_bytes()
            self._validate_pdf_content(pdf_data)
        except PermissionError:
            raise ConversionError(f"Permission denied: Cannot read input file {input_path}")
        except OSError as e:
            raise ConversionError(f"Cannot read input file {input_path}: {e}")
    
    def _read_pdf_file(self, file_path: Path) -> bytes:
        """
        Read PDF file as binary data.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Binary content of the PDF file
            
        Raises:
            ConversionError: If the file cannot be read
        """
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise ConversionError(f"Failed to read PDF file {file_path}: {e}")
    
    def _encode_pdf_base64(self, pdf_data: bytes) -> str:
        """
        Encode PDF data as base64 string.
        
        Args:
            pdf_data: Binary PDF data
            
        Returns:
            Base64 encoded PDF data
        """
        return base64.b64encode(pdf_data).decode('utf-8')
    
    def _call_mistral_api(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Call MistralAI API with circuit breaker protection.
        
        Args:
            pdf_data: Binary PDF data
            
        Returns:
            API response
            
        Raises:
            APIError: If API call fails
            ConversionError: If request processing fails
        """
        def make_api_call():
            """Internal function for the actual API call."""
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            payload = {
                'model': 'pixtral-12b-2409',
                'messages': [{'role': 'user', 'content': 'Process this PDF'}],
                'temperature': 0.1,
                'max_tokens': 4000
            }
            
            try:
                response = self.client.chat.complete(**payload)
                if not response or not response.choices:
                    raise APIError("Empty response from MistralAI API")
                
                return response
                
            except MistralException as e:
                error_msg = str(e).lower()
                
                if "rate limit" in error_msg or "429" in error_msg:
                    raise APIError("Rate limit exceeded. Please try again later.")
                elif "quota" in error_msg or "billing" in error_msg:
                    raise APIError("API quota exceeded. Please check your billing status.")
                elif "unauthorized" in error_msg or "invalid" in error_msg:
                    raise APIError("Invalid API key. Please check your credentials.")
                elif "timeout" in error_msg:
                    raise APIError("API request timed out. Please try again.")
                else:
                    raise APIError(f"MistralAI API error: {e}")
                    
            except requests.exceptions.ConnectionError as e:
                raise APIError(f"Network connection error: {e}")
            except requests.exceptions.Timeout as e:
                raise APIError(f"Request timeout: {e}")
            except Exception as e:
                raise APIError(f"Unexpected API error: {e}")
        
        try:
            return self.circuit_breaker.call(make_api_call)
        except APIError:
            raise  # Re-raise API errors as-is
        except Exception as e:
            raise ConversionError(f"Failed to process API request: {e}")
    
    async def _upload_pdf_to_mistral(self, pdf_data: bytes, filename: str) -> str:
        """
        Upload PDF to MistralAI Files API.
        
        Args:
            pdf_data: Binary PDF content
            filename: Original filename for reference
            
        Returns:
            File ID from MistralAI
            
        Raises:
            APIError: If upload fails
        """
        try:
            self.logger.debug(f"Uploading PDF '{filename}' to MistralAI...")
            
            file_upload = await self.client.files.upload(
                file={
                    'fileName': filename,
                    'content': pdf_data
                },
                purpose='ocr'
            )
            
            if not file_upload or not hasattr(file_upload, 'id') or not file_upload.id:
                raise APIError("Failed to upload file to MistralAI - no file ID returned")
            
            self.logger.debug(f"Successfully uploaded file with ID: {file_upload.id}")
            return file_upload.id
            
        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            raise APIError(f"MistralAI file upload error: {e}")

    async def _get_signed_url(self, file_id: str) -> str:
        """
        Get signed URL for uploaded file.
        
        Args:
            file_id: MistralAI file ID
            
        Returns:
            Signed URL for OCR processing
            
        Raises:
            APIError: If URL generation fails
        """
        try:
            self.logger.debug(f"Getting signed URL for file ID: {file_id}")
            
            signed_url_response = await self.client.files.get_signed_url(
                file_id=file_id
            )
            
            if not signed_url_response or not hasattr(signed_url_response, 'url') or not signed_url_response.url:
                raise APIError("Failed to get signed URL from MistralAI")
            
            self.logger.debug("Successfully obtained signed URL")
            return signed_url_response.url
            
        except Exception as e:
            self.logger.error(f"Signed URL generation failed: {e}")
            raise APIError(f"MistralAI signed URL error: {e}")

    def _call_mistral_ocr(self, pdf_data: bytes, extraction_mode: str) -> Dict[str, Any]:
        """
        Call MistralAI OCR API using file upload pattern.
        
        Args:
            pdf_data: Binary PDF data 
            extraction_mode: Type of extraction to perform
            
        Returns:
            OCR response from MistralAI
            
        Raises:
            APIError: If the API call fails
        """
        def make_ocr_call():
            """Internal function for OCR API call with proper file upload flow."""
            try:
                # Step 1: Upload PDF file
                self.logger.debug("Step 1: Uploading PDF to MistralAI...")
                file_upload = self.client.files.upload(
                    file={
                        'fileName': 'document.pdf',
                        'content': pdf_data
                    },
                    purpose='ocr'
                )
                
                if not file_upload or not hasattr(file_upload, 'id') or not file_upload.id:
                    raise APIError("Failed to upload file to MistralAI")
                
                # Step 2: Get signed URL
                self.logger.debug(f"Step 2: Getting signed URL for file {file_upload.id}...")
                signed_url_response = self.client.files.get_signed_url(
                    file_id=file_upload.id
                )
                
                if not signed_url_response or not hasattr(signed_url_response, 'url'):
                    raise APIError("Failed to get signed URL from MistralAI")
                
                # Step 3: Process OCR
                self.logger.debug("Step 3: Processing OCR...")
                include_images = extraction_mode in ['images', 'all']
                
                ocr_response = self.client.ocr.process(
                    model='mistral-ocr-latest',
                    document={
                        'type': 'document_url',
                        'document_url': signed_url_response.url
                    },
                    include_image_base64=include_images,
                    image_limit=self.config.get('image_settings', {}).get('limit', 0),
                    image_min_size=self.config.get('image_settings', {}).get('min_size', 0)
                )
                
                if not ocr_response:
                    raise APIError("Empty response from MistralAI OCR API")
                
                return ocr_response
                
            except MistralException as e:
                error_msg = str(e).lower()
                
                if "rate limit" in error_msg:
                    raise APIError("Rate limit exceeded. Please try again later.")
                elif "quota" in error_msg:
                    raise APIError("API quota exceeded. Please check your billing status.")
                elif "unauthorized" in error_msg or "invalid" in error_msg:
                    raise APIError("Invalid API key. Please check your credentials.")
                elif "timeout" in error_msg:
                    raise APIError("API request timed out. Please try again.")
                else:
                    raise APIError(f"MistralAI API error: {e}")
                    
            except requests.exceptions.ConnectionError as e:
                raise APIError(f"Network connection error: {e}")
            except requests.exceptions.Timeout as e:
                raise APIError(f"Request timeout: {e}")
            except Exception as e:
                raise APIError(f"Unexpected OCR API error: {e}")
        
        # Use circuit breaker with retry decorator
        max_retries = self.config['api_settings']['max_retries']
        retry_delay = self.config['api_settings']['retry_delay']
        
        @retry_on_failure(max_retries, retry_delay)
        def retryable_ocr_call():
            return self.circuit_breaker.call(make_ocr_call)
        
        try:
            return retryable_ocr_call()
        except APIError:
            raise  # Re-raise API errors as-is
        except Exception as e:
            raise APIError(f"OCR processing failed after all retries: {e}")
    
    def _generate_ocr_prompt(self, extraction_mode: str) -> str:
        """
        Generate the OCR prompt based on extraction mode.
        
        Args:
            extraction_mode: The type of extraction to perform
            
        Returns:
            Formatted prompt for the OCR API
        """
        base_prompt = (
            "Please process this PDF document and convert it to clean Markdown format. "
        )
        
        if extraction_mode == 'text':
            return base_prompt + (
                "Extract only the text content, preserving structure with appropriate "
                "Markdown headers, lists, and formatting. Ignore any images."
            )
        elif extraction_mode == 'images':
            return base_prompt + (
                "Extract and describe any images, charts, or visual elements found in the document. "
                "Provide detailed descriptions that could be used as alt text. "
                "Ignore text content."
            )
        else:  # 'all'
            return base_prompt + (
                "Extract both text content and describe any images or visual elements. "
                "For text: preserve structure with Markdown formatting. "
                "For images: provide detailed descriptions and note their position in the document. "
                "Create a comprehensive Markdown representation of the entire document."
            )
    
    def _process_ocr_response(self, response: Dict[str, Any], 
                            output_path: Path) -> Tuple[str, List[str]]:
        """
        Process the OCR response and extract content.
        
        Args:
            response: Response from MistralAI OCR API
            output_path: Path where the output will be saved
            
        Returns:
            Tuple of (markdown_content, list_of_image_paths)
        """
        if not response:
            raise ConversionError("Empty OCR response from MistralAI")
        
        # Handle new OCR API response structure with pages
        pages = getattr(response, 'pages', None)
        if not pages:
            self.logger.warning("OCR response contains no pages")
            return '', []
        
        # Extract markdown content from all pages
        markdown_content = ""
        image_paths = []
        page_separator = self.config.get('pagination', {}).get('page_separator', '\n\n---\n\n')
        
        for i, page in enumerate(pages):
            # Add page content
            page_markdown = getattr(page, 'markdown', '')
            if page_markdown:
                if i > 0:  # Add separator between pages
                    markdown_content += page_separator
                markdown_content += page_markdown
            
            # Extract images if present and enabled
            if self.config['image_settings']['save_images']:
                page_images = getattr(page, 'images', [])
                for j, image_data in enumerate(page_images):
                    try:
                        # Generate unique filename for each image
                        image_filename = f"{output_path.stem}_page_{i+1:02d}_image_{j+1:02d}.png"
                        image_path = self.image_dir / image_filename
                        
                        # Save base64 image data
                        if hasattr(image_data, 'base64') and image_data.base64:
                            self._save_base64_image(image_data.base64, image_path)
                            image_paths.append(str(image_path))
                            self.logger.debug(f"Saved image: {image_path}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to save image from page {i+1}, image {j+1}: {e}")
        
        if not markdown_content:
            self.logger.warning("No markdown content extracted from OCR response")
            return '', []
        
        return markdown_content, image_paths
    
    def _save_base64_image(self, base64_data: str, image_path: Path) -> None:
        """
        Save base64 encoded image data to file.
        
        Args:
            base64_data: Base64 encoded image data
            image_path: Path where the image should be saved
            
        Raises:
            ConversionError: If image saving fails
        """
        try:
            # Remove data URL prefix if present (e.g., "data:image/png;base64,")
            if base64_data.startswith('data:'):
                base64_data = base64_data.split(',', 1)[1]
            
            # Decode and save image
            image_bytes = base64.b64decode(base64_data)
            
            # Ensure the image directory exists
            image_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write image file
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
                
        except Exception as e:
            raise ConversionError(f"Failed to save image {image_path}: {e}")
    
    def _save_images(self, images: List[Dict[str, Any]], 
                    base_name: str) -> List[str]:
        """
        Save extracted images to files.
        
        Args:
            images: List of image data dictionaries
            base_name: Base name for the image files
            
        Returns:
            List of saved image file paths
        """
        saved_paths = []
        image_settings = self.config['image_settings']
        
        # Apply image limit
        if image_settings['limit'] > 0:
            images = images[:image_settings['limit']]
        
        for i, image_data in enumerate(images):
            try:
                # Generate filename
                image_filename = f"{base_name}_image_{i+1:03d}.png"
                image_path = self.image_dir / image_filename
                
                # Decode and save image (placeholder implementation)
                # TODO: Implement actual image decoding and saving
                # This would typically involve decoding base64 data
                
                saved_paths.append(str(image_path))
                self.logger.debug(f"Saved image: {image_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to save image {i}: {e}")
                
        return saved_paths
    
    def _generate_markdown_with_images(self, content: str, 
                                     image_paths: List[str]) -> str:
        """
        Generate final Markdown content with image references.
        
        Args:
            content: Base Markdown content
            image_paths: List of image file paths
            
        Returns:
            Enhanced Markdown content with image links
        """
        if not image_paths:
            return content
            
        # Add image section at the end
        image_section = "\\n\\n## Extracted Images\\n\\n"
        for i, image_path in enumerate(image_paths):
            # Use relative path for the markdown link
            relative_path = Path(image_path).relative_to(self.output_dir)
            image_section += f"![Image {i+1}]({relative_path})\\n\\n"
            
        return content + image_section
    
    def convert(self, input_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Convert PDF to Markdown using MistralAI OCR.
        
        Args:
            input_path: Path to the input PDF file
            output_dir: Directory for output files
            
        Returns:
            Dictionary containing conversion results and metadata
            
        Raises:
            ConversionError: If the conversion fails
            APIError: If API calls fail
        """
        start_time = time.time()
        cleanup_files = []
        
        try:
            # Comprehensive validation
            self.logger.debug("Validating input file...")
            self._validate_input_file(input_path)
            
            self.logger.debug("Validating output directory...")
            self._validate_output_directory(output_dir)
            
            # Get extraction mode
            extraction_mode = self.config.get('extraction_mode', 'all')
            self._validate_extraction_mode(extraction_mode)
            
            # Generate output path
            output_filename = f"{input_path.stem}_converted.md"
            output_path = output_dir / output_filename
            
            self.log_conversion_start(input_path, output_path)
            
            # Read and validate PDF content
            self.logger.debug("Reading and validating PDF file...")
            pdf_data = self._read_pdf_file(input_path)
            
            # Call MistralAI OCR API with enhanced error handling
            self.logger.debug("Calling MistralAI OCR API...")
            ocr_response = self._call_mistral_ocr(pdf_data, extraction_mode)
            
            # Process response
            self.logger.debug("Processing OCR response...")
            markdown_content, image_paths = self._process_ocr_response(
                ocr_response, output_path
            )
            
            # Track image files for cleanup
            cleanup_files.extend(image_paths)
            
            # Generate final content with image links
            if self.config['image_settings']['save_images'] and image_paths:
                final_content = self._generate_markdown_with_images(
                    markdown_content, image_paths
                )
            else:
                final_content = markdown_content
            
            # Add metadata header
            metadata = self.get_conversion_metadata(input_path)
            metadata_header = self._generate_metadata_header(metadata, extraction_mode)
            
            final_content = metadata_header + final_content
            
            # Save output file with error handling
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
            except PermissionError:
                raise ConversionError(f"Permission denied: Cannot write to {output_path}")
            except OSError as e:
                if "No space left on device" in str(e):
                    raise ConversionError("Disk space full - cannot save output file")
                raise ConversionError(f"Cannot write output file {output_path}: {e}")
                
            duration = time.time() - start_time
            
            # Create result dictionary
            result = {
                'success': True,
                'input_file': str(input_path),
                'output_file': str(output_path),
                'output_dir': str(output_dir),
                'extraction_mode': extraction_mode,
                'duration': duration,
                'file_size': input_path.stat().st_size,
                'pages': 1,  # TODO: Extract actual page count
                'image_count': len(image_paths),
                'image_paths': image_paths,
                'api_usage': getattr(ocr_response, 'usage_info', {}),
                'conversion_quality': 'high'  # TODO: Implement quality assessment
            }
            
            self.log_conversion_success(input_path, output_path, duration)
            self.logger.info(f"Conversion completed: {result}")
            
            return result
            
        except (ConversionError, APIError):
            # Clean up any partial files on error
            self._cleanup_files(cleanup_files)
            raise  # Re-raise expected errors as-is
            
        except Exception as e:
            # Clean up any partial files on error
            self._cleanup_files(cleanup_files)
            self.log_conversion_error(input_path, e)
            raise ConversionError(f"PDF conversion failed: {e}") from e
    
    def _cleanup_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary or partial files.
        
        Args:
            file_paths: List of file paths to clean up
        """
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    self.logger.debug(f"Cleaned up file: {file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup file {file_path}: {e}")
    
    def _process_pdf_content(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Process PDF content with memory management.
        
        Args:
            pdf_data: Binary PDF data
            
        Returns:
            Processed content dictionary
            
        Raises:
            ConversionError: If processing fails
            MemoryError: If insufficient memory
        """
        try:
            # Monitor memory usage
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Process content (placeholder for actual processing)
            result = {"processed": True, "size": len(pdf_data)}
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Log memory usage
            self.logger.debug(f"Memory usage: {memory_increase / 1024 / 1024:.2f}MB increase")
            
            # Check for excessive memory usage (>50MB increase)
            if memory_increase > 50 * 1024 * 1024:
                self.logger.warning(f"High memory usage detected: {memory_increase / 1024 / 1024:.2f}MB")
            
            return result
            
        except MemoryError:
            raise ConversionError(
                "Insufficient memory to process PDF. "
                "Try processing a smaller file or free up system memory."
            )
        except Exception as e:
            raise ConversionError(f"Failed to process PDF content: {e}")
    
    def _generate_metadata_header(self, metadata: Dict[str, Any], 
                                extraction_mode: str) -> str:
        """
        Generate metadata header for the Markdown output.
        
        Args:
            metadata: Conversion metadata
            extraction_mode: The extraction mode used
            
        Returns:
            Formatted metadata header
        """
        header = f"""---
source_file: {metadata['input_file']}
converter: {metadata['converter']}
extraction_mode: {extraction_mode}
conversion_time: {metadata['conversion_time']}
file_size: {metadata['input_size']} bytes
---

# PDF Conversion: {Path(metadata['input_file']).name}

Converted using {metadata['converter']} with extraction mode: **{extraction_mode}**

"""
        return header
    
    def get_supported_modes(self) -> Dict[str, str]:
        """
        Get supported extraction modes with descriptions.
        
        Returns:
            Dictionary mapping mode names to descriptions
        """
        return self.EXTRACTION_MODES.copy()
    
    def convert_standalone(self, file_path: Path, output_dir: Path, 
                          options: Optional[Dict[str, Any]] = None) -> Path:
        """
        Convert a PDF file standalone without email context.
        
        Args:
            file_path: Path to the PDF file to convert
            output_dir: Directory where output should be saved
            options: Optional conversion options
            
        Returns:
            Path to the converted file
            
        Raises:
            ConversionError: If conversion fails
        """
        # Generate output filename
        output_filename = f"{file_path.stem}.md"
        output_path = output_dir / output_filename
        
        # Use existing convert method with the specified output path
        self.convert(file_path, output_path)
        
        return output_path
