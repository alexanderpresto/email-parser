"""
Email Processor module for processing emails with attachments and inline content.
"""
import logging
import os
from typing import Dict, List, Optional, Tuple, Any, Callable, Union, BinaryIO

from email_parser.core.mime_parser import MIMEParser
from email_parser.core.component_extractor import ComponentExtractor
from email_parser.converters.excel_converter import ExcelConverter
from email_parser.exceptions.parsing_exceptions import (
    EmailParsingError,
    MIMEParsingError,
    SecurityError,
    ExcelConversionError,
)
from email_parser.utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)


class EmailProcessor:
    """
    Main email processing class that orchestrates parsing, extraction, and conversion.
    
    This class provides the primary interface for processing emails, handling
    the entire workflow from parsing to extraction and conversion.
    """

    def __init__(
        self,
        output_dir: str = "output",
        enable_excel_conversion: bool = True,
        excel_prompt_callback: Optional[Callable[[str, List[str]], List[str]]] = None,
    ):
        """
        Initialize the email processor.
        
        Args:
            output_dir: Base directory for all output files
            enable_excel_conversion: Whether to enable Excel to CSV conversion
            excel_prompt_callback: Optional callback for Excel sheet selection prompts
        """
        self.output_dir = output_dir
        ensure_directory(output_dir)
        
        # Subdirectories
        self.text_dir = os.path.join(output_dir, "processed_text")
        self.attachments_dir = os.path.join(output_dir, "attachments")
        self.inline_images_dir = os.path.join(output_dir, "inline_images")
        self.excel_conversion_dir = os.path.join(output_dir, "converted_excel")
        
        # Set up components
        self.mime_parser = MIMEParser()
        self.component_extractor = ComponentExtractor(
            output_dir=output_dir,
            text_dir="processed_text",
            attachments_dir="attachments",
            inline_images_dir="inline_images",
            excel_conversion_dir="converted_excel",
        )
        
        # Excel conversion settings
        self.enable_excel_conversion = enable_excel_conversion
        self.excel_prompt_callback = excel_prompt_callback
        if enable_excel_conversion:
            self.excel_converter = ExcelConverter(output_dir=self.excel_conversion_dir)
            
    def process_email(self, email_content: Union[bytes, BinaryIO, str], email_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an email from raw content.
        
        Args:
            email_content: Raw email content as bytes, file object, or path to email file
            email_id: Optional unique identifier for the email (generated if not provided)
            
        Returns:
            Dictionary with information about the processed email and extracted components
            
        Raises:
            EmailParsingError: If email processing fails
        """
        try:
            # Generate email ID if not provided
            if not email_id:
                import uuid
                email_id = str(uuid.uuid4())
                
            # Convert string (file path) to bytes
            if isinstance(email_content, str):
                with open(email_content, "rb") as f:
                    email_content = f.read()
                    
            # Convert file object to bytes
            if hasattr(email_content, "read"):
                email_content = email_content.read()
                
            # Parse email
            logger.info(f"Parsing email {email_id}")
            self.mime_parser.parse_email(email_content)
            
            # Get email components
            headers = self.mime_parser.get_headers()
            plain_text, html_text = self.mime_parser.get_text_content()
            attachments = self.mime_parser.get_attachments()
            inline_images = self.mime_parser.get_inline_images()
            
            # Extract and save components
            logger.info(f"Extracting components from email {email_id}")
            result = self.component_extractor.extract_components(
                email_id,
                plain_text,
                html_text,
                attachments,
                inline_images,
                headers
            )
            
            # Handle Excel conversions if enabled
            if self.enable_excel_conversion:
                self._process_excel_attachments(result, email_id)
                
            logger.info(f"Email {email_id} processed successfully")
            return result
            
        except MIMEParsingError as e:
            logger.error(f"MIME parsing error: {str(e)}")
            raise EmailParsingError(f"MIME parsing error: {str(e)}")
        except SecurityError as e:
            logger.error(f"Security violation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to process email: {str(e)}")
            raise EmailParsingError(f"Failed to process email: {str(e)}")
            
    def _process_excel_attachments(self, result: Dict[str, Any], email_id: str) -> None:
        """
        Process Excel attachments for conversion to CSV.
        
        Args:
            result: Result dictionary from component extraction
            email_id: Unique identifier for the email
            
        Raises:
            ExcelConversionError: If Excel conversion fails
        """
        if not self.enable_excel_conversion:
            return
            
        try:
            for attachment in result.get("attachments", []):
                if attachment.get("is_excel"):
                    logger.info(f"Converting Excel file: {attachment['original_filename']}")
                    
                    conversions = self.excel_converter.convert_excel_to_csv(
                        attachment["path"],
                        attachment["original_filename"],
                        attachment["secure_filename"],
                        email_id,
                        self.excel_prompt_callback
                    )
                    
                    # Register Excel conversions
                    for conversion in conversions:
                        self.component_extractor.register_excel_conversion(
                            attachment["secure_filename"],
                            conversion["sheet_name"],
                            conversion["csv_filename"],
                            conversion["csv_path"]
                        )
                        
                    # Update the result with Excel conversions
                    result["excel_conversions"] = self.component_extractor.processed_components.get(
                        "excel_conversions", []
                    )
                    
        except ExcelConversionError as e:
            logger.error(f"Excel conversion error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to process Excel attachments: {str(e)}")
            raise ExcelConversionError(f"Failed to process Excel attachments: {str(e)}", "unknown")
            
    def process_email_batch(
        self, 
        email_contents: List[Union[bytes, BinaryIO, str]],
        email_ids: Optional[List[str]] = None,
        continue_on_error: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process multiple emails in batch.
        
        Args:
            email_contents: List of raw email content (bytes, file objects, or paths)
            email_ids: Optional list of unique identifiers for the emails
            continue_on_error: Whether to continue processing on error
            
        Returns:
            List of dictionaries with processing results
            
        Raises:
            EmailParsingError: If batch processing fails and continue_on_error is False
        """
        results = []
        errors = []
        
        # Generate email IDs if not provided
        if not email_ids:
            import uuid
            email_ids = [str(uuid.uuid4()) for _ in range(len(email_contents))]
        elif len(email_ids) != len(email_contents):
            raise ValueError("Number of email IDs must match number of emails")
            
        # Process each email
        for i, (email_content, email_id) in enumerate(zip(email_contents, email_ids)):
            try:
                logger.info(f"Processing email {i+1}/{len(email_contents)}: {email_id}")
                result = self.process_email(email_content, email_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process email {email_id}: {str(e)}")
                errors.append({"email_id": email_id, "error": str(e)})
                if not continue_on_error:
                    raise EmailParsingError(f"Batch processing failed at email {i+1}/{len(email_contents)}: {str(e)}")
                    
        # Log batch processing results
        logger.info(f"Batch processing completed: {len(results)} succeeded, {len(errors)} failed")
        
        # Include errors in result
        batch_result = {
            "successful": results,
            "errors": errors,
            "total": len(email_contents),
            "success_count": len(results),
            "error_count": len(errors)
        }
        
        return batch_result