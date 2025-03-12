# Enterprise Email Parser

Enterprise-grade email processing system with MIME parsing, security features, and performance optimization.

## Overview

This package provides a robust, secure, and efficient email parsing system for enterprise environments with high volume email processing requirements. It handles complex MIME structures, extracts components securely, and converts Excel attachments to CSV format.

## Features

- **MIME Parsing**: Parse and extract MIME structure from emails
  - Support for multi-part MIME messages
  - Handling of nested MIME structures
  - Extraction of MIME headers and metadata

- **Component Extraction**:
  - Body text extraction (plain and HTML)
  - Attachment identification and extraction
  - Inline image extraction
  - Unique filename generation for all extracted files
  - Positional reference insertion in processed text

- **Excel Conversion**:
  - Conversion of Excel workbook attachments to CSV
  - Support for multiple worksheets
  - User prompt for conversion preferences

- **Security Features**:
  - File type validation
  - Path traversal protection
  - Malicious content detection
  - Size limits and quotas
  - Sanitized filenames

- **Performance Optimization**:
  - Batch processing capability
  - Memory usage optimization
  - Processing speed enhancements

## Installation

### Using Conda (Recommended)

```bash
# Create environment from environment.yml
conda env create -f environment.yml
conda activate email-parser
pip install -e .
