# CLAUDE-DESKTOP.md - Email Parser Project Instructions (Windows)

Single source of truth for Email Parser project when using Claude Desktop on Windows 11.

**Platform**: `win32` (Windows environment)  
**Context**: You are running on Windows and accessing WSL2 remotely  
**Key Rule**: ALL commands must be prefixed with `wsl -d Ubuntu-24.04`

## Cross-Reference

For Claude Code (running IN WSL2/Linux), see: [CLAUDE.md](CLAUDE.md)

**IMPORTANT**: This file is for Windows/Claude Desktop ONLY. If you're running in WSL2 (platform: linux), use CLAUDE.md instead.

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
wsl -d Ubuntu-24.04 git branch --show-current  # Should show: main

# All Phase 2 features merged and production ready

# Project Location:
WSL2 Path: /home/alexp/dev/email-parser
Windows Access: \\wsl.localhost\Ubuntu-24.04\home\alexp\dev\email-parser
```

## Quick Reference

```bash
# Memory: recent_activity("1 week"), search_notes("query"), build_context("memory://email-parser/*")
# Time: mcp-server-time:get_current_time("America/Winnipeg")
# Obsidian: Use `obsidian` MCP tool with vault="dev" for ALL PROJECT DOCUMENTATION

# File operations (Windows paths for Claude Desktop):
list_directory("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser")
read_file("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser\\file.py")
write_file("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser\\file.py", content)

# ALWAYS activate venv before Python work:
wsl -d Ubuntu-24.04 source /home/alexp/dev/email-parser/email-parser-env/bin/activate
```

## Archival Protocol (CRITICAL)

**Rule**: Archive before ANY modification to `archive/filename_YYYY-MM-DD.ext`

```bash
# WSL2 Copy from Windows:
wsl -d Ubuntu-24.04 cp /home/alexp/dev/email-parser/file.py /home/alexp/dev/email-parser/archive/file_2025-07-05.py

# Then edit with Edit tool for targeted changes
# Multiple same-day: Use _001, _002 suffix
```

## Testing & Quality

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

## Windows Integration Commands

```bash
# File Operations (Desktop Commander)
list_directory("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser")
read_file("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser\\file.py")
write_file("\\wsl.localhost\\Ubuntu-24.04\\home\\alexp\\dev\\email-parser\\file.py", content)

# Terminal Operations (WSL Commands)
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && command"

# Git Operations
wsl -d Ubuntu-24.04 git -C /home/alexp/dev/email-parser status
wsl -d Ubuntu-24.04 git -C /home/alexp/dev/email-parser branch --show-current

# Python Operations (Always with venv activation)
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python command"
```

## Virtual Environment Management

```bash
# Activate virtual environment (required before all Python work)
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate"

# Install dependencies
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pip install package_name"

# Check virtual environment status
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python -c 'import sys; print(sys.prefix)'"
```

## Production Guidelines

1. **Always**: Check project="dev", activate venv, archive first
2. **Branch**: Work on main branch (all features production ready)
3. **Dependencies**: Install missing requests/psutil before development
4. **Use**: WSL commands for all operations
5. **Document**: Insights in Basic-Memory, not code
6. **Test**: Edge cases, MIME variants, large files
7. **Secure**: Validate inputs, sanitise outputs, protect API keys
8. **Monitor**: Performance metrics, error rates, user feedback

## Key Differences from Claude Code

When using Claude Desktop on Windows:

1. **ALL commands** need `wsl -d Ubuntu-24.04` prefix
2. **File paths** use Windows format for tool functions: `\\wsl.localhost\\Ubuntu-24.04\\...`
3. **Complex commands** use `bash -c` wrapper: `wsl -d Ubuntu-24.04 bash -c "cd ... && ..."`
4. **No direct Linux commands** - everything goes through WSL

## Common Patterns

### Running Python Scripts

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python script.py"
```

### Installing Packages

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pip install package"
```

### Running Tests

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && pytest"
```

### Git Operations

```bash
wsl -d Ubuntu-24.04 git -C /home/alexp/dev/email-parser status
wsl -d Ubuntu-24.04 git -C /home/alexp/dev/email-parser add .
wsl -d Ubuntu-24.04 git -C /home/alexp/dev/email-parser commit -m "message"
```

---
**Remember**: When on Windows, EVERY command to WSL2 needs the `wsl -d Ubuntu-24.04` prefix.
