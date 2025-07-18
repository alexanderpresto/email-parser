# Personal Email Parser Environment Configuration

**Personal Development Environment**: Windows 11 Pro | PowerShell/Git Bash | User: alexp | Timezone: America/Winnipeg

> This file contains my personal environment-specific configurations. Do not commit to repository.

## Personal Environment Setup

```bash
# Personal Windows paths
export PROJECTS_ROOT="D:\Users\alexp"
export DEV_PATH="D:\Users\alexp\dev"
export VAULT_PATH="D:\Users\alexp\vault"
export PROJECT_PATH="D:\Users\alexp\dev\email-parser"
export PYTHONPATH="D:\Users\alexp\dev\email-parser;D:\Users\alexp\dev\email-parser\src"

# Personal virtual environment activation (Windows Git Bash/Claude Code)
source email-parser-env/Scripts/activate

# PowerShell reference (for personal use)
# .\email-parser-env\Scripts\Activate.ps1
```

## Personal MCP Server Configuration

```yaml
# My current MCP server setup (as of 2025-07-14)
Available Tools:
  basic-memory: Personal memory management and project notes
  obsidian-dev: Development vault integration  
  context7: Library documentation (resolve-library-id → get-library-docs)
  mcp-server-time: Timestamps/timezones for America/Winnipeg
  sequential-thinking: Complex analysis and planning
  playwright: Browser automation for testing
  ide: VS Code integration for diagnostics and code execution

# Personal memory management
get_current_project() && list_directory(".")
switch_project("dev")  # Personal development project
```

## Personal Workflow

```bash
# My session startup routine
build_context("memory://email-parser/*", timeframe="1 week")
get_current_project()  # Should show email-parser or dev
recent_activity("1 week") 

# My archival pattern (MANDATORY before editing)
cp "file.py" "archive/file_$(date +%Y-%m-%d_%H%M).py"

# My testing workflow  
black . && isort . && mypy . && flake8 . && pytest --cov=src && bandit -r src/
```

## Personal API Keys and Services

```bash
# My API configurations (use your own)
export MISTRALAI_API_KEY="[MY_MISTRAL_API_KEY]"
export GEMINI_API_KEY="[MY_GEMINI_API_KEY]"

# My personal database connections
# [Your database server instances would go here]
```

## Personal Gemini CLI Integration

```bash
# My Gemini CLI setup for large file analysis
# File size thresholds I use:
# Email text files >100KB → Route to Gemini automatically
# PDF conversion outputs >50KB → Consider Gemini for analysis
# DOCX conversion outputs >75KB → Use Gemini for content extraction
# Metadata files >20KB → Use Gemini for pattern analysis

# My preferred models:
# gemini-2.5-pro (default): General email analysis, content summarization
# gemini-2.0-flash-thinking-exp: Complex multi-step email processing workflows
# gemini-exp-1206: Advanced reasoning for compliance and business intelligence

# My delegation workflow
cat output/processed_text/large_email.txt | gemini -p "extract key information and summarize email contents"
cat output/converted_pdf/document.md | gemini -p "analyze document structure and extract actionable items"
find output/converted_docx -name "*.md" -exec cat {} \; | gemini -p "identify common themes across these documents"
```

## Personal Development Environment Details

```bash
# My specific virtual environment path
"D:\Users\alexp\dev\email-parser\email-parser-env"

# My memory project context
switch_project("dev")  # Personal development project
build_context("memory://email-parser/*")

# My obsidian vault integration
obsidian-dev: vault="dev" for ALL PROJECT DOCUMENTATION
```

## Personal Project Status Tracking

### Current Work
- **Current Branch**: feature/phase-4-direct-file-conversion
- **Version**: 2.3.0-dev (personal development branch)
- **Phase**: Phase 4: Direct File Conversion (Core implementation completed 2025-07-09)

### Personal Implementation Notes

#### Completed Components
- `email_parser/cli/file_converter.py` ✅ Direct conversion interface
- `email_parser/utils/file_detector.py` ✅ File type detection
- `email_parser/converters/*_converter.py` ✅ Standalone methods added

#### Success Criteria Met
- ✅ All three converters (PDF, DOCX, Excel) work standalone
- ✅ Batch processing operational
- ✅ CLI commands `convert` and `convert-batch` functional
- ✅ Maintains backward compatibility

## Personal Recovery and Troubleshooting

```bash
# My venv recovery process (Windows)
rm -rf email-parser-env
python -m venv email-parser-env
source email-parser-env/Scripts/activate
pip install -r requirements.txt

# My git operations
git -C "D:\Users\alexp\dev\email-parser" status
git -C "D:\Users\alexp\dev\email-parser" diff

# My backup locations
archive/ # Versioned files
"D:\Users\alexp\dev\backup\" # External backup location
```

## Personal Time and Timezone

```bash
# My timezone context
get_current_time("America/Winnipeg")
convert_time("UTC", "12:00", "America/Winnipeg") 
```

## Personal Email Parser Library Documentation

### Email Parser Dependencies I Use
- `mammoth>=1.6.0` → DOCX to HTML conversion patterns
- `mistralai>=1.5.2` → PDF OCR API usage and best practices
- `beautifulsoup4>=4.12.0` → HTML parsing and manipulation
- `tiktoken>=0.5.0` → Token counting for AI-ready chunking
- `python-docx>=0.8.11` → Advanced DOCX metadata extraction
- `openpyxl` → Excel file processing
- `pillow` → Image handling and optimization

### My Documentation Lookup Workflow
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

## Personal Testing & Quality Standards

### My Testing Commands
```bash
# Activate virtual environment first
source email-parser-env/Scripts/activate

# Full test suite
pytest

# With coverage
pytest --cov=email_parser

# Specific test categories
pytest tests/unit/
pytest tests/integration/

# Quality checks
black email_parser tests
isort email_parser tests
mypy email_parser
bandit -r email_parser
```

## Personal Preferences

- Language: Canadian English, Metric, ISO dates (YYYY-MM-DD), 24h time
- Quality: TDD, clear docs with examples, factual only
- Archival: MANDATORY before any file edit
- Virtual Environment: ALWAYS activate before Python work
- Context: Load project memory at session start
- Documentation: Store in obsidian vault="dev"
- Platform: Windows-only development (no more WSL2)

## Personal Performance Benchmarks

- Single file conversion: ~3-5 seconds overhead
- Batch processing efficiency: 85% vs sequential
- Memory usage stable up to 100 files

---

**Note**: This configuration is specific to my personal Windows development environment. Contributors should create their own `.claude/CLAUDE.md` with their environment-specific paths and configurations.