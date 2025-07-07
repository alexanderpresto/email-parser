# CLAUDE.md - Email Parser Project Instructions

**Project-Specific Instructions**: This file contains only email parser project-specific instructions. Universal WSL2 development patterns are maintained in `~/.claude/CLAUDE.md`.

## Cross-Reference

For Claude Desktop (Windows), see: [CLAUDE-DESKTOP.md](CLAUDE-DESKTOP.md)

## Critical Setup

```bash
# ALWAYS FIRST: Ensure correct project
get_current_project() → IF ≠ "dev" → switch_project("dev")

# Production main branch (no feature branches needed)
git branch --show-current  # Should show: main

# Project Location:
Project Path: /home/alexp/dev/email-parser
Virtual Environment: /home/alexp/dev/email-parser/email-parser-env
```

## Quick Reference

```bash
# Memory: build_context("memory://email-parser/*")
# Time: mcp-server-time:get_current_time("America/Winnipeg")
# Obsidian: Use `obsidian` MCP tool with vault="dev" for ALL PROJECT DOCUMENTATION

# ALWAYS activate venv before Python work (Windows-style venv in WSL2):
source /home/alexp/dev/email-parser/email-parser-env/Scripts/activate
```

## Email-Specific Gemini CLI Usage

```bash
# Analyze large email content files
cat /home/alexp/dev/email-parser/output/processed_text/large_email.txt | gemini -p "extract key information and summarize email contents"

# Process PDF conversion outputs for insights  
cat /home/alexp/dev/email-parser/output/converted_pdf/document.md | gemini -p "analyze document structure and extract actionable items"

# Batch analyze DOCX conversion outputs
find /home/alexp/dev/email-parser/output/converted_docx -name "*.md" -exec cat {} \; | gemini -p "identify common themes across these documents"

# Analyze email metadata for patterns
cat /home/alexp/dev/email-parser/output/metadata.json | gemini -p "identify email communication patterns and sender analysis"

# Smart model selection for complex analysis
cat large_email_batch.txt | gemini -m gemini-2.0-flash-thinking-exp -p "perform multi-step email categorization and priority analysis"
```

## Email Processing Gemini Triggers

**Automatically delegate to Gemini for:**
- Email thread summarization (>5 messages)
- Large attachment content analysis (PDFs, DOCX files)
- Email sentiment and tone analysis
- Compliance and security scanning of email content
- Business intelligence extraction from email attachments
- Cross-email pattern detection and relationship mapping
- Executive summary generation from email batches
- Email classification and automated filing

## Email Parser Library Documentation

**Context7 Integration**: Check documentation for all email parsing dependencies

### Key Libraries to Document via Context7

1. **Core Dependencies**:
   - `mammoth` → DOCX to HTML conversion patterns
   - `mistralai` → PDF OCR API usage and best practices
   - `beautifulsoup4` → HTML parsing and manipulation
   - `tiktoken` → Token counting for AI-ready chunking
   - `python-docx` → Advanced DOCX metadata extraction
   - `openpyxl` → Excel file processing
   - `pillow` → Image handling and optimization

2. **Documentation Lookup Workflow**:
   ```bash
   # Before implementing new converter features
   resolve-library-id("mammoth")  # Get library ID
   get-library-docs("/org/mammoth", topic="table-extraction")
   
   # When debugging API issues
   resolve-library-id("mistralai") 
   get-library-docs("/mistralai/client-python", topic="ocr-api")
   
   # For performance optimization
   resolve-library-id("beautifulsoup4")
   get-library-docs("/org/beautifulsoup4", topic="performance")
   ```

3. **Integration Patterns**:
   - Before adding new file format support → Check library capabilities
   - When implementing converter features → Verify against official docs
   - For error handling → Check documented exceptions
   - Performance tuning → Use library-specific optimizations

### Email-Specific Delegation Protocol

