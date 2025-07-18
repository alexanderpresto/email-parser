# CLAUDE.md - Email Parser Project Instructions

This file provides comprehensive guidance for working with the Email Parser project in both Claude Desktop and Claude Code (claude.ai/code). It serves as the single source of truth for project instructions.

**Compatibility**: This document is designed to be:

- Copy-pasted as Claude Project instructions
- Used directly by Claude Code when working in the repository
- Referenced by Claude Desktop for comprehensive project context

## Platform Context

- **Claude Desktop**: Running on Windows 11 Pro (native Windows paths and PowerShell commands)
- **Claude Code**: Running on Ubuntu via WSL2 (accessing Windows D: drive through `/mnt/d/`)
- **Desktop-commander**: Works in both environments but paths need adjustment
- **Project Location**: Stored on Windows D: drive, accessible from both environments

Throughout this document:

- Windows-specific commands are marked for Claude Desktop
- Linux/WSL2 commands are marked for Claude Code
- Platform-agnostic commands work in both environments

## Project Overview

The Email Parser is an enterprise-grade email processing system designed to extract, organize, and convert email content into formats that can be analyzed by Claude and other AI tools. It handles complex MIME structures, extracts attachments, processes inline images, converts Excel files to CSV format, and includes advanced PDF to Markdown conversion using MistralAI OCR capabilities.

## Project Initialization

**CRITICAL**: Before starting any work on this project:

```
IF get_current_project() ≠ "dev":
  → switch_project("dev")
  → IF switch fails → Request user intervention
```

Always ensure you're in the correct project context before making changes.

## Essential Commands (Quick Reference)

### Development Environment Setup

**Virtual Environment** (REQUIRED): Always activate before development:

```bash
# Windows PowerShell (Claude Desktop on Windows 11 Pro)
cd "D:\Users\alexp\dev\email-parser"
.\email-parser-env\Scripts\Activate.ps1

# Linux/WSL2 (Claude Code on Ubuntu)
cd /mnt/d/Users/alexp/dev/email-parser
source email-parser-env/bin/activate

# Verify activation (both platforms)
python -c "import sys; print('Virtual env active:', 'email-parser-env' in sys.prefix)"
```

**Working Directory**:

- Windows: `D:\Users\alexp\dev\email-parser`
- WSL2: `/mnt/d/Users/alexp/dev/email-parser`

**Archive Directory**:

- Windows: `D:\Users\alexp\dev\email-parser\archive`
- WSL2: `/mnt/d/Users/alexp/dev/email-parser/archive`

### Testing

```bash
# Run full test suite
pytest

# Run with coverage
pytest --cov=email_parser

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Test PDF-specific functionality
pytest tests/unit/test_pdf_converter.py
pytest tests/integration/test_pdf_integration.py
```

### Code Quality

```bash
# Format code
black email_parser tests

# Sort imports
isort email_parser tests

# Type checking
mypy email_parser

# Security checks
bandit -r email_parser
```

### Development Validation

```bash
# Test package imports
python -c "from email_parser.converters import BaseConverter, PDFConverter; print('Imports successful')"

# Test main functionality
python -c "from email_parser import EmailProcessor, ProcessingConfig; print('Core imports successful')"

# Generate test data
python scripts/test_email_generator.py

# Run examples for manual testing
python examples/basic_parsing.py test_simple.eml
python examples/batch_processing.py test_emails/
```

## Environment Configuration

- **Python Virtual Environment**: `email-parser-env/` (activate before development)
- **MCP Tools**:
  - mcp-server-time (for accurate timestamps)
  - desktop-commander (for file operations)
  - basic-memory (for knowledge management)
- **Working Directory**: `D:\Users\alexp\dev\email-parser`
- **Archive Directory**: `D:\Users\alexp\dev\email-parser\archive`

### MistralAI API Setup (Required for PDF conversion)

```bash
# Windows PowerShell
$env:MISTRALAI_API_KEY = "your-api-key-here"

# Linux/Mac
export MISTRALAI_API_KEY="your-api-key-here"
```

**Note on Path Separators**:

