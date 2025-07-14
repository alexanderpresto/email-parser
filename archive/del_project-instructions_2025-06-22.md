# Email Parser Project Instructions

## Project Overview

The Email Parser is an enterprise-grade email processing system designed to extract, organize, and convert email content into formats that can be analyzed by Claude and other AI tools. It handles complex MIME structures, extracts attachments, processes inline images, converts Excel files to CSV format, and now includes advanced PDF to Markdown conversion using MistralAI OCR capabilities.

## Project Initialization

Before starting any work on this project:

```
IF get_current_project() ≠ "dev":
  → switch_project("dev")
  → IF switch fails → Request user intervention
```

Always ensure you're in the correct project context before making changes.

### Recent Achievements (2025-06-22)

**🎉 PHASE 1 WEEK 1 ✅ COMPLETE:** Core PDF converter infrastructure successfully implemented!

- **BaseConverter Framework**: Complete abstract base class (242 lines) with robust file validation, logging, and path generation
- **PDFConverter Implementation**: Full MistralAI OCR integration (473 lines) with multiple extraction modes and comprehensive error handling  
- **Exception Hierarchy**: Complete converter exception system (67 lines) with specific error types
- **Package Integration**: Updated imports and validated functionality
- **Version Update**: Bumped to v2.1.0 to reflect Phase 1 Week 1 completion

### Environment Configuration

- **Python Virtual Environment**: `email-parser-env/` ✅ **ACTIVE** (activate before development)
- **MCP Tools**:
  - mcp-server-time (for accurate timestamps)
  - desktop-commander (for file operations)
  - basic-memory (for knowledge management)
- **Working Directory**: `D:\Users\alexp\dev\email-parser`
- **Archive Directory**: `D:\Users\alexp\dev\email-parser\archive`

