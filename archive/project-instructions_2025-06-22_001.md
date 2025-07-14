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

### 🎉 **MAJOR MILESTONE ACHIEVED** (2025-06-22)

**✅ PHASE 1 WEEK 1 COMPLETED** - Core PDF converter structure successfully implemented!

### Current Development Status

**Version:** 2.0.0-dev  
**Current Phase:** Phase 1, Week 2 - Core Architecture Design  
**Last Updated:** 2025-06-22  
**Next Review:** End of Week 2

### Recent Major Progress (2025-06-22)

**✅ INFRASTRUCTURE COMPLETE:**
- ✅ **BaseConverter Framework** (242 lines): Abstract base class with common interface, file validation, logging, and path generation
- ✅ **PDFConverter Implementation** (473 lines): Complete MistralAI Pixtral-12b-2409 integration with multiple extraction modes
- ✅ **Exception Hierarchy** (67 lines): Comprehensive converter-specific exceptions for robust error handling
- ✅ **Virtual Environment**: Properly configured with MistralAI SDK v1.8.2
- ✅ **Import Validation**: All modules import successfully without errors
- ✅ **Module Integration**: Updated package structure with proper imports

**✅ TECHNICAL ACHIEVEMENTS:**
- **Extraction Modes**: text-only, images-only, or comprehensive extraction
- **API Integration**: MistralAI Pixtral-12b-2409 model with retry logic
- **Error Handling**: Exponential backoff, timeout management, detailed logging
- **Image Processing**: Configurable limits, size filtering, directory management
- **Security**: Environment variable API key management, file validation

### Implementation Details

#### Files Created
1. **`email_parser/converters/base_converter.py`** (242 lines)
   - Abstract base class for all converters
   - File validation (size limits, extension checking)
   - Output path generation with timestamps
   - Comprehensive logging and metadata generation
   - Configurable settings management

2. **`email_parser/converters/pdf_converter.py`** (473 lines)
   - MistralAI OCR integration with Pixtral-12b-2409
   - Multiple extraction modes: 'text', 'images', 'all'
   - Robust API error handling with exponential backoff
   - Configurable image processing and limits
   - Base64 encoding for PDF transmission

3. **`email_parser/exceptions/converter_exceptions.py`** (67 lines)
   - Custom exception hierarchy for conversion operations
   - Specific error types: ConversionError, APIError, ConfigurationError, etc.

#### Files Updated
- **`email_parser/converters/__init__.py`**: Added BaseConverter and PDFConverter imports
- **`email_parser/exceptions/__init__.py`**: Added converter exception imports

#### Dependencies
- **`mistralai>=1.5.2`**: Already in requirements.txt, version 1.8.2 installed

### Current Implementation Status

**COMPLETED ✅ (Phase 1, Week 1):**
- ✅ Development environment setup with virtual environment
- ✅ MistralAI SDK installed and validated: `mistralai>=1.5.2` (v1.8.2)
- ✅ Base converter framework with abstract interface
- ✅ Complete PDF converter implementation
- ✅ Comprehensive exception hierarchy
- ✅ Module integration and import validation
- ✅ Virtual environment workflow established

**IN PROGRESS 🔄 (Phase 1, Week 2):**
- 🔄 PDF configuration in `config/default.yaml`
- 🔄 Test structure creation (unit and integration tests)
- 🔄 API connectivity testing (requires API key setup)
- 🔄 ExcelConverter refactoring to use BaseConverter

**NEXT PRIORITY 📋 (Phase 1, Week 2):**
- 📋 Complete configuration infrastructure
- 📋 Create comprehensive test structure
- 📋 Technical design documentation
- 📋 API integration testing

### Environment Configuration