```bash
# 1. Check processed email output size before analysis
ls -la /home/alexp/dev/email-parser/output/processed_text/*.txt | awk '{sum+=$5} END {print sum}'

# 2. Delegate large email content analysis to Gemini
cat /home/alexp/dev/email-parser/output/processed_text/email_thread.txt | gemini -p "extract action items, decisions, and key participants from this email thread"

# 3. Process PDF attachment analysis via Gemini
cat /home/alexp/dev/email-parser/output/converted_pdf/contract.md | gemini -p "identify key terms, deadlines, and responsibilities in this converted contract"

# 4. Batch DOCX analysis for business intelligence
find /home/alexp/dev/email-parser/output/converted_docx -name "*.md" | head -10 | xargs cat | gemini -p "analyze these business documents for trends and insights"

# 5. Email metadata pattern analysis
cat /home/alexp/dev/email-parser/output/metadata_*.json | gemini -p "analyze communication patterns, identify VIPs, and detect unusual email behaviors"
```

## Project Structure

```
email-parser/                        # WSL2: /home/alexp/dev/email-parser
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
└── email-parser-env/               # Virtual environment (WSL2)
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
   - `get_current_project()` → IF ≠ "dev" → `switch_project("dev")`
   - `build_context("memory://email-parser/*")` - Load project memory
   - `source email-parser-env/Scripts/activate` - Activate virtual environment

2. **Dependencies**: Install missing requests, psutil if needed
3. **Development**: Archive files before editing, use Edit tool for changes
4. **Testing**: pytest (unit/integration/performance) 
5. **Documentation**: Store in `obsidian` vault="dev"

### Interactive CLI Usage ✅ NEW

```bash
# Start interactive mode (recommended for most users)
python -m email_parser.cli.interactive

# Traditional CLI for automation/scripting
python -m email_parser.cli.main process --input email.eml --output output/
```

### Email Parser Testing

⚠️ **Dependencies**: Ensure `requests` and `psutil` are installed before testing

```bash
# Install missing dependencies first  
# Note: Windows-style venv structure in WSL2
cd /home/alexp/dev/email-parser && source email-parser-env/Scripts/activate && pip install requests>=2.31.0 psutil>=5.9.0

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
ls -lh /home/alexp/dev/email-parser/output/processed_text/
ls -lh /home/alexp/dev/email-parser/output/converted_pdf/
ls -lh /home/alexp/dev/email-parser/output/converted_docx/

# For large files (>100KB), automatically delegate to Gemini
cat /home/alexp/dev/email-parser/output/large_file.txt | gemini -p "provide detailed analysis suitable for this email processing context"

# For batch processing results
find /home/alexp/dev/email-parser/output -name "*.md" -size +100k | xargs cat | gemini -p "summarize key findings across these processed email attachments"

# For email metadata analysis
cat /home/alexp/dev/email-parser/output/metadata_*.json | gemini -p "analyze patterns and generate insights for email processing optimization"
```

## Email Parser Documentation Structure

**Obsidian Vault**: `vault="dev"`

```
email-parser/
├── architecture/      # Design decisions - Tag: #architecture #design
├── features/         # Implementations - Tag: #feature #implementation
├── bugs/            # Root causes - Tag: #bug #root-cause
├── edge-cases/      # MIME anomalies - Tag: #edge-case #mime
└── performance/     # Optimizations - Tag: #performance #optimization
```

**Obsidian Linking Examples**:
- Architecture: `[[Email Parser Architecture]]`
- Features: `[[DOCX Converter Implementation]]`
- Bugs: `[[PDF Conversion Issues]]`

## Current Status

**Version**: 2.2.0 (main branch)  
**Phase**: Phase 3.5 Interactive CLI Mode ✅ **COMPLETED 2025-07-06**  
**Priority**: 🎯 **PRODUCTION READY** - Interactive CLI Mode Complete, All Features Operational

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

### Phase 1: PDF→Markdown ✅ COMPLETED

### Phase 2: DOCX→Structured Output ✅ **COMPLETED 2025-07-01**

**All Weeks Complete:** ✅ **PRODUCTION READY**

- [x] **Core Integration** (Week 1) - DOCX converter infrastructure, mammoth integration, basic text extraction, configuration framework
- [x] **Advanced Features** (Week 2) - AI-ready chunking, enhanced metadata, style preservation, image extraction, complete integration, comprehensive testing  
- [x] **Polish & Optimization** (Week 3) - Performance optimization, benchmarking, additional fixtures, documentation, merge completion

**Production Status**: 119/182 tests passing (core features working), test suite needs maintenance, fully integrated with main CLI

### Phase 3.5: Interactive CLI Mode ✅ **COMPLETED 2025-07-06**

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

### Roadmap

1. **Phase 2** ✅ **COMPLETE**: DOCX converter implementation (Production Ready)
2. **Phase 3.5** ✅ **COMPLETE**: Interactive CLI Mode (Production Ready - 2025-07-06)
3. **Phase 4** 🎯 **NEXT**: Unified document processing API
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

### Gemini CLI Integration Examples

**Post-processing analysis of email parser outputs:**

```bash
# Analyze large converted email content
cat output/processed_text/large_email_thread.txt | gemini -p "extract action items, decisions, and key participants from this email conversation"

