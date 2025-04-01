"""
MIME Parser module for parsing and extracting MIME structure from emails.
"""

import email
import logging
from email.message import Message
from email.policy import default
from typing import Any, Dict, List, Optional, Tuple

from email_parser.exceptions.parsing_exceptions import MIMEParsingError
from email_parser.utils.encodings import decode_content

logger = logging.getLogger(__name__)


class MIMEParser:
    """
    Parser for MIME email messages.

    This class handles parsing of email messages according to the MIME standard,
    extracting headers, parts, and content.
    """

    def __init__(self) -> None:
        """Initialize the MIME parser."""
        self.email_message: Optional[Message] = None
        self.headers: Dict[str, str] = {}
        self.parts: List[Dict[str, Any]] = []

    def parse_email(self, email_content: bytes) -> None:
        """
        Parse an email message from raw bytes.

        Args:
            email_content: Raw email content as bytes.

        Raises:
            MIMEParsingError: If parsing fails.
        """
        try:
            self.email_message = email.message_from_bytes(email_content, policy=default)  # type: ignore
            self._extract_headers()
            self._extract_parts()
        except Exception as e:
            logger.error(f"Failed to parse email: {str(e)}")
            raise MIMEParsingError(f"Failed to parse email: {str(e)}")

    def _extract_headers(self) -> None:
        """
        Extract headers from the email message.

        Raises:
            MIMEParsingError: If header extraction fails.
        """
        if not self.email_message:
            raise MIMEParsingError("No email message to extract headers from")

        try:
            # Extract common headers
            for header in ["From", "To", "Subject", "Date", "Message-ID", "Reply-To", "CC", "BCC"]:
                value = self.email_message.get(header)
                if value:
                    self.headers[header] = value

            # Add all other headers
            for header, value in self.email_message.items():
                if header not in self.headers:
                    self.headers[header] = value
        except Exception as e:
            logger.error(f"Failed to extract headers: {str(e)}")
            raise MIMEParsingError(f"Failed to extract headers: {str(e)}")

    def _extract_parts(self) -> None:
        """
        Extract parts from the email message.

        Raises:
            MIMEParsingError: If part extraction fails.
        """
        if not self.email_message:
            raise MIMEParsingError("No email message to extract parts from")

        try:
            if self.email_message.is_multipart():
                for i, part in enumerate(self.email_message.walk()):
                    self._process_part(part, f"part_{i}")
            else:
                self._process_part(self.email_message, "main_part")
        except Exception as e:
            logger.error(f"Failed to extract parts: {str(e)}")
            raise MIMEParsingError(f"Failed to extract parts: {str(e)}")

    def _process_part(self, part: Message, part_id: str) -> None:
        """
        Process a single MIME part.

        Args:
            part: Email part to process.
            part_id: Identifier for the part.

        Raises:
            MIMEParsingError: If part processing fails.
        """
        try:
            content_type = part.get_content_type()
            content_disposition = part.get_content_disposition() or "inline"
            filename = part.get_filename()
            content_id = part.get("Content-ID")

            # Strip angle brackets from Content-ID if present
            if content_id and content_id.startswith("<") and content_id.endswith(">"):
                content_id = content_id[1:-1]

            # Extract part headers
            part_headers = {}
            for header, value in part.items():
                part_headers[header] = value

            # Get content based on type
            content = None
            if not part.is_multipart():
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        # For text parts, decode to string
                        if content_type.startswith("text/"):
                            if isinstance(payload, bytes):
                                content = decode_content(payload, charset)
                            else:
                                content = str(payload)
                        else:
                            # For binary parts, keep as bytes
                            content = payload if isinstance(payload, bytes) else str(payload).encode()
                    except Exception as e:
                        logger.warning(f"Failed to decode content for part {part_id}: {str(e)}")
                        # Ensure content is either str or bytes
                        content = payload if isinstance(payload, (str, bytes)) else str(payload).encode()

            part_info = {
                "part_id": part_id,
                "content_type": content_type,
                "content_disposition": content_disposition,
                "filename": filename,
                "content_id": content_id,
                "headers": part_headers,
                "content": content,
            }

            self.parts.append(part_info)

            # Process nested parts if multipart
            if part.is_multipart():
                for i, subpart in enumerate(part.walk()):
                    self._process_part(subpart, f"{part_id}_subpart_{i}")

        except Exception as e:
            logger.error(f"Failed to process part {part_id}: {str(e)}")
            raise MIMEParsingError(f"Failed to process part {part_id}: {str(e)}")

    def get_headers(self) -> Dict[str, str]:
        """
        Get the extracted email headers.

        Returns:
            Dict of header names to values.
        """
        return self.headers

    def get_parts(self) -> List[Dict[str, Any]]:
        """
        Get the extracted email parts.

        Returns:
            List of dictionaries containing part information.
        """
        return self.parts

    def get_text_content(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the text and HTML content from the email.

        Returns:
            Tuple of (plain_text, html_text) content, either may be None.
        """
        plain_text = None
        html_text = None

        for part in self.parts:
            if part["content_type"] == "text/plain" and isinstance(part["content"], str):
                plain_text = part["content"]
            elif part["content_type"] == "text/html" and isinstance(part["content"], str):
                html_text = part["content"]

        return plain_text, html_text

    def get_attachments(self) -> List[Dict[str, Any]]:
        """
        Get attachments from the email.

        Returns:
            List of dictionaries containing attachment information.
        """
        attachments = []
        for part in self.parts:
            if part["content_disposition"] == "attachment" and part["content"] is not None:
                attachments.append(part)
        return attachments

    def get_inline_images(self) -> List[Dict[str, Any]]:
        """
        Get inline images from the email.

        Returns:
            List of dictionaries containing inline image information.
        """
        inline_images = []
        for part in self.parts:
            content_type = part["content_type"]
            if (
                part["content_disposition"] == "inline"
                and content_type.startswith("image/")
                and part["content_id"]
                and part["content"] is not None
            ):
                inline_images.append(part)
        return inline_images