- Windows (Claude Desktop): Can use either `\` or `/` in paths
- Linux/WSL2 (Claude Code): Always use `/` in paths
- Desktop-commander accepts both formats

**WSL2 Mount Point Access**:

- The project lives on Windows D: drive and is accessed from WSL2 via `/mnt/d/`
- This ensures both environments work with the same files
- No synchronization needed between Windows and WSL2

## Project Folder Structure

```
email-parser/
├── .cspell.json               # Spell checker configuration
├── .github/                   # GitHub workflows and templates
├── .gitignore                 # Git ignore rules
├── archive/                   # Archived versions (gitignored)
│   ├── del_*                  # Deprecated files
│   └── *_YYYY-MM-DD.*         # Archived versions
├── benchmarks/                # Performance benchmarking scripts
├── config/                    # Configuration files
│   ├── default.yaml           # Default configuration
│   ├── README.md              # Config usage guide
│   └── local/                 # Local overrides (gitignored)
├── docs/                      # Documentation
│   ├── cli_examples.txt       # CLI usage examples
│   ├── index.md               # Documentation index
│   ├── requirements/          # Project requirements
│   │   ├── product_requirements_document.md
│   │   ├── project_plan_and_phasing.md
│   │   └── technical_specification_document.md
│   ├── specifications/        # Detailed specifications
│   └── specs/                 # Project specifications
├── email_parser/              # Main package
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # Main entry point
│   ├── cli.py                 # Command-line interface│   ├── converters/            # File converters
│   ├── core/                  # Core processing logic
│   ├── exceptions/            # Custom exceptions
│   ├── security/              # Security validators
│   └── utils/                 # Utility functions
├── examples/                  # Example scripts
│   ├── basic_parsing.py       # Simple parsing example
│   ├── batch_processing.py    # Batch processing example
│   └── excel_conversion.py    # Excel conversion example
├── scripts/                   # Utility scripts
│   ├── ascii_tree.py          # Directory tree generator
│   ├── README.md              # Scripts documentation
│   └── test_email_generator.py # Email test data generator
├── tests/                     # Test suite
│   ├── __init__.py            # Test initialization
│   ├── integration/           # Integration tests
│   ├── performance/           # Performance tests
│   ├── unit/                  # Unit tests
│   └── test_image.jpg         # Test resources
├── CLAUDE.md                 # This file (project instructions)
├── CONTRIBUTING.md           # Contribution guidelines
├── DEVELOPMENT_SETUP.md      # Virtual environment setup guide
├── email-parser-env/         # Virtual environment (gitignored)
├── LICENSE                   # MIT License
├── README.md                 # Project documentation
├── environment.yml           # Conda environment
├── pyproject.toml           # Python project metadata
├── requirements.txt         # pip requirements
└── setup.py                 # Setup script
```

## Architecture Overview

### Core Processing Flow

1. **EmailProcessor** (`email_parser/core/email_processor.py`) - Main orchestrator
2. **MIMEParser** (`email_parser/core/mime_parser.py`) - Email parsing
3. **ComponentExtractor** (`email_parser/core/component_extractor.py`) - Content extraction
4. **Converters** (`email_parser/converters/`) - File conversion (Excel, PDF)

### Key Components

#### Converter Architecture

- **BaseConverter** (`converters/base_converter.py`) - Abstract base with common functionality
- **PDFConverter** (`converters/pdf_converter.py`) - MistralAI OCR integration
- **ExcelConverter** (`converters/excel_converter.py`) - Excel to CSV conversion

#### Configuration System

- **ProcessingConfig** (`core/config.py`) - Main configuration class
- **default.yaml** (`config/default.yaml`) - Default settings including PDF conversion

#### Exception Hierarchy

- **parsing_exceptions.py** - Email parsing errors
- **converter_exceptions.py** - File conversion errors

### Data Flow

```
Email Input → MIMEParser → ComponentExtractor → Converters → Structured Output
```

### Output Structure

```
output/
├── processed_text/          # Extracted text content
├── attachments/            # Original attachments
├── inline_images/          # Embedded images
├── converted_excel/        # CSV conversions
├── converted_pdf/          # PDF to Markdown
└── metadata.json          # Processing metadata
```

## Archival Protocol

**CRITICAL**: Never overwrite existing files. Always archive before modification.

### Archival Rules

1. **Before any file modification**: Archive to `archive\filename_YYYY-MM-DD.ext`
2. **Deprecated files**: Move to `archive\del_filename_YYYY-MM-DD.ext`
3. **Multiple archives same day**: Use incremental numbering `filename_YYYY-MM-DD_001.ext`
4. **Never overwrite archives**: Check for existing files and increment counter
5. **Use desktop-commander** for all file operations to ensure consistent archival

### Archival Naming Convention

- **First archive of day**: `filename_YYYY-MM-DD.ext`
- **Second archive of day**: `filename_YYYY-MM-DD_001.ext`
- **Third archive of day**: `filename_YYYY-MM-DD_002.ext`
- **Deprecated files**: `del_filename_YYYY-MM-DD.ext` (first), `del_filename_YYYY-MM-DD_001.ext` (second)

### Efficient Archival Workflow

**RECOMMENDED**: Use native copy commands for maximum efficiency:

#### For Claude Desktop (Windows)

```python
# Step 1: Check for existing archives
desktop-commander:list_directory("archive/")

