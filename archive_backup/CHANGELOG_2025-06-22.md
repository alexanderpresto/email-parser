# Changelog

All notable changes to the Email Parser project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-21

### Added
- **PDF to Markdown Conversion**: Major new feature using MistralAI OCR technology
  - Support for text-only, images-only, or combined extraction modes
  - Automatic image extraction and saving with proper linking
  - Multi-page PDF support with optional pagination
  - Configurable image filtering by size and count
  - Caching system for repeated document processing
  - Comprehensive error handling and retry logic
- **Enhanced Configuration**: New PDF-specific configuration options in `config/default.yaml`
- **API Integration**: MistralAI client integration with connection pooling
- **Security**: PDF content validation to detect malicious content
- **Documentation**: 
  - Product Requirements Document
  - Project Plan with 16-week implementation timeline
  - Technical Specification Document
- **Examples**: PDF conversion examples in documentation

### Changed
- Updated all dependencies to include `mistralai>=1.5.2`
- Enhanced EmailProcessor to route PDFs to the new converter
- Improved batch processing to handle PDFs in parallel
- Updated output directory structure to include `converted_pdf/`
- Expanded error handling to include PDF and OCR-specific exceptions

### Improved
- Performance optimization with API connection pooling
- Memory management for large PDF processing
- Progress tracking for long-running conversions
- Caching strategy for both email and PDF processing

### Acknowledgments
- The PDF to Markdown conversion feature was inspired by the [obsidian-marker](https://github.com/l3-n0x/obsidian-marker) project by [l3-n0x](https://github.com/l3-n0x), which provided valuable insights into MistralAI OCR integration patterns.

## [1.1.0] - 2025-06-10

### Added
- Enhanced Excel conversion capabilities
- Support for multiple sheet selection
- Improved error handling for corrupted Excel files

### Changed
- Updated pandas dependency to 2.0.0
- Improved memory usage for large Excel files

### Fixed
- Excel conversion failing on password-protected files
- Memory leak in batch Excel processing

## [1.0.0] - 2025-02-25

### Added
- Initial release
- Complete MIME structure parsing
- Text and HTML content extraction
- Attachment extraction with security validation
- Inline image extraction
- Excel to CSV conversion
- Batch processing capabilities
- Comprehensive test suite
- Full documentation

### Security
- Path traversal prevention
- Filename sanitization
- File size limits
- Malware scanning hooks

---

*For more details on upcoming features, see the [Enhancement Roadmap](project-instructions.md#enhancement-roadmap) in the project instructions.*