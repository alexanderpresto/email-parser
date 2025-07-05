# Email Parser Documentation

Enterprise-grade email processing system with MIME parsing, PDF to Markdown conversion, security features, and performance optimization.

## Overview

This documentation covers the Email Parser project, an enterprise-grade system designed for processing emails with a focus on:
- MIME parsing
- PDF to Markdown conversion using MistralAI OCR
- DOCX to Markdown conversion with AI-ready features
- Excel to CSV conversion
- Gemini CLI integration for intelligent analysis (Claude Code environments)
- Security implementation
- Performance optimization

## Documentation Sections

- [API Documentation](api/index.md): Technical API references
- [Implementation Guide](implementation/index.md): Internal technical documentation
- [Examples](examples/index.md): Usage examples for common scenarios
- [Project Requirements](requirements/): Comprehensive project requirements
  - [Product Requirements Document](requirements/product_requirements_document.md)
  - [Project Plan & Phasing](requirements/project_plan_and_phasing.md)
  - [Technical Specification](requirements/technical_specification_document.md)
- [Project Specifications](specifications/): Formal project requirements and technical specifications with version history

## What's New in Version 2.2.0

### ✅ DOCX to Markdown Conversion (Phase 2 Complete)
- **AI-ready document chunking** with 3 strategies (token, semantic, hybrid)
- **Enhanced metadata extraction** with comprehensive document analysis
- **Advanced style preservation** with CSS and JSON output formats
- **Embedded image extraction** with quality control and deduplication
- **Complete CLI integration** with all advanced options
- **Comprehensive testing** with 63/63 tests passing (100% success rate)

### PDF to Markdown Conversion (Phase 1 Complete)
- Integrated MistralAI OCR for high-accuracy PDF processing
- Support for text-only, images-only, or combined extraction
- Automatic image extraction and linking
- Multi-page PDF support with optional pagination
- Configurable image filtering by size and count
- Caching for improved performance

### Enhanced Features
- Parallel processing for PDF, Excel, and DOCX conversions
- Improved batch processing capabilities
- API connection pooling for better performance
- Comprehensive error handling for all conversion operations

## Project Information

- **Version:** 2.2.0 (main branch)
- **Created:** 2025-02-25
- **Last Updated:** 2025-07-01
- **Framework:** Enhanced-Intent v3.0
- **Python Version:** 3.12.9
- **Major Dependencies:** mistralai>=1.5.2, mammoth>=1.6.0, tiktoken>=0.5.0, pandas, openpyxl

## Getting Started

Please refer to the README.md file in the project root for installation and basic usage instructions.

### Quick Setup

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up MistralAI API key: `export MISTRALAI_API_KEY="your-key"`
5. Optional: Set up Gemini CLI: `pip install gemini-cli && export GEMINI_API_KEY="your-key"`
6. Run basic example: `python examples/basic_parsing.py`

**Note**: For detailed, platform-specific setup instructions, see:
- [CLAUDE.md](../CLAUDE.md) - Claude Code (WSL2/Linux) instructions
- [CLAUDE-DESKTOP.md](../CLAUDE-DESKTOP.md) - Claude Desktop (Windows) instructions

## Key Features

- **Complete Email Parsing**: Extract all components from complex MIME structures
- **PDF Conversion**: Convert PDF attachments to searchable Markdown with OCR
- **DOCX Conversion**: ✅ AI-ready document processing with advanced features (Week 2 Complete)
  - AI-ready chunking for LLM processing
  - Enhanced metadata extraction and analysis
  - Style preservation with CSS/JSON output
  - Advanced image extraction with quality control
- **Excel Conversion**: Automatically convert Excel files to CSV format
- **Gemini CLI Integration**: Intelligent analysis of large files (>100KB) and advanced processing
  - Automatic delegation for complex tasks and large file analysis
  - Advanced business intelligence extraction
  - Available in Claude Code environments (WSL2/Linux)
- **Security**: Built-in protection against common attack vectors
- **Performance**: Optimized for high-volume processing with caching and parallelization
- **Flexibility**: Configurable processing pipeline for custom workflows