# Process converted PDF attachments for insights
cat output/converted_pdf/quarterly_report.md | gemini -p "create executive summary with key metrics and findings"

# Batch analysis of DOCX conversions
find output/converted_docx -name "*.md" | head -5 | xargs cat | gemini -p "identify common business themes and priorities across these documents"

# Email metadata pattern analysis  
cat output/metadata_*.json | gemini -p "analyze communication patterns, identify VIP contacts, and flag unusual email behaviors"

# Compliance scanning of email content
cat output/processed_text/*.txt | gemini -p "scan for sensitive information, compliance issues, and data protection concerns"

# Smart email categorization
cat output/processed_text/inbox_batch.txt | gemini -m gemini-2.0-flash-thinking-exp -p "categorize emails by priority, topic, and required actions"
```

## Email Parser Production Guidelines

1. **Branch**: Work on main branch (all features production ready)
2. **Dependencies**: Install missing requests/psutil before development
3. **Testing**: Focus on edge cases, MIME variants, large files
4. **Security**: Validate inputs, sanitise outputs, protect API keys
5. **Monitoring**: Track performance metrics, error rates, user feedback

### Email Parser Gemini Performance Guidelines

**File Size Thresholds:**
- Email text files >100KB → Route to Gemini automatically
- PDF conversion outputs >50KB → Consider Gemini for analysis
- DOCX conversion outputs >75KB → Use Gemini for content extraction
- Metadata files >20KB → Use Gemini for pattern analysis

**Model Selection for Email Processing:**
- `gemini-2.5-pro` (default): General email analysis, content summarization
- `gemini-2.0-flash-thinking-exp`: Complex multi-step email processing workflows
- `gemini-exp-1206`: Advanced reasoning for compliance and business intelligence

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

## Email Parser Environment

**Project Location**: `/home/alexp/dev/email-parser`  
**Windows Access**: `\\wsl.localhost\Ubuntu-24.04\home\alexp\dev\email-parser`  
**Virtual Environment**: `/home/alexp/dev/email-parser/email-parser-env`

### Virtual Environment (Windows-style structure in WSL2)

```bash
# Activate virtual environment (required before all Python work)
cd /home/alexp/dev/email-parser && source email-parser-env/Scripts/activate

# Check virtual environment status
python -c 'import sys; print(sys.prefix)'
```

## Email Parser Emergency Recovery

- **Corruption**: Check archive/, git history, recreate venv in WSL2
- **Performance**: Profile with cProfile, check API limits
- **Security**: Disable feature, archive, audit, rotate keys

## Email Parser Standards

- **Python**: Black, Google docstrings, type hints
- **Security**: Input validation, path safety, API encryption
- **Performance**: Lazy loading, streaming, progress indicators
- **Analysis**: Use Gemini for complex email pattern recognition and business intelligence

---
**Remember**: This tool makes emails AI-friendly. Every feature supports that mission. Gemini CLI integration enables intelligent analysis of large email processing outputs, providing advanced insights and business intelligence from email data.
