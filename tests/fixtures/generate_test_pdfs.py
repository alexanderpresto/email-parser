#!/usr/bin/env python3
"""
Generate test PDF files for PDF converter testing.

This script creates various types of PDF files for testing different
scenarios including valid PDFs, corrupted files, and edge cases.
"""

import os
from pathlib import Path
from typing import List

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def create_simple_pdf(output_path: Path) -> None:
    """Create a simple single-page PDF with text content."""
    if not REPORTLAB_AVAILABLE:
        # Create a minimal PDF manually
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Simple test PDF) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000136 00000 n 
0000000229 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
323
%%EOF"""
        output_path.write_bytes(pdf_content)
    else:
        # Use reportlab for better PDF generation
        c = canvas.Canvas(str(output_path), pagesize=letter)
        c.drawString(100, 750, "Simple Test PDF")
        c.drawString(100, 730, "This is a test document for PDF converter testing.")
        c.drawString(100, 710, "It contains basic text content only.")
        c.showPage()
        c.save()


def create_multi_page_pdf(output_path: Path) -> None:
    """Create a multi-page PDF for pagination testing."""
    if not REPORTLAB_AVAILABLE:
        # Create a basic multi-page PDF manually
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R 5 0 R]
/Count 2
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 40
>>
stream
BT
/F1 12 Tf
100 700 Td
(Page 1 content) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 6 0 R
>>
endobj

6 0 obj
<<
/Length 40
>>
stream
BT
/F1 12 Tf
100 700 Td
(Page 2 content) Tj
ET
endstream
endobj

xref
0 7
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000144 00000 n 
0000000237 00000 n 
0000000327 00000 n 
0000000420 00000 n 
trailer
<<
/Size 7
/Root 1 0 R
>>
startxref
510
%%EOF"""
        output_path.write_bytes(pdf_content)
    else:
        c = canvas.Canvas(str(output_path), pagesize=letter)
        
        # Page 1
        c.drawString(100, 750, "Multi-Page Test PDF - Page 1")
        c.drawString(100, 730, "This document has multiple pages for testing pagination.")
        c.showPage()
        
        # Page 2
        c.drawString(100, 750, "Multi-Page Test PDF - Page 2")
        c.drawString(100, 730, "This is the second page of the test document.")
        c.showPage()
        
        # Page 3
        c.drawString(100, 750, "Multi-Page Test PDF - Page 3")
        c.drawString(100, 730, "Final page for comprehensive testing.")
        c.showPage()
        
        c.save()


def create_pdf_with_images(output_path: Path) -> None:
    """Create a PDF with embedded images (placeholder)."""
    if not REPORTLAB_AVAILABLE:
        # Simple PDF claiming to have images
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 60
>>
stream
BT
/F1 12 Tf
100 700 Td
(PDF with embedded images) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000136 00000 n 
0000000229 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
339
%%EOF"""
        output_path.write_bytes(pdf_content)
    else:
        c = canvas.Canvas(str(output_path), pagesize=letter)
        c.drawString(100, 750, "PDF with Images Test")
        c.drawString(100, 730, "This PDF contains embedded images for testing.")
        c.drawString(100, 710, "[IMAGE PLACEHOLDER - would contain actual image]")
        c.rect(100, 600, 200, 100)  # Rectangle representing an image
        c.drawString(100, 580, "Image caption: Test image for OCR")
        c.showPage()
        c.save()


def create_large_pdf(output_path: Path, target_size_mb: int = 10) -> None:
    """Create a large PDF file for size testing."""
    if not REPORTLAB_AVAILABLE:
        # Create large file by repeating content
        base_content = b"Large PDF content for testing. " * 1000
        with open(output_path, "wb") as f:
            # Write PDF header
            f.write(b"%PDF-1.4\n")
            
            # Write large amount of content to reach target size
            target_bytes = target_size_mb * 1024 * 1024
            current_size = len("%PDF-1.4\n")
            
            while current_size < target_bytes:
                f.write(base_content)
                current_size += len(base_content)
            
            # Write PDF footer
            f.write(b"\n%%EOF\n")
    else:
        c = canvas.Canvas(str(output_path), pagesize=letter)
        
        # Create many pages with content to reach target size
        target_bytes = target_size_mb * 1024 * 1024
        page_count = 0
        
        while True:
            page_count += 1
            c.drawString(100, 750, f"Large PDF Test - Page {page_count}")
            
            # Add lots of text to make file larger
            y_pos = 730
            for i in range(50):
                text = f"Line {i}: This is content to make the PDF file larger for testing purposes. " * 3
                c.drawString(50, y_pos, text[:80])  # Truncate to fit page
                y_pos -= 12
                if y_pos < 50:
                    break
            
            c.showPage()
            
            # Check file size approximation
            if page_count > target_size_mb * 20:  # Rough estimate
                break
        
        c.save()


def create_corrupted_pdf(output_path: Path) -> None:
    """Create a corrupted PDF file for error testing."""
    corrupted_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

CORRUPTED_SECTION_HERE_INVALID_DATA
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R  # MISSING CLOSING >>

4 0 obj
<<
/Length 40
>>
stream
BT
/F1 12 Tf
100 700 Td
(Corrupted PDF) Tj
ET
MISSING_ENDSTREAM

xref
0 5
0000000000 65535 f 
INVALID_XREF_ENTRY
0000000136 00000 n 
0000000229 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
INVALID_STARTXREF
%%EOF"""
    output_path.write_bytes(corrupted_content)


