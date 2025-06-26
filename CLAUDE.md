# CLAUDE.md - Email Parser Project Instructions

Single source of truth for Email Parser project. Compatible with Claude Desktop (Windows 11) and Claude Code (WSL2/Ubuntu).

## Critical Setup

```bash
# ALWAYS FIRST: Ensure correct project
get_current_project() → IF ≠ "dev" → switch_project("dev")

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

**Version**: 2.1.0  
**Phase**: Phase 1 Week 3 - Integration & Testing  
**Priority**: Dependency resolution, API testing, performance optimization

⚠️ **Current Issues**: Missing dependencies (`requests`, `psutil`) need installation

### Phase 1: PDF→Markdown (12-16 weeks)

- ✅ Converter infrastructure (Week 1)
- ✅ MistralAI API integration (Week 2)
- 🔄 Dependency resolution (Week 3)
- 🔄 API connectivity testing
- ⏳ Performance benchmarking

### Roadmap

1. **Week 3**: Dependency resolution, API testing, performance optimization
2. Summary generator integration
3. Batch processing enhancements
4. Claude API integration

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

# Batch
python -m email_parser emails/ output/ --batch --parallel
```

## Guidelines

1. **Always**: Check project="dev", activate venv, archive first
2. **Dependencies**: Install missing requests/psutil before development
3. **Use**: Native copy + edit_block for efficiency
4. **Document**: Insights in Basic-Memory, not code
5. **Test**: Edge cases, MIME variants, large files
6. **Secure**: Validate inputs, sanitize outputs, protect API keys

## Week 3 Current Priorities (2025-06-26)

1. **Dependency Resolution**: Install missing `requests` and `psutil` packages
2. **API Testing**: Validate MistralAI connectivity with real API key
3. **Performance Testing**: Benchmark PDF conversion with various file sizes
4. **Integration Testing**: Complete email-to-PDF workflow validation
5. **Documentation**: Update status and align all project documentation

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
