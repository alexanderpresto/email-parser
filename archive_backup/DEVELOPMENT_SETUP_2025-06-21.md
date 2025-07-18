# Email Parser Development Setup

## Virtual Environment Setup

This project uses a Python virtual environment for dependency isolation.

### Initial Setup (One-time)

```powershell
# Navigate to project directory
cd "D:\Users\alexp\dev\email-parser"

# Create virtual environment
python -m venv email-parser-env

# Activate virtual environment (Windows PowerShell)
.\email-parser-env\Scripts\Activate.ps1

# Install package in development mode
pip install -e .
```

### Daily Development Workflow

```powershell
# Navigate to project directory
cd "D:\Users\alexp\dev\email-parser"

# Activate virtual environment
.\email-parser-env\Scripts\Activate.ps1

# Your virtual environment is now active!
# Run tests, development commands, etc.

# When done, deactivate (optional)
deactivate
```

### Verification

To verify the setup is working:

```powershell
# With virtual environment activated
python -c "import email_parser; print('Success!')"
python -m email_parser --help
```

### Notes

- Virtual environment directory `email-parser-env/` is excluded from git
- Always activate the virtual environment before development
- Dependencies are isolated from global Python installation
- Use `pip list` to see installed packages in the current environment

### Troubleshooting

If you get permission errors with PowerShell execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
