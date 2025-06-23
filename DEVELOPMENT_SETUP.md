# Email Parser Development Setup

## Virtual Environment Setup

This project uses a Python virtual environment for dependency isolation.

### Initial Setup (One-time)

```powershell
# Navigate to project directory
cd "/path/to/email-parser"  # Use your actual project path

# Activate virtual environment (Windows PowerShell)
.\email-parser-env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Linux/Mac/WSL2 Setup

```bash
# Navigate to project directory
cd /path/to/email-parser  # Use your actual project path

# Create virtual environment
python -m venv email-parser-env

# Activate virtual environment
source email-parser-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### MistralAI API Setup (Required for PDF Conversion)

The PDF to Markdown conversion feature requires a MistralAI API key.

#### Windows PowerShell
```powershell
# Set for current session
$env:MISTRALAI_API_KEY = "your-api-key-here"

# Set permanently for user
[Environment]::SetEnvironmentVariable("MISTRALAI_API_KEY", "your-api-key-here", "User")
```

#### Windows Command Prompt
```cmd
# Set for current session
set MISTRALAI_API_KEY=your-api-key-here

# Set permanently
setx MISTRALAI_API_KEY "your-api-key-here"
```

#### Linux/Mac
```bash
# Set for current session
export MISTRALAI_API_KEY="your-api-key-here"

# Add to ~/.bashrc or ~/.zshrc for permanent setting
echo 'export MISTRALAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Daily Development Workflow

```powershell
# Navigate to project directory
cd "/path/to/email-parser"  # Use your actual project path

# Activate virtual environment
.\email-parser-env\Scripts\Activate.ps1

# Verify MistralAI API key is set (optional)
python -c "import os; print('API Key set:', bool(os.environ.get('MISTRALAI_API_KEY')))"

# Your virtual environment is now active!
# Run tests, development commands, etc.

# When done, deactivate (optional)
deactivate
```

### Linux/Mac/WSL2 Daily Workflow

```bash
# Navigate to project directory
cd /path/to/email-parser  # Use your actual project path

# Activate virtual environment
source email-parser-env/bin/activate

# Verify MistralAI API key is set (optional)
python -c "import os; print('API Key set:', bool(os.environ.get('MISTRALAI_API_KEY')))"

# Your virtual environment is now active!
# Run tests, development commands, etc.

# When done, deactivate (optional)
deactivate
```

### Verification

To verify the setup is working:

```powershell
# With virtual environment activated
python -c "import email_parser; print('Email Parser: Success!')"
python -c "import mistralai; print('MistralAI: Success!')"
python -m email_parser --help

# Test MistralAI connection (requires API key)
python -m email_parser test-connection --service mistralai
```

### Running Tests

```powershell
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/test_pdf_converter.py

# Run with coverage
pytest --cov=email_parser

# Run PDF-specific tests
pytest tests/unit/test_pdf_converter.py -v
```

### Development Tools

```powershell
# Format code with Black
black email_parser tests

# Sort imports
isort email_parser tests

# Type checking
mypy email_parser

# Security scanning
bandit -r email_parser
```

### Common Issues

#### Issue: MistralAI API Key Not Found
```
Error: MISTRALAI_API_KEY environment variable not set
```
**Solution**: Set the environment variable as shown above.

#### Issue: Module Import Errors
```
ImportError: No module named 'mistralai'
```
**Solution**: Ensure you've activated the virtual environment and run `pip install -r requirements.txt`

#### Issue: Permission Denied on Activation
```
cannot be loaded because running scripts is disabled on this system
```
**Solution**: Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Notes

- Always activate the virtual environment before development work
- The virtual environment directory (`email-parser-env/`) is git-ignored
- Dependencies are managed in `requirements.txt` and `pyproject.toml`
- PDF conversion features require the MistralAI API key to be set
- Cache directory (`.cache/pdf/`) is created automatically and is git-ignored

## Archival Protocol (Development)

**CRITICAL**: Never overwrite existing files. Always archive before modification.

### Archival Rules for Development

1. **Before any file modification**: Archive to `archive/filename_YYYY-MM-DD.ext`
2. **Multiple archives same day**: Use incremental numbering `filename_YYYY-MM-DD_001.ext`
3. **Deprecated files**: Move to `archive/del_filename_YYYY-MM-DD.ext`
4. **Never overwrite archives**: Check for existing files and increment counter

### Efficient Archival Method

Use native file system operations for maximum efficiency:

#### Windows PowerShell
```powershell
# Check for existing archives
ls archive/

# Copy file using native PowerShell (zero token transmission!)
Copy-Item -Path "email_parser\core\email_processor.py" `
          -Destination "archive\email_processor_2025-06-22.py"

# Make targeted edits after archiving
# Edit specific sections of the file
```

#### Linux/Mac/WSL2
```bash
# Check for existing archives
ls archive/

# Copy file using native bash (zero token transmission!)
cp email_parser/core/email_processor.py archive/email_processor_2025-06-22.py

# Make targeted edits after archiving
# Edit specific sections of the file
```

### Benefits of Native Copy Method

- ✅ **Zero token transmission** for file content
- ✅ **Native file system operation** (fastest possible)
- ✅ **Handles large files effortlessly**
- ✅ **Preserves all file attributes**
- ✅ **Creates archive copy** before modifications
- ✅ **Platform-agnostic approach**

### Example Development Workflow

1. Check for existing archives: `ls archive/filename_*`
2. Archive current version: `Copy-Item` or `cp` command
3. Make targeted modifications to the original file
4. Test changes thoroughly
5. Document changes in project notes