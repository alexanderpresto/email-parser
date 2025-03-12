# email_parser/cli.py
import argparse
import os
import sys
from typing import List, Optional

from email_parser.core.config import ProcessingConfig
from email_parser.core.email_processor import EmailProcessor


def process_email(args: argparse.Namespace) -> int:
    """Process a single email file."""
    config = ProcessingConfig(
        output_directory=args.output,
        convert_excel=args.convert_excel,
        max_attachment_size=args.max_attachment_size,
    )

    parser = EmailProcessor(config)
    try:
        result = parser.process_email(args.input)
        print(f"Successfully processed email: {args.input}")
        print(f"Extracted {len(result.attachments)} attachments")
        return 0
    except Exception as e:
        print(f"Error processing email: {e}", file=sys.stderr)
        return 1


def process_batch(args: argparse.Namespace) -> int:
    """Process a batch of emails from a directory."""
    if not os.path.isdir(args.input):
        print(f"Error: {args.input} is not a directory", file=sys.stderr)
        return 1

    config = ProcessingConfig(
        output_directory=args.output,
        convert_excel=args.convert_excel,
        max_attachment_size=args.max_attachment_size,
        batch_size=args.batch_size,
    )

    parser = EmailProcessor(config)

    # Get all email files in the directory
    email_files = []
    pattern = args.pattern.lower()
    for filename in os.listdir(args.input):
        if filename.lower().endswith(pattern):
            email_files.append(os.path.join(args.input, filename))

    if not email_files:
        print(f"No matching email files found in {args.input}", file=sys.stderr)
        return 1

    try:
        results = parser.process_batch(email_files)
        print(f"Successfully processed {len(results)} emails")
        return 0
    except Exception as e:
        print(f"Error processing batch: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Enterprise Email Parser")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process a single email")
    process_parser.add_argument("--input", required=True, help="Input email file")
    process_parser.add_argument("--output", required=True, help="Output directory")
    process_parser.add_argument("--convert-excel", action="store_true", help="Convert Excel to CSV")
    process_parser.add_argument(
        "--max-attachment-size",
        type=int,
        default=10_000_000,
        help="Maximum attachment size in bytes",
    )

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Process a batch of emails")
    batch_parser.add_argument("--input", required=True, help="Input directory containing emails")
    batch_parser.add_argument("--output", required=True, help="Output directory")
    batch_parser.add_argument("--pattern", default=".eml", help="File pattern to match")
    batch_parser.add_argument("--convert-excel", action="store_true", help="Convert Excel to CSV")
    batch_parser.add_argument(
        "--max-attachment-size",
        type=int,
        default=10_000_000,
        help="Maximum attachment size in bytes",
    )
    batch_parser.add_argument("--batch-size", type=int, default=100, help="Batch size")

    args = parser.parse_args(argv)

    if args.command == "process":
        return process_email(args)
    elif args.command == "batch":
        return process_batch(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
