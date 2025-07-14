# CLAUDE.md - Email Parser Project Instructions

**Project-Specific Instructions**: This file contains email parser project-specific instructions for any developer or AI assistant working on this project.

## Project-Specific Setup

**Note**: Basic environment setup is handled by global CLAUDE.md. This file contains only email parser-specific configurations.

## Critical Setup

```bash
# Production main branch (no feature branches needed)
git branch --show-current  # Should show: main
```

## Email Parser Specific Commands

```bash
# Project context (email parser specific)
build_context("memory://email-parser/*", timeframe="1 week")

# Interactive CLI mode (email parser specific)
python -m email_parser.cli.interactive

# Direct file conversion (Phase 4 - email parser specific)
python -m email_parser.cli.main convert --file document.pdf --output output/
python -m email_parser.cli.main convert-batch --directory docs/ --output output/
```


## Email Parser Library Documentation

**Documentation Integration**: Use available MCP documentation tools for library references

### Key Libraries to Document

1. **Core Dependencies**:
   - `mammoth` → DOCX to HTML conversion patterns
   - `mistralai` → PDF OCR API usage and best practices
   - `beautifulsoup4` → HTML parsing and manipulation
   - `tiktoken` → Token counting for AI-ready chunking
   - `python-docx` → Advanced DOCX metadata extraction
   - `openpyxl` → Excel file processing
   - `pillow` → Image handling and optimization

2. **Documentation Lookup Workflow** (if available):
   ```bash
   # Example workflow - adapt to your MCP setup
   # Before implementing new converter features
   [documentation-tool] library-lookup "mammoth" "table-extraction"
   
   # When debugging API issues
   [documentation-tool] library-lookup "mistralai" "ocr-api"
   
   # For performance optimization
   [documentation-tool] library-lookup "beautifulsoup4" "performance"
   ```

3. **Integration Patterns**:
   - Before adding new file format support → Check library capabilities
   - When implementing converter features → Verify against official docs
   - For error handling → Check documented exceptions
   - Performance tuning → Use library-specific optimizations


## Project Structure

```
email-parser/                        # Project root: [YOUR_PROJECT_PATH]/email-parser
├── email_parser/                    # Main package
│   ├── cli/                        # ✅ NEW: CLI package structure
│   │   ├── __init__.py            # CLI exports
│   │   ├── main.py                # Traditional CLI entry point
│   │   └── interactive.py         # ✅ Interactive CLI Mode
│   ├── converters/                 # File converters (PDF, Excel, DOCX)
│   ├── core/                       # Processing logic
│   │   ├── scanner.py             # ✅ Email content scanner
│   │   └── ...                    # Other core modules
│   ├── config/                     # ✅ Configuration system
│   │   ├── profiles.py            # ✅ Processing profiles manager
│   │   └── ...                    # Other config modules
│   ├── exceptions/                 # Custom exceptions
│   ├── security/                   # File validation and security
│   └── utils/                      # Utilities
│       ├── progress.py            # ✅ Progress tracking system
│       └── ...                    # Other utilities
├── archive/                        # Versioned files (gitignored)
├── config/                         # Configuration (comprehensive 135-line setup)
├── docs/                           # Documentation
│   └── phase-3.5-interactive-cli-design.md  # ✅ Interactive CLI design
├── tests/                          # Test suite (unit, integration, performance)
└── email-parser-env/               # Virtual environment
```

## Architecture

**Flow**: Email → MIMEParser → ComponentExtractor → Converters → Output

**Key Classes**:

- EmailProcessor (orchestrator)
- BaseConverter (abstract base)
- PDFConverter (MistralAI OCR)
- ExcelConverter (Excel→CSV)
- DocxConverter (DOCX→Markdown)
- ProcessingConfig (settings)

**Phase 3.5 Interactive Components** ✅ NEW:

- InteractiveCLI (main interface)
- EmailScanner (content analysis)
- ProfileManager (processing profiles)
- ProgressTracker (real-time updates)
- ProcessingProfile (configuration presets)

**Output Structure**:

```
output/
├── processed_text/
├── attachments/
├── converted_excel/
├── converted_pdf/
├── converted_docx/                  # ✅ NEW: Week 2 DOCX outputs
│   ├── document.md                 # Main markdown conversion
│   └── document_docx_output/       # Advanced features
│       ├── conversion_manifest.json
│       ├── metadata.json
│       ├── styles.json
│       ├── images/                 # Extracted images
│       └── chunks/                 # AI-ready chunks
└── metadata.json
```

