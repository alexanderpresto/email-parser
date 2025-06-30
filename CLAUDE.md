# CLAUDE.md - Email Parser Project Instructions

Single source of truth for Email Parser project. Compatible with Claude Desktop (Windows 11) and Claude Code (WSL2/Ubuntu).

## Critical Setup

```bash
# ALWAYS FIRST: Ensure correct project
get_current_project() → IF ≠ "dev" → switch_project("dev")

# CRITICAL FOR PHASE 2: Verify correct branch before ANY work
git branch --show-current → IF ≠ "feature/docx-converter" → STOP
# If on wrong branch:
# 1. DO NOT make any changes
# 2. Alert user: "Currently on [branch_name]. Switch to feature/docx-converter?"
# 3. Wait for explicit confirmation before proceeding

# Platform paths:
Windows: D:\Users\alexp\dev\email-parser
WSL2: /mnt/d/Users/alexp/dev/email-parser
```

## Quick Reference

```bash
# Memory: recent_activity("1 week"), search_notes("query"), build_context("memory://email-parser/*")
# Time: mcp-server-time:get_current_time("America/Winnipeg")
# Files: list_directory(), read_file(), write_file(), edit_block()

# ALWAYS activate venv before Python work:
Windows: .\email-parser-env\Scripts\Activate.ps1
WSL2: source email-parser-env/bin/activate
```

## Archival Protocol (CRITICAL)

**Rule**: Archive before ANY modification to `archive/filename_YYYY-MM-DD.ext`

```powershell
# Efficient: Native copy (zero tokens) + edit_block
# Windows
Copy-Item "D:\...\file.py" "D:\...\archive\file_2025-06-25.py"
# WSL2
cp /mnt/d/.../file.py /mnt/d/.../archive/file_2025-06-25.py

# Then edit with edit_block() for targeted changes
# Multiple same-day: Use _001, _002 suffix
```

## Project Structure

```
email-parser/
├── email_parser/          # Main package
│   ├── cli.py            # CLI entry
│   ├── converters/       # File converters (PDF, Excel)
│   ├── core/             # Processing logic
│   ├── exceptions/       # Custom exceptions
│   ├── security/         # File validation and security
│   └── utils/            # Utilities
├── archive/              # Versioned files (gitignored)
├── config/               # Configuration (comprehensive 135-line setup)
├── docs/                 # Documentation
├── tests/                # Test suite (unit, integration, performance)
└── email-parser-env/     # Virtual environment
```

## Architecture

**Flow**: Email → MIMEParser → ComponentExtractor → Converters → Output

**Key Classes**:

- EmailProcessor (orchestrator)
- BaseConverter (abstract base)
- PDFConverter (MistralAI OCR)
- ExcelConverter (Excel→CSV)
- ProcessingConfig (settings)

**Output Structure**:

```
output/
├── processed_text/
├── attachments/
├── converted_excel/
├── converted_pdf/
└── metadata.json
```

## Development Workflow

1. **Check context**: recent_activity(), search_notes()
2. **Activate venv**: REQUIRED for all Python work
3. **Resolve dependencies**: Install missing requests, psutil if needed
4. **Archive**: Use native copy before changes
5. **Edit**: Use edit_block() for changes
6. **Test**: pytest (unit/integration/performance)
7. **Document**: Save insights to Basic-Memory

## Testing & Quality

⚠️ **Dependencies**: Ensure `requests` and `psutil` are installed before testing

```bash
# Install missing dependencies first
pip install requests>=2.31.0 psutil>=5.9.0

# Testing
pytest                          # Full suite
pytest --cov=email_parser      # Coverage
pytest tests/unit/             # Unit tests (includes test_pdf_converter.py)
pytest tests/integration/      # Integration tests

# Quality
black email_parser tests       # Format
isort email_parser tests       # Imports
mypy email_parser             # Types
bandit -r email_parser        # Security
```

## Knowledge Management