# Step 2: Use PowerShell to copy file directly (zero token transmission!)
desktop-commander:execute_command(
    command='Copy-Item -Path "D:\\Users\\alexp\\dev\\email-parser\\email_parser\\core\\email_processor.py" -Destination "D:\\Users\\alexp\\dev\\email-parser\\archive\\email_processor_2025-06-22.py"',
    shell="powershell",
    timeout_ms=5000
)

# Step 3: Make targeted edits using edit_block
desktop-commander:edit_block(
    file_path="email_parser/core/email_processor.py",
    old_string="specific code to change",
    new_string="updated code",
    expected_replacements=1
)
```

#### For Claude Code (WSL2/Linux)

```python
# Step 1: Check for existing archives
desktop-commander:list_directory("archive/")

# Step 2: Use bash to copy file directly (zero token transmission!)
desktop-commander:execute_command(
    command='cp /mnt/d/Users/alexp/dev/email-parser/email_parser/core/email_processor.py /mnt/d/Users/alexp/dev/email-parser/archive/email_processor_2025-06-22.py',
    shell="bash",
    timeout_ms=5000
)

# Step 3: Make targeted edits using edit_block
desktop-commander:edit_block(
    file_path="email_parser/core/email_processor.py",
    old_string="specific code to change",
    new_string="updated code",
    expected_replacements=1
)
```

#### Native Copy Command Examples

**Windows (PowerShell)**:

```powershell
# Using absolute paths (most reliable)
Copy-Item -Path "D:\Users\alexp\dev\email-parser\email_parser\core\email_processor.py" `
          -Destination "D:\Users\alexp\dev\email-parser\archive\email_processor_2025-06-22.py"
# Multiple archives same day
Copy-Item -Path "D:\Users\alexp\dev\email-parser\email_parser\file.py" `
          -Destination "D:\Users\alexp\dev\email-parser\archive\file_2025-06-22_001.py"
```

**Linux/WSL2 (Bash)**:

```bash
# Using absolute paths (most reliable)
cp /mnt/d/Users/alexp/dev/email-parser/email_parser/core/email_processor.py \
   /mnt/d/Users/alexp/dev/email-parser/archive/email_processor_2025-06-22.py

# Multiple archives same day
cp /mnt/d/Users/alexp/dev/email-parser/email_parser/file.py \
   /mnt/d/Users/alexp/dev/email-parser/archive/file_2025-06-22_001.py
```

#### Benefits of Native Copy Method

- ✅ **Zero token transmission** for file content
- ✅ **Native file system operation** (fastest possible)
- ✅ **Handles large files effortlessly**
- ✅ **Preserves all file attributes**
- ✅ **Creates archive copy** before modifications
- ✅ **Combined with edit_block** for surgical changes
- ✅ **Platform-agnostic approach** using desktop-commander

#### When Deprecating Files

```python
# For files being removed/deprecated
desktop-commander:move_file(
    source="email_parser/old_module.py",
    destination="archive/del_old_module_2025-06-22.py"
)
```

### Legacy Safe Archival Workflow (Less Efficient)

```python
# Always check for existing archives first
# If archive/email_processor_2025-06-21.py exists, use:
# archive/email_processor_2025-06-21_001.py

