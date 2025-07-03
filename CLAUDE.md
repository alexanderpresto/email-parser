---
TQ_explain: 
TQ_extra_instructions: 
TQ_short_mode: 
TQ_show_backlink: 
TQ_show_cancelled_date: 
TQ_show_created_date: 
TQ_show_depends_on: 
TQ_show_done_date: 
TQ_show_due_date: 
TQ_show_edit_button: 
TQ_show_id: 
TQ_show_on_completion: 
TQ_show_postpone_button: 
TQ_show_priority: 
TQ_show_recurrence_rule: 
TQ_show_scheduled_date: 
TQ_show_start_date: 
TQ_show_tags: 
TQ_show_task_count: 
TQ_show_tree: 
TQ_show_urgency: 
---
# CLAUDE.md - Email Parser Project Instructions

Single source of truth for Email Parser project. Compatible with Claude Desktop (Windows 11) and Claude Code (WSL2/Ubuntu).

## Critical Setup

```bash
# ALWAYS FIRST: Ensure correct project
get_current_project() → IF ≠ "dev" → switch_project("dev")

# Production main branch (no feature branches needed)
git branch --show-current → Should show: main
# All Phase 2 features merged and production ready

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
├── converted_docx/          # ✅ NEW: Week 2 DOCX outputs
│   ├── document.md         # Main markdown conversion
│   └── document_docx_output/  # Advanced features
│       ├── conversion_manifest.json
│       ├── metadata.json
│       ├── styles.json
│       ├── images/         # Extracted images
│       └── chunks/         # AI-ready chunks
└── metadata.json
```

## Production Maintenance Workflow

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

**Version**: 2.2.0 (main branch)  
**Phase**: Phase 3.5 Interactive CLI Mode - Planning Stage  
**Priority**: 🎯 **PRODUCTION READY** - All Core Features Complete, Next Phase Planning

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

### Phase 1: PDF→Markdown ✅ COMPLETED

### Phase 2: DOCX→Structured Output ✅ **COMPLETED 2025-07-01**

**All Weeks Complete:** ✅ **PRODUCTION READY**

- [x] **Core Integration** (Week 1) - DOCX converter infrastructure, mammoth integration, basic text extraction, configuration framework
- [x] **Advanced Features** (Week 2) - AI-ready chunking, enhanced metadata, style preservation, image extraction, complete integration, comprehensive testing  
- [x] **Polish & Optimization** (Week 3) - Performance optimization, benchmarking, additional fixtures, documentation, merge completion

**Production Status**: All 63 Week 2 tests passing, 34% test coverage, fully integrated with main CLI

### Roadmap

1. **Phase 2** ✅ **COMPLETE**: DOCX converter implementation (Production Ready)
2. **Phase 3.5** 🎯 **CURRENT**: Interactive CLI Mode (Planning Stage - 3 weeks)
   - Intelligent email content scanning
   - Interactive processing options  
   - Smart conversion recommendations
   - Progress indicators and profiles
3. **Phase 4**: Unified document processing API
4. **Phase 5**: Advanced content analysis features
5. **Phase 6**: Production deployment and scaling

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
python -m email_parser process --input email.eml --output output/

# With conversions
python -m email_parser process --input email.eml --output output/ --convert-excel --convert-pdf --pdf-mode all

# DOCX with Week 2 features (ALL ENABLED)
python -m email_parser process --input email.eml --output output/ --convert-docx --docx-chunking --docx-images --docx-styles

# Advanced DOCX processing with custom settings
python -m email_parser process --input email.eml --output output/ --convert-docx \
  --docx-chunk-size 1500 --docx-chunk-overlap 150 \
  --docx-chunk-strategy semantic --docx-metadata --docx-comments

# Batch with all converters and Week 2 features
python -m email_parser batch --input emails/ --output output/ \
  --convert-excel --convert-pdf --pdf-mode all --convert-docx \
  --docx-chunking --docx-images --docx-styles

# Complete Week 2 DOCX feature demonstration
python -m email_parser process --input email.eml --output output/ --convert-docx \
  --docx-chunking --docx-chunk-size 2000 --docx-chunk-overlap 200 \
  --docx-chunk-strategy hybrid --docx-metadata --docx-images \
  --docx-styles --docx-comments
```

## Production Guidelines

1. **Always**: Check project="dev", activate venv, archive first
2. **Branch**: Work on main branch (all features production ready)
3. **Dependencies**: Install missing requests/psutil before development
4. **Use**: Native copy + edit_block for efficiency
5. **Document**: Insights in Basic-Memory, not code
6. **Test**: Edge cases, MIME variants, large files
7. **Secure**: Validate inputs, sanitize outputs, protect API keys
8. **Monitor**: Performance metrics, error rates, user feedback

## Phase 2: DOCX Converter Integration ✅ PRODUCTION READY

### Integration Strategy

**Approach**: Wrapper-based integration preserving docx-processor functionality
**Timeline**: 3 weeks (2025-06-28 to 2025-07-01) ✅ COMPLETED EARLY
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

## Phase 3.5 Interactive CLI Mode - Planning (Current Focus)

### Planning Priorities (2025-07-02)

1. 🎯 **Requirements Analysis**: Define interactive CLI mode specifications
2. 🔍 **Email Content Scanner**: Design intelligent attachment detection system
3. 🤖 **Smart Recommendations**: Plan conversion recommendation engine
4. 📊 **Progress Indicators**: Design user experience for batch processing
5. 🔧 **Configuration Profiles**: Plan reusable processing configurations

### Production Maintenance

1. ✅ **API Configuration**: Ensure MistralAI API key setup documented
2. ✅ **Dependency Management**: Monitor and update production dependencies
3. ✅ **Performance Monitoring**: Track processing efficiency metrics
4. ✅ **Error Handling**: Monitor and improve graceful degradation
5. ✅ **Documentation**: Keep production guides current

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