Use Basic-Memory for insights, NOT code files:

```
email-parser/
├── architecture/      # Design decisions
├── features/         # Implementations
├── bugs/            # Root causes
├── edge-cases/      # MIME anomalies
└── performance/     # Optimizations
```

## Current Status

**Version**: 2.2.0-dev (feature/docx-converter branch)  
**Phase**: Phase 2 - DOCX Converter Integration  
**Priority**: ✅ **WEEK 2 COMPLETE** - All Advanced Features Implemented

### ✅ Completed Features (Main Branch)

- ✅ PDF Conversion with MistralAI OCR
- ✅ Excel to CSV conversion
- ✅ Core email processing infrastructure

### ✅ **COMPLETED Development (This Branch) - WEEK 2 DONE**

- ✅ DOCX to Markdown converter integration
- ✅ Mammoth-based text extraction
- ✅ **AI-ready document chunking** (token, semantic, hybrid strategies)
- ✅ **Enhanced metadata extraction** with analysis and insights
- ✅ **Style preservation system** with CSS/JSON output
- ✅ **Advanced image extraction** with quality control
- ✅ **Complete CLI integration** with Week 2 options
- ✅ **Comprehensive error handling** with DocxConversionError
- ✅ **Production configuration** with all features enabled

### Phase 1: PDF→Markdown ✅ COMPLETED

### Phase 2: DOCX→Structured Output ✅ **COMPLETED 2025-06-30**

**Week 1**: Core Integration ✅ COMPLETED

- [x] DOCX converter infrastructure
- [x] Mammoth library integration
- [x] Basic text extraction
- [x] Configuration framework

**Week 2**: Advanced Features ✅ **COMPLETED**

- [x] **AI-ready chunking system** (3 strategies, tiktoken integration)
- [x] **Enhanced metadata extraction** (comprehensive properties + analysis)
- [x] **Style preservation** (fonts, paragraphs, CSS/JSON export)
- [x] **Advanced image extraction** (multi-format, quality control, manifests)
- [x] **Complete integration** (DocxConverter + CLI + config updates)
- [x] **Comprehensive testing** (81/82 tests passing, 98.8% success)

**Week 3**: Polish & Optimization ⏭️ **READY TO START**

- [ ] Performance optimization and benchmarking
- [ ] Additional test fixtures and edge cases
- [ ] Documentation refinement
- [ ] Merge preparation and final validation

### Roadmap

1. **Phase 2** (Current): DOCX converter implementation
2. **Phase 3**: DOCX optimization and performance enhancement
3. **Phase 3.5**: Interactive CLI Mode (3 weeks)
   - Intelligent email content scanning
   - Interactive processing options
   - Smart conversion recommendations
   - Progress indicators and profiles
4. **Phase 4**: Unified document processing API
5. **Phase 5**: Advanced content analysis features
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

```bash
# Basic
python -m email_parser email.eml output/

# With conversions
python -m email_parser email.eml output/ --convert-excel --pdf-mode all

# DOCX with Week 2 features (ALL ENABLED)
python -m email_parser email.eml output/ --convert-docx --docx-chunking --docx-images --docx-styles

# Advanced DOCX processing with custom settings
python -m email_parser email.eml output/ --convert-docx \
  --docx-chunk-size 1500 --docx-chunk-overlap 150 \
  --docx-chunk-strategy semantic --docx-metadata --docx-comments

# Batch with all converters and Week 2 features
python -m email_parser emails/ output/ --batch --parallel \
  --convert-excel --pdf-mode all --convert-docx \
  --docx-chunking --docx-images --docx-styles

# Complete Week 2 DOCX feature demonstration
python -m email_parser email.eml output/ --convert-docx \
  --docx-chunking --docx-chunk-size 2000 --docx-chunk-overlap 200 \
  --docx-chunk-strategy hybrid --docx-metadata --docx-images \
  --docx-styles --docx-comments
```

## Guidelines

