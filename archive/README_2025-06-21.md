# Enterprise Email Parser

[![Python Version](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/python/mypy)

An enterprise-grade email processing system with robust MIME parsing, security features, and performance optimization.

## Overview

This library provides a comprehensive solution for parsing and processing emails in enterprise environments with high volume requirements. It handles complex MIME structures, extracts all components (text, HTML, attachments, inline images), and ensures secure processing throughout.

Key features include:

- Complete MIME structure parsing and extraction
- Secure file handling with protection against common attack vectors
- Automatic Excel to CSV conversion capability
- Support for multiple encodings (UTF-8, UTF-16, ASCII, ISO-8859, Base64, etc.) with automatic encoding detection
- High-performance batch processing
- Comprehensive error handling and logging
- Complete type annotations and rigorous testing

## Installation

### Prerequisites

- Python 3.12.9 or higher
- Anaconda distribution (recommended)

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
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

```python
from email_parser import EmailParser, ProcessingConfig

# Configure the parser
config = ProcessingConfig(
    output_directory="output/",
    convert_excel=True,
    max_attachment_size=10_000_000,  # 10MB
    batch_size=100
)

# Create parser instance
parser = EmailParser(config)

# Process a single email
result = parser.process_email("path/to/email.eml")
print(f"Processed email with {len(result.attachments)} attachments")

# Process a batch of emails
batch_results = parser.process_batch(["email1.eml", "email2.eml", "email3.eml"])
print(f"Processed {len(batch_results)} emails")
```

## Core Features

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

```python
# Configure security settings
config = ProcessingConfig(
    max_attachment_size=5_000_000,  # 5MB
    allowed_extensions=[".pdf", ".docx", ".xlsx", ".txt", ".jpg", ".png"],
    enable_malware_scanning=True
)
parser = EmailParser(config)
```

### Batch Processing

Process multiple emails efficiently:

```python
# Configure batch settings
config = ProcessingConfig(
    batch_size=100,
    max_workers=4,
    enable_progress_bar=True
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
└── metadata.json
```

The `metadata.json` file contains comprehensive information about the processed email, including:

- Email headers
- Processing timestamp
- List of extracted components with paths
- Mapping of original filenames to unique filenames
- Positional information for each extraction
- Excel to CSV conversion mappings
- Processing statistics

## Advanced Usage

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
from email_parser.exceptions import MIMEParsingError, AttachmentExtractionError

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
except AttachmentExtractionError as e:
    print(f"Attachment extraction error: {e}")
    # Access partial results if available
    if e.partial_result:
        print(f"Partial extraction completed with {len(e.partial_result.attachments)} attachments")
```

## Performance Tuning

Optimize performance for your specific environment:

```python
from email_parser import EmailParser, PerformanceConfig

# Configure performance settings
perf_config = PerformanceConfig(
    enable_caching=True,
    cache_size=100,  # Number of parsed emails to cache
    parallel_extraction=True,
    max_workers=4,
    chunk_size=1024 * 1024,  # 1MB chunks for processing
    use_memory_mapping=True  # For large files
)

parser = EmailParser(performance_config=perf_config)
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/alexanderpresto/email-parser.git
cd email-parser

# Create development environment with Anaconda
conda env create -f environment.yml
conda activate email-parser

# Or use pip with a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

This project is actively maintained and developed. For updates and roadmap information, please check our GitHub repository.
