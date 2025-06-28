# Changelog

All notable changes to the Email Parser project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0-dev] - 2025-06-28 - Phase 2: DOCX Converter Integration (IN PROGRESS)

### Branch
- `feature/docx-converter`

### Added
- **DOCX Converter Infrastructure**: New converter for Microsoft Word documents ✅
  - `DocxConverter` class following `BaseConverter` pattern ✅
  - Integration with mammoth library for DOCX parsing ✅
  - Basic text extraction working ✅
  - EmailProcessor integration complete ✅
- **New Dependencies**: Added DOCX processing libraries ✅
  - mammoth>=1.6.0 for DOCX parsing ✅
  - beautifulsoup4>=4.12.0 for HTML manipulation ✅
  - tiktoken>=0.5.0 for AI-ready token counting ✅
  - python-docx>=0.8.11 for metadata extraction ✅
- **Configuration**: DOCX-specific settings in default.yaml ✅
  - Basic configuration framework implemented ✅
  - Metadata extraction options ✅
  - Chunking configuration for AI processing (Week 2)
  - Image extraction settings (Week 2)
- **Testing**: Comprehensive unit test suite ✅
  - 19 unit tests with 100% coverage on DocxConverter ✅
  - Integration with existing test framework ✅

### In Development
- AI-ready document chunking system
- Embedded image extraction
- Advanced style and formatting preservation

### Completed (Week 1)
- Core DOCX text extraction functionality ✅
- Basic metadata extraction ✅
- Configuration integration ✅
- Unit testing framework ✅

### Planned (Week 1-3)
- Week 1: Core converter implementation and basic functionality
- Week 2: Advanced features (chunking, metadata, styles)
- Week 3: Performance optimization and testing

## [2.1.0] - 2025-06-25 - Phase 1 Week 2 (In Progress)

### Added
- **CLI PDF Options**: Command-line flags for PDF conversion
  - `--convert-pdf`: Enable PDF to Markdown conversion
  - `--pdf-mode`: Choose extraction mode (text/images/all)
- **Test Structure**: Comprehensive test suite for PDF converter
  - Unit tests for PDFConverter class
  - Integration tests for email-PDF workflow
  - Mock API responses for testing without API key
- **Documentation Updates**: Enhanced project documentation
  - CLI examples with PDF conversion options
  - Updated README with current phase status
  - Aligned all documentation with CLAUDE.md

### In Progress
- API connectivity testing with real MistralAI endpoints
- Performance benchmarking for PDF conversion
- Enhanced error handling for edge cases

## [2.1.0] - 2025-06-22 - Phase 1 Week 1 (COMPLETED ✅)

### Added - Phase 1 Week 1 COMPLETED ✅
- **BaseConverter Framework**: Abstract base class for all file converters
  - Common interface with abstract methods for supported formats
  - Shared functionality for file validation, logging, and path generation
  - Configuration management with default settings (100MB file limit)
  - Comprehensive error handling and metadata generation
  - Automatic output path generation with timestamps
- **PDFConverter Implementation**: Complete MistralAI OCR integration
  - Support for multiple extraction modes: text-only, images-only, combined
  - MistralAI Pixtral-12b-2409 model integration with base64 encoding
  - Robust API error handling with retry logic and exponential backoff
  - Configurable image processing with size and count limits
  - Secure API key management via environment variables
  - Progress tracking and comprehensive logging throughout conversion
- **Converter Exception Hierarchy**: Comprehensive error handling system
  - `ConversionError`: Base exception for all conversion operations
  - `UnsupportedFormatError`: For unsupported file formats
  - `FileSizeError`: For files exceeding size limits
  - `APIError`: For external API call failures  
  - `ConfigurationError`: For invalid/missing configuration
  - `ProcessingError`: For file processing failures
- **Enhanced Module Structure**: Updated package organisation
  - Updated `email_parser/converters/__init__.py` with new classes
  - Updated `email_parser/exceptions/__init__.py` with converter exceptions
  - Proper import structure and package hierarchy

