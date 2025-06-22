# Configuration Directory

This directory contains configuration files for the Email Parser system.

## Files

- `default.yaml` - Default configuration settings
- `local/` - Local configuration overrides (gitignored)

## Usage

The configuration system follows a hierarchy:
1. Default settings from `default.yaml`
2. Local overrides from `local/*.yaml` (if present)
3. Environment variables (prefixed with `EMAIL_PARSER_`)
4. Command-line arguments

## Creating Local Overrides

To create local configuration overrides:

```bash
mkdir -p config/local
cp config/default.yaml config/local/my-config.yaml
# Edit config/local/my-config.yaml as needed
```

Local configuration files are ignored by git to prevent accidental commits of sensitive data.

## Configuration Schema

See `default.yaml` for the complete configuration schema and available options.