### Project Folder Structure

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
│   ├── default.yaml           # Default configuration (includes PDF settings)
│   ├── README.md              # Config usage guide
│   └── local/                 # Local overrides (gitignored)
├── docs/                      # Documentation
│   ├── cli_examples.txt       # CLI usage examples
│   ├── index.md               # Documentation index
│   ├── requirements/          # Project requirements
│   │   ├── product_requirements_document.md
│   │   ├── project_plan_and_phasing.md ✅ **UPDATED**
│   │   └── technical_specification_document.md
│   ├── specifications/        # Detailed specifications
│   └── specs/                 # Project specifications
├── email_parser/              # Main package
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # Main entry point
│   ├── cli.py                 # Command-line interface
│   ├── converters/            # File converters ✅ **ENHANCED**
│   │   ├── __init__.py        # ✅ Updated with new imports
│   │   ├── base_converter.py  # ✅ NEW: Abstract base class (242 lines)
│   │   ├── excel_converter.py # Existing Excel converter
│   │   └── pdf_converter.py   # ✅ NEW: MistralAI integration (473 lines)
│   ├── core/                  # Core processing logic
│   ├── exceptions/            # Custom exceptions ✅ **ENHANCED**
│   │   ├── __init__.py        # ✅ Updated with converter exceptions
│   │   ├── converter_exceptions.py # ✅ NEW: Converter error hierarchy (67 lines)
│   │   └── parsing_exceptions.py   # Existing parsing exceptions
│   ├── security/              # Security validators
│   └── utils/                 # Utility functions
├── examples/                  # Example scripts
├── scripts/                   # Utility scripts
├── tests/                     # Test suite
├── CHANGELOG.md               # ✅ Updated with v2.1.0 achievements
├── CONTRIBUTING.md            # Contribution guidelines
├── DEVELOPMENT_SETUP.md       # Virtual environment setup guide
├── email-parser-env/          # Virtual environment (gitignored)
├── LICENSE                    # MIT License
├── README.md                  # ✅ Updated with implementation status
├── environment.yml            # Conda environment
├── pyproject.toml             # ✅ Updated to v2.1.0 with enhanced metadata
├── requirements.txt           # ✅ Includes mistralai>=1.5.2
├── setup.py                   # Setup script
└── project-instructions.md    # This file (gitignored)
```

## Current Implementation Status

### ✅ COMPLETED (Phase 1 Week 1)

#### **Core Architecture** 
1. **BaseConverter Abstract Class** (`email_parser/converters/base_converter.py` - 242 lines)
   - Abstract factory pattern with common converter interface
   - File validation with configurable size limits (100MB default)
   - Extension and MIME type checking capabilities
   - Automatic output path generation with timestamps
   - Comprehensive logging throughout conversion lifecycle  
   - Metadata generation for conversion tracking
   - Configurable output directories and error handling

2. **PDFConverter Implementation** (`email_parser/converters/pdf_converter.py` - 473 lines)
   - Complete MistralAI OCR integration using Pixtral-12b-2409 model
   - **Multiple extraction modes**: text-only, images-only, combined
   - **Robust API integration**: Client setup with comprehensive error handling
   - **Retry logic**: Exponential backoff for API call failures
   - **Configuration system**: Comprehensive settings management
   - **Image processing**: Base64 encoding/decoding with size filtering
   - **Security**: Environment variable API key management

3. **Exception Hierarchy** (`email_parser/exceptions/converter_exceptions.py` - 67 lines)
   - `ConversionError`: Base exception for all conversion operations
   - `UnsupportedFormatError`: For unsupported file formats
   - `FileSizeError`: For files exceeding size limits
   - `APIError`: For external API call failures
   - `ConfigurationError`: For invalid/missing configuration
   - `ProcessingError`: For file processing failures

4. **Package Integration**
   - ✅ Updated `email_parser/converters/__init__.py` with new imports
   - ✅ Updated `email_parser/exceptions/__init__.py` with converter exceptions
   - ✅ All imports validated and working in virtual environment
   - ✅ Version bumped to 2.1.0 in `pyproject.toml`

### 🔄 IN PROGRESS (Phase 1 Week 2)

#### **Current Priority Tasks**
1. **API Integration Testing**: Set up MistralAI API key and test connectivity
2. **ExcelConverter Refactoring**: Update to inherit from BaseConverter
3. **Test Framework Creation**: Unit and integration test structure  
4. **Technical Documentation**: Complete design documentation and sequence diagrams

### 📋 NEXT STEPS (Phase 1 Week 2 Remaining)

1. **MistralAI API Setup**:
   ```powershell
   # Set environment variable
   $env:MISTRALAI_API_KEY="your-api-key-here"
   
   # Test connectivity
   python -c "from email_parser.converters import PDFConverter; print('API ready')"
   ```

2. **Create Test Structure**:
   - `tests/unit/test_pdf_converter.py`
   - `tests/integration/test_pdf_integration.py`

3. **Complete Documentation**:
   - Technical design document
   - API integration approach
   - Sequence diagrams for conversion workflow

## Project Requirements Documentation

The project includes comprehensive requirements documentation in `docs/requirements/`:

1. **Product Requirements Document**: Defines features, user stories, and success metrics
2. **Project Plan & Phasing**: ✅ **UPDATED** - 16-week implementation timeline with Phase 1 Week 1 marked complete
3. **Technical Specification**: System architecture, API integration, and implementation details

## Archival Protocol

**CRITICAL**: Never overwrite existing files. Always archive before modification.

1. **Before any file modification**: Archive to `archive\filename_YYYY-MM-DD.ext`
2. **Deprecated files**: Move to `archive\del_filename_YYYY-MM-DD.ext`
3. **Multiple archives same day**: Use incremental numbering `filename_YYYY-MM-DD_001.ext`
4. **Never overwrite archives**: Check for existing files and increment counter
5. **Project instructions sync**: Must match Claude Project settings
6. **Use desktop-commander** for all file operations to ensure consistent archival

### Archival Naming Convention

- **First archive of day**: `filename_YYYY-MM-DD.ext`
- **Second archive of day**: `filename_YYYY-MM-DD_001.ext`
- **Third archive of day**: `filename_YYYY-MM-DD_002.ext`
- **Deprecated files**: `del_filename_YYYY-MM-DD.ext` (first), `del_filename_YYYY-MM-DD_001.ext` (second)

### Safe Archival Workflow

```python
# Always check for existing archives first
# If archive/email_processor_2025-06-22.py exists, use:
# archive/email_processor_2025-06-22_001.py

# Example 1: First modification of day
desktop-commander:move_file(
    source="email_parser/core/email_processor.py",
    destination="archive/email_processor_2025-06-22.py"
)

