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
│   └── utils/            # Utilities
├── archive/              # Versioned files (gitignored)
├── config/               # Configuration
├── docs/                 # Documentation
├── tests/                # Test suite
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
3. **Archive**: Use native copy before changes
4. **Edit**: Use edit_block() for changes
5. **Test**: pytest (unit/integration/performance)
6. **Document**: Save insights to Basic-Memory

## Testing & Quality

```bash
# Testing
pytest                          # Full suite
pytest --cov=email_parser      # Coverage
pytest tests/unit/             # Specific

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
**Phase**: PDF Conversion (Week 2)  
**Priority**: MistralAI OCR integration

### Phase 1: PDF→Markdown (12-16 weeks)

- ✅ Converter infrastructure
- 🔄 MistralAI API integration
- 🔄 Test coverage
- ⏳ CLI integration

### Roadmap

1. PDF conversion completion
2. Summary generator
3. Batch processing
4. Claude API integration

## Configuration

```yaml
# config/default.yaml
processing:
  convert_pdf: true
  convert_excel: true
security:
  max_attachment_size: 10000000  # 10MB
pdf:
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
2. **Use**: Native copy + edit_block for efficiency
3. **Document**: Insights in Basic-Memory, not code
4. **Test**: Edge cases, MIME variants, large files
5. **Secure**: Validate inputs, sanitize outputs, protect API keys

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
