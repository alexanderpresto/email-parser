# Email Parser Development Environment Setup

## 🚨 CRITICAL: Virtual Environment is MANDATORY

**This project REQUIRES virtual environment activation for ALL Python work.**

## 📋 Platform-Specific Setup Instructions

**IMPORTANT**: Choose the correct setup based on your development environment:

### 🪟 **Windows Development**  
- **See**: [CLAUDE.md](CLAUDE.md) for project-specific development instructions
- **Personal Setup**: [CLAUDE.local.md](CLAUDE.local.md) for environment-specific configuration
- Uses PowerShell or Git Bash commands

### 🐧 **Linux/Mac Development**
- Standard Unix commands and terminal
- Virtual environment with `source` activation
- Package management with system package managers

## Development Environment Checklist

Before ANY Python work on this project:
1. ✅ Virtual environment exists (`email-parser-env` folder present)
2. ✅ Virtual environment is activated (prompt shows `(email-parser-env)`)
3. ✅ Correct Python interpreter is active (run verification command below)
4. ✅ All dependencies installed and up to date

## Universal Setup Steps (All Platforms)

### Project Structure
- **Project Root**: `[YOUR_PROJECT_PATH]/email-parser`
- **Virtual Environment**: `email-parser-env/` (in project root)
- **Dependencies**: See `requirements.txt` for full list

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
```

## Daily Development Workflow

**🔴 NEVER run Python commands without virtual environment active!**

### Essential Steps
1. Navigate to project directory
2. Activate virtual environment:
   ```bash
   # Windows
   .\email-parser-env\Scripts\Activate.ps1  # PowerShell
   source email-parser-env/Scripts/activate  # Git Bash
   
   # Linux/Mac
   source email-parser-env/bin/activate
   ```
3. Verify Python version: `python --version` (should be Python 3.12+)
4. Verify virtual environment: Check that prompt shows `(email-parser-env)`
5. Run your development commands

**Note**: Adapt commands to your specific platform and shell environment.

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

**Note**: Commands shown in standard bash format. Adapt to your platform as needed.

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
**Solution**: Adapt commands to your platform and shell environment. Check that you're using the correct syntax for your operating system.

## Version Control Best Practices

**IMPORTANT**: Follow proper version control workflows for file modifications.

### Git Workflow
1. **Create feature branches** for development work
2. **Commit frequently** with descriptive messages  
3. **Test before committing** to ensure code quality
4. **Use pull requests** for code review before merging

### File Management
- Use git for version control rather than manual archiving
- Follow conventional commit message format
- Keep the repository clean with appropriate `.gitignore` rules

## Benefits of This Setup Approach

- ✅ **Clear development environment** requirements
- ✅ **Consistent dependency management** across platforms
- ✅ **Reliable virtual environment** isolation
- ✅ **Comprehensive testing** and quality tools
- ✅ **Professional development** workflow

## Next Steps

1. **Set up your development environment** following the steps above
2. **Read project documentation** in [CLAUDE.md](CLAUDE.md) and [README.md](README.md)
3. **Run the test suite** to verify your setup is working
4. **Start contributing** following the project's contribution guidelines

---
**Remember**: This file provides the essential development environment setup. Refer to other project documentation for specific development workflows and contribution guidelines.