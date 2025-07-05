# Scripts Directory

This directory contains utility scripts for development and testing.

## Scripts

### test_email_generator.py
Generates various test email files for testing the parser:
- Simple text emails
- Complex emails with attachments and inline images
- Emails with Excel attachments
- Batch test emails
- Large emails for performance testing
- Malformed emails for error handling tests

**Usage:**
```bash
# Claude Code (WSL2/Linux):
python scripts/test_email_generator.py

# Claude Desktop (Windows):
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python scripts/test_email_generator.py"
```

This will generate test email files in the current directory.

### ascii_tree.py
Generates an ASCII tree representation of the project directory structure.

**Usage:**
```bash
# Claude Code (WSL2/Linux):
python scripts/ascii_tree.py
# Or to show a specific directory:
python scripts/ascii_tree.py path/to/directory

# Claude Desktop (Windows):
wsl -d Ubuntu-24.04 bash -c "cd /home/alexp/dev/email-parser && source email-parser-env/bin/activate && python scripts/ascii_tree.py"
```

## Adding New Scripts

When adding new utility scripts:
1. Place them in this directory
2. Add documentation here
3. Include proper docstrings in the script
4. Update [CLAUDE.md](../CLAUDE.md) or [CLAUDE-DESKTOP.md](../CLAUDE-DESKTOP.md) if the script is part of the development workflow