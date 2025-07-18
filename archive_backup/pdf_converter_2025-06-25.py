"""
PDF to Markdown converter using MistralAI OCR.

This module provides PDF to Markdown conversion functionality using MistralAI's
OCR API for text extraction and image processing.
"""

import os
import base64
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging

try:
    from mistralai import Mistral
except ImportError:
    Mistral = None

from email_parser.converters.base_converter import BaseConverter
from email_parser.exceptions.converter_exceptions import (
    ConversionError,
    APIError,
    ConfigurationError
)


logger = logging.getLogger(__name__)


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
            'retry_delay': 1.0
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise the PDF converter.
        
        Args:
            config: Configuration dictionary for the converter
            
        Raises:
            ConfigurationError: If MistralAI SDK is not available or API key is missing
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
        
        # Get API key
        api_key_env = self.config['api_key_env']
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ConfigurationError(
                f"MistralAI API key not found in environment variable: {api_key_env}"
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
    
    def _call_mistral_ocr(self, pdf_base64: str, extraction_mode: str) -> Dict[str, Any]:
        """
        Call MistralAI OCR API to process the PDF.
        
        Args:
            pdf_base64: Base64 encoded PDF data
            extraction_mode: Type of extraction to perform
            
        Returns:
            OCR response from MistralAI
            
        Raises:
            APIError: If the API call fails
        """
        max_retries = self.config['api_settings']['max_retries']
        retry_delay = self.config['api_settings']['retry_delay']
        timeout = self.config['api_settings']['timeout']
        
        # Prepare the request payload
        payload = {
            'model': 'pixtral-12b-2409',  # MistralAI's vision model
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': self._generate_ocr_prompt(extraction_mode)
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:application/pdf;base64,{pdf_base64}'
                            }
                        }
                    ]
                }
            ],
            'temperature': 0.1,  # Low temperature for consistent results
            'max_tokens': 4000
        }
        
        # Retry logic
        last_exception = None
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Calling MistralAI OCR API (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.chat.complete(**payload)
                
                if response and response.choices:
                    content = response.choices[0].message.content
                    return {
                        'success': True,
                        'content': content,
                        'usage': getattr(response, 'usage', None)
                    }
                else:
                    raise APIError("Empty response from MistralAI API")
                    
            except Exception as e:
                last_exception = e
                self.logger.warning(f"OCR API attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    
        # If we get here, all retries failed
        raise APIError(f"MistralAI OCR API failed after {max_retries} attempts: {last_exception}")
    
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
        if not response.get('success', False):
            raise ConversionError("OCR processing was not successful")
            
        content = response.get('content', '')
        if not content:
            self.logger.warning("OCR response contains no content")
            return '', []
        
        # For now, we'll return the content as-is since MistralAI should
        # already format it as Markdown. In future versions, we could
        # add post-processing here (e.g., extracting embedded images)
        
        markdown_content = content
        image_paths = []  # TODO: Implement image extraction from base64 data
        
        return markdown_content, image_paths
    
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
    
    def convert(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Convert PDF to Markdown using MistralAI OCR.
        
        Args:
            input_path: Path to the input PDF file
            output_path: Optional path for the output file
            
        Returns:
            Path to the converted Markdown file
            
        Raises:
            ConversionError: If the conversion fails
        """
        start_time = time.time()
        
        # Validate input
        self.validate_file(input_path)
        
        # Generate output path if not provided
        if output_path is None:
            output_path = self.generate_output_path(input_path, "pdf_converted")
            
        # Get extraction mode
        extraction_mode = self.config.get('extraction_mode', 'all')
        self._validate_extraction_mode(extraction_mode)
        
        self.log_conversion_start(input_path, output_path)
        
        try:
            # Read and encode PDF
            self.logger.debug("Reading PDF file...")
            pdf_data = self._read_pdf_file(input_path)
            pdf_base64 = self._encode_pdf_base64(pdf_data)
            
            # Call MistralAI OCR API
            self.logger.debug("Calling MistralAI OCR API...")
            ocr_response = self._call_mistral_ocr(pdf_base64, extraction_mode)
            
            # Process response
            self.logger.debug("Processing OCR response...")
            markdown_content, image_paths = self._process_ocr_response(
                ocr_response, output_path
            )
            
            # Generate final content with image links
            if self.config['image_settings']['save_images']:
                final_content = self._generate_markdown_with_images(
                    markdown_content, image_paths
                )
            else:
                final_content = markdown_content
            
            # Add metadata header
            metadata = self.get_conversion_metadata(input_path)
            metadata_header = self._generate_metadata_header(metadata, extraction_mode)
            
            final_content = metadata_header + final_content
            
            # Save output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
                
            duration = time.time() - start_time
            self.log_conversion_success(input_path, output_path, duration)
            
            return output_path
            
        except Exception as e:
            self.log_conversion_error(input_path, e)
            raise ConversionError(f"PDF conversion failed: {e}") from e
    
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