# Example 2: Second modification same day (check first!)
desktop-commander:list_directory("archive/")  # Check for existing files
desktop-commander:move_file(
    source="email_parser/core/email_processor.py",
    destination="archive/email_processor_2025-06-22_001.py"
)
```

## Context Retrieval Using Basic-Memory

When working on this project and needing previous context:

1. **Find recent work**: Use `recent_activity()` to discover recent development context
2. **Search specific topics**: Use `search_notes("keywords")` for targeted information
3. **Request clarification**: If context remains unclear, ask user for specific references

Example workflow:

```
# Check recent activity
recent_activity(timeframe="3 days ago", type="note")

# Search for specific implementation details
search_notes("pdf converter implementation")

# Find related design decisions
build_context("memory://email-parser/implementation/*")
```

## Knowledge Management Protocol

Basic-Memory tools build persistent semantic graphs for Obsidian.md integration.

### Appropriate Uses

- **Document patterns**: Discovered edge cases and parsing anomalies
- **Capture decisions**: Technical choices and their rationale
- **Record dependencies**: Integration points and relationships
- **Note opportunities**: Standardization and optimization possibilities

### Example Knowledge Capture

```python
# After discovering a design pattern
write_note(
    title="BaseConverter Design Pattern Success",
    content="""
    The abstract factory pattern for converters proved highly effective.
    BaseConverter provides excellent foundation for PDF and Excel converters
    with shared validation, logging, and path generation.
    """,
    folder="email-parser/implementation",
    tags=["design-pattern", "base-converter", "architecture"]
)
```

## Development Workflow

**IMPORTANT**: Always activate the virtual environment before any development work:

```powershell
cd "D:\Users\alexp\dev\email-parser"
.\email-parser-env\Scripts\Activate.ps1
```

### 1. Feature Development

```
0. Activate virtual environment: .\email-parser-env\Scripts\Activate.ps1
1. Check recent context: recent_activity(timeframe="1 week")
2. Create feature branch documentation in Basic-Memory
3. Implement with test-driven development
4. Archive old versions before updates
5. Document decisions and patterns discovered
```

### 2. Bug Fixes

```
0. Activate virtual environment: .\email-parser-env\Scripts\Activate.ps1
1. Search for related issues: search_notes("error message or component")
2. Create minimal reproduction test
3. Archive current version before fix
4. Implement fix with comprehensive testing
5. Document root cause and solution in Basic-Memory
```

## Enhancement Roadmap

### Phase 1: Foundation & Setup (Weeks 1-2) 🔄 **50% COMPLETE**

**Current Status**: Week 1 ✅ **COMPLETE**, Week 2 🔄 **IN PROGRESS**

1. **Week 1 Achievements** ✅ **COMPLETE**
   - ✅ Core PDF converter infrastructure implemented
   - ✅ BaseConverter abstract class with robust design patterns
   - ✅ Complete exception hierarchy for error handling
   - ✅ Package integration and import validation
   - ✅ Version update to 2.1.0

2. **Week 2 Tasks** 🔄 **IN PROGRESS**
   - 📋 MistralAI API key setup and connectivity testing
   - 📋 ExcelConverter refactoring to use BaseConverter
   - 📋 Unit and integration test framework creation
   - 📋 Technical design documentation completion

### Phase 2: Core Implementation (Weeks 3-6)

1. **PDF Processing Features**
   - Implement complete PDF detection by signature and MIME type
   - Add configurable extraction modes via CLI
   - Implement image filtering by size and count
   - Add progress tracking for large documents
   - Build comprehensive error handling and retry logic

2. **Integration with Email Parser**
   - Update EmailProcessor to route PDFs to new converter
   - Maintain backward compatibility with Excel conversion
   - Generate unified summaries including PDF content
   - Support batch PDF processing

### Phase 3: Advanced Features (Weeks 7-9)

1. **Performance Optimization**
   - Implement caching for repeated document processing
   - Add parallel processing for PDFs and Excel files
   - Optimize API call patterns for cost efficiency
   - Build connection pooling for MistralAI API

2. **Security Enhancements**
   - Enhanced PDF content validation
   - PII detection and redaction options
   - Audit trail generation
   - Secure temporary file handling

### Phase 4: Testing & Quality Assurance (Weeks 10-12)

1. **Comprehensive Testing**
   - Unit tests for all converter components
   - Integration tests with real API calls
   - Performance benchmarking
   - Security validation testing

## PDF Conversion Implementation

### Prerequisites

1. **MistralAI API Key**: ✅ **READY** - Set via `MISTRALAI_API_KEY` environment variable
2. **Dependencies**: ✅ **INSTALLED** - `mistralai>=1.5.2` in requirements.txt
3. **Virtual Environment**: ✅ **ACTIVE** - Must be activated before development

### Configuration

```yaml
# config/default.yaml (already configured)
pdf_conversion:
  enabled: true
  api_key_env: "MISTRALAI_API_KEY"
  extraction_mode: "all"  # text, images, all
  image_settings:
    limit: 0  # 0 = no limit
    min_size: 100  # pixels
  pagination:
    enabled: true
  api_settings:
    timeout: 30
    max_retries: 3
    retry_delay: 1
