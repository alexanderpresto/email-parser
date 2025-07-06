"""Unit tests for the EmailScanner component."""

import pytest
import tempfile
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from email_parser.core.scanner import (
    EmailScanner, 
    ScanResult, 
    AttachmentInfo, 
    FileType, 
    ComplexityLevel
)


class TestEmailScanner:
    """Test the EmailScanner class."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.scanner = EmailScanner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_email(self, subject="Test Subject", attachments=None):
        """Create a test email with optional attachments."""
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = 'test@example.com'
        msg['Date'] = 'Mon, 01 Jan 2024 12:00:00 +0000'
        
        # Add text body
        text_part = MIMEText("This is a test email body.", 'plain')
        msg.attach(text_part)
        
        # Add attachments if provided
        if attachments:
            for filename, content, content_type in attachments:
                if content_type.startswith('application/'):
                    attachment = MIMEApplication(content, _subtype=content_type.split('/')[-1])
                else:
                    attachment = MIMEText(content.decode('utf-8') if isinstance(content, bytes) else content)
                
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attachment)
        
        return msg

    def save_email_to_file(self, msg, filename="test.eml"):
        """Save email message to file and return path."""
        email_path = self.temp_dir / filename
        with open(email_path, 'wb') as f:
            f.write(msg.as_bytes())
        return email_path

    def test_scan_simple_email(self):
        """Test scanning a simple email without attachments."""
        msg = self.create_test_email()
        email_path = self.save_email_to_file(msg)
        
        result = self.scanner.scan(email_path)
        
        assert isinstance(result, ScanResult)
        assert result.subject == "Test Subject"
        assert result.sender == "test@example.com"
        assert result.date == "Mon, 01 Jan 2024 12:00:00 +0000"
        assert len(result.attachments) == 0
        assert result.complexity_score < 2  # Simple email

    def test_scan_email_with_pdf_attachment(self):
        """Test scanning email with PDF attachment."""
        # Create fake PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        
        attachments = [("document.pdf", pdf_content, "application/pdf")]
        msg = self.create_test_email(attachments=attachments)
        email_path = self.save_email_to_file(msg)
        
        result = self.scanner.scan(email_path)
        
        assert len(result.attachments) == 1
        
        pdf_att = result.attachments[0]
        assert pdf_att.filename == "document.pdf"
        assert pdf_att.file_type == FileType.PDF
        assert pdf_att.size_bytes == len(pdf_content)
        assert pdf_att.estimated_pages is not None

    def test_scan_email_with_multiple_attachments(self):
        """Test scanning email with multiple different attachment types."""
        attachments = [
            ("document.pdf", b"fake pdf content", "application/pdf"),
            ("spreadsheet.xlsx", b"fake excel content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("report.docx", b"fake word content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("image.png", b"fake png content", "image/png")
        ]
        
        msg = self.create_test_email(attachments=attachments)
        email_path = self.save_email_to_file(msg)
        
        result = self.scanner.scan(email_path)
        
        assert len(result.attachments) == 4
        
        # Check file types are correctly identified
        file_types = {att.file_type for att in result.attachments}
        expected_types = {FileType.PDF, FileType.XLSX, FileType.DOCX, FileType.IMAGE}
        assert file_types == expected_types

    def test_scan_email_with_large_attachments(self):
        """Test scanning email with large attachments."""
        # Create large fake content
        large_content = b"x" * (5 * 1024 * 1024)  # 5MB
        
        attachments = [("large_file.pdf", large_content, "application/pdf")]
        msg = self.create_test_email(attachments=attachments)
        email_path = self.save_email_to_file(msg)
        
        result = self.scanner.scan(email_path)
        
        assert len(result.attachments) == 1
        
        large_att = result.attachments[0]
        assert large_att.size_mb > 4.5  # Should be around 5MB
        assert large_att.complexity == ComplexityLevel.COMPLEX
        assert len(large_att.warnings) > 0  # Should have size warning

    def test_attachment_complexity_analysis(self):
        """Test attachment complexity analysis."""
        # Test different sizes and complexities
        test_cases = [
            (b"small", FileType.PDF, ComplexityLevel.SIMPLE),
            (b"x" * (2 * 1024 * 1024), FileType.PDF, ComplexityLevel.MODERATE),  # 2MB
            (b"x" * (10 * 1024 * 1024), FileType.PDF, ComplexityLevel.COMPLEX),  # 10MB
        ]
        
        for i, (content, file_type, expected_complexity) in enumerate(test_cases):
            attachments = [(f"test_{i}.pdf", content, "application/pdf")]
            msg = self.create_test_email(attachments=attachments)
            email_path = self.save_email_to_file(msg, f"test_{i}.eml")
            
            result = self.scanner.scan(email_path)
            
            assert len(result.attachments) == 1
            assert result.attachments[0].complexity == expected_complexity

    def test_scan_recommendations_generation(self):
        """Test that recommendations are generated based on content."""
        # Email with PDF that should trigger PDF recommendations
        pdf_content = b"x" * (3 * 1024 * 1024)  # 3MB PDF
        attachments = [("large_document.pdf", pdf_content, "application/pdf")]
        msg = self.create_test_email(attachments=attachments)
        email_path = self.save_email_to_file(msg)
        
        result = self.scanner.scan(email_path)
        
        assert len(result.recommendations) > 0
        
        # Should recommend comprehensive or ai_ready profile for complex content
        profile_recommendations = [r for r in result.recommendations if "profile" in r.lower()]
        assert len(profile_recommendations) > 0

    def test_processing_time_estimation(self):
        """Test processing time estimation."""
        # Email with multiple attachments
        attachments = [
            ("document.pdf", b"x" * (2 * 1024 * 1024), "application/pdf"),  # 2MB PDF
            ("spreadsheet.xlsx", b"x" * (500 * 1024), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),  # 500KB Excel
        ]
        
        msg = self.create_test_email(attachments=attachments)
        email_path = self.save_email_to_file(msg)
        
        result = self.scanner.scan(email_path)
        
        # Should have reasonable time estimate
        assert result.estimated_time.total_seconds() > 10  # At least 10 seconds for 2MB PDF
        assert result.estimated_time.total_seconds() < 300  # Less than 5 minutes

    def test_feature_extraction(self):
        """Test feature extraction from email content."""
        msg = self.create_test_email()
        # Add HTML content
        html_part = MIMEText("<html><body><h1>HTML Content</h1></body></html>", 'html')
        msg.attach(html_part)
        
        email_path = self.save_email_to_file(msg)
        result = self.scanner.scan(email_path)
        
        # Should detect both text and HTML bodies
        assert result.features.get('has_text_body', False)
        assert result.features.get('has_html_body', False)

    def test_warning_collection(self):
        """Test that warnings are properly collected."""
        # Create very large attachment that should trigger warnings
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB
        attachments = [("huge_file.pdf", large_content, "application/pdf")]
        msg = self.create_test_email(attachments=attachments)
        email_path = self.save_email_to_file(msg)
        
        result = self.scanner.scan(email_path)
        
        # Should have warnings about large file size
        assert len(result.warnings) > 0
        
        # Should have attachment-specific warnings
        large_att = result.attachments[0]
        assert len(large_att.warnings) > 0

    def test_file_type_detection(self):
        """Test file type detection based on extensions."""
        test_files = [
            ("document.pdf", FileType.PDF),
            ("document.doc", FileType.DOCX),
            ("document.docx", FileType.DOCX),
            ("spreadsheet.xls", FileType.XLSX),
            ("spreadsheet.xlsx", FileType.XLSX),
            ("image.png", FileType.IMAGE),
            ("image.jpg", FileType.IMAGE),
            ("image.jpeg", FileType.IMAGE),
            ("text.txt", FileType.TEXT),
            ("data.csv", FileType.TEXT),
            ("unknown.xyz", FileType.OTHER),
        ]
        
        for filename, expected_type in test_files:
            attachments = [(filename, b"test content", "application/octet-stream")]
            msg = self.create_test_email(attachments=attachments)
            email_path = self.save_email_to_file(msg, f"test_{filename}.eml")
            
            result = self.scanner.scan(email_path)
            
            assert len(result.attachments) == 1
            assert result.attachments[0].file_type == expected_type

    def test_scan_nonexistent_file(self):
        """Test scanning a non-existent email file."""
        nonexistent_path = self.temp_dir / "nonexistent.eml"
        
        with pytest.raises(FileNotFoundError):
            self.scanner.scan(nonexistent_path)

    def test_scan_invalid_email_file(self):
        """Test scanning an invalid email file."""
        invalid_path = self.temp_dir / "invalid.eml"
        
        # Create invalid email content
        with open(invalid_path, 'w') as f:
            f.write("This is not a valid email file")
        
        with pytest.raises(ValueError):
            self.scanner.scan(invalid_path)

    def test_attachment_info_properties(self):
        """Test AttachmentInfo properties and methods."""
        # Create attachment info
        att = AttachmentInfo(
            filename="test.pdf",
            content_type="application/pdf",
            size_bytes=1024 * 1024,  # 1MB
            file_type=FileType.PDF,
            complexity=ComplexityLevel.MODERATE
        )
        
        # Test size properties
        assert att.size_mb == 1.0
        assert att.size_display == "1.0 MB"
        
        # Test smaller file
        small_att = AttachmentInfo(
            filename="small.txt",
            content_type="text/plain",
            size_bytes=512,
            file_type=FileType.TEXT,
            complexity=ComplexityLevel.SIMPLE
        )
        
        assert small_att.size_display == "512 B"

    def test_scan_result_properties(self):
        """Test ScanResult properties and methods."""
        attachments = [
            ("document.pdf", b"test content", "application/pdf"),
            ("spreadsheet.xlsx", b"test content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ]
        
        msg = self.create_test_email(attachments=attachments)
        email_path = self.save_email_to_file(msg)
        
        result = self.scanner.scan(email_path)
        
        # Test convenience properties
        assert result.attachment_count == 2
        assert result.has_pdf
        assert result.has_excel
        assert not result.has_docx  # No DOCX in this test

    def test_pdf_page_estimation(self):
        """Test PDF page estimation based on file size."""
        # Test different PDF sizes
        test_cases = [
            (50 * 1024, 1),      # 50KB -> 1 page minimum
            (150 * 1024, 2),     # 150KB -> ~2 pages
            (750 * 1024, 10),    # 750KB -> ~10 pages
        ]
        
        for size_bytes, expected_min_pages in test_cases:
            content = b"x" * size_bytes
            attachments = [("test.pdf", content, "application/pdf")]
            msg = self.create_test_email(attachments=attachments)
            email_path = self.save_email_to_file(msg)
            
            result = self.scanner.scan(email_path)
            
            pdf_att = result.attachments[0]
            assert pdf_att.estimated_pages >= expected_min_pages