## Email Parser Maintenance Workflow

1. **Project Setup**:
   - Ensure Python 3.12+ is installed (`python --version`)
   - Load project context using available memory tools
   - Activate virtual environment (see platform-specific commands above)

2. **Dependencies**: Install missing requests, psutil, prompt_toolkit if needed
3. **Development**: Archive files before editing, use Edit tool for changes
4. **Testing**: pytest (unit/integration/performance) 
5. **Documentation**: Store using available documentation tools

### Interactive CLI Usage ✅ NEW

```bash
# Start interactive mode (recommended for most users)
python -m email_parser.cli.interactive

# Traditional CLI for automation/scripting
python -m email_parser.cli.main process --input email.eml --output output/
```

### Email Parser Testing

⚠️ **Dependencies**: Ensure all required dependencies are installed before testing

```bash
# Install missing dependencies first  
pip install requests>=2.31.0 psutil>=5.9.0 prompt_toolkit>=3.0.0

# Testing
pytest                          # Full suite
pytest --cov=email_parser      # Coverage
pytest tests/unit/             # Unit tests
pytest tests/integration/      # Integration tests
```

### Email Parser Analysis Workflow

When working with large email processing outputs:

```bash
# Check output file sizes first
ls -lh output/processed_text/
ls -lh output/converted_pdf/
ls -lh output/converted_docx/
```

## Email Parser Documentation Structure

**Documentation Organization**: Organize documentation by topic

```
email-parser/
├── architecture/      # Design decisions 
├── features/         # Implementations
├── bugs/            # Root causes and fixes
├── edge-cases/      # MIME anomalies and handling
└── performance/     # Optimizations and benchmarks
```

**Documentation Examples**:
- Architecture: Design patterns and system overview
- Features: Implementation details and usage
- Bugs: Root cause analysis and solutions

## Current Status

**Phase**: Phase 4: Direct File Conversion ✅ **IMPLEMENTATION COMPLETED (Updated: 2025-07-14)**
**Priority**: ✅ **Phase 4 Complete** - All direct file conversion features implemented and tested
**Next**: Phase 4.5 - Interactive CLI integration for direct conversion workflows

### ✅ Completed Features (Production Ready)

- ✅ PDF Conversion with MistralAI OCR (Production ready - requires API key)
- ✅ Excel to CSV conversion (Production ready)
- ✅ Core email processing infrastructure (Production ready)
- ✅ **DOCX to Markdown converter** (Production ready)
- ✅ **AI-ready document chunking** (3 strategies, production ready)
- ✅ **Enhanced metadata extraction** with analysis and insights (Production ready)
- ✅ **Style preservation system** with CSS/JSON output (Production ready)
- ✅ **Advanced image extraction** with quality control (Production ready)
- ✅ **Complete CLI integration** with all features (Production ready)
- ✅ **Comprehensive error handling** with all custom exceptions (Production ready)
- ✅ **Performance optimization** with benchmarking suite (Production ready)
- ✅ **Interactive CLI Mode** with guided workflows (Production ready - 2025-07-06)
- ✅ **Email content scanning** with smart recommendations (Production ready)
- ✅ **Processing profiles system** with built-in and custom profiles (Production ready)
- ✅ **Real-time progress tracking** with rich terminal UI (Production ready)
- ✅ **Configuration management** with preferences persistence (Production ready)
- ✅ **Batch processing support** with interactive workflow (Production ready)
- ✅ **Direct File Conversion** with standalone document processing (Feature complete)
- ✅ **File Type Detection** with automatic converter selection (Feature complete)
- ✅ **Batch file conversion** with progress tracking (Feature complete)

### Phase 1: PDF→Markdown ✅ COMPLETED (Updated: 2025-07-09)

### Phase 2: DOCX→Structured Output ✅ **COMPLETED (Updated: 2025-07-09)

**All Weeks Complete:** ✅ **PRODUCTION READY**

- [x] **Core Integration** (Week 1) - DOCX converter infrastructure, mammoth integration, basic text extraction, configuration framework
- [x] **Advanced Features** (Week 2) - AI-ready chunking, enhanced metadata, style preservation, image extraction, complete integration, comprehensive testing  
- [x] **Polish & Optimization** (Week 3) - Performance optimization, benchmarking, additional fixtures, documentation, merge completion

**Production Status**: Core features working, fully integrated with main CLI

### Phase 3.5: Interactive CLI Mode ✅ **COMPLETED (Updated: 2025-07-09)

**All Components Complete:** ✅ **PRODUCTION READY**

