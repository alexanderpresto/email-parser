# email_parser/cli.py
import argparse
import os
import sys
from typing import List, Optional

from email_parser.core.config import ProcessingConfig
from email_parser.core.email_processor import EmailProcessor


def process_email(args: argparse.Namespace) -> int:
    """Process a single email file."""
    # Check if input is a directory
    if os.path.isdir(args.input):
        print(f"Error: {args.input} is a directory. Use 'batch' command for directories.", file=sys.stderr)
        return 1

    # Check if input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Email file not found: {args.input}", file=sys.stderr)
        return 1
        
    config = ProcessingConfig(
        output_directory=args.output,
        convert_excel=args.convert_excel,
        convert_pdf=args.convert_pdf,
        convert_docx=getattr(args, 'convert_docx', False),
        pdf_extraction_mode=args.pdf_mode if hasattr(args, 'pdf_mode') else 'all',
        docx_extract_metadata=getattr(args, 'docx_metadata', True),
        docx_extract_images=getattr(args, 'docx_images', False),
        docx_enable_chunking=getattr(args, 'docx_chunking', True),
        docx_chunk_size=getattr(args, 'docx_chunk_size', 2000),
        docx_chunk_overlap=getattr(args, 'docx_chunk_overlap', 200),
        docx_chunk_strategy=getattr(args, 'docx_chunk_strategy', 'hybrid'),
        docx_extract_styles=getattr(args, 'docx_styles', True),
        docx_extract_comments=getattr(args, 'docx_comments', True),
        max_attachment_size=args.max_attachment_size,
    )

    parser = EmailProcessor(config)
    try:
        result = parser.process_email(args.input)
        print(f"Successfully processed email: {args.input}")
        print(f"Extracted {len(result['attachments'])} attachments")
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
        convert_pdf=args.convert_pdf,
        convert_docx=getattr(args, 'convert_docx', False),
        pdf_extraction_mode=args.pdf_mode if hasattr(args, 'pdf_mode') else 'all',
        docx_extract_metadata=getattr(args, 'docx_metadata', True),
        docx_extract_images=getattr(args, 'docx_images', False),
        docx_enable_chunking=getattr(args, 'docx_chunking', True),
        docx_chunk_size=getattr(args, 'docx_chunk_size', 2000),
        docx_chunk_overlap=getattr(args, 'docx_chunk_overlap', 200),
        docx_chunk_strategy=getattr(args, 'docx_chunk_strategy', 'hybrid'),
        docx_extract_styles=getattr(args, 'docx_styles', True),
        docx_extract_comments=getattr(args, 'docx_comments', True),
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
    process_parser.add_argument("--convert-pdf", action="store_true", help="Convert PDF to Markdown")
    process_parser.add_argument("--pdf-mode", choices=['text', 'images', 'all'], default='all', 
                               help="PDF extraction mode (default: all)")
    process_parser.add_argument("--convert-docx", action="store_true", help="Convert DOCX to Markdown")
    process_parser.add_argument("--docx-metadata", action="store_true", default=True, 
                               help="Extract metadata from DOCX files (default: True)")
    process_parser.add_argument("--docx-images", action="store_true", 
                               help="Extract images from DOCX files (Week 2 feature)")
    process_parser.add_argument("--docx-chunking", action="store_true", default=True,
                               help="Enable AI-ready document chunking (Week 2 feature)")
    process_parser.add_argument("--docx-chunk-size", type=int, default=2000,
                               help="Maximum tokens per chunk (default: 2000)")
    process_parser.add_argument("--docx-chunk-overlap", type=int, default=200,
                               help="Token overlap between chunks (default: 200)")
    process_parser.add_argument("--docx-chunk-strategy", choices=['token', 'semantic', 'hybrid'], 
                               default='hybrid', help="Chunking strategy (default: hybrid)")
    process_parser.add_argument("--docx-styles", action="store_true", default=True,
                               help="Extract style information (Week 2 feature)")
    process_parser.add_argument("--docx-comments", action="store_true", default=True,
                               help="Extract comments and track changes (default: True)")
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
    batch_parser.add_argument("--convert-pdf", action="store_true", help="Convert PDF to Markdown")
    batch_parser.add_argument("--pdf-mode", choices=['text', 'images', 'all'], default='all',
                             help="PDF extraction mode (default: all)")
    batch_parser.add_argument("--convert-docx", action="store_true", help="Convert DOCX to Markdown")
    batch_parser.add_argument("--docx-metadata", action="store_true", default=True, 
                             help="Extract metadata from DOCX files (default: True)")
    batch_parser.add_argument("--docx-images", action="store_true", 
                             help="Extract images from DOCX files (Week 2 feature)")
    batch_parser.add_argument("--docx-chunking", action="store_true", default=True,
                             help="Enable AI-ready document chunking (Week 2 feature)")
    batch_parser.add_argument("--docx-chunk-size", type=int, default=2000,
                             help="Maximum tokens per chunk (default: 2000)")
    batch_parser.add_argument("--docx-chunk-overlap", type=int, default=200,
                             help="Token overlap between chunks (default: 200)")
    batch_parser.add_argument("--docx-chunk-strategy", choices=['token', 'semantic', 'hybrid'], 
                             default='hybrid', help="Chunking strategy (default: hybrid)")
    batch_parser.add_argument("--docx-styles", action="store_true", default=True,
                             help="Extract style information (Week 2 feature)")
    batch_parser.add_argument("--docx-comments", action="store_true", default=True,
                             help="Extract comments and track changes (default: True)")
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