- **Python Virtual Environment**: `email-parser-env/` ✅ **ACTIVE REQUIRED**
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
│   ├── *_2025-06-22.*         # Today's archived versions
│   └── *_YYYY-MM-DD.*         # Other archived versions
├── benchmarks/                # Performance benchmarking scripts
├── config/                    # Configuration files
│   ├── default.yaml           # Default configuration (⚠️ needs PDF settings)
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
│   ├── converters/            # ✅ **File converters**
│   │   ├── __init__.py        # ✅ **Updated with new imports**
│   │   ├── base_converter.py  # ✅ **NEW: Abstract base class**
│   │   ├── excel_converter.py # Existing Excel converter
│   │   └── pdf_converter.py   # ✅ **NEW: MistralAI PDF converter**
│   ├── core/                  # Core processing logic
│   ├── exceptions/            # ✅ **Custom exceptions**
│   │   ├── __init__.py        # ✅ **Updated with converter exceptions**
│   │   ├── converter_exceptions.py # ✅ **NEW: Converter-specific exceptions**
│   │   └── parsing_exceptions.py   # Existing parsing exceptions
│   ├── security/              # Security validators
│   └── utils/                 # Utility functions
├── examples/                  # Example scripts
├── scripts/                   # Utility scripts
├── tests/                     # Test suite (⚠️ needs PDF test structure)
├── CONTRIBUTING.md            # Contribution guidelines
├── DEVELOPMENT_SETUP.md       # Virtual environment setup guide
├── email-parser-env/          # ✅ **Virtual environment (active)**
├── LICENSE                    # MIT License
├── README.md                  # ✅ **Updated project documentation**
├── requirements.txt           # ✅ **pip requirements (includes mistralai)**
└── project-instructions.md    # ✅ **This file (updated)**
```

## Development Workflow

**CRITICAL**: Always activate the virtual environment before any development work:

```powershell
cd "D:\Users\alexp\dev\email-parser"
.\email-parser-env\Scripts\Activate.ps1
```

### Virtual Environment Validation

```powershell
# Verify activation
python -c "import sys; print('Virtual env active:', 'email-parser-env' in sys.prefix)"

# Test imports
python -c "from email_parser.converters import BaseConverter, PDFConverter; print('✅ Converter imports successful')"
python -c "from email_parser.exceptions import ConversionError, APIError; print('✅ Exception imports successful')"
```

### 1. Feature Development

```
0. ✅ **DONE** Activate virtual environment
1. ✅ **DONE** Check recent context: recent_activity()
2. ✅ **DONE** Core PDF converter structure implemented
3. 🔄 **IN PROGRESS** Implement configuration and testing
4. Archive old versions before updates
5. Document decisions and patterns discovered
```

### 2. Next Development Tasks (Phase 1, Week 2)

**Priority 1: Configuration Infrastructure**
```powershell
# Update config/default.yaml with PDF settings
# Test configuration loading
# Validate API key handling
```

**Priority 2: Test Structure**
```powershell
# Create tests/unit/test_pdf_converter.py
# Create tests/integration/test_pdf_integration.py
# Implement mock testing for API calls
```

**Priority 3: API Integration**
```powershell
# Set up MISTRALAI_API_KEY environment variable
# Test real API connectivity
# Validate OCR processing pipeline
```

## Enhancement Roadmap

### ✅ Phase 1: Foundation & Setup (Weeks 1-2)

#### ✅ Week 1: Environment Preparation **COMPLETED 2025-06-22**
- ✅ **DONE** Virtual environment setup and MistralAI SDK installation
- ✅ **DONE** Project structure updates (BaseConverter, PDFConverter)
- ✅ **DONE** Exception framework and module integration

#### 🔄 Week 2: Core Architecture Design **CURRENT PRIORITY**
- 📋 Configuration infrastructure completion
- 📋 Test structure creation  
- 📋 Technical design documentation
- 📋 ExcelConverter refactoring

### 📋 Phase 2: Core Implementation (Weeks 3-6)

**Week 3-4: PDF Processing**
- PDF detection and OCR processing implementation
- Image extraction and processing
- API response handling and content processing

**Week 5-6: Email Integration**
- Email processor updates for PDF handling
- Summary generation with PDF content
- Backward compatibility maintenance

### 📋 Phase 3: Advanced Features (Weeks 7-9)

**Batch Processing & CLI**
- Parallel processing for PDFs
- CLI enhancements with PDF options
- Performance optimization and caching

### 📋 Phase 4: Testing & Quality (Weeks 10-12)

**Comprehensive Testing**
- Unit, integration, and performance tests
- Security validation and optimization
- Quality assurance and benchmarking

### 📋 Phase 5: Documentation & Deployment (Weeks 13-14)

**Documentation & Release**
- Complete documentation update
- Package distribution and release preparation
- Migration guides and examples

### 📋 Phase 6: Post-Launch Support (Weeks 15-16)

**Monitoring & Enhancement**
- Production monitoring and bug fixes
- Feature requests and optimization opportunities

## Archival Protocol

**CRITICAL**: Never overwrite existing files. Always archive before modification.

1. **Before any file modification**: Archive to `archive\filename_YYYY-MM-DD.ext`
2. **Today's archives**: Use incremental numbering for multiple same-day changes
3. **Example from today**: `archive\project-instructions_2025-06-22.md`
4. **Use desktop-commander** for all file operations

### Safe Archival Workflow

```python
# Always check for existing archives first
desktop-commander:list_directory("archive/")  # Check for existing files

