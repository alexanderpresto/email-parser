# Enterprise Email Parser

[![Python Version](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/python/mypy)
[![Development Status](https://img.shields.io/badge/status-production%20ready-green.svg)](https://github.com/alexanderpresto/email-parser)

An enterprise-grade email processing system with robust MIME parsing, security features, PDF/DOCX to Markdown conversion, and an intuitive Interactive CLI Mode for guided email processing workflows.

## 🚀 Production Status

**Current Version:** 2.4.0 (Phase 4.5 Interactive File Conversion - Day 7+ Testing & Documentation)  
**PDF Conversion Status:** ✅ **PRODUCTION READY** - MistralAI OCR Integration Complete  
**DOCX Conversion Status:** ✅ **PRODUCTION READY** - All Advanced Features Complete  
**Interactive CLI Status:** ⚠️ **FUNCTIONAL** - Phase 3.5 Complete, Unicode display issues on Windows  
**Direct File Conversion Status:** ✅ **PRODUCTION READY** - Phase 4 Complete & Tested (2025-07-14)  
**Interactive File Conversion Status:** 🎯 **FEATURE COMPLETE** - Phase 4.5 Implementation Complete, Testing Phase (2025-07-18)  
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

**✅ Phase 4.5 Feature Complete (Interactive File Conversion):**
- ✅ **Interactive File Converter** - Rich terminal UI with guided workflows (production ready)
- ✅ **File Conversion Profiles** - 5 built-in profiles with intelligent recommendations (production ready)
- ✅ **File Discovery Engine** - Intelligent document scanning with progress tracking (complete)
- ✅ **DirectFileConverter Integration** - Profile-based conversion mapping (complete)
- ✅ **Enhanced InteractiveCLI Integration** - Unified navigation and progress tracking (complete)
- ✅ **Navigation Context System** - Breadcrumbs and error recovery (complete)
- 🎯 **Final Testing & Documentation** - Quality assurance and merge preparation (in progress)

## Overview

This library provides a comprehensive solution for parsing and processing emails in enterprise environments with high volume requirements. It handles complex MIME structures, extracts all components (text, HTML, attachments, inline images), converts PDFs to searchable Markdown using MistralAI OCR, and ensures secure processing throughout.

### ✅ Production Features

- Complete MIME structure parsing and extraction
- ✅ **PDF to Markdown conversion with MistralAI OCR** - Production ready with full API integration
- ✅ **DOCX to Markdown conversion** - Complete mammoth library integration
- ✅ **AI-ready document chunking** - Token-based, semantic, and hybrid strategies
- ✅ **Enhanced DOCX metadata extraction** - Comprehensive document properties and analysis
- ✅ **Style preservation system** - CSS and JSON output with formatting preservation
- ✅ **Advanced image extraction** - Quality control and deduplication for DOCX files
- ✅ **Comments and revision tracking** extraction from Word documents
- 🎯 **Interactive File Conversion** - Rich UI for standalone document processing (Phase 4.5 - Day 3-4 implementation)
- 🎯 **Conversion Quality Analysis** - Validation and reporting with intelligent recommendations (Phase 4.5 development)
- Automatic Excel to CSV conversion capability
- Secure file handling with protection against common attack vectors
- Support for multiple encodings (UTF-8, UTF-16, ASCII, ISO-8859, Base64, etc.) with automatic encoding detection
- Comprehensive error handling and logging
- Complete type annotations and rigorous testing

### 🎯 Latest Enhancement (Phase 3.5 Complete)

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

### Interactive CLI Mode (Recommended) ✅ ENHANCED

The easiest way to use the Email Parser is through the Interactive CLI Mode with both email processing and file conversion capabilities:

```bash
# Start interactive mode
python -m email_parser.cli.interactive

# Main menu options:
# 1. Process Emails (Phase 3.5 - Production ready)
# 2. Convert Documents (Phase 4.5 - Active development)
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

**🎯 File Conversion Features (Phase 4.5 - Active Development):**
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

## Direct File Conversion ✅ **PRODUCTION READY** (Phase 4 Complete)

Convert documents directly without email processing:

```bash
# Convert a single file (Phase 4 - tested and working)
python -m email_parser.cli.main convert --file document.pdf --output converted/

# Convert single DOCX with all features
python -m email_parser.cli.main convert --file report.docx --output converted/

# Batch convert all supported files in directory
python -m email_parser.cli.main convert-batch --directory documents/ --output converted/

# Batch convert with pattern matching and recursive search
python -m email_parser.cli.main convert-batch --directory docs/ --output converted/ --pattern "*.pdf" --recursive

# Interactive conversion mode (Phase 4.5 - Active Development)
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

**Week 3 (Completed 2025-07-01):**

- ✅ Performance optimization for large document processing
- ✅ Enhanced error handling and graceful fallbacks
- ✅ Sliding window chunking algorithm implementation
- ✅ Performance profiler and benchmarking infrastructure
- ✅ Edge case testing and production resilience
- ✅ Documentation completion and merge preparation
- ✅ Comprehensive test coverage completion
- ✅ Documentation updates and merge preparation

### 📋 Phase 4: Unified Document Processing API (Next Development Phase)

- Unified API for all document types
- Additional file format support (PowerPoint, etc.)
- Enhanced batch processing optimization
- Advanced analytics and monitoring
- API and integration improvements

### ✅ Phase 3.5: Interactive CLI Mode (Complete - 2025-07-06)

- ✅ **Email Scanner Component** - Intelligent attachment detection and complexity analysis
- ✅ **Smart Recommendations Engine** - AI-powered processing suggestions based on content
- ✅ **Processing Profiles System** - Pre-configured settings (Quick, Comprehensive, AI-Ready, Archive, Dev)
- ✅ **Real-time Progress Tracking** - Rich terminal UI with resource monitoring
- ✅ **Interactive CLI Framework** - Intuitive guided workflows for single and batch processing
- ✅ **Configuration Management** - Profile creation, API setup, and preference persistence
- ✅ **Comprehensive Test Suite** - Unit and integration tests for all interactive components

### 📋 Phase 5: Advanced Content Analysis Features

- Natural language processing integration
- Sentiment analysis for emails
- Entity extraction and relationship mapping
- Advanced email categorization

### 📋 Phase 6: Production Deployment and Scaling

- Cloud deployment preparation
- Horizontal scaling architecture
- Advanced monitoring and alerting
- Enterprise integration features

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
2. **Instructions**: Follow project instructions in [CLAUDE.md](CLAUDE.md) and create personal configuration in `.claude/CLAUDE.md`
3. **Archival**: Archive existing files before modifications
4. **Testing**: Run tests before committing changes
5. **Documentation**: Update relevant documentation with changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

**Version 2.2.0** - All major features complete and production ready!

This project has successfully completed:
- ✅ Phase 1: PDF to Markdown conversion with MistralAI OCR
- ✅ Phase 2: DOCX to structured output with advanced features
- ✅ Phase 3.5: Interactive CLI Mode with guided workflows (Completed 2025-07-06)
- ✅ Phase 4: Direct File Conversion (Completed 2025-07-14)

### Version History

- v2.4.0 (2025-07-14): Phase 4.5 Interactive File Conversion - Day 3-4 implementation phase, Phase 4 complete
- v2.3.0 (2025-07-14): Phase 4 Direct File Conversion complete - standalone document processing
- v2.2.0 (2025-07-06): Phase 3.5 Interactive CLI Mode complete - guided workflows, smart recommendations, processing profiles
- v2.1.1 (2025-07-01): DOCX Phase 2 complete - AI chunking, metadata, styles, images, performance optimization
- v2.1.0 (2025-06-25): PDF converter API integration phase complete
- v2.0.0 (2025-06-22): PDF converter core infrastructure complete
- v1.1.0: Enhanced Excel conversion capabilities  
- v1.0.0: Initial release with core email parsing features

---

**Requirements:** Python 3.12.10+ with virtual environment support  
**Last Updated:** 2025-07-14  
**Current Status:** Phase 4.5 Active Development - Interactive File Conversion (Day 3-4 Implementation), Phase 4 Production Ready
