"""
Email Processor module for processing emails with attachments and inline content.
"""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Callable, Dict, List, Optional, Union, cast
from io import TextIOBase, BufferedIOBase

# from typing import List, Union, BinaryIO, cast

from email_parser.converters.excel_converter import ExcelConverter
from email_parser.converters.pdf_converter import PDFConverter
from email_parser.core.component_extractor import ComponentExtractor
from email_parser.core.config import ProcessingConfig
from email_parser.core.mime_parser import MIMEParser
from email_parser.exceptions.parsing_exceptions import (
    EmailParsingError,
    ExcelConversionError,
    MIMEParsingError,
    PDFConversionError,
    SecurityError,
)
from email_parser.utils.file_utils import ensure_directory, sanitize_filename

logger = logging.getLogger(__name__)

# # Cast BufferedReader to the expected type
# email_streams_typed = cast(List[Union[bytes, BinaryIO, str]], email_streams)
# result = self.process_email_batch(email_streams_typed, email_ids)


class EmailProcessor:
    """
    Main email processing class that orchestrates parsing, extraction, and conversion.

    This class provides the primary interface for processing emails, handling
    the entire workflow from parsing to extraction and conversion.
    """

    def __init__(
        self,
        config: ProcessingConfig,
        excel_prompt_callback: Optional[Callable[[str, List[str]], List[str]]] = None,
    ):
        """
        Initialize the email processor.

        Args:
            config: Configuration object for processing parameters
            excel_prompt_callback: Optional callback for Excel sheet selection prompts
        """
        if not isinstance(config, ProcessingConfig):
            raise TypeError("config must be a ProcessingConfig instance")

        if not config.output_directory:
            raise ValueError("Output directory must be specified in config")

        self.config = config
        self.output_dir = config.output_directory

        # Ensure output directory exists
        ensure_directory(self.output_dir)

        # Subdirectories
        self.text_dir = os.path.join(self.output_dir, "processed_text")
        self.attachments_dir = os.path.join(self.output_dir, "attachments")
        self.inline_images_dir = os.path.join(self.output_dir, "inline_images")
        self.excel_conversion_dir = os.path.join(self.output_dir, "converted_excel")
        self.converted_pdf_dir = os.path.join(self.output_dir, "converted_pdf")

        # Ensure all subdirectories exist
        ensure_directory(self.text_dir)
        ensure_directory(self.attachments_dir)
        ensure_directory(self.inline_images_dir)
        ensure_directory(self.excel_conversion_dir)
        ensure_directory(self.converted_pdf_dir)

        # Set up components
        self.mime_parser = MIMEParser()
        self.component_extractor = ComponentExtractor(
            output_dir=self.output_dir,
            text_dir="processed_text",
            attachments_dir="attachments",
            inline_images_dir="inline_images",
            excel_conversion_dir="converted_excel",
        )

        # Excel conversion settings
        self.enable_excel_conversion = getattr(config, "convert_excel", False)
        self.excel_prompt_callback = excel_prompt_callback
        if self.enable_excel_conversion:
            self.excel_converter = ExcelConverter(output_dir=self.excel_conversion_dir)
        
        # PDF conversion settings
        self.enable_pdf_conversion = getattr(config, "convert_pdf", False)
        if self.enable_pdf_conversion:
            self.pdf_converter = PDFConverter()

    def process_email(
        self, email_content: Union[bytes, BinaryIO, str], email_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an email from raw content.

        Args:
            email_content: Raw email content as bytes, file object, or path to email file
            email_id: Optional unique identifier for the email (generated if not provided)

        Returns:
            Dictionary with information about the processed email and extracted components

        Raises:
            EmailParsingError: If email processing fails
            SecurityError: If a security violation is detected
        """
        try:
            # Generate email ID if not provided
            if not email_id:
                email_id = str(uuid.uuid4())

            # Convert string path to bytes
            if isinstance(email_content, str):
                with open(email_content, "rb") as f:
                    email_content = f.read()

            # Convert file object to bytes
            if isinstance(email_content, (TextIOBase, BufferedIOBase)):
                email_content = cast(Union[TextIOBase, BufferedIOBase], email_content).read()
            elif hasattr(email_content, "read") and callable(getattr(email_content, "read")):
                email_content = cast(BinaryIO, email_content).read()

            # Ensure we have bytes
            if not isinstance(email_content, bytes):
                email_content = cast(bytes, email_content)

            # Check size limit
            max_size = getattr(self.config, "max_attachment_size", 10_000_000)
            if len(email_content) > max_size:
                raise SecurityError(
                    f"Email size ({len(email_content)} bytes) exceeds maximum allowed size "
                    f"({max_size} bytes)",
                    "size_limit_exceeded",
                )

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
                email_id, plain_text, html_text, attachments, inline_images, headers
            )

            # Handle Excel conversions if enabled
            if self.enable_excel_conversion:
                self._process_excel_attachments(result, email_id)
            
            # Handle PDF conversions if enabled
            if self.enable_pdf_conversion:
                self._process_pdf_attachments(result, email_id)

            # Add metadata
            result["processing_metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "email_id": email_id,
                "processor_version": "1.0.0",
                "success": True,
            }

            logger.info(f"Email {email_id} processed successfully")
            return result

        except MIMEParsingError as e:
            logger.error(f"MIME parsing error: {str(e)}")
            raise EmailParsingError(f"MIME parsing error: {str(e)}")
        except SecurityError as e:
            logger.error(f"Security violation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to process email: {str(e)}", exc_info=True)
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
            excel_conversions = []

            for attachment in result.get("attachments", []):
                if attachment.get("is_excel"):
                    logger.info(f"Converting Excel file: {attachment['original_filename']}")

                    conversions = self.excel_converter.convert_excel_to_csv(
                        attachment["path"],
                        attachment["original_filename"],
                        attachment["secure_filename"],
                        email_id,
                        self.excel_prompt_callback,
                    )

                    # Register Excel conversions
                    for conversion in conversions:
                        self.component_extractor.register_excel_conversion(
                            attachment["secure_filename"],
                            conversion["sheet_name"],
                            conversion["csv_filename"],
                            conversion["csv_path"],
                        )
                        excel_conversions.append(conversion)

            # Update the result with Excel conversions
            if excel_conversions:
                result["excel_conversions"] = excel_conversions

        except ExcelConversionError as e:
            logger.error(f"Excel conversion error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to process Excel attachments: {str(e)}", exc_info=True)
            raise ExcelConversionError(f"Excel conversion failed: {str(e)}", "unknown")

    def _process_pdf_attachments(self, result: Dict[str, Any], email_id: str) -> None:
        """
        Process PDF attachments for conversion to Markdown.

        Args:
            result: Result dictionary from component extraction
            email_id: Unique identifier for the email

        Raises:
            Exception: If PDF conversion fails
        """
        if not self.enable_pdf_conversion:
            return

        try:
            pdf_conversions = []

            for attachment in result.get("attachments", []):
                if attachment.get("original_filename", "").lower().endswith('.pdf'):
                    logger.info(f"Converting PDF file: {attachment['original_filename']}")

                    # Create output directory for this PDF
                    pdf_output_dir = os.path.join(self.converted_pdf_dir, f"pdf_{email_id}_{len(pdf_conversions)}")
                    ensure_directory(pdf_output_dir)

                    # Convert PDF to Markdown
                    conversion_result = self.pdf_converter.convert(
                        input_path=Path(attachment["path"]),
                        output_dir=Path(pdf_output_dir)
                    )

                    # Register PDF conversion
                    pdf_conversions.append({
                        "original_filename": attachment["original_filename"],
                        "secure_filename": attachment["secure_filename"],
                        "markdown_path": conversion_result.get("output_path"),
                        "output_dir": pdf_output_dir,
                        "pages_converted": conversion_result.get("pages_converted", 0),
                        "images_extracted": conversion_result.get("images_extracted", 0)
                    })

            # Update the result with PDF conversions
            if pdf_conversions:
                result["pdf_conversions"] = pdf_conversions

        except Exception as e:
            logger.error(f"Failed to process PDF attachments: {str(e)}", exc_info=True)
            # Don't raise exception to allow email processing to continue
            result["pdf_conversion_errors"] = str(e)

    def process_email_batch(
        self,
        email_contents: List[Union[bytes, BinaryIO, str]],
        email_ids: Optional[List[str]] = None,
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        """
        Process multiple emails in batch.

        Args:
            email_contents: List of raw email content (bytes, file objects, or paths)
            email_ids: Optional list of unique identifiers for the emails
            continue_on_error: Whether to continue processing on error

        Returns:
            Dictionary with processing results including successful and failed emails

        Raises:
            EmailParsingError: If batch processing fails and continue_on_error is False
            ValueError: If email_ids is provided but length doesn't match email_contents
        """
        results = []
        errors = []

        # Generate email IDs if not provided
        if not email_ids:
            email_ids = [str(uuid.uuid4()) for _ in range(len(email_contents))]
        elif len(email_ids) != len(email_contents):
            raise ValueError("Number of email IDs must match number of emails")

        # Check batch size against configuration
        batch_size = len(email_contents)
        if hasattr(self.config, "batch_size") and batch_size > self.config.batch_size:
            logger.warning(
                f"Batch size ({batch_size}) exceeds configured limit "
                f"({self.config.batch_size}). This may affect performance."
            )

        # Process each email
        total = len(email_contents)
        for i, (email_content, email_id) in enumerate(zip(email_contents, email_ids)):
            logger.info(f"Processing email {i+1}/{total} ({(i+1)/total:.1%}): {email_id}")
            try:
                result = self.process_email(email_content, email_id)
                results.append(result)
            except Exception as e:
                error_detail = {
                    "email_id": email_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat(),
                }
                logger.error(f"Failed to process email {email_id}: {str(e)}", exc_info=True)
                errors.append(error_detail)
                if not continue_on_error:
                    raise EmailParsingError(
                        f"Batch processing failed at email {i+1}/{total}: {str(e)}"
                    )

        # Log batch processing results
        logger.info(f"Batch processing completed: {len(results)} succeeded, {len(errors)} failed")

        # Include batch metadata
        batch_result = {
            "successful": results,
            "errors": errors,
            "total": total,
            "success_count": len(results),
            "error_count": len(errors),
            "batch_metadata": {
                "timestamp": datetime.now().isoformat(),
                "batch_size": total,
                "continue_on_error": continue_on_error,
                "processor_version": "1.0.0",
            },
        }

        return batch_result

    def process_batch(self, email_paths: List[str]) -> Dict[str, Any]:
        """
        Process a batch of emails from file paths.

        Args:
            email_paths: List of file paths to email files

        Returns:
            Dictionary with processing results

        Raises:
            EmailParsingError: If batch processing fails
        """
        # Validate paths
        for path in email_paths:
            if not os.path.exists(path):
                raise ValueError(f"Email file not found: {path}")

        # Create file streams for each email
        email_streams = []
        for path in email_paths:
            try:
                email_streams.append(open(path, "rb"))
            except Exception as e:
                # Close any already opened streams
                for stream in email_streams:
                    try:
                        stream.close()
                    except:
                        pass
                raise EmailParsingError(f"Failed to open email file {path}: {str(e)}")

        try:
            # Generate email IDs based on filenames
            email_ids = [sanitize_filename(os.path.basename(path)) for path in email_paths]

            # Process the batch - use cast here
            email_streams_typed = cast(List[Union[bytes, BinaryIO, str]], email_streams)
            result = self.process_email_batch(email_streams_typed, email_ids)

            # Add filepath information to result
            for i, path in enumerate(email_paths):
                if i < len(result["successful"]):
                    result["successful"][i]["source_path"] = path

            return result

        finally:
            # Ensure all streams are closed
            for stream in email_streams:
                try:
                    stream.close()
                except:
                    pass