# Archive current file before modification
desktop-commander:move_file(
    source="email_parser/core/email_processor.py",
    destination="archive/email_processor_2025-06-22.py"
)
```

## Knowledge Management Protocol

### Recent Development Documentation

Using Basic-Memory to track development progress:

- **Implementation notes**: Core structure completion documented
- **Technical decisions**: MistralAI integration approach
- **Progress tracking**: Phase 1 Week 1 completion status
- **Next steps**: Configuration and testing priorities

### Example Knowledge Capture

```python
# Document completed implementation
write_note(
    title="PDF Converter Core Implementation Complete",
    content="""Phase 1 Week 1 completed with BaseConverter framework 
    and PDFConverter implementation. Ready for configuration and testing.""",
    folder="email-parser/milestones",
    tags=["implementation", "pdf-converter", "phase-1", "completed"]
)
```

## Testing Guidelines

### Current Test Status

**✅ Import Validation**: All new modules import successfully
**🔄 Pending**: Unit and integration test structure creation
**📋 Next**: Mock API testing and configuration validation

### Test Execution (Virtual Environment Required)

```powershell
# Activate virtual environment first
.\email-parser-env\Scripts\Activate.ps1

# Validate imports
python -c "from email_parser.converters import BaseConverter, PDFConverter"
python -c "from email_parser.exceptions import ConversionError, APIError"

# Run tests (when structure is created)
python -m pytest tests/unit/
python -m pytest tests/integration/
```

## Configuration Management

### Current Configuration Status

**✅ Requirements**: MistralAI dependency included in requirements.txt
**🔄 Pending**: PDF settings in config/default.yaml
**📋 Next**: API key management and validation

### Example PDF Configuration (To Be Implemented)

```yaml
# config/default.yaml additions needed
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

## Success Metrics

### ✅ Phase 1 Week 1 Success Criteria (ACHIEVED)

- ✅ **Environment Ready**: Virtual environment activated with all dependencies
- ✅ **Core Structure**: BaseConverter and PDFConverter implemented
- ✅ **Exception Handling**: Comprehensive error management framework
- ✅ **Import Validation**: All modules import without errors
- ✅ **Documentation**: Updated project documentation and status

### 🔄 Phase 1 Week 2 Success Criteria (TARGET)

- 📋 **Configuration**: PDF settings integrated into config system
- 📋 **Testing**: Unit and integration test structure created
- 📋 **API Integration**: MistralAI connectivity validated
- 📋 **Refactoring**: ExcelConverter updated to use BaseConverter

## Communication Protocols

### Progress Updates

- **Development notes**: Documented in Basic-Memory
- **Milestone completion**: Updated in project documentation
- **Technical decisions**: Recorded with rationale
- **Implementation status**: Tracked in project plan

### Current Development Context

**Last Session Achievement**: Complete implementation of PDF converter core structure
**Current Focus**: Configuration, testing, and API integration
**Next Session Goal**: Complete Phase 1 Week 2 objectives

---

**Last Updated**: 2025-06-22  
**Version**: 2.1.0  
**Phase Status**: Phase 1 Week 1 ✅ **COMPLETED**, Week 2 🔄 **IN PROGRESS**  
**Maintainer**: alexanderpresto