- [x] **Email Content Scanner** - Intelligent attachment detection with complexity analysis
- [x] **Interactive CLI Framework** - Beautiful guided workflows with prompt toolkit
- [x] **Processing Profiles System** - 5 built-in profiles (Quick, Comprehensive, AI-Ready, Archive, Dev)
- [x] **Smart Recommendations** - Content-based processing suggestions and time estimates
- [x] **Real-time Progress Tracking** - Rich terminal UI with fallback to simple mode
- [x] **Configuration Management** - Profile persistence and API configuration
- [x] **Batch Processing Support** - Multi-email processing with progress tracking
- [x] **User Experience Enhancements** - Settings management, help system, preferences

**Production Status**: Fully tested and operational, all bugs resolved, comprehensive error handling

### Phase 4: Direct File Conversion ✅ **IMPLEMENTATION COMPLETED (Updated: 2025-07-14)**

**Objective**: Enable standalone file conversion without email wrapper ✅ **ACHIEVED**

**Core Features Implemented**:
- [x] DirectFileConverter implementation
- [x] File type auto-detection
- [x] Integration with existing converters
- [x] Batch conversion support  
- [x] CLI commands (convert, convert-batch)

**Technical Components**:
- `email_parser/cli/file_converter.py` - Direct conversion interface ✅ Working
- `email_parser/utils/file_detector.py` - File type detection ✅ Working
- `email_parser/converters/*_converter.py` - Standalone methods added ✅ Working

**Success Criteria Met**:
- ✅ All three converters (PDF, DOCX, Excel) work standalone
- ✅ Batch processing operational
- ✅ CLI commands fully functional and tested
- ✅ Maintains backward compatibility with email processing
- ✅ Error handling and file validation working

### Roadmap

1. **Phase 2** ✅ **COMPLETE**: DOCX converter implementation (Production Ready)
2. **Phase 3.5** ✅ **COMPLETE**: Interactive CLI Mode (Production Ready - 2025-07-06)
3. **Phase 4** ✅ **COMPLETE**: Direct File Conversion (Feature Complete - 2025-07-14)
4. **Phase 4.5** 🎯 **NEXT**: Interactive CLI integration for direct conversion and unified API
5. **Phase 5**: Advanced content analysis features and additional file formats
6. **Phase 6**: Production deployment and scaling

## Configuration

See `config/default.yaml` for comprehensive configuration options (135 lines) including:

- **PDF conversion**: MistralAI API settings, extraction modes, image processing
- **Security**: File validation, size limits, malware protection  
- **Performance**: Caching, memory management, parallel processing
- **API resilience**: Circuit breaker patterns, retry logic, connection pooling
- **Error handling**: Graceful degradation, logging, recovery options

Key settings:

```yaml
# Essential configuration sections
processing:
  convert_pdf: true
  convert_excel: true
security:
  max_attachment_size: 10000000  # 10MB
pdf_conversion:
  api_key_env: "MISTRALAI_API_KEY"
  extraction_mode: "all"  # text/images/all
```

## CLI Examples

### Interactive Mode (Recommended) ✅ NEW

```bash
# Start interactive mode with guided workflows
python -m email_parser.cli.interactive

# Interactive mode features:
# - Email content scanning with smart recommendations
# - Processing profile selection (Quick, Comprehensive, AI-Ready, Archive, Dev)
# - Real-time progress tracking with beautiful UI
# - Batch processing support with guided workflow
# - Configuration management and API setup
# - Preferences persistence across sessions
```

### Traditional CLI Mode

```bash
# Basic
python -m email_parser process --input email.eml --output output/

# With conversions
python -m email_parser process --input email.eml --output output/ --convert-excel --convert-pdf --pdf-mode all

# DOCX with Week 2 features (ALL ENABLED)
python -m email_parser process --input email.eml --output output/ --convert-docx --docx-chunking --docx-images --docx-styles

# Advanced DOCX processing with custom settings
python -m email_parser process --input email.eml --output output/ --convert-docx --docx-chunk-size 1500 --docx-chunk-overlap 150 --docx-chunk-strategy semantic --docx-metadata --docx-comments

# Batch with all converters and Week 2 features
python -m email_parser batch --input emails/ --output output/ --convert-excel --convert-pdf --pdf-mode all --convert-docx --docx-chunking --docx-images --docx-styles
```

### Direct File Conversion ✅ **PRODUCTION READY** (Phase 4 Complete)

