# Enterprise Email Parser

[![Python Version](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/python/mypy)
[![Development Status](https://img.shields.io/badge/status-active%20development-orange.svg)](https://github.com/alexanderpresto/email-parser)

An enterprise-grade email processing system with robust MIME parsing, security features, PDF to Markdown conversion, and performance optimization.

## 🚀 Development Status

**Current Version:** 2.1.0  
**PDF Conversion Status:** ✅ **Core Implementation Complete** (Phase 1, Week 1)  
**Next Milestone:** Integration & Testing (Phase 1, Week 2)

## Overview

This library provides a comprehensive solution for parsing and processing emails in enterprise environments with high volume requirements. It handles complex MIME structures, extracts all components (text, HTML, attachments, inline images), converts PDFs to searchable Markdown using MistralAI OCR, and ensures secure processing throughout.

### ✅ Implemented Features

- Complete MIME structure parsing and extraction
- ✅ **PDF to Markdown conversion core infrastructure** (NEW in v2.0)
- Automatic Excel to CSV conversion capability
- Secure file handling with protection against common attack vectors
- Support for multiple encodings (UTF-8, UTF-16, ASCII, ISO-8859, Base64, etc.) with automatic encoding detection
- Comprehensive error handling and logging
- Complete type annotations and rigorous testing

### 🔄 In Development

- **PDF to Markdown conversion API integration** (Phase 1, Week 2)
- High-performance batch processing with parallel PDF/Excel conversion
- Enhanced CLI with PDF options
- Performance benchmarks and optimization

## Installation

### Prerequisites

- Python 3.12.9 or higher
- Virtual environment (required for development)
- MistralAI API key (for PDF conversion)

### Development Setup

**⚠️ Important:** Always use the virtual environment for development work.

```bash
# Clone the repository
git clone https://github.com/alexanderpresto/email-parser.git
cd email-parser

# Create virtual environment (if not exists)
python -m venv email-parser-env

# Activate the virtual environment (REQUIRED for all development)
# Windows PowerShell
.\email-parser-env\Scripts\Activate.ps1

# Linux/Mac/WSL2
source email-parser-env/bin/activate

# Verify virtual environment is active
python -c "import sys; print('Virtual env active:', 'email-parser-env' in sys.prefix)"

# Install dependencies (MistralAI SDK already included)
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### MistralAI API Setup

For PDF to Markdown conversion, you'll need a MistralAI API key:

```bash
# Set as environment variable
export MISTRALAI_API_KEY="your-api-key-here"  # Linux/Mac
set MISTRALAI_API_KEY=your-api-key-here       # Windows PowerShell
```

## Quick Start

### Basic Email Processing

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
```

### PDF Conversion (Development Preview)

**Note:** PDF conversion is currently in active development. Core infrastructure is complete.

```python
# PDF conversion will be available as:
from email_parser.converters import PDFConverter
from email_parser.exceptions import ConversionError, APIError

# Initialize PDF converter
pdf_converter = PDFConverter(config={
    'extraction_mode': 'all',  # 'text', 'images', or 'all'
    'image_settings': {
        'limit': 10,
        'min_size': 100
    }
})

# Convert PDF to Markdown (once API integration is complete)
try:
    markdown_path = pdf_converter.convert(pdf_path)
    print(f"PDF converted to: {markdown_path}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
```

## Architecture

### Converter Framework

The new converter architecture provides a robust foundation for file conversions:

```python
from email_parser.converters import BaseConverter, PDFConverter

# All converters inherit from BaseConverter
class CustomConverter(BaseConverter):
    @property
    def supported_extensions(self):
        return ['.custom']
    
    @property 
    def supported_mime_types(self):
        return ['application/custom']
    
    def convert(self, input_path, output_path=None):
        # Implementation here
        pass
```

### Exception Hierarchy

Comprehensive exception handling for conversion operations:

```python
from email_parser.exceptions import (
    ConversionError,          # Base conversion exception
    UnsupportedFormatError,   # Unsupported file format
    FileSizeError,           # File too large
    APIError,                # External API failures
    ConfigurationError,      # Invalid configuration
    ProcessingError          # File processing errors
)
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

## Development Status & Roadmap

### ✅ Phase 1, Week 1 (Complete - 2025-06-22)

- ✅ **Virtual environment setup and activation**
- ✅ **MistralAI SDK dependency integration** (v1.8.2)
- ✅ **BaseConverter abstract class** (242 lines)
  - File validation and size limits
  - Extension and MIME type checking
  - Output path generation with timestamps
  - Comprehensive logging and metadata
- ✅ **PDFConverter implementation** (473 lines)
  - MistralAI Pixtral-12b-2409 integration
  - Multiple extraction modes (text, images, all)
  - Retry logic with exponential backoff
  - Configurable image processing
- ✅ **Exception framework** (67 lines)
  - Custom exception hierarchy
  - Specific error types for different scenarios
- ✅ **Module integration and import validation**

### 🔄 Phase 1, Week 2 (Current Priority - 2025-06-23 to 2025-06-29)

- 📋 **API connectivity testing** (requires API key)
- 📋 **Configuration file updates** (`config/default.yaml`)
- 📋 **Test structure creation**
  - Unit tests for PDF converter
  - Integration tests for email processing
- 📋 **ExcelConverter refactoring** to use BaseConverter
- 📋 **Technical design documentation**

### 📋 Phase 2: Core Implementation (Weeks 3-6)

- PDF OCR processing implementation
- Image extraction and processing
- Email processor integration
- Summary generation with PDF content

### 📋 Phase 3: Advanced Features (Weeks 7-9)

- Batch processing enhancements
- CLI enhancements with PDF options
- Performance optimization
- Security validation

### 📋 Phase 4: Testing & Quality Assurance (Weeks 10-12)

- Comprehensive test suite
- Performance benchmarking
- Integration testing
- Quality assurance

## Output Structure

The library creates a structured output with the following organization:

```
output/
├── processed_text/
│   └── email_123abc.txt
├── attachments/
│   ├── 20250622_123abc_report.pdf
│   └── 20250622_456def_presentation.pptx
├── inline_images/
│   ├── 20250622_123abc_image1.png
│   └── 20250622_456def_image2.jpg
├── converted_excel/
│   ├── 20250622_123abc_sheet1.csv
│   └── 20250622_123abc_sheet2.csv
├── converted_pdf/                    # 🆕 PDF conversions
│   ├── 20250622_123abc_report.md
│   └── 20250622_123abc_report_images/
│       ├── img_001.png
│       └── img_002.png
└── metadata.json
```

## Development

### Setting Up Development Environment

**⚠️ Virtual Environment Required**: Always activate the virtual environment before development:

```bash
# Navigate to project directory
cd /path/to/email-parser

# Activate virtual environment (REQUIRED for all Python work)
# Windows PowerShell
.\email-parser-env\Scripts\Activate.ps1

# Linux/Mac/WSL2
source email-parser-env/bin/activate

# Verify activation
python -c "import sys; print('Virtual env active:', 'email-parser-env' in sys.prefix)"

# Install development dependencies
pip install -r requirements.txt
```

### Running Tests

**⚠️ Virtual Environment Required**: Always activate before running tests:

```bash
# Activate virtual environment first
# Windows PowerShell
.\email-parser-env\Scripts\Activate.ps1

# Linux/Mac/WSL2  
source email-parser-env/bin/activate

# Run the full test suite
pytest

# Run with coverage
pytest --cov=email_parser

# Run specific test categories
pytest tests/test_mime_parsing.py
pytest tests/test_security.py
# pytest tests/test_pdf_converter.py  # Coming in Phase 1, Week 2
```

### Code Quality Checks

**⚠️ Virtual Environment Required**: Always activate before running quality checks:

```bash
# Activate virtual environment first
# Windows PowerShell
.\email-parser-env\Scripts\Activate.ps1

# Linux/Mac/WSL2
source email-parser-env/bin/activate

# Format code with Black
black email_parser tests

# Sort imports
isort email_parser tests

# Run type checking
mypy email_parser

# Run security checks
bandit -r email_parser
```

### Import Validation

Test that new components import correctly:

```bash
# Test converter imports
python -c "from email_parser.converters import BaseConverter, PDFConverter; print('Converter imports successful')"

# Test exception imports
python -c "from email_parser.exceptions import ConversionError, APIError; print('Exception imports successful')"
```

## Recent Development Activity

### 2025-06-22 Implementation Summary

**Files Created:**
- `email_parser/converters/base_converter.py` - Abstract converter framework
- `email_parser/converters/pdf_converter.py` - MistralAI PDF converter implementation  
- `email_parser/exceptions/converter_exceptions.py` - Conversion exception hierarchy

**Files Updated:**
- `email_parser/converters/__init__.py` - Added new converter imports
- `email_parser/exceptions/__init__.py` - Added exception imports

**Dependencies:**
- `mistralai>=1.5.2` - MistralAI SDK for OCR functionality

**Technical Achievements:**
- Complete converter architecture with abstract base class
- Comprehensive error handling and retry logic
- Configurable extraction modes and image processing
- Proper virtual environment integration
- Import validation and module structure

## Acknowledgments

The PDF to Markdown conversion feature in this project was inspired by the excellent work in the [obsidian-marker](https://github.com/l3-n0x/obsidian-marker) project by [l3-n0x](https://github.com/l3-n0x). Their implementation of MistralAI OCR integration for PDF processing provided valuable insights and design patterns that influenced our approach.

While our implementation is independently developed and tailored for email processing workflows, we are grateful for the open-source contributions that helped shape our understanding of effective PDF to Markdown conversion strategies.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. **Environment**: Always activate virtual environment before development
2. **Archival**: Archive existing files before modifications (see `project-instructions.md`)
3. **Testing**: Run tests before committing changes
4. **Documentation**: Update relevant documentation with changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

**Version 2.0.0-dev** - PDF conversion core infrastructure complete!

This project is in active development with focus on PDF to Markdown conversion capabilities. Current development follows a detailed 16-week project plan with defined milestones and deliverables.

### Version History

- v2.0.0-dev (2025-06-22): PDF converter core infrastructure complete
- v1.1.0: Enhanced Excel conversion capabilities  
- v1.0.0: Initial release with core email parsing features

---

**Development Environment:** Windows 11 Pro with Python 3.12.9  
**Last Updated:** 2025-06-22  
**Current Phase:** Phase 1, Week 2 - Core Architecture Design
