# Enterprise Email Parser

[![Python Version](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/python/mypy)
[![Development Status](https://img.shields.io/badge/status-production%20ready-green.svg)](https://github.com/alexanderpresto/email-parser)

An enterprise-grade email processing system with robust MIME parsing, security features, PDF/DOCX to Markdown conversion, and an intuitive Interactive CLI Mode for guided email processing workflows.

## 🚀 Production Status

**Current Version:** 2.4.0
**PDF Conversion Status:** ✅ **PRODUCTION READY** - MistralAI OCR Integration Complete
**DOCX Conversion Status:** ✅ **PRODUCTION READY** - All Advanced Features Complete
**Interactive CLI Status:** ✅ **PRODUCTION READY** - Feature Complete with minor display issues on Windows
**Direct File Conversion Status:** ✅ **PRODUCTION READY** - Feature Complete & Tested
**Interactive File Conversion Status:** ✅ **PRODUCTION READY** - Implementation Complete
**Performance Status:** ✅ **OPTIMIZED** - Benchmarked & Production Tested

### ✅ Production Ready Features

Production ready features and active development:

**✅ Production Ready Features:**

- ✅ **Interactive CLI Mode** - Intuitive guided email processing (Note: Unicode display issues on Windows)
- ✅ **Direct File Conversion** - Standalone document processing without email context (Phase 4 complete & tested)
- ✅ DOCX to Markdown conversion using mammoth library
- ✅ AI-ready document chunking for LLM processing
- ✅ Comprehensive metadata and style extraction
- ✅ Embedded image extraction from Word documents
- ✅ Automatic file type detection and batch processing
- ✅ Performance optimization and benchmarking
- ✅ Edge case handling and error resilience
- ✅ Production-ready configuration and monitoring

**✅ Interactive File Conversion Features:**

- ✅ **Interactive File Converter** - Rich terminal UI with guided workflows
- ✅ **File Conversion Profiles** - 5 built-in profiles with intelligent recommendations
- ✅ **File Discovery Engine** - Intelligent document scanning with progress tracking
- ✅ **DirectFileConverter Integration** - Profile-based conversion mapping
- ✅ **Enhanced InteractiveCLI Integration** - Unified navigation and progress tracking
- ✅ **Navigation Context System** - Breadcrumbs and error recovery

## Overview

This library provides a comprehensive solution for parsing and processing emails in enterprise environments with high volume requirements. It handles complex MIME structures, extracts all components (text, HTML, attachments, inline images), converts PDFs to searchable Markdown using MistralAI OCR, and ensures secure processing throughout.

### 📦 Windows Executable Available

For users who prefer not to install Python, a standalone Windows executable is available. The executable includes all dependencies and can be run without any installation.

### ✅ Production Features

- Complete MIME structure parsing and extraction
- ✅ **PDF to Markdown conversion with MistralAI OCR** - Production ready with full API integration
- ✅ **DOCX to Markdown conversion** - Complete mammoth library integration
- ✅ **AI-ready document chunking** - Token-based, semantic, and hybrid strategies
- ✅ **Enhanced DOCX metadata extraction** - Comprehensive document properties and analysis
- ✅ **Style preservation system** - CSS and JSON output with formatting preservation
- ✅ **Advanced image extraction** - Quality control and deduplication for DOCX files
- ✅ **Comments and revision tracking** extraction from Word documents
- ✅ **Interactive File Conversion** - Rich UI for standalone document processing
- ✅ **Conversion Quality Analysis** - Validation and reporting with intelligent recommendations
- Automatic Excel to CSV conversion capability
- Secure file handling with protection against common attack vectors
- Support for multiple encodings (UTF-8, UTF-16, ASCII, ISO-8859, Base64, etc.) with automatic encoding detection
- Comprehensive error handling and logging
- Complete type annotations and rigorous testing

### 🎯 Latest Enhancements

- ✅ **Interactive CLI mode** with intuitive guided workflows
- ✅ **Email content scanning** with smart recommendations and complexity analysis
- ✅ **Processing profiles system** with 5 built-in profiles (Quick, Comprehensive, AI-Ready, Archive, Dev)
- ✅ **Real-time progress tracking** with beautiful terminal UI and fallback modes
- ✅ **Batch processing support** with guided workflow and progress indicators
- ✅ **Configuration management** with preferences persistence and API setup

## Installation

### Prerequisites

- Python 3.12.10 or higher (verified working)
- Virtual environment (recommended for development)
- MistralAI API key (for PDF conversion)

### 📋 Development Instructions

**IMPORTANT**: Set up your development environment:

#### Development Environment Instructions

- **See**: [CLAUDE.md](CLAUDE.md) - Project-specific development instructions
- **For AI assistants**: Create environment-specific instructions in `.claude/CLAUDE.md` (see `.claude/README.md` for setup)

### Development Setup

**🚨 CRITICAL:** Virtual environment activation is MANDATORY for all Python development work.

**Requirements:**

- Python 3.12.10 or higher (verified working)
- Virtual environment support (venv activation has known issues on this setup)

```bash
# Clone the repository
git clone https://github.com/alexanderpresto/email-parser.git
cd email-parser

# STEP 1: Create virtual environment (if not exists)
python -m venv email-parser-env

# STEP 2: Activate the virtual environment (REQUIRED - Never skip this!)
# Windows PowerShell
.\email-parser-env\Scripts\Activate.ps1

# Windows Git Bash
source email-parser-env/Scripts/activate

# Linux/Mac
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
# Set as permanent user environment variable
# Windows (via System Properties -> Environment Variables)
# Add MISTRALAI_API_KEY = your-api-key-here to User Variables

# Or via PowerShell (permanent)
[Environment]::SetEnvironmentVariable("MISTRALAI_API_KEY", "your-api-key-here", "User")

# Linux/Mac (add to ~/.bashrc or ~/.zshrc for permanence)
echo 'export MISTRALAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Temporary session (for testing)
export MISTRALAI_API_KEY="your-api-key-here"  # Linux/Mac/Git Bash
set MISTRALAI_API_KEY=your-api-key-here       # Windows CMD/PowerShell
```

## Quick Start

### Option 1: Using Windows Executable (No Installation Required)

1. Download the latest release (when available)
2. Extract the `email-parser-windows.zip` file
3. Run `email-parser.exe` from the extracted folder

```bash
# Interactive mode
email-parser.exe

# Convert a single file
email-parser.exe convert --file document.pdf --output output/

# Process email with attachments
email-parser.exe process --input email.eml --output output/
```

**Note:** Set `MISTRALAI_API_KEY` environment variable for PDF processing.

### Option 2: Interactive CLI Mode (Python Installation) ✅ ENHANCED

The easiest way to use the Email Parser is through the Interactive CLI Mode with both email processing and file conversion capabilities:

```bash
# Start interactive mode
python -m email_parser.cli.interactive

# Main menu options:
# 1. Process Emails
# 2. Convert Documents
# 3. Batch Operations
# 4. Settings & Configuration
```

**Email Processing Features (Production Ready):**

- Email content scanning with smart recommendations
- Processing profile selection (Quick, Comprehensive, AI-Ready, Archive, Dev)
- Real-time progress tracking with beautiful UI
- Batch processing support with guided workflow
- Configuration management and API setup
- Preferences persistence across sessions

**🎯 File Conversion Features:**

```bash
# Interactive file conversion workflow
python -m email_parser.cli.interactive
# Select "2. Convert Documents"

# Features include:
# - Directory scanning with intelligent file discovery
# - 5 built-in conversion profiles (AI Processing, Document Archive, etc.)
# - Interactive file selection with filtering
# - Real-time conversion progress with quality reporting
# - Support for PDF, DOCX, Excel files
# - Rich terminal UI with tables and recommendations
```

### Interactive File Conversion (NEW in v2.4.0)

Convert documents interactively with intelligent recommendations:

```bash
# Launch interactive mode and select "Convert Documents"
python -m email_parser.cli.interactive

# Features:
- **Smart File Discovery**: Automatically finds convertible documents
- **Conversion Profiles**: 5 pre-configured profiles for different use cases
- **Real-time Progress**: Beautiful UI with conversion status
- **Batch Operations**: Process multiple files with one command
```

#### Conversion Profiles

1. **AI Processing** - Optimized for LLM ingestion with smart chunking
2. **Document Archive** - Preserves maximum formatting and metadata
3. **Quick Conversion** - Fast basic text extraction
4. **Research Mode** - Comprehensive extraction with citations
5. **Batch Optimization** - Tuned for processing many files efficiently

### Traditional CLI Mode

```bash
# Basic email processing
python -m email_parser process --input email.eml --output output/

# With all conversions enabled
python -m email_parser process --input email.eml --output output/ \
    --convert-excel --convert-pdf --convert-docx \
    --docx-chunking --docx-images --docx-styles

# Batch processing
python -m email_parser batch --input emails/ --output output/ \
    --convert-pdf --convert-docx
```

## Direct File Conversion ✅ **PRODUCTION READY**

Convert documents directly without email processing:

```bash
# Convert a single file
python -m email_parser.cli.main convert --file document.pdf --output converted/

# Convert single DOCX with all features
python -m email_parser.cli.main convert --file report.docx --output converted/

# Batch convert all supported files in directory
python -m email_parser.cli.main convert-batch --directory documents/ --output converted/

# Batch convert with pattern matching and recursive search
python -m email_parser.cli.main convert-batch --directory docs/ --output converted/ --pattern "*.pdf" --recursive

# Interactive conversion mode
python -m email_parser.cli.interactive  # Select "2. Convert Documents" for interactive file conversion UI
# Features: file discovery, conversion profiles, progress tracking, quality reporting
```

### Supported Formats ✅ OPERATIONAL

- **PDF**: Converts to Markdown using MistralAI OCR with full feature support
- **DOCX**: Converts to Markdown with metadata, styling, AI-ready chunking, and image extraction
- **Excel (XLSX/XLS)**: Converts to CSV format with multi-sheet support
- **Automatic Detection**: File type automatically detected by MIME type and extension

### Programmatic Usage

For automation and scripting, you can use the Python API directly:

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

### 🎯 Interactive Mode (Recommended)

**NEW in v2.2.0**: Interactive mode provides an intuitive, guided experience with smart recommendations:

```bash
# Launch interactive mode
python -m email_parser --interactive
# or
python -m email_parser -i
```

**Interactive Mode Features:**

- 📧 **Email scanning** with attachment analysis
- 🤖 **Smart recommendations** based on content complexity
- 📋 **Processing profiles** (Quick, Comprehensive, AI-Ready, Archive)
- 📊 **Real-time progress** tracking with resource monitoring
- ⚙️ **Configuration management** and API setup assistance

**Prerequisites for Interactive Mode:**

```bash
pip install rich prompt-toolkit
```

### Traditional Command Line

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

# DOCX conversion with advanced features
python -m email_parser process --input email.eml --output output/ --convert-docx --docx-chunking --docx-images

# DOCX with all advanced options
python -m email_parser process --input email.eml --output output/ --convert-docx \
  --docx-images --docx-metadata --docx-chunk-size 2000 --docx-styles --docx-comments
```

## Features

### ✅ Core Features Implemented

**Email Processing:**

- Complete MIME structure parsing and extraction
- Secure file handling with protection against common attack vectors
- Support for multiple encodings with automatic encoding detection
- Comprehensive error handling and logging
- Complete type annotations and rigorous testing

**File Conversion:**

- PDF to Markdown conversion using MistralAI OCR
- DOCX to Markdown conversion with mammoth library integration
- Excel to CSV conversion with multi-sheet support
- AI-ready document chunking (token-based, semantic, and hybrid strategies)
- Enhanced metadata extraction with comprehensive document analysis
- Style preservation system with CSS and JSON output
- Advanced image extraction with quality control and deduplication

**Interactive CLI:**

- Email content scanning with smart recommendations
- Processing profiles system with 5 built-in profiles
- Real-time progress tracking with rich terminal UI
- Batch processing support with guided workflows
- Configuration management with preferences persistence
- Interactive file conversion with guided workflows

**Direct File Processing:**

- Standalone document processing without email context
- Automatic file type detection
- Batch conversion support
- Interactive file converter with rich UI
- File conversion profiles with intelligent recommendations

### 🔮 Future Enhancements

**Advanced Content Analysis:**

- Natural language processing integration
- Sentiment analysis for emails
- Entity extraction and relationship mapping
- Advanced email categorization

**Enterprise Features:**

- Cloud deployment capabilities
- Horizontal scaling architecture
- Advanced monitoring and alerting
- Enterprise integration APIs

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

### Building Windows Executable

To create a standalone Windows executable:

```bash
# Install build dependencies
pip install -r requirements-build.txt

# Build the executable
pyinstaller email_parser.spec
# Or use the batch script
build_exe.bat

# Find executable in dist/email-parser/
```

See [Building Executable Guide](docs/building-executable.md) for detailed instructions.

### Setting Up Development Environment

**⚠️ Virtual Environment Required**: Always activate the virtual environment before development:

```bash
# Navigate to project directory
cd /path/to/email-parser

# Activate virtual environment (REQUIRED for all Python work)
# Windows PowerShell
.\email-parser-env\Scripts\Activate.ps1

# Windows Git Bash
source email-parser-env/Scripts/activate

# Linux/Mac
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

# Windows Git Bash
source email-parser-env/Scripts/activate

# Linux/Mac
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

# Windows Git Bash
source email-parser-env/Scripts/activate

# Linux/Mac
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

## Technical Architecture

### Core Components

**Converter Framework:**

- `email_parser/converters/base_converter.py` - Abstract converter framework
- `email_parser/converters/pdf_converter.py` - MistralAI PDF converter implementation
- `email_parser/converters/docx_converter.py` - DOCX converter with advanced features
- `email_parser/converters/excel_converter.py` - Excel to CSV converter
- `email_parser/exceptions/converter_exceptions.py` - Conversion exception hierarchy

**Interactive CLI:**

- `email_parser/cli/interactive.py` - Main interactive CLI interface
- `email_parser/cli/interactive_file.py` - Interactive file conversion interface
- `email_parser/core/scanner.py` - Email content analysis
- `email_parser/config/profiles.py` - Processing profile management

**Core Processing:**

- `email_parser/core/email_processor.py` - Main email processing engine
- `email_parser/core/mime_parser.py` - MIME structure parsing
- `email_parser/security/file_validator.py` - Security validation
- `email_parser/utils/` - Utility modules for various functions

## Acknowledgments

The PDF to Markdown conversion feature in this project was inspired by the excellent work in the [obsidian-marker](https://github.com/l3-n0x/obsidian-marker) project by [l3-n0x](https://github.com/l3-n0x). Their implementation of MistralAI OCR integration for PDF processing provided valuable insights and design patterns that influenced our approach.

While our implementation is independently developed and tailored for email processing workflows, we are grateful for the open-source contributions that helped shape our understanding of effective PDF to Markdown conversion strategies.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. **Environment**: Always activate virtual environment before development
2. **Instructions**: Follow project instructions in [CLAUDE.md](CLAUDE.md) and create personal configuration in `.claude/personal.md`
3. **Archival**: Archive existing files before modifications
4. **Testing**: Run tests before committing changes
5. **Documentation**: Update relevant documentation with changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

**Version 2.4.0** - Production ready email parser with comprehensive file conversion capabilities

This project features:

- ✅ PDF to Markdown conversion with MistralAI OCR
- ✅ DOCX to structured output with advanced features
- ✅ Interactive CLI Mode with guided workflows
- ✅ Direct File Conversion capabilities
- ✅ Interactive File Conversion interface

### Version History

- v2.4.0: Interactive File Conversion complete - unified document processing interface
- v2.3.0: Direct File Conversion complete - standalone document processing
- v2.2.0: Interactive CLI Mode complete - guided workflows and smart recommendations
- v2.1.1: DOCX converter complete - AI chunking, metadata, styles, and images
- v2.1.0: PDF converter integration complete
- v2.0.0: PDF converter infrastructure complete
- v1.1.0: Enhanced Excel conversion capabilities
- v1.0.0: Initial release with core email parsing features

---

**Requirements:** Python 3.12+ with virtual environment support
**Status:** Production Ready
