# Email Parser Production Environment Setup

## 🚨 CRITICAL: Virtual Environment is MANDATORY

**This production-ready project REQUIRES virtual environment activation for ALL Python work.**

## 📋 Platform-Specific Setup Instructions

**IMPORTANT**: Choose the correct setup based on your development environment:

### 🐧 **Claude Code (WSL2/Linux)**
If you're using Claude Code and running IN WSL2/Ubuntu environment:
- **See**: [CLAUDE.md](CLAUDE.md) for complete setup instructions
- Uses native Linux commands directly (no WSL prefix)

### 🪟 **Claude Desktop (Windows)**  
If you're using Claude Desktop on Windows 11 accessing WSL2:
- **See**: [CLAUDE.md](CLAUDE.md) for project-specific development instructions
- All commands use `wsl -d Ubuntu-24.04` prefix

**Quick Check**: Your environment platform determines which setup to follow:
- Platform: `linux` → Follow [CLAUDE.md](CLAUDE.md) setup
- Platform: `win32` → Adapt commands for Windows environment

## Production Environment Checklist

Before ANY Python work on this production system:
1. ✅ Virtual environment exists (`email-parser-env` folder present)
2. ✅ Virtual environment is activated (prompt shows `(email-parser-env)`)
3. ✅ Correct Python interpreter is active (run verification command below)
4. ✅ All production dependencies installed and up to date

## Universal Setup Steps (All Platforms)

### Project Location
- **WSL2 Path**: `/home/alexp/dev/email-parser`
- **Windows Access** (for Claude Desktop): `\\wsl.localhost\Ubuntu-24.04\home\alexp\dev\email-parser`

### MistralAI API Setup (Required for PDF Conversion)

The PDF to Markdown conversion feature requires a MistralAI API key:

```bash
# Set as environment variable (Linux/WSL2)
export MISTRALAI_API_KEY="your-api-key-here"

# Add to ~/.bashrc for permanent setting
echo 'export MISTRALAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Gemini CLI Setup (Optional, Enhanced Analysis)

For intelligent analysis of large email processing outputs (>100KB), optionally install Gemini CLI:

**Platform Availability:**
- ✅ **Claude Code (WSL2/Linux)**: Full Gemini CLI support via Bash tool
- ❌ **Claude Desktop (Windows)**: Not available due to terminal compatibility limitations

**Installation (WSL2/Linux only):**

```bash
# Install Gemini CLI
pip install gemini-cli

# Set up Gemini API key
export GEMINI_API_KEY="your-gemini-api-key-here"

# Add to ~/.bashrc for permanent setting
echo 'export GEMINI_API_KEY="your-gemini-api-key-here"' >> ~/.bashrc
source ~/.bashrc

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
python -c "import os; print('Gemini API Key set:', bool(os.environ.get('GEMINI_API_KEY')))"

# Gemini CLI verification (WSL2/Linux only)
gemini --version  # Should show version if installed
```

## Daily Development Workflow

**🔴 NEVER run Python commands without virtual environment active!**

### Essential Steps (All Platforms)
1. Navigate to project directory: `/home/alexp/dev/email-parser`
2. **MANDATORY**: Activate virtual environment: `source email-parser-env/Scripts/activate` *(Windows-style venv)*
3. Verify activation shows `(email-parser-env)` in prompt
4. Run your development commands
5. Deactivate when done (optional): `deactivate`

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