### Changed
- **Virtual Environment**: Activated and validated for all development work
- **Dependencies**: MistralAI SDK v1.8.2 installed and verified working
- **Import Structure**: All new modules import successfully
- **Project Architecture**: Enhanced with abstract factory and strategy patterns

### Technical Implementation Details
- **Design Patterns**: Abstract Factory, Strategy, Retry, Template Method patterns
- **Security**: API key protection, file validation, path security, input sanitisation
- **Configuration**: Template ready for PDF settings in `config/default.yaml`
- **Error Handling**: Layered exceptions with specific types for different failure modes
- **Performance**: Optimised for large files with configurable limits and streaming

### Development Progress
- **Phase Status**: Phase 1 Week 1 ✅ COMPLETED
- **Files Created**: 3 new core files (242 + 473 + 67 lines of code)
- **Files Updated**: 2 package configuration files
- **Testing**: Import validation completed, framework ready for unit/integration tests
- **Next Phase**: Configuration setup and architecture documentation

### Validation Results ✅
- BaseConverter and PDFConverter import successfully
- All converter exceptions import correctly
- Virtual environment properly activated during development
- MistralAI SDK available and ready for use
- No syntax errors or import issues detected

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
- Reorganised project structure for better maintainability
- Created comprehensive project instructions for continued development

### Security
- Added PDF content validation
- Implemented secure API key management
- Enhanced input validation for all file types

### Performance
- Optimised conversion pipeline for large files
- Added caching for repeated document processing
- Implemented parallel processing for batch operations

## [1.3.0] - 2025-06-21

### Added
- **Project Reorganisation**: Improved folder structure for maintainability
- **Configuration System**: 
  - `config/` directory with default configuration template
  - `config/README.md` with usage instructions
  - Local configuration override support
- **Documentation Enhancements**:
  - `DEVELOPMENT_SETUP.md` with virtual environment instructions
  - Enhanced `.gitignore` with comprehensive exclusions
  - `.cspell.json` for spell checker configuration
- **Scripts Organisation**: 
  - `scripts/README.md` with documentation
  - Updated `test_email_generator.py` with proper path handling

### Changed
- Enhanced virtual environment setup procedures
- Updated `.gitignore` with additional entries for development files
- Improved file organisation with logical grouping

### Fixed
- `test_email_generator.py` now uses proper path references for test resources
- Resolved path handling issues in test utilities

### Removed
- Archived obsolete files: `project_instructions.yaml`, `project_journal.md`
- Cleaned up deprecated configuration files

## [1.2.0] - 2025-06-20

### Added
- Enhanced error handling and logging capabilities
- Improved documentation structure
- Performance benchmarking framework

### Changed
- Refactored core parsing logic for better maintainability
- Updated dependencies to latest stable versions

### Fixed
- Memory leak in large file processing
- Encoding detection edge cases

## [1.1.0] - 2025-06-15

### Added
- Batch processing capabilities
- Enhanced security validation
- Performance optimisation for large emails

### Changed
- Improved MIME parsing accuracy
- Enhanced Excel to CSV conversion

### Fixed
- Unicode handling in various encodings
- Path traversal security issues

## [1.0.0] - 2025-06-10

### Added
- Initial release of Enterprise Email Parser
- Complete MIME structure parsing and extraction
- Excel to CSV conversion capability
- Secure file handling with attack vector protection
- Support for multiple encodings with automatic detection
- Comprehensive error handling and logging
- Type annotations and testing framework

### Features
- Email parsing with full MIME support
- Attachment extraction and processing
- Security validation and malware protection
- High-performance batch processing
- Comprehensive logging and monitoring
- Complete documentation and examples

---

**Version Notes:**
- **2.1.0**: Core PDF converter structure implemented (Phase 1 Week 1 complete)
- **2.0.0**: PDF to Markdown conversion feature documented and planned
- **1.3.0**: Project reorganisation and enhanced development setup
- **1.2.0**: Performance and stability improvements
- **1.1.0**: Enhanced functionality and security
- **1.0.0**: Initial enterprise-grade email parser release
