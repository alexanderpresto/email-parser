# Test Fixtures for PDF Converter

This directory contains test files for PDF converter testing.

## File Descriptions

### Valid PDFs
- `valid_simple.pdf` - Simple 1-page PDF with text content
- `valid_multi_page.pdf` - Multi-page PDF for pagination testing
- `valid_with_images.pdf` - PDF containing embedded images
- `large_10mb.pdf` - Large PDF file (~10MB) for size testing

### Invalid/Edge Case PDFs
- `corrupted.pdf` - Corrupted PDF file with damaged structure
- `empty.pdf` - Zero-byte empty file
- `password_protected.pdf` - Password-protected PDF
- `fake.pdf` - Text file with .pdf extension
- `unsupported_version.pdf` - PDF with unsupported version

### Test Utilities
- `generate_test_pdfs.py` - Script to generate test PDF files
- `validate_fixtures.py` - Script to validate test fixture integrity

## Usage

These fixtures are used by:
- Unit tests in `tests/unit/test_pdf_converter.py`
- Integration tests in `tests/integration/test_mistral_api_live.py`
- Error scenario tests in `tests/unit/test_pdf_error_scenarios.py`
- Performance benchmarks in `benchmarks/pdf_converter_benchmark.py`

## Generating Test Files

Run the generation script to create test PDF files:

```bash
python tests/fixtures/generate_test_pdfs.py
```

This will create all necessary test files for the test suite.

## Notes

- Test files are automatically generated and should not be committed to git
- Password for `password_protected.pdf` is "test123"
- Large files are created for performance testing only
- Corrupted files are intentionally malformed for error testing