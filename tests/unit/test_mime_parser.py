"""
Unit tests for the MIME parser.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from email.message import EmailMessage

from email_parser.core.mime_parser import MIMEParser
from email_parser.exceptions.parsing_exceptions import MIMEParsingError


class TestMIMEParser(unittest.TestCase):
    """Test cases for the MIMEParser class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.parser = MIMEParser()

        # Create a test directory for sample emails if needed
        self.test_data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "test_data", "sample_emails"
        )
        os.makedirs(self.test_data_dir, exist_ok=True)

        # Simple test email content
        self.test_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Email
Content-Type: multipart/mixed; boundary="boundary"

--boundary
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 7bit

This is a test email.

--boundary
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: 7bit

<html><body><p>This is a test email.</p></body></html>

--boundary
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="test.txt"
Content-Transfer-Encoding: base64

VGhpcyBpcyBhIHRlc3QgYXR0YWNobWVudC4=

--boundary--
"""

    def test_parse_email(self) -> None:
        """Test parsing an email message."""
        self.parser.parse_email(self.test_email)

        # Check headers
        headers = self.parser.get_headers()
        self.assertEqual(headers.get("From"), "sender@example.com")
        self.assertEqual(headers.get("To"), "recipient@example.com")
        self.assertEqual(headers.get("Subject"), "Test Email")

        # Check parts
        parts = self.parser.get_parts()
        self.assertGreaterEqual(len(parts), 3)  # At least 3 parts

        # Check text content
        plain_text, html_text = self.parser.get_text_content()
        self.assertIsNotNone(plain_text)
        self.assertIsNotNone(html_text)
        if plain_text is not None:
            self.assertIn("This is a test email", plain_text)
        if html_text is not None:
            self.assertIn("<p>This is a test email.</p>", html_text)

        # Check attachments
        attachments = self.parser.get_attachments()
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]["filename"], "test.txt")

    def test_parse_email_error(self) -> None:
        """Test handling of parsing errors."""
        with self.assertRaises(MIMEParsingError):
            self.parser.parse_email(b"Invalid email content")

    def test_extract_headers(self) -> None:
        """Test header extraction."""
        # Mock EmailMessage
        self.parser.email_message = EmailMessage()
        self.parser.email_message["From"] = "sender@example.com"
        self.parser.email_message["To"] = "recipient@example.com"
        self.parser.email_message["Subject"] = "Test Subject"

        self.parser._extract_headers()

        headers = self.parser.get_headers()
        self.assertEqual(headers.get("From"), "sender@example.com")
        self.assertEqual(headers.get("To"), "recipient@example.com")
        self.assertEqual(headers.get("Subject"), "Test Subject")

    def test_extract_headers_error(self) -> None:
        """Test handling of header extraction errors."""
        self.parser.email_message = None
        with self.assertRaises(MIMEParsingError):
            self.parser._extract_headers()

    def test_process_part(self) -> None:
        """Test processing of email parts."""
        # Mock part
        part = EmailMessage()
        part.set_content("Test content")

        # Delete existing Content-Type before setting a new one
        del part["Content-Type"]
        part["Content-Type"] = "text/plain"

        self.parser._process_part(part, "test_part")

        # Check if part was processed
        parts = self.parser.get_parts()
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0]["part_id"], "test_part")
        self.assertEqual(parts[0]["content_type"], "text/plain")

    def test_get_inline_images(self) -> None:
        """Test extraction of inline images."""
        # Add a mock inline image part
        self.parser.parts = [
            {
                "part_id": "image_part",
                "content_type": "image/jpeg",
                "content_disposition": "inline",
                "content_id": "image1",
                "filename": "image.jpg",
                "content": b"image data",
            }
        ]

        images = self.parser.get_inline_images()
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["content_id"], "image1")


if __name__ == "__main__":
    unittest.main()
