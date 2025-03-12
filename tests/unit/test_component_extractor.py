"""
Unit tests for the component extractor.
"""
import os
import shutil
import unittest
from unittest.mock import patch, MagicMock

from email_parser.core.component_extractor import ComponentExtractor
from email_parser.exceptions.parsing_exceptions import SecurityError

class TestComponentExtractor(unittest.TestCase):
    """Test cases for the ComponentExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_output_dir = "test_output"
        self.test_text_dir = os.path.join(self.test_output_dir, "processed_text")
        self.test_attachments_dir = os.path.join(self.test_output_dir, "attachments")
        self.test_inline_images_dir = os.path.join(self.test_output_dir, "inline_images")
        self.test_excel_dir = os.path.join(self.test_output_dir, "converted_excel")
        
        # Create test directories
        for directory in [
            self.test_text_dir,
            self.test_attachments_dir,
            self.test_inline_images_dir,
            self.test_excel_dir
        ]:
            os.makedirs(directory, exist_ok=True)
            
        self.extractor = ComponentExtractor(
            output_dir=self.test_output_dir,
            text_dir="processed_text",
            attachments_dir="attachments",
            inline_images_dir="inline_images",
            excel_conversion_dir="converted_excel"
        )
        
        # Test data
        self.test_email_id = "test_email_123"
        self.test_plain_text = "This is a test email."
        self.test_html_text = "<html><body><p>This is a test email.</p></body></html>"
        self.test_attachments = [{
            "filename": "test.txt",
            "content_type": "text/plain",
            "content_disposition": "attachment",
            "content": b"This is a test attachment.",
            "part_id": "part_1"
        }]
        self.test_inline_images = [{
            "filename": "image.jpg",
            "content_type": "image/jpeg",
            "content_disposition": "inline",
            "content_id": "image1",
            "content": b"fake image data",
            "part_id": "part_2"
        }]
        self.test_headers = {
            "From": "sender@example.com",
            "To": "recipient@example.com",
            "Subject": "Test Email"
        }
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove test directories
        shutil.rmtree(self.test_output_dir, ignore_errors=True)
        
    def test_extract_components(self):
        """Test extraction of all components."""
        result = self.extractor.extract_components(
            self.test_email_id,
            self.test_plain_text,
            self.test_html_text,
            self.test_attachments,
            self.test_inline_images,
            self.test_headers
        )
        
        # Check result structure
        self.assertEqual(result["email_id"], self.test_email_id)
        self.assertIn("timestamp", result)
        self.assertEqual(result["headers"], self.test_headers)
        
        # Check text files
        self.assertEqual(len(result["text_files"]), 2)
        text_types = [text["type"] for text in result["text_files"]]
        self.assertIn("plain", text_types)
        self.assertIn("html", text_types)
        
        # Check attachments
        self.assertEqual(len(result["attachments"]), 1)
        self.assertEqual(result["attachments"][0]["original_filename"], "test.txt")
        
        # Check inline images
        self.assertEqual(len(result["inline_images"]), 1)
        self.assertEqual(result["inline_images"][0]["content_id"], "image1")
        
        # Check files were created
        for text_file in result["text_files"]:
            self.assertTrue(os.path.exists(text_file["path"]))
            
        for attachment in result["attachments"]:
            self.assertTrue(os.path.exists(attachment["path"]))
            
        for image in result["inline_images"]:
            self.assertTrue(os.path.exists(image["path"]))
            
    def test_process_text_content(self):
        """Test processing of text content."""
        text_info = self.extractor._process_text_content(
            self.test_email_id,
            self.test_plain_text,
            self.test_html_text,
            "20250101000000"
        )
        
        self.assertEqual(len(text_info), 2)
        
        # Check files were created
        for text_file in text_info:
            self.assertTrue(os.path.exists(text_file["path"]))
            with open(text_file["path"], "r", encoding="utf-8") as f:
                content = f.read()
                if text_file["type"] == "plain":
                    self.assertEqual(content, self.test_plain_text)
                else:
                    self.assertEqual(content, self.test_html_text)
                    
    def test_process_attachments(self):
        """Test processing of attachments."""
        with patch("email_parser.security.file_validator.FileValidator.validate_file") as mock_validate:
            attachment_info = self.extractor._process_attachments(
                self.test_email_id,
                self.test_attachments,
                "20250101000000"
            )
            
            self.assertEqual(len(attachment_info), 1)
            self.assertEqual(attachment_info[0]["original_filename"], "test.txt")
            self.assertTrue(os.path.exists(attachment_info[0]["path"]))
            
            # Check file content
            with open(attachment_info[0]["path"], "rb") as f:
                content = f.read()
                self.assertEqual(content, b"This is a test attachment.")
                
    def test_process_attachments_security_error(self):
        """Test handling of security errors in attachment processing."""
        with patch("email_parser.security.file_validator.FileValidator.validate_file") as mock_validate:
            mock_validate.side_effect = SecurityError("Test security error", "test_violation")
            
            with self.assertRaises(SecurityError):
                self.extractor._process_attachments(
                    self.test_email_id,
                    self.test_attachments,
                    "20250101000000"
                )
                
    def test_process_inline_images(self):
        """Test processing of inline images."""
        with patch("email_parser.security.file_validator.FileValidator.validate_file") as mock_validate:
            image_info = self.extractor._process_inline_images(
                self.test_email_id,
                self.test_inline_images,
                "20250101000000"
            )
            
            self.assertEqual(len(image_info), 1)
            self.assertEqual(image_info[0]["content_id"], "image1")
            self.assertTrue(os.path.exists(image_info[0]["path"]))
            
            # Check file content
            with open(image_info[0]["path"], "rb") as f:
                content = f.read()
                self.assertEqual(content, b"fake image data")
                
    def test_update_text_with_references(self):
        """Test updating text content with references."""
        # Setup test components
        self.extractor.processed_components = {
            "text_files": [
                {
                    "type": "plain",
                    "path": os.path.join(self.test_text_dir, "test_plain.txt")
                },
                {
                    "type": "html",
                    "path": os.path.join(self.test_text_dir, "test_html.html")
                }
            ],
            "attachments": [
                {
                    "original_filename": "test.txt",
                    "secure_filename": "test_secure.txt"
                }
            ],
            "inline_images": [
                {
                    "content_id": "image1",
                    "original_filename": "image.jpg",
                    "secure_filename": "image_secure.jpg"
                }
            ],
            "excel_conversions": []
        }
        
        # Create test text files
        with open(os.path.join(self.test_text_dir, "test_plain.txt"), "w") as f:
            f.write("This is a test plain text.")
            
        with open(os.path.join(self.test_text_dir, "test_html.html"), "w") as f:
            f.write('<html><body><img src="cid:image1"></body></html>')
            
        # Update text with references
        self.extractor._update_text_with_references(self.test_email_id)
        
        # Check updated plain text
        with open(os.path.join(self.test_text_dir, "test_plain.txt"), "r") as f:
            content = f.read()
            self.assertIn("Attachments", content)
            self.assertIn("test.txt", content)
            self.assertIn("Inline Images", content)
            self.assertIn("image.jpg", content)
            
        # Check updated HTML
        with open(os.path.join(self.test_text_dir, "test_html.html"), "r") as f:
            content = f.read()
            self.assertIn('../inline_images/image_secure.jpg', content)
            self.assertIn("Attachments", content)
            self.assertIn("test.txt", content)

if __name__ == "__main__":
    unittest.main()