```bash
# Convert single file directly (without email context)
python -m email_parser.cli.main convert --file document.pdf --output output/

# Convert single DOCX with full features
python -m email_parser.cli.main convert --file report.docx --output output/

# Batch convert all supported files in directory
python -m email_parser.cli.main convert-batch --directory documents/ --output output/

# Batch convert with file pattern and recursive search
python -m email_parser.cli.main convert-batch --directory docs/ --output output/ --pattern "*.pdf" --recursive

# Supported file types: PDF, DOCX, XLSX, XLS
# Features: Automatic file type detection, progress tracking, batch processing, error handling
# Status: All commands tested and working (2025-07-14)
```


## Email Parser Production Guidelines

1. **Branch**: Currently on feature/phase-4-direct-file-conversion (Phase 4 complete, ready for merge)
2. **Dependencies**: All dependencies installed and verified (requirements.txt up to date)
3. **Testing**: 161 tests passing, focus on edge cases, MIME variants, large files
4. **Security**: Validate inputs, sanitise outputs, protect API keys
5. **Monitoring**: Track performance metrics, error rates, user feedback
6. **Known Issues**: Interactive CLI has Unicode encoding issues on Windows (functional but display problems)


## Phase 2: DOCX Converter Integration ✅ PRODUCTION READY

### Integration Strategy

**Approach**: Wrapper-based integration preserving docx-processor functionality
**Timeline**: 3 weeks (2025-06-28 to 2025-07-01) ✅ COMPLETED (Updated: 2025-07-09)
**Status**: Merged to `main` and production ready

### Production Architecture

```
email_parser/
├── converters/
│   ├── base_converter.py      # Abstract base
│   ├── pdf_converter.py       # PDF converter (production ready)  
│   ├── excel_converter.py     # Excel converter (production ready)
│   ├── docx_converter.py      # ✅ DOCX converter (production ready)
│   └── docx/                  # ✅ DOCX processing modules
│       ├── __init__.py        # Module exports and interfaces
│       ├── chunking.py        # ✅ AI-ready chunking (production ready)
│       ├── metadata_extractor.py  # ✅ Enhanced metadata (production ready)
│       ├── style_extractor.py     # ✅ Style preservation (production ready)
│       └── image_handler.py       # ✅ Advanced image extraction (production ready)
```

### Production Dependencies

```txt
mammoth>=1.6.0          # DOCX parsing and HTML conversion
beautifulsoup4>=4.12.0  # HTML manipulation
lxml>=4.9.0            # XML processing support
tiktoken>=0.5.0        # Token counting for AI chunking
python-docx>=0.8.11    # Enhanced DOCX metadata access
```

All dependencies installed and tested in production environment.

### Production Configuration Schema

```yaml
docx_conversion:
  enabled: true
  max_file_size: 52428800  # 50MB
  
  # Output options
  output_format: "both"  # json, html, both
  extract_tables: true
  
  # AI-ready chunking
  enable_chunking: true
  max_chunk_tokens: 2000
  chunk_overlap: 200
  
  # Metadata extraction
  extract_metadata: true
  extract_styles: true
  include_comments: true
  
  # Image handling
  extract_images: true
  image_quality: 85
  max_image_size: 1200
```

All configuration options tested and validated in production.

## PDF Conversion Implementation Details (Completed 2025-06-28)

### MistralAI OCR Integration

**Implementation Pattern**:

1. Upload PDF to MistralAI Files API using `client.files.upload()`
2. Obtain signed URL via `client.files.get_signed_url()`
3. Process via OCR endpoint using `client.ocr.process()`
4. Extract markdown and images from response pages

**Key Changes Made**:

- `email_parser/converters/pdf_converter.py`: Full OCR implementation
- Model: Updated to `mistral-ocr-latest` from `pixtral-12b-2409`
- API: Changed from `chat.complete()` to `ocr.process()` endpoint
- Response: Handle page-based structure with `response.pages[*].markdown`
- Line 952: Fixed `usage_info` attribute access

**API Configuration**:

- Endpoint: `client.ocr.process()` with document upload pattern
- Model: `mistral-ocr-latest`
- Cost: ~$0.001 per page

## Email Parser Emergency Recovery

- **Corruption**: Check archive/, git history, recreate venv 
- **Performance**: Profile with cProfile, check API limits
- **Security**: Disable feature, archive, audit, rotate keys

## Email Parser Standards

- **Python**: Black, Google docstrings, type hints
- **Security**: Input validation, path safety, API encryption
- **Performance**: Lazy loading, streaming, progress indicators

---
**Remember**: This tool makes emails AI-friendly. Every feature supports that mission.
