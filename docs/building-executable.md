# Building Email Parser as Windows Executable

This guide explains how to build the Email Parser as a standalone Windows executable (.exe) file.

## Prerequisites

- Windows 10 or 11
- Python 3.12+
- All dependencies from `requirements.txt` installed
- PyInstaller (installed via `requirements-build.txt`)

## Quick Build

1. **Install build dependencies:**
   ```bash
   pip install -r requirements-build.txt
   ```

2. **Build the executable:**
   ```bash
   # Using the batch script
   build_exe.bat
   
   # Or directly with PyInstaller
   pyinstaller email_parser.spec
   ```

3. **Find the executable:**
   The built executable will be in `dist/email-parser/email-parser.exe`

## Build Configuration

The build is configured through `email_parser.spec`:

- **Entry point**: `email_parser_exe.py` (wrapper that handles both CLI and interactive modes)
- **Hidden imports**: All email_parser modules and dependencies
- **Data files**: Includes `config/default.yaml`
- **Output**: Multi-file build (exe + dependencies in folder)

## Using the Executable

### Command Line Mode

```bash
# Show help
email-parser.exe --help

# Convert a single file
email-parser.exe convert --file document.pdf --output output/

# Convert batch of files
email-parser.exe convert-batch --directory docs/ --output output/

# Process email with attachments
email-parser.exe process --input email.eml --output output/
```

### Interactive Mode

```bash
# Run without arguments for interactive mode
email-parser.exe

# Or explicitly
email-parser.exe --interactive
```

## Distribution

### Folder Distribution

The `dist/email-parser/` folder contains:
- `email-parser.exe` - Main executable
- `_internal/` - Required libraries and dependencies
- Total size: ~150-200MB

To distribute:
1. Zip the entire `dist/email-parser/` folder
2. Users extract and run `email-parser.exe`

### Single-File Build (Optional)

To create a single portable executable:

1. Uncomment the `exe_onefile` section in `email_parser.spec`
2. Rebuild with `pyinstaller email_parser.spec`
3. Find `email-parser-portable.exe` in `dist/`

Note: Single-file builds are larger and slower to start.

## Environment Variables

The executable requires:
- `MISTRALAI_API_KEY` - For PDF OCR processing (set as system environment variable)

## Troubleshooting

### Missing Dependencies

If you get import errors, add the missing module to `hiddenimports` in `email_parser.spec`.

### Antivirus False Positives

Some antivirus software may flag PyInstaller executables. To resolve:
1. Add an exception for the executable
2. Consider code signing (see below)

### Large File Size

To reduce size:
- Use UPX compression (already enabled)
- Exclude unnecessary modules in `excludes`
- Use `--onefile` with caution (increases startup time)

## Advanced Options

### Code Signing

To sign the executable:
1. Obtain a code signing certificate
2. Use `signtool.exe` after building:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.url dist/email-parser/email-parser.exe
   ```

### Custom Icon

To add a custom icon:
1. Create `resources/icon.ico`
2. The spec file will automatically use it

### Version Information

Edit `version_info.txt` to update:
- File version
- Product version
- Company name
- Copyright information

## Build Artifacts

The build process creates:
- `build/` - Temporary build files (can be deleted)
- `dist/` - Final executable and dependencies
- `*.spec` - Build specification
- `warn-*.txt` - Build warnings (in build/)

## Clean Build

To perform a clean build:
```bash
# Remove previous build artifacts
rmdir /s /q build dist

# Rebuild
pyinstaller email_parser.spec
```