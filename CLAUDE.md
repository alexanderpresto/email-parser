# Enterprise Document Processing System - Developer Instructions

**Project Instructions**: This file contains instructions for any developer or AI assistant working on the Enterprise Document Processing System.

## System Overview

The Enterprise Document Processing System is a comprehensive platform for converting PDF, DOCX, and Excel files into AI-ready formats. The system supports both email attachment processing and direct document conversion through multiple interfaces.

## Core Commands

```bash
# Interactive CLI mode (recommended)
python -m email_parser.cli.interactive

# Direct file conversion
python -m email_parser.cli.main convert --file document.pdf --output output/
python -m email_parser.cli.main convert-batch --directory docs/ --output output/

# Traditional email processing
python -m email_parser.cli.main process --input email.eml --output output/
```

## Library Dependencies

### Core Dependencies

- **mammoth** - DOCX to HTML conversion
- **mistralai** - PDF OCR API integration  
- **beautifulsoup4** - HTML parsing and manipulation
- **tiktoken** - Token counting for AI-ready chunking
- **python-docx** - DOCX metadata extraction
- **openpyxl** - Excel file processing
- **pillow** - Image handling and optimization
- **prompt_toolkit** - Interactive CLI interface


## Project Structure

```
email-parser/
├── email_parser/                    # Main package
│   ├── cli/                        # CLI interfaces
│   │   ├── main.py                # Traditional CLI
│   │   ├── interactive.py         # Interactive CLI mode
│   │   └── interactive_file.py    # File conversion interface
│   ├── converters/                 # Document converters
│   │   ├── pdf_converter.py       # PDF processing
│   │   ├── docx_converter.py      # DOCX processing  
│   │   └── excel_converter.py     # Excel processing
│   ├── core/                       # Core processing logic
│   ├── config/                     # Configuration system
│   ├── exceptions/                 # Custom exceptions
│   ├── security/                   # File validation
│   └── utils/                      # Utilities
├── config/                         # Configuration files
├── docs/                           # Documentation
├── tests/                          # Test suite
└── requirements.txt                # Dependencies
```

## Architecture

**Processing Flow**: Email → MIMEParser → ComponentExtractor → Converters → Output

**Core Components**:

- **EmailProcessor** - Main orchestrator for email processing
- **BaseConverter** - Abstract base for all document converters
- **PDFConverter** - PDF processing with MistralAI OCR
- **ExcelConverter** - Excel to CSV conversion
- **DocxConverter** - DOCX to Markdown conversion
- **InteractiveCLI** - User-friendly interactive interface
- **DirectFileConverter** - Standalone document processing

**Output Structure**:

```
output/
├── processed_text/              # Email text content
├── attachments/                 # Original attachments  
├── converted_excel/             # CSV conversions
├── converted_pdf/               # PDF markdown output
├── converted_docx/              # DOCX conversions
│   ├── document.md             # Main markdown
│   └── document_docx_output/   # Advanced features
│       ├── metadata.json
│       ├── styles.json
│       ├── images/             # Extracted images
│       └── chunks/             # AI-ready chunks
└── metadata.json               # Processing summary
```

## Setup Requirements

- **Python**: 3.12+ required
- **Dependencies**: Install from requirements.txt  
- **API Keys**: MistralAI API key for PDF processing
- **Testing**: pytest for test execution

## Usage Examples

### Interactive Mode (Recommended)

```bash
# Start interactive CLI with guided workflows
python -m email_parser.cli.interactive
```

Features:
- Content scanning with smart recommendations
- Processing profile selection
- Real-time progress tracking
- Batch processing support
- Configuration management

### Traditional CLI

```bash
# Basic email processing
python -m email_parser.cli.main process --input email.eml --output output/

# With specific conversions
python -m email_parser.cli.main process --input email.eml --output output/ --convert-pdf --convert-docx
```

### Direct File Conversion  

```bash
# Convert single file
python -m email_parser.cli.main convert --file document.pdf --output output/

# Batch convert directory
python -m email_parser.cli.main convert-batch --directory docs/ --output output/
```

## Key Features

**Document Processing**:
- PDF conversion with OCR (MistralAI integration)
- DOCX to Markdown with AI-ready chunking
- Excel to CSV conversion
- Image extraction and processing
- Metadata preservation

**User Interfaces**:
- Interactive CLI with guided workflows
- Traditional command-line interface  
- Processing profiles for different use cases
- Real-time progress tracking

**Advanced Features**:
- Batch processing capabilities
- Security validation and file scanning
- Error handling and recovery
- Performance optimization

## Processing Profiles

The system includes 5 built-in processing profiles:

1. **AI Processing** - Optimized for LLM consumption with chunking
2. **Document Archive** - Maximum fidelity preservation  
3. **Quick Conversion** - Fast basic text extraction
4. **Research Mode** - Comprehensive metadata extraction
5. **Batch Optimization** - Performance-tuned for multiple files

## Configuration

Key configuration options in `config/default.yaml`:

```yaml
processing:
  convert_pdf: true
  convert_excel: true
  convert_docx: true

security:
  max_attachment_size: 10000000  # 10MB
  
pdf_conversion:
  api_key_env: "MISTRALAI_API_KEY"
  extraction_mode: "all"  # text/images/all

docx_conversion:
  enable_chunking: true
  max_chunk_tokens: 2000
  extract_images: true
```

## Testing

```bash
# Run test suite
pytest

# Run with coverage
pytest --cov=email_parser

# Run specific test categories  
pytest tests/unit/
pytest tests/integration/
```

## Production Guidelines

1. **Dependencies**: Install all requirements from requirements.txt
2. **Security**: Validate inputs and protect API keys  
3. **Testing**: Run comprehensive test suite before deployment
4. **Monitoring**: Track performance metrics and error rates

## Technical Notes

### API Integration
- **MistralAI OCR**: Used for PDF text extraction
- **Configuration**: Set MISTRALAI_API_KEY environment variable
- **Cost**: Approximately $0.001 per PDF page

### Development Standards
- **Code Quality**: Black formatting, type hints, comprehensive testing
- **Security**: Input validation, API key protection, file scanning
- **Performance**: Optimized for large file processing with progress tracking

---
*Enterprise Document Processing System - Transform documents into AI-ready formats*
