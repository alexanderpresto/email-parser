# CLAUDE.md - Email Parser Project Instructions (Claude Code/WSL2)

Single source of truth for Email Parser project when using Claude Code in WSL2/Ubuntu environment.

**Platform**: `linux` (WSL2/Ubuntu environment)  
**Context**: You are running IN WSL2 - use native Linux commands directly  
**Key Rule**: NO WSL prefix needed - you're already in the Linux environment

## Cross-Reference

For Claude Desktop (Windows), see: [CLAUDE-DESKTOP.md](CLAUDE-DESKTOP.md)

**IMPORTANT**: This file is for Claude Code (WSL2/Linux) ONLY. If you're running on Windows (platform: win32), use CLAUDE-DESKTOP.md instead.

## Memory System Overview

**Basic-Memory**: Claude's persistent memory system enabling conversation continuity across:

- **Time Spans**: Access context from days, weeks, months, or years ago
- **Session Boundaries**: Bridge disconnected conversations seamlessly
- **Context Windows**: Retrieve information beyond current conversation limits

**Primary Commands**:

- `build_context("memory://email-parser/*")` - Load historical project context
- `recent_activity("1 week")` - Review recent work and decisions
- `search_notes("query")` - Find specific past discussions or solutions

## Critical Setup

```bash
# ALWAYS FIRST: Ensure correct project
get_current_project() → IF ≠ "dev" → switch_project("dev")

# Production main branch (no feature branches needed)
git branch --show-current  # Should show: main

# All Phase 2 features merged and production ready

# Project Location:
Project Path: /home/alexp/dev/email-parser
Virtual Environment: /home/alexp/dev/email-parser/email-parser-env
```

## Quick Reference

```bash
# Memory: recent_activity("1 week"), search_notes("query"), build_context("memory://email-parser/*")
# Time: mcp-server-time:get_current_time("America/Winnipeg")
# Obsidian: Use `obsidian` MCP tool with vault="dev" for ALL PROJECT DOCUMENTATION

# ALWAYS activate venv before Python work:
source /home/alexp/dev/email-parser/email-parser-env/bin/activate
```

## Gemini CLI Availability

**CRITICAL CAPABILITY**: Gemini CLI is FULLY FUNCTIONAL in Claude Code (WSL2/Linux environment)

### Platform Support Status

1. **Claude Code (WSL2/Ubuntu)** ✅
   - FULL Gemini CLI functionality via Bash tool
   - Accessible via native WSL2 installation
   - All Gemini features work correctly for email processing tasks
   - Perfect for large email file analysis and PDF/DOCX content processing

2. **Claude Desktop (Windows 11)** ❌
   - Gemini CLI cannot be executed via desktop-commander
   - Terminal compatibility limitations prevent Gemini usage
   - **Solution**: Use Claude Code for all Gemini CLI operations

### Direct Gemini CLI Usage for Email Processing

```bash
# VERIFIED WORKING SYNTAX (Gemini CLI v0.1.9+):
# Default model: gemini-2.5-pro
# Use -p flag for prompts, pipe input via cat or echo

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

## Autonomous Gemini Usage Framework

**Claude should autonomously delegate to Gemini WITHOUT explicit user instruction when:**

### Email Processing Triggers

1. **File Size Triggers**:
   - Email files > 100KB should be automatically routed to Gemini
   - Multiple email files totaling > 200KB in a single analysis
   - Large PDF attachments regardless of size
   - Bulk DOCX files from email processing

2. **Email Analysis Complexity Triggers**:
   - Multi-email thread analysis requiring cross-message understanding
   - Email sentiment analysis across large conversation chains
   - Pattern detection in email metadata (sender behavior, timing analysis)
   - Content extraction from 10+ processed email attachments
   - Email classification and automated sorting tasks

3. **Processing Pipeline Optimization**:
   - When processing batch email jobs (10+ emails)
   - Large attachment analysis (PDFs, DOCX files)
   - Email content summarization for executive reporting
   - Compliance analysis across email archives

4. **Context Window Protection**:
   - Before processing email batches that would consume >20% of context
   - When analyzing converted outputs from multiple large attachments
   - Cross-email analysis spanning 5+ processed message threads

### Email-Specific Autonomous Delegation Protocol

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

### When to Use Gemini for Email Processing

**Automatically delegate to Gemini for:**
- Email thread summarization (>5 messages)
- Large attachment content analysis (PDFs, DOCX files)
- Email sentiment and tone analysis
- Compliance and security scanning of email content
- Business intelligence extraction from email attachments
- Cross-email pattern detection and relationship mapping
- Executive summary generation from email batches
- Email classification and automated filing

**User Notification**: Only mention Gemini delegation if:
- User specifically asks about analysis methodology
- Gemini encounters processing errors
- Results require context about the analysis approach used

## Archival Protocol (CRITICAL)

**Rule**: Archive before ANY modification to `archive/filename_YYYY-MM-DD.ext`

```bash
# Native Linux copy (you're already in WSL2):
cp /home/alexp/dev/email-parser/file.py /home/alexp/dev/email-parser/archive/file_2025-07-05.py