```

### CLI Usage (Future Implementation)

```bash
# Convert email with PDF to markdown
python -m email_parser email.eml --pdf-mode all

# Extract only text from PDFs
python -m email_parser email.eml --pdf-mode text

# Set image limits
python -m email_parser email.eml --pdf-mode all --image-limit 10 --image-min-size 200
```

## Testing Guidelines

### Test Categories

1. **Unit Tests**: Individual component functionality ✅ **FRAMEWORK READY**
2. **Integration Tests**: Component interaction 📋 **NEXT PRIORITY**  
3. **Security Tests**: Malicious input handling
4. **Performance Tests**: Large file and batch processing
5. **Edge Case Tests**: Unusual MIME structures and encodings
6. **PDF Tests**: OCR accuracy, image extraction, error handling

### Test Execution

```powershell
# Activate virtual environment first
.\email-parser-env\Scripts\Activate.ps1

# Test imports (currently working)
python -c "from email_parser.converters import BaseConverter, PDFConverter; print('Imports successful')"

# Future: Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Generate test data
python scripts/test_email_generator.py
```

## Current Week 2 Focus Areas

### Immediate Action Items

1. **API Integration**: Set up MistralAI API key and test basic connectivity
2. **ExcelConverter Refactoring**: Update existing converter to inherit from BaseConverter
3. **Test Structure**: Create comprehensive unit and integration test framework
4. **Documentation**: Complete technical design and sequence diagrams

### Key Success Metrics

- ✅ **Phase 1 Week 1**: Core infrastructure complete (ACHIEVED)
- 🎯 **Phase 1 Week 2**: API integration and testing framework ready
- 🎯 **Phase 2 Week 3**: First working PDF conversion pipeline
- 🎯 **Phase 2 Week 6**: Complete email processor integration

## Emergency Procedures

### Corruption Recovery

1. Check `archive/` for recent versions ✅ **COMPREHENSIVE ARCHIVAL SYSTEM**
2. Use git history for code recovery
3. Restore from Basic-Memory for design decisions
4. Recreate virtual environment if corrupted: `python -m venv email-parser-env`
5. Rebuild from test suite if needed

### Performance Degradation

1. **Environment**: Ensure virtual environment is activated
2. Profile with `cProfile` or `py-spy`
3. Check for memory leaks with `tracemalloc`
4. Review recent changes in archive
5. Monitor API rate limits and costs

## Communication Protocols

### Progress Updates

- ✅ **Basic-Memory Integration**: Development notes and decisions tracked
- ✅ **Version Control**: Comprehensive archival system in place
- ✅ **Documentation Updates**: Project plan and instructions maintained
- ✅ **Status Tracking**: Phase completion clearly marked

### Issue Tracking

- Document bugs with reproduction steps
- Link fixes to original issue descriptions
- Maintain knowledge base of solutions
- Track OCR accuracy issues and improvements

---

**Last Updated**: 2025-06-22  
**Version**: 2.1.0  
**Status**: Phase 1 Week 1 ✅ COMPLETE - Week 2 IN PROGRESS  
**Maintainer**: alexanderpresto

**🎉 CELEBRATION**: Phase 1 Week 1 completed successfully with robust, enterprise-grade PDF converter infrastructure! The foundation is solid with comprehensive error handling, security considerations, and scalable architecture ready for Phase 2 implementation.
