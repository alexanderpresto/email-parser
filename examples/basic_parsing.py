"""
Basic example of parsing an email file.
"""
import os
import sys
import logging
from pathlib import Path

from email_parser.core.config import ProcessingConfig

# Add the parent directory to the sys.path to import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from email_parser import EmailProcessor
from email_parser.utils.logging_config import configure_logging

# Set up logging
configure_logging(log_level=logging.INFO)

def parse_email(email_path: str) -> dict:
    """Parse a single email file."""
    # Initialize the email processor
    processor = EmailProcessor(
        config=ProcessingConfig(
            output_directory="output"
        )
    )
    # Process the email
    with open(email_path, "rb") as f:
        email_content = f.read()
    
    # Generate an ID based on filename
    email_id = os.path.splitext(os.path.basename(email_path))[0]
    
    # Process the email
    result = processor.process_email(email_content, email_id)
    
    # Print processing summary
    print(f"Email ID: {result['email_id']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Text files: {len(result.get('text_files', []))}")
    print(f"Attachments: {len(result.get('attachments', []))}")
    print(f"Inline images: {len(result.get('inline_images', []))}")
    print(f"Excel conversions: {len(result.get('excel_conversions', []))}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python basic_parsing.py <email_file_path>")
        sys.exit(1)
    
    email_path = sys.argv[1]
    if not os.path.isfile(email_path):
        print(f"Error: File not found: {email_path}")
        sys.exit(1)
    
    try:
        result = parse_email(email_path)
        print("Email processed successfully.")
        print(f"Output files are in the '{os.path.abspath('output')}' directory.")
    except Exception as e:
        print(f"Error processing email: {str(e)}")
        sys.exit(1)