# Example 1: First modification of day
desktop-commander:move_file(
    source="email_parser/core/email_processor.py",
    destination="archive/email_processor_2025-06-21.py"
)

# Example 2: Second modification same day (check first!)
desktop-commander:list_directory("archive/")  # Check for existing files
desktop-commander:move_file(
    source="email_parser/core/email_processor.py",
    destination="archive/email_processor_2025-06-21_001.py"
)

# Example 3: Deprecating file (second time same day)
desktop-commander:move_file(
    source="old_component.py",
    destination="archive/del_old_component_2025-06-21_001.py"
)
```

## Development Workflow

**IMPORTANT**: Always activate the virtual environment before any development work:

```powershell
# Windows
cd "D:\Users\alexp\dev\email-parser"
.\email-parser-env\Scripts\Activate.ps1

# Linux/WSL2
cd /mnt/d/Users/alexp/dev/email-parser
source email-parser-env/bin/activate
```

### 1. Feature Development

```
0. Activate virtual environment
1. Check recent context: recent_activity(timeframe="1 week")
2. Create feature branch documentation in Basic-Memory
3. Implement with test-driven development
4. Archive old versions before updates using native copy method
5. Document decisions and patterns discovered
```

### 2. Bug Fixes

```
0. Activate virtual environment
1. Search for related issues: search_notes("error message or component")
2. Create minimal reproduction test
3. Archive current version using native copy method
4. Implement fix with comprehensive testing
5. Document root cause and solution in Basic-Memory
```

### 3. Performance Optimization

```
0. Activate virtual environment
1. Profile current implementation
2. Document baseline metrics
3. Implement optimization (archive old version using native copy)
4. Measure improvement
5. Record optimization patterns for future use
```

### Development Patterns

#### Adding New Converters

1. Inherit from `BaseConverter`
2. Implement required abstract methods:
   - `supported_extensions`
   - `supported_mime_types`
   - `convert()`
3. Add to `converters/__init__.py`
4. Update configuration schema

#### Error Handling

- Use specific exception types from `exceptions/`
- Log errors with context using the class logger
- Implement retry logic for external API calls

## Knowledge Management with Basic-Memory

**IMPORTANT**: All development history, decisions, and insights are managed through basic-memory for persistent semantic graphs that integrate with Obsidian.md.

### Core Principles

- **Semantic Relationships**: Build connections between related concepts, issues, and solutions
- **Persistent Knowledge**: All insights become part of the project's knowledge graph
- **Contextual Discovery**: Use semantic search to find related information quickly

### Context Retrieval Workflows

Before starting any work:

```python
# Check recent activity
recent_activity(timeframe="2 weeks", type="note")

# Find related context
build_context("memory://email-parser/features/pdf-conversion")
search_notes("MIME parsing edge cases")

