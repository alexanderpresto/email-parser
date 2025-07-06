# CLAUDE-DESKTOP.md - Email Parser Project Instructions

**Project-Specific Instructions**: This file contains only email parser project-specific instructions for Windows/Claude Desktop. Universal Windows development patterns are maintained in `/mnt/d/Users/alexp/dev/settings/claude-personal-preferences.md`.

## Cross-Reference

For Claude Code (running IN WSL2/Linux), see: [CLAUDE.md](CLAUDE.md)

## Critical Setup

```bash
# ALWAYS FIRST: Ensure correct project
get_current_project() → IF ≠ "dev" → switch_project("dev")

# Production main branch (no feature branches needed)
wsl -d Ubuntu-24.04 git branch --show-current  # Should show: main

# Project Location:
WSL2 Path: /home/alexp/dev/email-parser
Windows Access: \\wsl.localhost\Ubuntu-24.04\home\alexp\dev\email-parser
```

## Quick Reference

```bash
# Memory: build_context("memory://email-parser/*")
# Time: mcp-server-time:get_current_time("America/Winnipeg")
# Obsidian: Use `obsidian` MCP tool with vault="dev" for ALL PROJECT DOCUMENTATION

# File operations (Windows paths for Claude Desktop):
list_directory("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser")
read_file("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser\\file.py")
write_file("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser\\file.py", content)

# ALWAYS activate venv before Python work (Windows-style venv):
wsl -d Ubuntu-24.04 source /home/alexp/dev/email-parser/email-parser-env/Scripts/activate
```

## Email Parser Testing & Quality

⚠️ **Dependencies**: Ensure `requests` and `psutil` are installed before testing

```bash
# Install missing dependencies first
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pip install requests>=2.31.0 psutil>=5.9.0"

# Testing
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pytest"                          # Full suite
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pytest --cov=email_parser"      # Coverage
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pytest tests/unit/"             # Unit tests
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pytest tests/integration/"      # Integration tests

# Quality
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && black email_parser tests"       # Format
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && isort email_parser tests"       # Imports
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && mypy email_parser"             # Types
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && bandit -r email_parser"        # Security
```

## CLI Examples

```bash
# Basic
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -m email_parser process --input email.eml --output output/"

# With conversions
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -m email_parser process --input email.eml --output output/ --convert-excel --convert-pdf --pdf-mode all"

# DOCX with Week 2 features (ALL ENABLED)
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -m email_parser process --input email.eml --output output/ --convert-docx --docx-chunking --docx-images --docx-styles"

# Advanced DOCX processing with custom settings
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -m email_parser process --input email.eml --output output/ --convert-docx --docx-chunk-size 1500 --docx-chunk-overlap 150 --docx-chunk-strategy semantic --docx-metadata --docx-comments"

# Batch with all converters and Week 2 features
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -m email_parser batch --input emails/ --output output/ --convert-excel --convert-pdf --pdf-mode all --convert-docx --docx-chunking --docx-images --docx-styles"
```

## Email Parser Windows Integration

### File Operations (Desktop Commander)

```bash
# Email parser specific file operations
list_directory("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser")
read_file("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser\\file.py")
write_file("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser\\file.py", content)
```

### Email Parser Virtual Environment

```bash
# Activate email parser virtual environment (required before all Python work)
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate"

# Check email parser virtual environment status
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -c 'import sys; print(sys.prefix)'"
```

## Current Status

**Version**: 2.2.0 (main branch)  
**Phase**: Phase 3.5 Interactive CLI Mode ✅ **COMPLETED 2025-07-06**  
**Priority**: 🎯 **PRODUCTION READY** - Interactive CLI Mode Complete, All Features Operational

### ✅ Completed Features (Production Ready)

- ✅ **Interactive CLI Mode** with guided workflows (Production ready - 2025-07-06)
- ✅ **Email content scanning** with smart recommendations (Production ready)
- ✅ **Processing profiles system** with built-in and custom profiles (Production ready)
- ✅ **Real-time progress tracking** with rich terminal UI (Production ready)
- ✅ **Batch processing support** with interactive workflow (Production ready)
- ✅ PDF Conversion with MistralAI OCR (Production ready - requires API key)
- ✅ Excel to CSV conversion (Production ready)
- ✅ **DOCX to Markdown converter** (Production ready)
- ✅ Core email processing infrastructure (Production ready)

### Interactive CLI Usage (Windows)

```bash
# Start interactive mode (recommended for most users)
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -m email_parser.cli.interactive"

# Traditional CLI for automation/scripting
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -m email_parser.cli.main process --input email.eml --output output/"
```

## Email Parser Production Guidelines

1. **Branch**: Work on main branch (all features production ready)
2. **Dependencies**: Install missing requests/psutil before development
3. **Testing**: Focus on edge cases, MIME variants, large files
4. **Security**: Validate inputs, sanitise outputs, protect API keys
5. **Monitoring**: Track performance metrics, error rates, user feedback

## Email Parser Common Patterns

### Running Email Parser Scripts

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -m email_parser"
```

### Installing Email Parser Dependencies

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pip install requests psutil"
```

### Email Parser Git Operations

```bash
wsl -d Ubuntu-24.04 git -C /home/alexp/dev/email-parser status
wsl -d Ubuntu-24.04 git -C /home/alexp/dev/email-parser add .
wsl -d Ubuntu-24.04 git -C /home/alexp/dev/email-parser commit -m "message"
```

---
**Remember**: When on Windows, EVERY command to WSL2 needs the `wsl -d Ubuntu-24.04` prefix.
