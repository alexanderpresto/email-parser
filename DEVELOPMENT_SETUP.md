# Email Parser Production Environment Setup

## 🚨 CRITICAL: Virtual Environment is MANDATORY

**This production-ready project REQUIRES virtual environment activation for ALL Python work.**

## 📋 Platform-Specific Setup Instructions

**IMPORTANT**: Choose the correct setup based on your development environment:

### 🪟 **Claude Code (Windows)**  
Current development environment: Windows 11 Pro with native Python
- **See**: [CLAUDE.md](CLAUDE.md) for project-specific development instructions
- **Personal Setup**: [CLAUDE.local.md](CLAUDE.local.md) for environment-specific configuration
- Uses native Windows commands and Git Bash

**Current Status**: Python 3.12.10, Git Bash environment, Windows-native development
- Platform: `win32` → Windows development environment
- Branch: `feature/phase-4-direct-file-conversion`
- Phase 4: Direct File Conversion ✅ Complete

## Production Environment Checklist

Before ANY Python work on this production system:
1. ✅ Virtual environment exists (`email-parser-env` folder present)
2. ✅ Virtual environment is activated (prompt shows `(email-parser-env)`)
3. ✅ Correct Python interpreter is active (run verification command below)
4. ✅ All production dependencies installed and up to date

## Universal Setup Steps (All Platforms)

### Project Location
- **Windows Path**: `D:\Users\alexp\dev\email-parser`
- **Virtual Environment**: `D:\Users\alexp\dev\email-parser\email-parser-env` (Note: activation issues)

### MistralAI API Setup (Required for PDF Conversion)

The PDF to Markdown conversion feature requires a MistralAI API key:

```bash
# Set as permanent user environment variable
# Windows: Add via System Properties -> Environment Variables
# Or via PowerShell (permanent):
[Environment]::SetEnvironmentVariable("MISTRALAI_API_KEY", "your-api-key-here", "User")

# Linux/Mac: Add to shell profile for permanence
echo 'export MISTRALAI_API_KEY="your-api-key-here"' >> ~/.bashrc

# Temporary session (for testing only)
export MISTRALAI_API_KEY="your-api-key-here"  # Git Bash
set MISTRALAI_API_KEY=your-api-key-here       # PowerShell

```

### Gemini CLI Setup (Optional, Enhanced Analysis)

For intelligent analysis of large email processing outputs (>100KB), optionally install Gemini CLI:

**Platform Availability:**
- ✅ **Windows Git Bash**: Compatible for Claude Code
- ⚠️ **Windows PowerShell**: Limited compatibility
- ❌ **Windows Command Prompt**: Not supported

**Installation (Windows Git Bash):**

```bash
# Install Gemini CLI
pip install gemini-cli

# Authenticate with Gemini CLI (uses OAuth)
gemini auth

# Verify installation
gemini --version
```

**Integration with Email Parser:**
The system automatically routes large files to Gemini CLI for analysis when available, enabling:
- Smart analysis of large email content files (>100KB)
- Advanced business intelligence extraction from attachments
- Autonomous delegation for complex processing tasks

### Verification Commands

To verify the setup is working (adapt command format to your platform):

```bash
# Basic imports check
python -c "import email_parser; print('Email Parser: Success!')"
python -c "import mistralai; print('MistralAI: Success!')"

# Help command
python -m email_parser --help

# API key verification
python -c "import os; print('MistralAI API Key set:', bool(os.environ.get('MISTRALAI_API_KEY')))"
gemini --version  # Verify Gemini CLI authentication

# Gemini CLI verification (WSL2/Linux only)
gemini --version  # Should show version if installed
```

## Daily Development Workflow

**🔴 NEVER run Python commands without virtual environment active!**

### Essential Steps (Windows)
1. Navigate to project directory: `D:\Users\alexp\dev\email-parser`
2. **NOTE**: Virtual environment activation has known issues - using global Python 3.12.10
3. Verify Python version: `python --version` (should show Python 3.12.10)
4. Run your development commands
5. All dependencies installed globally via `pip install -r requirements.txt`

**Note**: Command format varies by platform - see platform-specific instruction files for exact syntax.

## Testing & Quality

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories  
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=email_parser
```

### Development Tools
```bash
# Format code with Black
black email_parser tests

# Sort imports
isort email_parser tests

# Type checking
mypy email_parser

# Security scanning
bandit -r email_parser
```

**Note**: Above commands show the Linux format. Adapt to your platform using the appropriate instruction file.

## Common Issues & Solutions

### Issue: MistralAI API Key Not Found
```
Error: MISTRALAI_API_KEY environment variable not set
```
**Solution**: Set the environment variable as shown above.

### Issue: Module Import Errors
```
ImportError: No module named 'mistralai'
```
**Solution**: Ensure virtual environment is activated and dependencies installed.

### Issue: Wrong Command Format
```
Command not found or permission denied
```
**Solution**: Use platform-appropriate command format from your instruction file.

## Archival Protocol (Development)

**CRITICAL**: Never overwrite existing files. Always archive before modification.

### Universal Archival Rules
1. **Before any file modification**: Archive to `archive/filename_YYYY-MM-DD.ext`
2. **Multiple archives same day**: Use incremental numbering `filename_YYYY-MM-DD_001.ext`
3. **Deprecated files**: Move to `archive/del_filename_YYYY-MM-DD.ext`
4. **Never overwrite archives**: Check for existing files and increment counter

### Platform-Specific Archival Commands

**See your platform-specific instruction file for exact archival command syntax:**
- **WSL2/Linux**: Native `cp` commands
- **Windows**: WSL-prefixed commands

## Benefits of Platform-Specific Approach

- ✅ **Clear command format** for each environment
- ✅ **No command confusion** between platforms  
- ✅ **Platform-optimized workflows**
- ✅ **Reduced errors** from wrong command syntax
- ✅ **Context-appropriate instructions**

## Next Steps

1. **Identify your platform** (linux vs win32)
2. **Open the instruction file** ([CLAUDE.md](CLAUDE.md))
3. **Follow platform-specific setup** and daily workflow
4. **Refer back to this file** for universal concepts and troubleshooting

---
**Remember**: The instruction files contain the complete, platform-specific command sequences. This file provides the conceptual framework that applies to all platforms.