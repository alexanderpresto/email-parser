"""
Integration tests for the email processor.
"""

import os
import shutil
import unittest
from typing import cast, List, Union, BinaryIO
from unittest.mock import patch, MagicMock

from email_parser.core.email_processor import EmailProcessor
from email_parser.exceptions.parsing_exceptions import EmailParsingError
from email_parser.core.config import ProcessingConfig


class TestEmailProcessor(unittest.TestCase):
    """Integration tests for the EmailProcessor class."""

    #     def setUp(self):
    #         """Set up test fixtures."""
    #         self.test_output_dir = "test_output"

    #         # Create test output directory
    #         os.makedirs(self.test_output_dir, exist_ok=True)

    #         # Test data directory
    #         self.test_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data", "sample_emails")
    #         os.makedirs(self.test_data_dir, exist_ok=True)

    #         # Create a simple test email file
    #         self.test_email_path = os.path.join(self.test_data_dir, "test_email.eml")
    #         with open(self.test_email_path, "wb") as f:
    #             f.write(b"""From: sender@example.com
    # To: recipient@example.com
    # Subject: Test Email
    # Content-Type: multipart/mixed; boundary="boundary"

    # --boundary
    # Content-Type: text/plain; charset="utf-8"
    # Content-Transfer-Encoding: 7bit

    # This is an integration test email.

    # --boundary
    # Content-Type: text/html; charset="utf-8"
    # Content-Transfer-Encoding: 7bit

    # <html><body><p>This is an integration test email.</p></body></html>

    # --boundary
    # Content-Type: application/octet-stream
    # Content-Disposition: attachment; filename="test.txt"
    # Content-Transfer-Encoding: base64

    # VGhpcyBpcyBhIHRlc3QgYXR0YWNobWVudC4=

    # --boundary--
    # """)

    #         # Create a test Excel file for conversion testing
    #         self.test_excel_path = os.path.join(self.test_data_dir, "test_excel.eml")

    #         # Mock Excel file creation would go here in a real test

    #         # Initialize processor
    #         self.processor = EmailProcessor(
    #             output_dir=self.test_output_dir,
    #             enable_excel_conversion=True
    #         )
    # tests/integration/test_email_processor.py
    def setUp(self) -> None:
        """Set up test fixtures."""
        # Use temporary directory instead of OneDrive location
        self.test_output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "temp_test_output"
        )

        # Create test output directory
        os.makedirs(self.test_output_dir, exist_ok=True)

        # Test data directory - change to temp location
        self.test_data_dir = os.path.join(self.test_output_dir, "sample_emails")
        os.makedirs(self.test_data_dir, exist_ok=True)

        # Create a simple test email file
        self.test_email_path = os.path.join(self.test_data_dir, "test_email.eml")
        with open(self.test_email_path, "wb") as f:
            # Original content here...
            f.write(
                b'From: sender@example.com\nTo: recipient@example.com\nSubject: Test Email\nContent-Type: multipart/mixed; boundary="boundary"\n\n--boundary\nContent-Type: text/plain\n\nThis is an integration test email.\n\n--boundary\nContent-Type: text/html\n\n<html><body><p>This is an integration test email.</p></body></html>\n\n--boundary\nContent-Type: application/octet-stream\nContent-Disposition: attachment; filename="test.txt"\nContent-Transfer-Encoding: base64\n\nVGhpcyBpcyBhIHRlc3QgYXR0YWNobWVudC4=\n\n--boundary--\n'
            )

        # Initialize processor
        self.processor = EmailProcessor(
            config=ProcessingConfig(output_directory=self.test_output_dir, convert_excel=False)
        )

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Remove test directories
        shutil.rmtree(self.test_output_dir, ignore_errors=True)

    def test_process_email(self) -> None:
        """Test end-to-end email processing."""
        with open(self.test_email_path, "rb") as f:
            email_content = f.read()

        result = self.processor.process_email(email_content, "test_integration_email")

        # Check result structure
        self.assertEqual(result["email_id"], "test_integration_email")
        self.assertIn("timestamp", result)
        self.assertEqual(result["headers"]["From"], "sender@example.com")
        self.assertEqual(result["headers"]["To"], "recipient@example.com")
        self.assertEqual(result["headers"]["Subject"], "Test Email")

        # Check components were extracted
        self.assertEqual(len(result["text_files"]), 2)
        self.assertEqual(len(result["attachments"]), 1)

        # Check output directory structure
        text_dir = os.path.join(self.test_output_dir, "processed_text")
        attachments_dir = os.path.join(self.test_output_dir, "attachments")

        self.assertTrue(os.path.exists(text_dir))
        self.assertTrue(os.path.exists(attachments_dir))

        # Check text file content
        for text_file in result["text_files"]:
            self.assertTrue(os.path.exists(text_file["path"]))
            with open(text_file["path"], "r", encoding="utf-8") as text_file_handle:
                content = text_file_handle.read()
                if text_file["type"] == "plain":
                    self.assertIn("This is an integration test email", content)
                else:
                    self.assertIn("<p>This is an integration test email.</p>", content)

        # Check attachment content
        for attachment in result["attachments"]:
            self.assertTrue(os.path.exists(attachment["path"]))
            with open(attachment["path"], "rb") as f:
                content = f.read()
                self.assertEqual(content, b"This is a test attachment.")

        # Check metadata file
        metadata_files = [f for f in os.listdir(self.test_output_dir) if f.startswith("metadata_")]
        self.assertEqual(len(metadata_files), 1)

    def test_process_email_file_path(self) -> None:
        """Test processing an email from a file path."""
        result = self.processor.process_email(self.test_email_path, "test_file_path")

        # Check result structure
        self.assertEqual(result["email_id"], "test_file_path")
        self.assertIn("timestamp", result)

        # Check components were extracted
        self.assertEqual(len(result["text_files"]), 2)
        self.assertEqual(len(result["attachments"]), 1)

    def test_process_email_batch(self) -> None:
        """Test batch processing of emails."""
        # Create a second test email
        second_email_path = os.path.join(self.test_data_dir, "second_email.eml")
        shutil.copy(self.test_email_path, second_email_path)

        # Process batch
        email_paths = [self.test_email_path, second_email_path]
        email_ids = ["email1", "email2"]

        # Read email contents as bytes
        email_contents: List[Union[bytes, BinaryIO, str]] = []
        for path in email_paths:
            with open(path, "rb") as f:
                email_contents.append(f.read())

        batch_result = self.processor.process_email_batch(email_contents, email_ids)

        # Check batch result
        self.assertEqual(batch_result["total"], 2)
        self.assertEqual(batch_result["success_count"], 2)
        self.assertEqual(batch_result["error_count"], 0)

        # Check successful results
        self.assertEqual(len(batch_result["successful"]), 2)
        self.assertEqual(batch_result["successful"][0]["email_id"], "email1")
        self.assertEqual(batch_result["successful"][1]["email_id"], "email2")

    def test_process_email_error(self) -> None:
        """Test handling of processing errors."""
        with patch("email_parser.core.mime_parser.MIMEParser.parse_email") as mock_parse:
            mock_parse.side_effect = Exception("Test parsing error")

            with self.assertRaises(EmailParsingError):
                self.processor.process_email(b"Invalid email content", "error_email")


if __name__ == "__main__":
    unittest.main()