# Explore architecture decisions
build_context("memory://email-parser/architecture/*")
```

### When to Create Notes

1. **Feature Implementation** - Document new features with context, decisions, and implementation details
2. **Bug Fixes** - Record root causes, solutions, and prevention strategies
3. **Design Decisions** - Capture architectural choices and trade-offs
4. **Edge Cases** - Document unusual MIME structures or parsing anomalies
5. **Performance Insights** - Record optimization patterns and benchmarks

### Recommended Note Structure in Basic-Memory

```
email-parser/
├── architecture/          # Design decisions, patterns, system design
├── features/             # Feature implementations and specifications
│   ├── pdf-conversion/   # MistralAI OCR integration
│   ├── excel-conversion/ # Excel to CSV conversion
│   └── mime-parsing/     # MIME structure handling
├── bugs/                 # Bug reports and fixes
├── performance/          # Performance optimizations and analyses
├── edge-cases/          # Unusual email structures and handling
├── implementation/       # Technical implementation details
└── planning/            # Project planning and roadmaps
```

### Example Knowledge Capture

```python
# After discovering a parsing edge case
write_note(
    title="MIME Boundary Edge Case - Nested Multipart",
    content="""
    Discovered issue with nested multipart/alternative within multipart/mixed
    when boundary contains special characters. Solution: escape boundary
    regex pattern before matching.
    
    Test case: email with nested structure and boundary="----=_Part_123$456"
    """,
    folder="email-parser/edge-cases",
    tags=["mime", "parsing", "bug-fix"]
)
```

### Inappropriate Uses

- **DO NOT store**: Code files or deliverables (use file system)
- **DO NOT store**: Project documentation (keep in project folder)
- **DO NOT archive**: Old versions (use `/archive/` directory)

## Enhancement Roadmap

### Phase 1: PDF to Markdown Conversion (HIGHEST PRIORITY)

**Status**: In Active Development  
**Timeline**: 12-16 weeks

1. **MistralAI OCR Integration**
   - Implement PDF converter with MistralAI API
   - Support text-only, image-only, and combined extraction modes
   - Handle multi-page PDFs with optional pagination
   - Extract and save embedded images with proper linking
   - Implement secure API key management
   - Add caching for repeated document processing

2. **PDF Processing Features**
   - Automatic PDF detection by signature and MIME type
   - Configurable extraction modes via CLI
   - Image filtering by size and count
   - Progress tracking for large documents
   - Comprehensive error handling and retry logic

3. **Integration with Email Parser**
   - Update EmailProcessor to route PDFs to new converter
   - Maintain backward compatibility with Excel conversion
   - Generate unified summaries including PDF content
   - Support batch PDF processing
See `docs/requirements/` for detailed specifications and implementation plans.

### Phase 2: Core Enhancements

1. **Summary Generator**
   - Create unified markdown output combining all email components
   - Include metadata, text, attachment list, and image references
   - Integrate PDF and Excel conversion results
   - Optimize for Claude ingestion

2. **Batch Processing Improvements**
   - Thread relationship detection
   - Conversation reconstruction
   - Duplicate detection and handling
   - Parallel processing for PDFs and Excel files

### Phase 3: Advanced Features

1. **Smart Extraction**
   - Extract structured data (dates, contacts, action items)
   - Identify document types and relationships
   - Create knowledge graph of email content
   - Leverage OCR results for data extraction

2. **Security Enhancements**
   - Enhanced malware detection
   - PDF content validation
   - PII detection and redaction options
   - Audit trail generation

### Phase 4: Integration Features

1. **Claude API Integration**
   - Direct upload to Claude Projects
   - Batch analysis automation   - Result aggregation
   - Cost tracking for API usage

2. **Workflow Automation**
   - Watch folder monitoring
   - Scheduled processing
   - Webhook notifications
   - API usage monitoring

## Configuration

### Processing Configuration

Core settings in `config/default.yaml`:

- `processing.convert_pdf: true` - Enable PDF conversion
- `processing.convert_excel: true` - Enable Excel conversion
- `security.max_attachment_size: 10000000` - 10MB limit
- `pdf_conversion.extraction_mode: "all"` - Extract text and images

### PDF Conversion Configuration

```yaml
# config/default.yaml additions
pdf:
  enabled: true
  api_key_env: "MISTRALAI_API_KEY"
  extraction_mode: "all"  # text, images, all
  image_settings:
    limit: 0  # 0 = no limit
    min_size: 100  # pixels
  pagination:
    enabled: true
```

### CLI Usage (Future)

```bash
# Convert email with PDF to markdown
python -m email_parser email.eml --pdf-mode all

# Extract only text from PDFs
python -m email_parser email.eml --pdf-mode text

# Set image limits
python -m email_parser email.eml --pdf-mode all --image-limit 10 --image-min-size 200

