"""
Example of batch processing multiple email files.
"""

import os
import sys
import logging
import glob
from pathlib import Path

# Add the parent directory to the sys.path to import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from email_parser import EmailProcessor
from email_parser.utils.logging_config import configure_logging
from email_parser.core.config import ProcessingConfig

# Set up logging
configure_logging(log_level=logging.INFO)


def process_email_batch(email_dir: str, pattern: str = "*.eml") -> dict:
    """Process multiple email files in a directory."""
    # Find all email files in the directory
    email_files = glob.glob(os.path.join(email_dir, pattern))

    if not email_files:
        print(f"No email files found matching pattern '{pattern}' in directory: {email_dir}")
        return {}

    print(f"Found {len(email_files)} email files to process")
    # Initialize the email processor with default config
    processor = EmailProcessor(
        config=ProcessingConfig(
            output_directory="output",
            convert_excel=False,
            max_attachment_size=10_000_000,
            batch_size=100,
        )
    )

    # Prepare email contents and IDs
    email_contents = []
    email_ids = []

    for email_file in email_files:
        with open(email_file, "rb") as f:
            email_contents.append(f.read())

        # Generate email ID from filename
        email_id = os.path.splitext(os.path.basename(email_file))[0]
        email_ids.append(email_id)

    # Process the emails in batch
    batch_result = processor.process_email_batch(
        [str(content) for content in email_contents], email_ids=email_ids, continue_on_error=True
    )
    # Print batch processing results
    print(f"Batch processing completed:")
    print(f"  - Total emails: {batch_result['total']}")
    print(f"  - Successful: {batch_result['success_count']}")
    print(f"  - Failed: {batch_result['error_count']}")

    if batch_result["error_count"] > 0:
        print("\nErrors:")
        for error in batch_result["errors"]:
            print(f"  - Email {error['email_id']}: {error['error']}")

    return batch_result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python batch_processing.py <email_directory>")
        sys.exit(1)

    email_dir = sys.argv[1]
    if not os.path.isdir(email_dir):
        print(f"Error: Directory not found: {email_dir}")
        sys.exit(1)

    try:
        batch_result = process_email_batch(email_dir)
        print("Batch processing completed successfully.")
        print(f"Output files are in the '{os.path.abspath('output')}' directory.")
    except Exception as e:
        print(f"Error during batch processing: {str(e)}")
        sys.exit(1)