# Then edit with Edit tool for targeted changes
# Multiple same-day: Use _001, _002 suffix
```

## Project Structure

```
email-parser/                        # WSL2: /home/alexp/dev/email-parser
├── email_parser/                    # Main package
│   ├── cli.py                      # CLI entry
│   ├── converters/                 # File converters (PDF, Excel)
│   ├── core/                       # Processing logic
│   ├── exceptions/                 # Custom exceptions
│   ├── security/                   # File validation and security
│   └── utils/                      # Utilities
├── archive/                        # Versioned files (gitignored)
├── config/                         # Configuration (comprehensive 135-line setup)
├── docs/                           # Documentation
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
- ProcessingConfig (settings)

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

## Production Maintenance Workflow

1. **Retrieve context**:
   - `recent_activity("3 days")` - Check recent work
   - `build_context("memory://email-parser/*")` - Load project memory
   - `search_notes("specific issue")` - Find past solutions
2. **Activate venv**: REQUIRED for all Python work
3. **Resolve dependencies**: Install missing requests, psutil if needed
4. **Archive**: Use native copy (you're already in WSL2)
5. **Edit**: Use Edit tool for changes
6. **Process large files**: Use Gemini CLI for files >100KB or complex analysis
7. **Test**: pytest (unit/integration/performance)
8. **Document & Store**:
   - Technical documentation → `obsidian` (vault: "dev")
   - Conversation context & insights → `basic-memory` (for future retrieval)

### Gemini CLI Integration Workflow

When working with large email processing outputs or complex analysis:

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

## Testing & Quality

⚠️ **Dependencies**: Ensure `requests` and `psutil` are installed before testing

```bash
# Install missing dependencies first
cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pip install requests>=2.31.0 psutil>=5.9.0

# Testing
pytest                          # Full suite
pytest --cov=email_parser      # Coverage
pytest tests/unit/             # Unit tests
pytest tests/integration/      # Integration tests

# Quality
black email_parser tests       # Format
isort email_parser tests       # Imports
mypy email_parser             # Types
bandit -r email_parser        # Security
```

## Knowledge Management

**CRITICAL DISTINCTION**: Two separate tools serving different memory and documentation needs:

### 1. Basic-Memory (`basic-memory` MCP tool)

**PRIMARY PURPOSE**: Claude's persistent memory system for context continuity across:

- **Temporal Boundaries**: Days, weeks, months, or years ago
- **Conversation Windows**: Beyond current context limits
- **Session Continuity**: Bridging disconnected conversations

**KEY FUNCTIONS**:

1. **Context Retrieval**: `build_context("memory://email-parser/*")` - Retrieve historical context
2. **Recent Activity**: `recent_activity("1 week")` - Check recent work and decisions
3. **Search History**: `search_notes("query")` - Find past discussions and solutions
4. **Memory Storage**: Personal insights, learnings, debugging discoveries, conversation context
**USAGE SCENARIOS**:

- "What did we discuss about PDF conversion last month?"
- "Continue from where we left off yesterday"
- "What was the solution we found for that MIME parsing issue?"
- "Retrieve context from the architecture discussion in June"

### 2. Obsidian (`obsidian` MCP tool with `vault="dev"`)

**PURPOSE**: ALL FORMAL PROJECT DOCUMENTATION including:

```
email-parser/
├── architecture/      # Design decisions - Tag: #architecture #design
├── features/         # Implementations - Tag: #feature #implementation
├── bugs/            # Root causes - Tag: #bug #root-cause
├── edge-cases/      # MIME anomalies - Tag: #edge-case #mime
└── performance/     # Optimizations - Tag: #performance #optimization
```

**Documentation Guidelines**:

1. **Tool Selection**:
   - Personal insights/learnings → `basic-memory`
   - Project documentation → `obsidian` (vault: "dev")
2. **Tags**: Apply relevant tags from above categories
3. **Linking**: Use `[[Note Name]]` syntax for cross-references in Obsidian

**Obsidian Linking Examples**:

- Architecture: `[[Email Parser Architecture]]`
- Features: `[[DOCX Converter Implementation]]`
- Bugs: `[[PDF Conversion Issues]]`

## Tool Selection Decision Matrix

### When to Use Basic-Memory (`basic-memory`)

#### Primary Use Cases (Persistent Memory)

1. **Retrieving past context**: `build_context("memory://email-parser/*")`
2. **Checking recent work**: `recent_activity("3 days")` or `recent_activity("last week")`
3. **Finding historical solutions**: `search_notes("PDF conversion issue")`
4. **Bridging conversations**: When user references "yesterday", "last month", "that bug we discussed"
5. **Context beyond window**: When current conversation lacks necessary historical context

#### Secondary Use Cases (Knowledge Storage)

1. **Personal insights** from debugging sessions
2. **Learning notes** about Python patterns discovered
3. **Conversation summaries** for future reference
4. **Problem-solution pairs** for quick retrieval
5. **"Aha moments"** and breakthroughs

### When to Use Obsidian (`obsidian` with vault="dev")

1. **Technical specifications** and architecture docs
2. **Feature documentation** and implementation guides
3. **Bug reports** with reproduction steps
4. **API documentation** and integration guides
5. **Design decisions** and rationale
6. **Performance benchmarks** and optimization notes
7. **Edge case documentation** with test scenarios
8. **Project roadmaps** and planning documents

### Decision Rules

1. **Need historical context?** → Basic-Memory (search/retrieve)
2. **Storing conversation context?** → Basic-Memory (for future retrieval)
3. **Creating formal documentation?** → Obsidian
4. **User says "as we discussed"?** → Basic-Memory first, then continue

## Basic-Memory Practical Examples

### Context Retrieval Scenarios

**1. Resuming Previous Work**

```bash
# User: "Let's continue working on that PDF converter bug from last week"
build_context("memory://email-parser/bugs/pdf-converter")
recent_activity("1 week")
```

**2. Historical Problem Lookup**

```bash
# User: "How did we handle that MIME parsing edge case?"
search_notes("MIME parsing edge case")
search_notes("multipart boundary")
```

**3. Project Evolution Tracking**

```bash
# User: "What was our original approach for DOCX conversion?"
build_context("memory://email-parser/features/docx-converter")
search_notes("DOCX converter implementation" after_date="2025-06-01")
```

**4. Cross-Conversation Continuity**

```bash
# New conversation after days/weeks
# User: "Regarding the email parser project..."
recent_activity("2 weeks")  # Get recent context
build_context("memory://email-parser/*")  # Load project context
```

### Memory Storage Best Practices

1. **After Complex Debugging**: Store the problem, process, and solution
2. **Design Decisions**: Record why certain approaches were chosen
3. **Conversation Milestones**: Save key decisions and action items
4. **Learning Moments**: Document new patterns or techniques discovered
5. **Context Bridges**: Create notes that link related conversations

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

## Production Guidelines

1. **Always**: Check project="dev", activate venv, archive first
2. **Branch**: Work on main branch (all features production ready)
3. **Dependencies**: Install missing requests/psutil before development
4. **Use**: Native Linux commands (you're already in WSL2)
5. **Large files**: Automatically delegate to Gemini CLI for files >100KB
6. **Document**: Insights in Basic-Memory, not code
7. **Test**: Edge cases, MIME variants, large files
8. **Secure**: Validate inputs, sanitise outputs, protect API keys
9. **Monitor**: Performance metrics, error rates, user feedback

### Gemini CLI Performance Guidelines

**File Size Thresholds:**
- Email text files >100KB → Route to Gemini automatically
- PDF conversion outputs >50KB → Consider Gemini for analysis
- DOCX conversion outputs >75KB → Use Gemini for content extraction
- Metadata files >20KB → Use Gemini for pattern analysis

**Model Selection Strategy:**
- `gemini-2.5-pro` (default): General email analysis, content summarization
- `gemini-2.0-flash-thinking-exp`: Complex multi-step email processing workflows
- `gemini-exp-1206`: Advanced reasoning for compliance and business intelligence

**Optimization Tips:**
- Batch similar analysis tasks to reduce API calls
- Use piped commands for efficient file processing
- Monitor token usage for cost optimization
- Cache Gemini results for repeated analysis patterns

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

## WSL2 Development Environment

### Key Environment Details

**Project Location**: `/home/alexp/dev/email-parser`  
**Windows Access**: `\\wsl.localhost\Ubuntu-24.04\home\alexp\dev\email-parser`  
**Virtual Environment**: `/home/alexp/dev/email-parser/email-parser-env`

### Platform-Specific Commands

```bash
# File Operations
ls /home/alexp/dev/email-parser
cat /home/alexp/dev/email-parser/file.py

# Git Operations
git -C /home/alexp/dev/email-parser status
git -C /home/alexp/dev/email-parser branch --show-current

# Python Operations (Always with venv activation)
cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python command
```

### Virtual Environment Management

```bash
# Activate virtual environment (required before all Python work)
cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate

# Install dependencies
pip install package_name

# Check virtual environment status
python -c 'import sys; print(sys.prefix)'
```

## Emergency Recovery

- **Corruption**: Check archive/, git history, recreate venv in WSL2
- **Performance**: Profile with cProfile, check API limits
- **Security**: Disable feature, archive, audit, rotate keys

## Standards

- **Python**: Black, Google docstrings, type hints
- **Security**: Input validation, path safety, API encryption
- **Performance**: Lazy loading, streaming, progress indicators
- **Platform**: Native WSL2/Ubuntu commands (you're already inside)
- **Gemini CLI**: Autonomous delegation for >100KB files, intelligent model selection
- **Analysis**: Use Gemini for complex email pattern recognition and business intelligence

---
**Remember**: This tool makes emails AI-friendly. Every feature supports that mission. Gemini CLI integration enables intelligent analysis of large email processing outputs, providing advanced insights and business intelligence from email data.
