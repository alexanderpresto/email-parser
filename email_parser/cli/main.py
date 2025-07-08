# email_parser/cli.py
import argparse
import os
import sys
from typing import List, Optional

from email_parser.core.config import ProcessingConfig
from email_parser.core.email_processor import EmailProcessor
from email_parser.cli.file_converter import DirectFileConverter


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


def convert_file(args: argparse.Namespace) -> int:
    """Convert a single file directly without email context."""
    from pathlib import Path
    
    input_path = Path(args.file)
    output_dir = Path(args.output)
    
    # Check if input file exists
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1
    
    try:
        # Create converter
        converter = DirectFileConverter(output_directory=str(output_dir))
        
        # Convert the file
        result = converter.convert_file(input_path, output_dir)
        
        if result.success:
            print(f"Successfully converted {input_path.name}")
            print(f"Output: {result.output_path}")
            print(f"Type: {result.converter_type}")
            print(f"Duration: {result.duration_seconds:.2f}s")
            return 0
        else:
            print(f"Conversion failed: {result.error_message}", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"Error converting file: {e}", file=sys.stderr)
        return 1


def convert_batch(args: argparse.Namespace) -> int:
    """Convert multiple files in a directory."""
    from pathlib import Path
    
    input_dir = Path(args.directory)
    output_dir = Path(args.output)
    
    # Check if input directory exists
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Directory not found: {input_dir}", file=sys.stderr)
        return 1
    
    try:
        # Create converter
        converter = DirectFileConverter(output_directory=str(output_dir))
        
        # Scan for files
        files = converter.scan_directory(
            input_dir, 
            pattern=getattr(args, 'pattern', '*'),
            recursive=getattr(args, 'recursive', False)
        )
        
        if not files:
            print(f"No supported files found in {input_dir}")
            return 0
        
        print(f"Found {len(files)} supported files")
        
        # Convert files
        results = converter.convert_batch(files, output_dir)
        
        # Print summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        print(f"\nConversion completed:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        
        if failed > 0:
            print("\nFailed files:")
            for result in results:
                if not result.success:
                    print(f"  {result.input_path.name}: {result.error_message}")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        print(f"Error in batch conversion: {e}", file=sys.stderr)
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
    
    # Add interactive mode option
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode")
    
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

    # Convert file command
    convert_parser = subparsers.add_parser("convert", help="Convert a single file directly")
    convert_parser.add_argument("--file", required=True, help="Input file to convert")
    convert_parser.add_argument("--output", required=True, help="Output directory")
    
    # Convert batch command
    convert_batch_parser = subparsers.add_parser("convert-batch", help="Convert multiple files in a directory")
    convert_batch_parser.add_argument("--directory", required=True, help="Input directory containing files")
    convert_batch_parser.add_argument("--output", required=True, help="Output directory")
    convert_batch_parser.add_argument("--pattern", default="*", help="File pattern to match (default: *)")
    convert_batch_parser.add_argument("--recursive", action="store_true", help="Search subdirectories")

    args = parser.parse_args(argv)

    # Check for interactive mode
    if args.interactive:
        try:
            from email_parser.cli.interactive import InteractiveCLI
            cli = InteractiveCLI()
            return cli.run()
        except ImportError as e:
            print(f"Interactive mode requires additional dependencies: {e}", file=sys.stderr)
            print("Install with: pip install rich prompt-toolkit", file=sys.stderr)
            return 1

    if args.command == "process":
        return process_email(args)
    elif args.command == "batch":
        return process_batch(args)
    elif args.command == "convert":
        return convert_file(args)
    elif args.command == "convert-batch":
        return convert_batch(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