# ✨ Batch processing with all features
python -m email_parser input_dir/ output_dir/ --pdf-mode all --extract-excel --batch
```

## Testing Guidelines

### Test Strategy

- Unit tests for individual components
- Integration tests for full workflows
- Mock external dependencies (MistralAI API)
- Test error conditions and edge cases
- Performance tests for large files and batch processing
- Security tests for malicious input handling

### Test Data Management

- **Environment**: Always activate virtual environment before testing
- Use `scripts/test_email_generator.py` for synthetic test data
- Store real email samples in `tests/fixtures/` (gitignored)
- Include test PDFs with various formats and content types
- Document edge cases discovered in Basic-Memory

### Test Execution

```powershell
# Activate virtual environment first
# Windows
.\email-parser-env\Scripts\Activate.ps1

# Linux/WSL2
source email-parser-env/bin/activate

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/performance/

# Run PDF-specific tests
python -m pytest tests/unit/test_pdf_converter.py
python -m pytest tests/integration/test_pdf_integration.py

# Generate test data
python scripts/test_email_generator.py

# Run examples for manual testing
python examples/basic_parsing.py test_simple.eml
python examples/batch_processing.py test_emails/
```

## Code Style and Standards

### Python Standards

- **Style**: Black formatter with 88-character line length
- **Type Hints**: Required for all public functions
- **Docstrings**: Google style for all modules, classes, and functions
- **Imports**: isort with Black compatibility

### Security Requirements

- Input validation on all external data
- Path traversal prevention
- Size limit enforcement
- Secure temporary file handling
- API key encryption for MistralAI
- Email attachment sanitization
- MIME type verification

### Performance Guidelines

- Lazy loading for large files
- Streaming processing where possible
- Efficient memory usage for batch operations
- Progress indicators for long-running tasks
- API call optimization and caching
- Parallel processing for independent tasks

## AI Assistant Guidelines

When working on this project:

1. **Always check project context** - Ensure "dev" project is active
2. **Activate virtual environment** - Never run Python commands without it
3. **Archive before modifying** - Use native copy method for efficiency
4. **Preserve existing functionality** - Maintain backward compatibility
5. **Follow the phased approach** - Complete current phase before starting next
6. **Document decisions** - Capture all insights in Basic-Memory with semantic relationships
7. **Consider memory usage** - This tool processes potentially large email files
8. **Think about AI workflows** - Features should enhance AI's ability to analyze emails
9. **Test edge cases** - Email formats vary widely, test unusual structures
10. **Secure by default** - Validate all inputs and sanitize outputs

## Code Review Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] Functions have comprehensive docstrings
- [ ] Type hints added for public functions
- [ ] Error handling is comprehensive
- [ ] No hardcoded paths (use pathlib or config)
- [ ] Memory-efficient for large files
- [ ] Tests added/updated for new functionality
- [ ] Virtual environment was active during development
- [ ] Old versions archived using native copy method
- [ ] Knowledge captured in Basic-Memory
- [ ] Security implications considered
- [ ] API usage optimized (for MistralAI calls)
- [ ] Documentation updated (README, CHANGELOG)

## Deployment Considerations

### Development Environment

- **Virtual Environment**: Required for development
- **Setup Guide**: See `DEVELOPMENT_SETUP.md` for detailed instructions
- **Dependencies**: Managed via `requirements.txt` and `pyproject.toml`
- **API Keys**: Store securely, never commit to repository

### Package Distribution

- PyPI package: `enterprise-email-parser`
- Conda package: `email-parser`
- Docker image for containerized deployment

### Configuration Management

- Environment variables for sensitive settings
- YAML configuration files for complex options
- Command-line overrides for all settings
- Secure storage for MistralAI API keys
- Per-environment configuration support

### Monitoring and Logging

- Structured logging (JSON format option)
- Performance metrics collection
- Error reporting integration
- Processing audit trails
- API usage tracking
- Batch processing statistics

## Maintenance Protocol

### Regular Tasks

1. **Weekly**: Review and archive old development files
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Performance profiling and optimization
4. **Annually**: Major version planning and roadmap update

### Documentation Updates

- Keep README.md synchronized with features
- Update API documentation on changes
- Maintain CHANGELOG.md for all releases
- Document decisions in Basic-Memory
- Update requirements documents as needed
- Sync CLAUDE.md with project changes

## Emergency Procedures

### Corruption Recovery

1. Check `archive/` for recent versions
2. Use git history for code recovery
3. Restore from Basic-Memory for design decisions
4. Recreate virtual environment if corrupted: `python -m venv email-parser-env`
5. Rebuild from test suite if needed

### Performance Degradation

1. **Environment**: Ensure virtual environment is activated
2. Profile with `cProfile` or `py-spy`
3. Check for memory leaks with `tracemalloc`
4. Review recent changes in archive
5. Implement incremental optimization
6. Monitor API rate limits and costs

### Security Incident

1. Immediately disable affected features
2. Archive compromised versions
3. Audit all recent file operations
4. Document incident and resolution
5. Rotate API keys if necessary
6. Review email processing logs

## Quick Reference

### Command Examples

```bash
# Basic email parsing
python -m email_parser email.eml output/