def create_empty_pdf(output_path: Path) -> None:
    """Create an empty (zero-byte) PDF file."""
    output_path.write_bytes(b"")


def create_password_protected_pdf(output_path: Path) -> None:
    """Create a password-protected PDF (simulated)."""
    protected_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/Encrypt 5 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 50
/Filter /Standard
>>
stream
ENCRYPTED_CONTENT_PLACEHOLDER_DATA_HERE
endstream
endobj

5 0 obj
<<
/Filter /Standard
/V 1
/R 2
/O (encrypted_owner_password_placeholder)
/U (encrypted_user_password_placeholder)
/P -44
>>
endobj

xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000089 00000 n 
0000000146 00000 n 
0000000239 00000 n 
0000000349 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
/Encrypt 5 0 R
>>
startxref
523
%%EOF"""
    output_path.write_bytes(protected_content)


def create_fake_pdf(output_path: Path) -> None:
    """Create a text file with .pdf extension."""
    fake_content = """This is not a PDF file!
It's just a plain text file with a .pdf extension.
This should be detected as invalid by the PDF validator.

Some additional content to make it look like it might be a document:
- Item 1
- Item 2  
- Item 3

But it's definitely not a PDF format."""
    output_path.write_text(fake_content)


def create_unsupported_version_pdf(output_path: Path) -> None:
    """Create a PDF with unsupported version."""
    unsupported_content = b"""%PDF-3.0
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 60
>>
stream
BT
/F1 12 Tf
100 700 Td
(Unsupported PDF version 3.0) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000136 00000 n 
0000000229 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
349
%%EOF"""
    output_path.write_bytes(unsupported_content)


def main():
    """Generate all test PDF files."""
    fixtures_dir = Path(__file__).parent
    
    print("Generating test PDF fixtures...")
    
    if not REPORTLAB_AVAILABLE:
        print("Warning: ReportLab not available. Creating basic PDF files.")
        print("For better test files, install reportlab: pip install reportlab")
    
    # Create test files
    test_files = [
        ("valid_simple.pdf", create_simple_pdf),
        ("valid_multi_page.pdf", create_multi_page_pdf),
        ("valid_with_images.pdf", create_pdf_with_images),
        ("corrupted.pdf", create_corrupted_pdf),
        ("empty.pdf", create_empty_pdf),
        ("password_protected.pdf", create_password_protected_pdf),
        ("fake.pdf", create_fake_pdf),
        ("unsupported_version.pdf", create_unsupported_version_pdf),
    ]
    
    for filename, create_func in test_files:
        file_path = fixtures_dir / filename
        try:
            create_func(file_path)
            file_size = file_path.stat().st_size
            print(f"Created {filename} ({file_size} bytes)")
        except Exception as e:
            print(f"Error creating {filename}: {e}")
    
    # Create large file separately (optional)
    large_file = fixtures_dir / "large_10mb.pdf"
    try:
        print("Creating large test file (this may take a moment)...")
        create_large_pdf(large_file, target_size_mb=10)
        file_size = large_file.stat().st_size
        print(f"Created large_10mb.pdf ({file_size / 1024 / 1024:.1f} MB)")
    except Exception as e:
        print(f"Error creating large file: {e}")
    
    print(f"\nTest fixtures generated in: {fixtures_dir}")
    print("Files are ready for testing!")


if __name__ == "__main__":
    main()