1. **Always**: Check project="dev", activate venv, archive first
2. **Branch Verification**: Confirm `feature/docx-converter` branch before DOCX work
3. **Dependencies**: Install missing requests/psutil before development
4. **Use**: Native copy + edit_block for efficiency
5. **Document**: Insights in Basic-Memory, not code
6. **Test**: Edge cases, MIME variants, large files
7. **Secure**: Validate inputs, sanitize outputs, protect API keys

## Phase 2: DOCX Converter Integration (Started 2025-06-28)

### Integration Strategy

**Approach**: Wrapper-based integration preserving docx-processor functionality
**Timeline**: 3 weeks (2025-06-28 to 2025-07-19)
**Branch**: `feature/docx-converter`

### Technical Architecture

```
email_parser/
├── converters/
│   ├── base_converter.py      # Abstract base (existing)
│   ├── pdf_converter.py       # PDF converter (existing)
│   ├── excel_converter.py     # Excel converter (existing)
│   ├── docx_converter.py      # NEW: DOCX converter wrapper
│   └── docx/                  # NEW: DOCX processing modules
│       ├── processor.py       # Core processing from docx-processor
│       ├── chunking.py        # AI-ready chunking
│       ├── metadata_extractor.py
│       ├── style_extractor.py
│       ├── image_handler.py
│       └── html_generator.py
```

### New Dependencies

```txt
mammoth>=1.6.0          # DOCX parsing and HTML conversion
beautifulsoup4>=4.12.0  # HTML manipulation
lxml>=4.9.0            # XML processing support
tiktoken>=0.5.0        # Token counting for AI chunking
python-docx>=0.8.11    # Enhanced DOCX metadata access
```

### Configuration Schema

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

### DOCX Converter Development Workflow

**CRITICAL**: All DOCX converter work MUST be performed on `feature/docx-converter` branch

1. **Branch Verification** (MANDATORY FIRST STEP):

   ```bash
   git branch --show-current
   # Expected: feature/docx-converter
   # If different: STOP and alert user
   ```

2. **Virtual Environment**: Activate before any Python work
3. **Dependencies**: Install mammoth, python-docx, beautifulsoup4, tiktoken
4. **Archive Protocol**: Archive before any file modifications
5. **Testing**: Create comprehensive test fixtures for DOCX files
6. **Documentation**: Update in feature branch, plan for merge

### Implementation Checkpoints

**Week 1 (by 2025-07-05)** ✅ COMPLETED:

- [x] Core DocxConverter class implementation
- [x] Basic text extraction working
- [x] Configuration integration complete
- [x] Unit tests passing

**Week 2 (by 2025-07-12)**:

- [ ] AI chunking system integrated
- [x] Metadata extraction functional (basic implementation complete)
- [ ] Image extraction working
- [x] Integration tests passing (basic DOCX converter tests)

**Week 3 (by 2025-07-19)**:

- [ ] Performance optimization complete
- [ ] Full test coverage achieved
- [ ] Documentation updated
- [ ] Ready for merge to main

## Week 3 Current Priorities (2025-06-28) ✅ COMPLETED

1. ✅ **Dependency Resolution**: Install missing `requests` and `psutil` packages
2. ✅ **API Testing**: Validate MistralAI connectivity with real API key
3. ✅ **MistralAI OCR Implementation**: Complete file upload pattern integration
4. ✅ **Integration Testing**: Complete email-to-PDF workflow validation
5. 🔄 **Documentation**: Update status and align all project documentation

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

## Emergency Recovery

- **Corruption**: Check archive/, git history, recreate venv
- **Performance**: Profile with cProfile, check API limits
- **Security**: Disable feature, archive, audit, rotate keys

## Standards

- **Python**: Black, Google docstrings, type hints
- **Security**: Input validation, path safety, API encryption
- **Performance**: Lazy loading, streaming, progress indicators

---
**Remember**: This tool makes emails AI-friendly. Every feature supports that mission.
