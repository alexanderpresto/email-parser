#!/usr/bin/env python3
"""
PDF Conversion Example

This example demonstrates how to use the Email Parser to process emails
containing PDF attachments and convert them to Markdown using MistralAI OCR.

The PDF conversion feature was inspired by the obsidian-marker project:
https://github.com/l3-n0x/obsidian-marker

Usage:
    python pdf_conversion.py <email_file>
    
Example:
    python pdf_conversion.py sample_with_pdfs.eml
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from email_parser import EmailParser, ProcessingConfig


def main():
    """Demonstrate PDF conversion functionality."""
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python pdf_conversion.py <email_file>")
        sys.exit(1)
    
    email_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(email_file):
        print(f"Error: Email file '{email_file}' not found")
        sys.exit(1)
    
    # Check for MistralAI API key
    if not os.environ.get("MISTRALAI_API_KEY"):
        print("Error: MISTRALAI_API_KEY environment variable not set")
        print("Please set it with: export MISTRALAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    print(f"Processing email: {email_file}")
    print("-" * 50)
    
    try:
        # Configure the parser with PDF conversion enabled
        config = ProcessingConfig(
            output_directory="output/pdf_example",
            convert_excel=True,
            convert_pdf=True,  # Enable PDF conversion
            pdf_extraction_mode="all",  # Extract both text and images
            pdf_image_limit=10,  # Limit to 10 images per PDF
            pdf_image_min_size=100,  # Minimum 100x100 pixels
            pdf_paginate=True,  # Add page separators
            enable_detailed_logging=True
        )
        
        # Create parser instance
        parser = EmailParser(config)
        
        # Process the email
        print("Parsing email and extracting components...")
        result = parser.process_email(email_file)
        
        # Display results
        print(f"\nEmail processed successfully!")
        print(f"Subject: {result.subject}")
        print(f"From: {result.sender}")
        print(f"Date: {result.date}")
        print(f"\nAttachments found: {len(result.attachments)}")
        
        # Show PDF conversion results
        if hasattr(result, 'pdf_conversions') and result.pdf_conversions:
            print(f"\nPDF Conversions: {len(result.pdf_conversions)}")
            print("-" * 50)
            
            for pdf in result.pdf_conversions:
                print(f"\nPDF: {pdf['original_filename']}")
                print(f"  Pages: {pdf['page_count']}")
                print(f"  Extraction mode: {pdf['extraction_mode']}")
                print(f"  Markdown file: {pdf['markdown_path']}")
                
                if pdf.get('image_paths'):
                    print(f"  Images extracted: {len(pdf['image_paths'])}")
                    for img in pdf['image_paths'][:3]:  # Show first 3 images
                        print(f"    - {os.path.basename(img)}")
                    if len(pdf['image_paths']) > 3:
                        print(f"    ... and {len(pdf['image_paths']) - 3} more")
                
                # Show a preview of the markdown content
                if pdf.get('markdown_path') and os.path.exists(pdf['markdown_path']):
                    with open(pdf['markdown_path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                        preview = content[:500] + "..." if len(content) > 500 else content
                        print(f"\n  Markdown preview:")
                        print(f"  {preview}")
        else:
            print("\nNo PDFs found in this email.")
        
        # Show Excel conversion results if any
        if hasattr(result, 'csv_files') and result.csv_files:
            print(f"\n\nExcel Conversions: {len(result.csv_files)}")
            print("-" * 50)
            for csv in result.csv_files:
                print(f"  - {csv['original_filename']} → {csv['csv_filename']}")
        
        print(f"\n\nAll output saved to: {config.output_directory}")
        
    except Exception as e:
        print(f"\nError processing email: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()