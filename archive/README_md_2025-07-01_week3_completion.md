# Enterprise Email Parser

[![Python Version](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/python/mypy)
[![Development Status](https://img.shields.io/badge/status-active%20development-orange.svg)](https://github.com/alexanderpresto/email-parser)

An enterprise-grade email processing system with robust MIME parsing, security features, PDF to Markdown conversion, and performance optimization.

## 🚀 Development Status

**Current Version:** 2.2.0-dev (feature/docx-converter branch)  
**PDF Conversion Status:** ✅ **WORKING** - MistralAI OCR Integration Complete  
**DOCX Conversion Status:** ✅ **WEEK 2 COMPLETE** - Advanced Features Implemented  
**Next Milestone:** Week 3 - Performance Optimization & Polish

### 🆕 Feature Branch Notice

This branch (`feature/docx-converter`) includes completed implementation of:
- ✅ DOCX to Markdown conversion using mammoth library
- ✅ AI-ready document chunking for LLM processing (Week 2)
- ✅ Comprehensive metadata and style extraction (Week 2)
- ✅ Embedded image extraction from Word documents (Week 2)

## Overview

This library provides a comprehensive solution for parsing and processing emails in enterprise environments with high volume requirements. It handles complex MIME structures, extracts all components (text, HTML, attachments, inline images), converts PDFs to searchable Markdown using MistralAI OCR, and ensures secure processing throughout.

### ✅ Implemented Features

- Complete MIME structure parsing and extraction
- ✅ **PDF to Markdown conversion with MistralAI OCR** (v2.1.0)
- ✅ **Working PDF attachments processing** - Extracts text and images from PDFs
- ✅ **DOCX to Markdown conversion** with mammoth library (v2.2.0-dev)
- ✅ **AI-ready document chunking** - Token-based, semantic, and hybrid strategies (Week 2)
- ✅ **Enhanced DOCX metadata extraction** - Comprehensive document properties and analysis (Week 2)
- ✅ **Style preservation system** - CSS and JSON output with formatting preservation (Week 2)
- ✅ **Advanced image extraction** - Quality control and deduplication for DOCX files (Week 2)
- ✅ **Comments and revision tracking** extraction from Word documents (Week 2)
- Automatic Excel to CSV conversion capability
- Secure file handling with protection against common attack vectors
- Support for multiple encodings (UTF-8, UTF-16, ASCII, ISO-8859, Base64, etc.) with automatic encoding detection
- Comprehensive error handling and logging
- Complete type annotations and rigorous testing

### 🔄 Week 3 Development (Current)

- **Performance optimization** for large document processing
- **Enhanced error handling** and graceful fallbacks
- **Comprehensive test coverage** for all Week 2 features
- **Documentation completion** and merge preparation

### 📋 Planned Features

- High-performance batch processing with parallel PDF/Excel/DOCX conversion
- Performance benchmarks and optimization
- Enhanced error reporting and monitoring
- Additional output format options

## Installation

### Prerequisites

- Python 3.12.9 or higher
- Virtual environment (required for development)
- MistralAI API key (for PDF conversion)

### Development Setup

**🚨 CRITICAL:** Virtual environment activation is MANDATORY for all Python development work.

```bash
# Clone the repository
git clone https://github.com/alexanderpresto/email-parser.git
cd email-parser

# STEP 1: Create virtual environment (if not exists)
python -m venv email-parser-env

# STEP 2: Activate the virtual environment (REQUIRED - Never skip this!)
# Windows PowerShell
.\email-parser-env\Scripts\Activate.ps1

# Linux/Mac/WSL2
source email-parser-env/bin/activate

# STEP 3: Verify virtual environment is active (Must show True)
python -c "import sys; print('Virtual env active:', 'email-parser-env' in sys.prefix)"

# STEP 4: Install dependencies (MistralAI SDK already included)
pip install -r requirements.txt

# STEP 5: Install in development mode
pip install -e .
```

**⚠️ WARNING:** If virtual environment is not activated, the project will not work correctly.

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

### PDF Conversion (✅ Working)

**Status:** PDF conversion is fully implemented and working with MistralAI OCR integration.

```python
from email_parser.converters import PDFConverter
from email_parser.exceptions import ConversionError, APIError
from pathlib import Path

# Initialize PDF converter
pdf_converter = PDFConverter(config={
    'extraction_mode': 'all',  # 'text', 'images', or 'all'
    'image_settings': {
        'limit': 10,
        'min_size': 100,
        'save_images': True
    }
})

# Convert PDF to Markdown
try:
    result = pdf_converter.convert(
        input_path=Path("document.pdf"),
        output_dir=Path("output/")
    )
    print(f"✅ PDF converted successfully!")
    print(f"📄 Markdown file: {result['output_file']}")
    print(f"🖼️  Images extracted: {result['image_count']}")
    print(f"⏱️  Duration: {result['duration']:.2f}s")
except ConversionError as e:
    print(f"❌ Conversion failed: {e}")
except APIError as e:
    print(f"❌ API error: {e}")
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

## CLI Examples

The email parser provides comprehensive command-line options for processing emails:

```bash
# Basic email processing
python -m email_parser process --input email.eml --output output/

# With Excel and PDF conversions
python -m email_parser process --input email.eml --output output/ --convert-excel --convert-pdf --pdf-mode all

# Batch processing with conversions
python -m email_parser batch --input emails/ --output output/ --convert-pdf

# Custom PDF extraction mode
python -m email_parser process --input email.eml --output output/ --convert-pdf --pdf-mode text  # Text only
python -m email_parser process --input email.eml --output output/ --convert-pdf --pdf-mode images  # Images only
python -m email_parser process --input email.eml --output output/ --convert-pdf --pdf-mode all  # Everything (default)

# DOCX conversion with Week 2 features
python -m email_parser process --input email.eml --output output/ --convert-docx --docx-chunking --docx-images

# DOCX with all Week 2 options
python -m email_parser process --input email.eml --output output/ --convert-docx \
  --docx-images --docx-metadata --docx-chunk-size 2000 --docx-styles --docx-comments
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

### ✅ Phase 2: DOCX Converter Integration (2025-06-28 to 2025-07-19)

**Week 1 (Completed 2025-07-05):**
- ✅ Core DocxConverter class implementation
- ✅ Basic text extraction working
- ✅ Configuration integration complete
- ✅ Unit tests passing

**Week 2 (Completed 2025-07-12):**
- ✅ AI-ready chunking system (token-based, semantic, hybrid strategies)
- ✅ Enhanced metadata extraction with comprehensive document analysis
- ✅ Style preservation system with CSS and JSON output
- ✅ Advanced image extraction with quality control and deduplication
- ✅ Integration tests covering all Week 2 features

**Week 3 (Current - by 2025-07-19):**
- 🔄 Performance optimization for large document processing
- 🔄 Enhanced error handling and graceful fallbacks
- 🔄 Comprehensive test coverage completion
- 🔄 Documentation updates and merge preparation

### 📋 Phase 3: DOCX Optimization (Weeks 13-15)

- Performance optimization for large document processing
- Enhanced error handling and graceful fallbacks
- Comprehensive test coverage completion
- Documentation updates and merge preparation

### 📋 Phase 3.5: Interactive CLI Mode (3 weeks)

- Intelligent email content scanning
- Interactive processing options with smart recommendations
- Progress indicators and configuration profiles
- Single-command operation with progressive disclosure

### 📋 Phase 4: Production Readiness (Weeks 16-19)

- Batch processing optimization
- Performance benchmarking
- Security validation
- Production deployment preparation

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
├── converted_pdf/                    # PDF conversions
│   ├── 20250622_123abc_report.md
│   └── 20250622_123abc_report_images/
│       ├── img_001.png
│       └── img_002.png
├── converted_docx/                   # ✅ DOCX conversions (Week 2)
│   ├── 20250630_789ghi_document.md
│   └── 20250630_789ghi_document_docx_output/
│       ├── conversion_manifest.json
│       ├── metadata.json
│       ├── styles.json
│       ├── images/
│       │   ├── image_001.png
│       │   └── image_manifest.json
│       └── chunks/
│           ├── chunk_manifest.json
│           ├── chunk_001.md
│           └── chunk_002.md
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

**Version 2.2.0-dev** - DOCX Week 2 features complete!

This project is in active development with focus on comprehensive DOCX conversion capabilities. Current development follows a structured 3-week DOCX integration plan with Week 2 advanced features now complete.

### Version History

- v2.2.0-dev (2025-06-30): DOCX Week 2 features complete - AI chunking, metadata, styles, images
- v2.1.0 (2025-06-25): PDF converter API integration phase complete
- v2.0.0 (2025-06-22): PDF converter core infrastructure complete
- v1.1.0: Enhanced Excel conversion capabilities  
- v1.0.0: Initial release with core email parsing features

---

**Development Environment:** Windows 11 Pro with Python 3.12.9  
**Last Updated:** 2025-06-30  
**Current Phase:** Phase 2, Week 3 - DOCX Performance Optimization & Polish
