# Enterprise Email Parser

[![Python Version](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/python/mypy)

An enterprise-grade email processing system with robust MIME parsing, security features, PDF to Markdown conversion, and performance optimization.

## Overview

This library provides a comprehensive solution for parsing and processing emails in enterprise environments with high volume requirements. It handles complex MIME structures, extracts all components (text, HTML, attachments, inline images), converts PDFs to searchable Markdown using MistralAI OCR, and ensures secure processing throughout.

Key features include:

- Complete MIME structure parsing and extraction
- **PDF to Markdown conversion using MistralAI OCR** (NEW in v2.0)
- Automatic Excel to CSV conversion capability
- Secure file handling with protection against common attack vectors
- Support for multiple encodings (UTF-8, UTF-16, ASCII, ISO-8859, Base64, etc.) with automatic encoding detection
- High-performance batch processing with parallel PDF/Excel conversion
- Comprehensive error handling and logging
- Complete type annotations and rigorous testing

## Installation

### Prerequisites

- Python 3.12.9 or higher
- Anaconda distribution (recommended)
- MistralAI API key (for PDF conversion)

### Setup with Anaconda

We recommend creating a dedicated Anaconda environment:

```bash
# Clone the repository
git clone https://github.com/alexanderpresto/email-parser.git
cd email-parser

# Create and activate environment using provided configuration
conda env create -f environment.yml
conda activate email-parser

# Install in development mode
pip install -e .
```

### Setup with pip

Alternatively, you can use pip with the provided requirements file:

```bash
# Clone the repository
git clone https://github.com/alexanderpresto/email-parser.git
cd email-parser

# Create a virtual environment
python -m venv email-parser-env
source email-parser-env/bin/activate  # On Windows: .\email-parser-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### MistralAI API Setup

For PDF to Markdown conversion, you'll need a MistralAI API key:

```bash
# Set as environment variable
export MISTRALAI_API_KEY="your-api-key-here"  # Linux/Mac
set MISTRALAI_API_KEY=your-api-key-here       # Windows
```

## Quick Start

```python
from email_parser import EmailParser, ProcessingConfig

# Configure the parser with PDF conversion enabled
config = ProcessingConfig(
    output_directory="output/",
    convert_excel=True,
    convert_pdf=True,  # Enable PDF to Markdown conversion
    pdf_extraction_mode="all",  # Options: "text", "images", "all"
    max_attachment_size=10_000_000,  # 10MB
    batch_size=100
)

# Create parser instance
parser = EmailParser(config)

# Process a single email with PDF attachments
result = parser.process_email("path/to/email.eml")
print(f"Processed email with {len(result.attachments)} attachments")
print(f"Converted {len(result.pdf_files)} PDFs to Markdown")

# Process a batch of emails
batch_results = parser.process_batch(["email1.eml", "email2.eml", "email3.eml"])
print(f"Processed {len(batch_results)} emails")
```

## Core Features

### PDF to Markdown Conversion (NEW)

Convert PDF attachments to searchable Markdown using MistralAI's advanced OCR technology:

```python
# Configure PDF conversion options
config = ProcessingConfig(
    convert_pdf=True,
    pdf_extraction_mode="all",  # Extract both text and images
    pdf_image_limit=10,  # Limit number of images per PDF
    pdf_image_min_size=100,  # Minimum image size in pixels
    pdf_paginate=True  # Add page separators
)

parser = EmailParser(config)

# Process email with PDF attachments
result = parser.process_email("email_with_pdfs.eml")

# Access converted PDFs
for pdf_result in result.pdf_conversions:
    print(f"PDF: {pdf_result['original_filename']}")
    print(f"Markdown: {pdf_result['markdown_path']}")
    print(f"Images: {pdf_result['image_paths']}")
    print(f"Pages: {pdf_result['page_count']}")
```

### MIME Structure Parsing

The library thoroughly parses MIME structures, handling nested multipart messages and various encoding schemes:

```python
# Extract and analyze MIME structure
mime_structure = parser.extract_mime_structure("email.eml")
print(mime_structure.get_structure_tree())
```

### Component Extraction

Extract specific components from emails:

```python
# Extract just the text body
text_content = parser.extract_text("email.eml")

# Extract all attachments
attachments = parser.extract_attachments("email.eml")

# Extract everything with full processing
result = parser.process_email("email.eml")
```

### Excel to CSV Conversion

Automatically convert Excel workbooks to CSV files:

```python
# Configure with Excel conversion enabled
config = ProcessingConfig(convert_excel=True)
parser = EmailParser(config)

# Process email - Excel files will be converted automatically
result = parser.process_email("email_with_excel.eml")
print(f"Generated CSV files: {result.csv_files}")
```

### Secure File Handling

The library implements multiple security measures:

- Filename sanitization
- Path traversal prevention
- File type validation
- Size limits and quotas
- Malicious content scanning
- PDF content validation

```python
# Configure security settings
config = ProcessingConfig(
    max_attachment_size=5_000_000,  # 5MB
    allowed_extensions=[".pdf", ".docx", ".xlsx", ".txt", ".jpg", ".png"],
    enable_malware_scanning=True,
    validate_pdf_content=True  # Check PDFs for malicious content
)
parser = EmailParser(config)
```

### Batch Processing

Process multiple emails efficiently with parallel PDF/Excel conversion:

```python
# Configure batch settings
config = ProcessingConfig(
    batch_size=100,
    max_workers=4,
    enable_progress_bar=True,
    parallel_pdf_conversion=True  # Process PDFs in parallel
)
parser = EmailParser(config)

# Process a large batch of emails
results = parser.process_directory("mail_directory/")
```

## Output Structure

The library creates a structured output with the following organization:

```
output/
├── processed_text/
│   └── email_123abc.txt
├── attachments/
│   ├── 20250301_123abc_report.pdf
│   └── 20250301_456def_presentation.pptx
├── inline_images/
│   ├── 20250301_123abc_image1.png
│   └── 20250301_456def_image2.jpg
├── converted_excel/
│   ├── 20250301_123abc_sheet1.csv
│   └── 20250301_123abc_sheet2.csv
├── converted_pdf/
│   ├── 20250301_123abc_report.md
│   └── 20250301_123abc_report_images/
│       ├── img_001.png
│       └── img_002.png
└── metadata.json
```

The `metadata.json` file contains comprehensive information about the processed email, including:

- Email headers
- Processing timestamp
- List of extracted components with paths
- Mapping of original filenames to unique filenames
- Positional information for each extraction
- Excel to CSV conversion mappings
- PDF to Markdown conversion details
- OCR processing statistics
- Processing statistics

## Advanced Usage

### Custom PDF Processing

Configure advanced PDF processing options:

```python
from email_parser import EmailParser, ProcessingConfig, PDFConfig

# Advanced PDF configuration
pdf_config = PDFConfig(
    extraction_mode="all",
    image_limit=20,
    image_min_size=200,
    paginate=True,
    cache_enabled=True,
    api_timeout=30,
    max_retries=3
)

config = ProcessingConfig(
    convert_pdf=True,
    pdf_config=pdf_config
)

parser = EmailParser(config)
```

### Custom Processing Pipeline

Create a custom processing pipeline for specialized needs:

```python
from email_parser import EmailParser, Pipeline, ProcessingStep

# Create custom processing steps
class CustomValidationStep(ProcessingStep):
    def process(self, email_data, context):
        # Custom validation logic
        if not self.validate_headers(email_data):
            context.add_warning("Invalid headers detected")
        return email_data

# Configure a custom pipeline
pipeline = Pipeline([
    CustomValidationStep(),
    # Add more custom or built-in steps
])

# Use the custom pipeline
parser = EmailParser(pipeline=pipeline)
```

### Error Handling

The library provides a comprehensive error handling system:

```python
from email_parser import EmailParser, ProcessingConfig
from email_parser.exceptions import (
    MIMEParsingError, 
    AttachmentExtractionError,
    PDFConversionError,
    OCRError
)

# Configure error handling
config = ProcessingConfig(
    error_handling="graceful",  # Options: strict, graceful, permissive
    enable_detailed_logging=True
)
parser = EmailParser(config)

# Process with exception handling
try:
    result = parser.process_email("problematic_email.eml")
except MIMEParsingError as e:
    print(f"MIME parsing error: {e}")
except PDFConversionError as e:
    print(f"PDF conversion error: {e}")
    # Access partial results if available
    if e.partial_result:
        print(f"Partial extraction completed")
except OCRError as e:
    print(f"OCR processing error: {e}")
```

## Performance Tuning

Optimize performance for your specific environment:

```python
from email_parser import EmailParser, PerformanceConfig

# Configure performance settings
perf_config = PerformanceConfig(
    enable_caching=True,
    cache_size=100,  # Number of parsed emails to cache
    pdf_cache_size=50,  # Cache for PDF conversions
    parallel_extraction=True,
    max_workers=4,
    chunk_size=1024 * 1024,  # 1MB chunks for processing
    use_memory_mapping=True,  # For large files
    api_connection_pooling=True  # Reuse MistralAI connections
)

parser = EmailParser(performance_config=perf_config)
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/alexanderpresto/email-parser.git
cd email-parser

# Create development environment with virtual environment
python -m venv email-parser-env
source email-parser-env/bin/activate  # On Windows: .\email-parser-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run the full test suite
pytest

# Run with coverage
pytest --cov=email_parser

# Run specific test categories
pytest tests/test_mime_parsing.py
pytest tests/test_security.py
pytest tests/test_pdf_converter.py  # PDF conversion tests
```

### Code Quality Checks

```bash
# Format code with Black
black email_parser tests

# Sort imports
isort email_parser tests

# Run type checking
mypy email_parser

# Run security checks
bandit -r email_parser
```

## Documentation

Comprehensive documentation is available at: <https://email-parser.readthedocs.io/>

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html
```

## Acknowledgments

The PDF to Markdown conversion feature in this project was inspired by the excellent work in the [obsidian-marker](https://github.com/l3-n0x/obsidian-marker) project by [l3-n0x](https://github.com/l3-n0x). Their implementation of MistralAI OCR integration for PDF processing provided valuable insights and design patterns that influenced our approach.

While our implementation is independently developed and tailored for email processing workflows, we are grateful for the open-source contributions that helped shape our understanding of effective PDF to Markdown conversion strategies.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

**Version 2.0.0** - Now with PDF to Markdown conversion!

This project is actively maintained and developed. For updates and roadmap information, please check our GitHub repository.

### Recent Updates

- v2.0.0 (2025-06-21): Added PDF to Markdown conversion using MistralAI OCR
- v1.1.0: Enhanced Excel conversion capabilities
- v1.0.0: Initial release with core email parsing features