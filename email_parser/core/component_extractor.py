"""
Component Extractor module for extracting individual components from email.
"""

import hashlib
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from email_parser.converters.excel_converter import ExcelConverter
from email_parser.exceptions.parsing_exceptions import (
    EmailParsingError,
    SecurityError,
)
from email_parser.security.file_validator import FileValidator
from email_parser.utils.file_utils import ensure_directory, generate_unique_filename

logger = logging.getLogger(__name__)


class ComponentExtractor:
    """
    Extracts and saves individual components from parsed emails.

    This class handles the extraction of text content, attachments, and inline images,
    saving them to appropriate directories with secure handling.
    """

    def __init__(
        self,
        output_dir: str = "output",
        text_dir: str = "processed_text",
        attachments_dir: str = "attachments",
        inline_images_dir: str = "inline_images",
        excel_conversion_dir: str = "converted_excel",
    ):
        """
        Initialize the ComponentExtractor.

        Args:
            output_dir: Base output directory.
            text_dir: Directory for extracted text content.
            attachments_dir: Directory for extracted attachments.
            inline_images_dir: Directory for extracted inline images.
            excel_conversion_dir: Directory for Excel to CSV conversions.
        """
        self.base_output_dir = output_dir
        self.text_output_dir = os.path.join(output_dir, text_dir)
        self.attachments_output_dir = os.path.join(output_dir, attachments_dir)
        self.inline_images_output_dir = os.path.join(output_dir, inline_images_dir)
        self.excel_conversion_output_dir = os.path.join(output_dir, excel_conversion_dir)

        # Create output directories
        for directory in [
            self.text_output_dir,
            self.attachments_output_dir,
            self.inline_images_output_dir,
            self.excel_conversion_output_dir,
        ]:
            ensure_directory(directory)

        self.file_validator = FileValidator()
        self.excel_converter = ExcelConverter(self.excel_conversion_output_dir)
        self.processed_components: Dict[str, Any] = {
            "text_files": [],
            "attachments": [],
            "inline_images": [],
            "excel_conversions": [],
            "metadata": {},
        }

        # Track positional references for content
        self.position_map: Dict[str, Dict[str, Any]] = {}

    def extract_components(
        self,
        email_id: str,
        plain_text: Optional[str],
        html_text: Optional[str],
        attachments: List[Dict[str, Any]],
        inline_images: List[Dict[str, Any]],
        headers: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Extract and save all components from an email.

        Args:
            email_id: Unique identifier for the email
            plain_text: Plain text content of the email
            html_text: HTML content of the email
            attachments: List of attachment information dictionaries
            inline_images: List of inline image information dictionaries
            headers: Email headers

        Returns:
            Dictionary with information about all extracted components

        Raises:
            EmailParsingError: If component extraction fails
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.processed_components = {
            "email_id": email_id,
            "timestamp": timestamp,
            "headers": headers,
            "text_files": [],
            "attachments": [],
            "inline_images": [],
            "excel_conversions": [],
            "metadata": {},
        }

        try:
            # Process text content
            text_info = self._process_text_content(email_id, plain_text, html_text, timestamp)
            self.processed_components["text_files"] = text_info

            # Process attachments
            attachment_info = self._process_attachments(email_id, attachments, timestamp)
            self.processed_components["attachments"] = attachment_info

            # Process inline images
            inline_image_info = self._process_inline_images(email_id, inline_images, timestamp)
            self.processed_components["inline_images"] = inline_image_info

            # Update text content with positional references
            self._update_text_with_references(email_id)

            # Generate metadata
            self._generate_metadata(email_id, headers, timestamp)

            return self.processed_components

        except Exception as e:
            logger.error(f"Failed to extract components from email {email_id}: {str(e)}")
            raise EmailParsingError(f"Component extraction failed: {str(e)}")

    def _process_text_content(
        self, email_id: str, plain_text: Optional[str], html_text: Optional[str], timestamp: str
    ) -> List[Dict[str, Any]]:
        """
        Process and save text content from the email.

        Args:
            email_id: Unique identifier for the email
            plain_text: Plain text content
            html_text: HTML content
            timestamp: Timestamp string

        Returns:
            List of dictionaries with information about saved text files
        """
        text_files = []

        # Process plain text if available
        if plain_text:
            plain_filename = f"{email_id}_plain_{timestamp}.txt"
            plain_path = os.path.join(self.text_output_dir, plain_filename)

            with open(plain_path, "w", encoding="utf-8") as f:
                f.write(plain_text)

            text_files.append(
                {
                    "type": "plain",
                    "filename": plain_filename,
                    "path": plain_path,
                    "size": len(plain_text),
                }
            )

        # Process HTML text if available
        if html_text:
            html_filename = f"{email_id}_html_{timestamp}.html"
            html_path = os.path.join(self.text_output_dir, html_filename)

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_text)

            text_files.append(
                {
                    "type": "html",
                    "filename": html_filename,
                    "path": html_path,
                    "size": len(html_text),
                }
            )

        return text_files

    def _process_attachments(
        self, email_id: str, attachments: List[Dict[str, Any]], timestamp: str
    ) -> List[Dict[str, Any]]:
        """
        Process and save attachments from the email.

        Args:
            email_id: Unique identifier for the email
            attachments: List of attachment information
            timestamp: Timestamp string

        Returns:
            List of dictionaries with information about saved attachments

        Raises:
            SecurityError: If an attachment fails security validation
        """
        attachment_info = []

        for idx, attachment in enumerate(attachments):
            try:
                original_filename = attachment.get("filename", f"unnamed_attachment_{idx}")
                content_type = attachment.get("content_type", "application/octet-stream")
                content = attachment.get("content")

                if not content:
                    logger.warning(f"Empty content for attachment {original_filename}")
                    continue

                # Validate file for security
                self.file_validator.validate_file(content, original_filename, content_type)

                # Generate a secure filename
                filename_base = os.path.splitext(original_filename)[0]
                extension = os.path.splitext(original_filename)[1]
                if not extension:
                    # Try to determine extension from content type
                    ext_map = {
                        "application/pdf": ".pdf",
                        "image/jpeg": ".jpg",
                        "image/png": ".png",
                        "text/plain": ".txt",
                        "application/msword": ".doc",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
                        "application/vnd.ms-excel": ".xls",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
                    }
                    extension = ext_map.get(content_type, ".bin")

                # Create a unique filename
                secure_filename = generate_unique_filename(
                    filename_base, extension, email_id, idx, timestamp
                )

                file_path = os.path.join(self.attachments_output_dir, secure_filename)

                # Save the attachment
                with open(file_path, "wb") as f:
                    f.write(content)

                # Check if it might be an Excel file
                is_excel = extension.lower() in (".xls", ".xlsx") or content_type in (
                    "application/vnd.ms-excel",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "application/octet-stream",  # Allow octet-stream for Excel files
                )

                # For octet-stream, verify by extension
                if content_type == "application/octet-stream":
                    is_excel = extension.lower() in (".xls", ".xlsx")

                file_info = {
                    "original_filename": original_filename,
                    "secure_filename": secure_filename,
                    "path": file_path,
                    "content_type": content_type,
                    "size": len(content),
                    "position_id": f"attachment_{idx}",
                    "is_excel": is_excel,
                }

                # Store in position map for later reference
                self.position_map[f"attachment_{idx}"] = {
                    "type": "attachment",
                    "filename": secure_filename,
                    "original_filename": original_filename,
                    "path": file_path,
                }

                attachment_info.append(file_info)

            except SecurityError as e:
                logger.error(f"Security violation for attachment: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Failed to process attachment: {str(e)}")
                # Continue processing other attachments

        # Process Excel files for conversion
        for attachment in attachment_info:
            if attachment.get("is_excel"):
                try:
                    excel_path = attachment.get("path")
                    if excel_path is None:
                        logger.error("Excel path is None")
                        continue
                        
                    original_filename = attachment.get("original_filename")
                    secure_filename = attachment.get("secure_filename")
                    
                    logger.info(f"Converting Excel file: {original_filename}")
                    
                    # Check if the file exists and has content
                    if not os.path.exists(excel_path) or os.path.getsize(excel_path) == 0:
                        logger.error(f"Excel file not found or empty: {excel_path}")
                        continue

                    # Try detection by file content
                    with open(excel_path, "rb") as f:
                        file_content = f.read(8)  # Read first 8 bytes for signature

                    # Excel file signatures
                    xlsx_sig = b"PK\x03\x04"  # XLSX files are ZIP archives
                    xls_sig = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # XLS files signature

                    is_valid_excel = file_content.startswith(xlsx_sig) or file_content.startswith(
                        xls_sig
                    )

                    if not is_valid_excel:
                        logger.warning(
                            f"File {original_filename} has Excel extension but doesn't match Excel signature"
                        )
                        # Continue anyway as file extension was verified earlier

                    conversions = self.excel_converter.convert_excel_to_csv(
                        excel_path=excel_path,
                        original_filename=original_filename,
                        secure_filename=secure_filename,
                        email_id=email_id,
                    )

                    # Register conversions
                    for conversion in conversions:
                        self.processed_components["excel_conversions"].append(conversion)

                    logger.info(
                        f"Converted Excel file {original_filename} to {len(conversions)} CSV files"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to convert Excel file {attachment.get('original_filename')}: {str(e)}"
                    )
                    # Continue processing - don't let Excel conversion failure stop the whole process

        return attachment_info

    def _process_inline_images(
        self, email_id: str, inline_images: List[Dict[str, Any]], timestamp: str
    ) -> List[Dict[str, Any]]:
        """
        Process and save inline images from the email.

        Args:
            email_id: Unique identifier for the email
            inline_images: List of inline image information
            timestamp: Timestamp string

        Returns:
            List of dictionaries with information about saved inline images
        """
        inline_image_info = []

        for idx, image in enumerate(inline_images):
            try:
                content_id = image.get("content_id", f"image_{idx}")
                content_type = image.get("content_type", "image/jpeg")
                content = image.get("content")
                original_filename = image.get("filename", f"inline_image_{idx}")

                if not content:
                    logger.warning(f"Empty content for inline image {content_id}")
                    continue

                # Validate file for security
                self.file_validator.validate_file(content, original_filename, content_type)

                # Generate a secure filename
                filename_base = os.path.splitext(original_filename)[0] or f"inline_{content_id}"
                extension = os.path.splitext(original_filename)[1]
                if not extension:
                    # Try to determine extension from content type
                    ext_map = {
                        "image/jpeg": ".jpg",
                        "image/png": ".png",
                        "image/gif": ".gif",
                        "image/svg+xml": ".svg",
                    }
                    extension = ext_map.get(content_type, ".bin")

                secure_filename = generate_unique_filename(
                    filename_base, extension, email_id, idx, timestamp
                )

                file_path = os.path.join(self.inline_images_output_dir, secure_filename)

                # Save the inline image
                with open(file_path, "wb") as f:
                    f.write(content)

                file_info = {
                    "content_id": content_id,
                    "original_filename": original_filename,
                    "secure_filename": secure_filename,
                    "path": file_path,
                    "content_type": content_type,
                    "size": len(content),
                    "position_id": f"inline_{idx}",
                }

                # Store in position map for later reference
                self.position_map[f"inline_{idx}"] = {
                    "type": "inline_image",
                    "filename": secure_filename,
                    "content_id": content_id,
                    "path": file_path,
                }

                inline_image_info.append(file_info)

            except SecurityError as e:
                logger.error(f"Security violation for inline image: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Failed to process inline image: {str(e)}")
                # Continue processing other inline images

        return inline_image_info

    def _update_text_with_references(self, email_id: str) -> None:
        """
        Update text content with positional references to attachments and inline images.

        Args:
            email_id: Unique identifier for the email
        """
        text_files = self.processed_components.get("text_files", [])

        for text_file in text_files:
            if text_file["type"] == "plain":
                self._update_plain_text_references(text_file["path"])
            elif text_file["type"] == "html":
                self._update_html_references(text_file["path"])

    def _update_plain_text_references(self, file_path: str) -> None:
        """
        Update plain text file with references to attachments and images.

        Args:
            file_path: Path to the text file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Add attachment references at the end of the file
            if self.processed_components.get("attachments"):
                content += "\n\n--- Attachments ---\n"
                for idx, attachment in enumerate(self.processed_components["attachments"]):
                    content += f"\n[Attachment {idx+1}]: {attachment['original_filename']} "
                    content += f"(Saved as: {attachment['secure_filename']})"

                    # Add reference to Excel conversion if applicable
                    excel_conversions = self._find_excel_conversions(attachment["secure_filename"])
                    if excel_conversions:
                        content += "\n    Converted Excel sheets:"
                        for conv in excel_conversions:
                            content += f"\n    - {conv['sheet_name']}: {conv['csv_filename']}"

            # Add inline image references
            if self.processed_components.get("inline_images"):
                content += "\n\n--- Inline Images ---\n"
                for idx, image in enumerate(self.processed_components["inline_images"]):
                    content += (
                        f"\n[Image {idx+1}]: {image.get('original_filename', 'Unnamed image')} "
                    )
                    content += f"(Saved as: {image['secure_filename']})"

            # Write updated content back to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            logger.error(f"Failed to update plain text references: {str(e)}")

    def _update_html_references(self, file_path: str) -> None:
        """
        Update HTML file with references to attachments and fix image links.

        Args:
            file_path: Path to the HTML file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace content IDs with file paths for inline images
            for image in self.processed_components.get("inline_images", []):
                content_id = image.get("content_id")
                if content_id:
                    # Look for references to the content ID in image tags
                    # Both cid: format and direct content ID references
                    content = content.replace(
                        f'src="cid:{content_id}"',
                        f'src="../inline_images/{image["secure_filename"]}"',
                    )
                    content = content.replace(
                        f"src='cid:{content_id}'",
                        f'src="../inline_images/{image["secure_filename"]}"',
                    )

            # Add attachment references at the end of the file
            if self.processed_components.get("attachments"):
                attachment_html = "<hr><h3>Attachments</h3><ul>"
                for idx, attachment in enumerate(self.processed_components["attachments"]):
                    attachment_html += f"<li><strong>Attachment {idx+1}</strong>: {attachment['original_filename']} "
                    attachment_html += f"(Saved as: {attachment['secure_filename']})"

                    # Add reference to Excel conversion if applicable
                    excel_conversions = self._find_excel_conversions(attachment["secure_filename"])
                    if excel_conversions:
                        attachment_html += "<ul><li>Converted Excel sheets:</li><ul>"
                        for conv in excel_conversions:
                            attachment_html += (
                                f"<li>{conv['sheet_name']}: {conv['csv_filename']}</li>"
                            )
                        attachment_html += "</ul></ul>"

                    attachment_html += "</li>"

                attachment_html += "</ul>"

                # Add attachment section before the closing body tag
                if "</body>" in content:
                    content = content.replace("</body>", f"{attachment_html}</body>")
                else:
                    content += attachment_html

            # Write updated content back to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            logger.error(f"Failed to update HTML references: {str(e)}")

    def _find_excel_conversions(self, attachment_filename: str) -> List[Dict[str, Any]]:
        """
        Find Excel conversions for a specific attachment.

        Args:
            attachment_filename: The secure filename of the attachment

        Returns:
            List of dictionaries with information about CSV conversions
        """
        return [
            conv
            for conv in self.processed_components.get("excel_conversions", [])
            if conv.get("source_filename") == attachment_filename
        ]

    def register_excel_conversion(
        self, source_filename: str, sheet_name: str, csv_filename: str, csv_path: str
    ) -> None:
        """
        Register an Excel to CSV conversion.

        Args:
            source_filename: The secure filename of the Excel file
            sheet_name: Name of the Excel worksheet
            csv_filename: Filename of the generated CSV
            csv_path: Path to the generated CSV file
        """
        conversion_info = {
            "source_filename": source_filename,
            "sheet_name": sheet_name,
            "csv_filename": csv_filename,
            "csv_path": csv_path,
        }

        self.processed_components["excel_conversions"].append(conversion_info)

    def _generate_metadata(self, email_id: str, headers: Dict[str, str], timestamp: str) -> None:
        """
        Generate metadata for the processed email.

        Args:
            email_id: Unique identifier for the email
            headers: Email headers
            timestamp: Processing timestamp
        """
        # Basic metadata
        metadata = {
            "email_id": email_id,
            "processing_time": timestamp,
            "headers": headers,
            "components": {
                "text_files": len(self.processed_components.get("text_files", [])),
                "attachments": len(self.processed_components.get("attachments", [])),
                "inline_images": len(self.processed_components.get("inline_images", [])),
                "excel_conversions": len(self.processed_components.get("excel_conversions", [])),
            },
            "file_mappings": {
                "attachments": [
                    {
                        "original": attachment["original_filename"],
                        "secure": attachment["secure_filename"],
                        "content_type": attachment["content_type"],
                    }
                    for attachment in self.processed_components.get("attachments", [])
                ],
                "inline_images": [
                    {
                        "content_id": image.get("content_id", ""),
                        "original": image.get("original_filename", ""),
                        "secure": image["secure_filename"],
                    }
                    for image in self.processed_components.get("inline_images", [])
                ],
                "excel_conversions": [
                    {
                        "source": conv["source_filename"],
                        "sheet": conv["sheet_name"],
                        "csv": conv["csv_filename"],
                    }
                    for conv in self.processed_components.get("excel_conversions", [])
                ],
            },
            "position_map": self.position_map,
        }

        self.processed_components["metadata"] = metadata

        # Save metadata to file
        metadata_path = os.path.join(self.base_output_dir, f"metadata_{email_id}_{timestamp}.json")
        try:
            import json

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")