# With all conversions enabled
python -m email_parser email.eml output/ --convert-excel --pdf-mode all
# Batch processing directory
python -m email_parser email_directory/ output/ --batch

# Extract specific components
python -m email_parser email.eml output/ --extract-attachments --extract-images

# PDF conversion with options
python -m email_parser email.eml output/ --pdf-mode text --image-limit 5

# High-performance processing
python -m email_parser email.eml output/ --parallel --cache-enabled

# Debug mode with verbose logging
python -m email_parser email.eml output/ --debug --log-file processing.log
```

## Communication Protocols

### Progress Updates

- Use Basic-Memory for development notes
- Update project documentation regularly
- Create summary reports for major milestones
- Track PDF conversion implementation progress

### Issue Tracking

- Document bugs with reproduction steps
- Link fixes to original issue descriptions
- Maintain knowledge base of solutions
- Track OCR accuracy issues
- Record MIME parsing edge cases

### Feature Requests

- Evaluate against project goals
- Document technical feasibility
- Plan implementation approach
- Update roadmap accordingly

## Current Status

**Version**: 2.1.0  
**Phase**: 1 Week 2 (API Integration & Testing)  
**Last Updated**: 2025-06-22  
**Maintainer**: alexanderpresto

### Completed Features

- ✅ Core email parsing and MIME handling
- ✅ Excel to CSV conversion
- ✅ PDF converter infrastructure with MistralAI integration
- ✅ Comprehensive exception handling
- ✅ Security validation and file size limits
- ✅ Virtual environment setup and documentation

### In Development

- 🔄 MistralAI API integration testing
- 🔄 Enhanced test coverage for converters
- 🔄 ExcelConverter refactoring to BaseConverter pattern
- 🔄 Batch processing optimization

### Recent Changes (2025-06-22)

- **Merged project instructions** into single CLAUDE.md file
- **Enhanced archival protocol** with native copy method for efficiency
- **Added platform context** for Claude Desktop and Claude Code compatibility
- **Integrated knowledge management** best practices from docx-processor
- **Added AI assistant guidelines** and code review checklist
- **Improved quick reference** section with command examples

### Recent Changes (2025-06-21)

- Reorganized folder structure for better maintainability
- Created `config/` directory with default configuration template- Added README files to `config/` and `scripts/` directories
- Updated `test_email_generator.py` to use proper path references
- Archived obsolete files: `project_instructions.yaml`, `project_journal.md`
- Created `.cspell.json` for spell checker configuration
- Enhanced `.gitignore` with additional entries
- **Migrated to virtual environment setup for proper dependency isolation**
- **Created DEVELOPMENT_SETUP.md with environment instructions**
- **Created comprehensive documentation for PDF to Markdown conversion feature**
- **Added Product Requirements, Project Plan, and Technical Specification documents**
- **Prioritized PDF to Markdown conversion as the primary enhancement**

## Contact and Resources

- **Developer**: Alexander Presto
- **Repository**: [Email Parser Project](https://github.com/alexanderpresto/email-parser)
- **Issues**: Report bugs and feature requests on GitHub
- **License**: MIT License

---

**Note**: This file serves as the authoritative source for project instructions. When switching between Claude Desktop and Claude Code, refer to this document for consistent guidance.

**Remember**: This tool makes emails AI-friendly. Every feature should support that mission.
