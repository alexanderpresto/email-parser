# Email Parser Project Instructions

## Project Overview

The Email Parser is an enterprise-grade email processing system designed to extract, organize, and convert email content into formats that can be analyzed by Claude and other AI tools. It handles complex MIME structures, extracts attachments, processes inline images, and converts Excel files to CSV format.

## Project Initialization

Before starting any work on this project:

```
IF get_current_project() ≠ "dev":
  → switch_project("dev")
  → IF switch fails → Request user intervention
```

Always ensure you're in the correct project context before making changes.

### Recent Changes (2025-06-21)

- Reorganized folder structure for better maintainability
- Created `config/` directory with default configuration template
- Added README files to `config/` and `scripts/` directories
- Updated `test_email_generator.py` to use proper path references
- Archived obsolete files: `project_instructions.yaml`, `project_journal.md`
- Created `.cspell.json` for spell checker configuration
- Enhanced `.gitignore` with additional entries

### Environment Configuration

- **MCP Tools**:
  - mcp-server-time (for accurate timestamps)
  - desktop-commander (for file operations)
  - basic-memory (for knowledge management)
- **Working Directory**: `D:\Users\alexp\dev\email-parser`
- **Archive Directory**: `D:\Users\alexp\dev\email-parser\archive`

### Project Folder Structure

```
email-parser/
├── .cspell.json               # Spell checker configuration
├── .github/                   # GitHub workflows and templates
├── .gitignore                 # Git ignore rules
├── archive/                   # Archived versions (gitignored)
│   ├── del_*                  # Deprecated files
│   └── *_YYYY-MM-DD.*         # Archived versions
├── benchmarks/                # Performance benchmarking scripts
├── config/                    # Configuration files
│   ├── default.yaml           # Default configuration
│   ├── README.md              # Config usage guide
│   └── local/                 # Local overrides (gitignored)
├── docs/                      # Documentation
│   ├── cli_examples.txt       # CLI usage examples
│   ├── index.md               # Documentation index
│   ├── specifications/        # Detailed specifications
│   └── specs/                 # Project specifications
├── email_parser/              # Main package
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # Main entry point
│   ├── cli.py                 # Command-line interface
│   ├── converters/            # File converters
│   ├── core/                  # Core processing logic
│   ├── exceptions/            # Custom exceptions
│   ├── security/              # Security validators
│   └── utils/                 # Utility functions
├── examples/                  # Example scripts
│   ├── basic_parsing.py       # Simple parsing example
│   ├── batch_processing.py    # Batch processing example
│   └── excel_conversion.py    # Excel conversion example
├── scripts/                   # Utility scripts
│   ├── ascii_tree.py          # Directory tree generator
│   ├── README.md              # Scripts documentation
│   └── test_email_generator.py # Email test data generator
├── tests/                     # Test suite
│   ├── __init__.py            # Test initialization
│   ├── integration/           # Integration tests
│   ├── performance/           # Performance tests
│   ├── unit/                  # Unit tests
│   └── test_image.jpg         # Test resources
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # MIT License
├── README.md                  # Project documentation
├── environment.yml            # Conda environment
├── pyproject.toml            # Python project metadata
├── requirements.txt          # pip requirements
├── setup.py                  # Setup script
└── project-instructions.md   # This file (gitignored)
```

## Archival Protocol

**CRITICAL**: Never overwrite existing files. Always archive before modification.

1. **Before any file modification**: Archive to `archive\filename_YYYY-MM-DD.ext`
2. **Deprecated files**: Move to `archive\del_filename_YYYY-MM-DD.ext`
3. **Project instructions sync**: Must match Claude Project settings
4. **Use desktop-commander** for all file operations to ensure consistent archival

Example archival workflow:

```python
# Before modifying email_processor.py
desktop-commander:move_file(
    source="email_parser/core/email_processor.py",
    destination="archive/email_processor_2025-06-21.py"
)
# Then create new version
desktop-commander:write_file(
    path="email_parser/core/email_processor.py",
    content=new_content
)
```

## Context Retrieval Using Basic-Memory

When working on this project and needing previous context:

1. **Find recent work**: Use `recent_activity()` to discover recent development context
2. **Search specific topics**: Use `search_notes("keywords")` for targeted information
3. **Request clarification**: If context remains unclear, ask user for specific references

Example workflow:

```
# Check recent activity
recent_activity(timeframe="3 days ago", type="note")

# Search for specific implementation details
search_notes("email parser enhancement")

# Find related design decisions
build_context("memory://email-parser/design/*")
```

## Knowledge Management Protocol

Basic-Memory tools build persistent semantic graphs for Obsidian.md integration.

### Appropriate Uses

- **Document patterns**: Discovered edge cases and parsing anomalies
- **Capture decisions**: Technical choices and their rationale
- **Record dependencies**: Integration points and relationships
- **Note opportunities**: Standardization and optimization possibilities

### Inappropriate Uses

- **DO NOT store**: Code files or deliverables (use file system)
- **DO NOT store**: Project documentation (keep in project folder)
- **DO NOT archive**: Old versions (use `/archive/` directory)

### Example Knowledge Capture

```python
# After discovering a parsing edge case
write_note(
    title="MIME Boundary Edge Case - Nested Multipart",
    content="""
    Discovered issue with nested multipart/alternative within multipart/mixed
    when boundary contains special characters. Solution: escape boundary
    regex pattern before matching.
    """,
    folder="email-parser/edge-cases",
    tags=["mime", "parsing", "bug-fix"]
)
```

## Development Workflow

### 1. Feature Development

```
1. Check recent context: recent_activity(timeframe="1 week")
2. Create feature branch documentation in Basic-Memory
3. Implement with test-driven development
4. Archive old versions before updates
5. Document decisions and patterns discovered
```

### 2. Bug Fixes

```
1. Search for related issues: search_notes("error message or component")
2. Create minimal reproduction test
3. Archive current version before fix
4. Implement fix with comprehensive testing
5. Document root cause and solution in Basic-Memory
```

### 3. Performance Optimization

```
1. Profile current implementation
2. Document baseline metrics
3. Implement optimization (archive old version)
4. Measure improvement
5. Record optimization patterns for future use
```

## Enhancement Roadmap

### Phase 1: Core Enhancements (Priority)

1. **Summary Generator**
   - Create unified markdown output combining all email components
   - Include metadata, text, attachment list, and image references
   - Optimize for Claude ingestion

2. **Batch Processing Improvements**
   - Thread relationship detection
   - Conversation reconstruction
   - Duplicate detection and handling

3. **Integration Helper**
   - Analyze email content and suggest relevant files for Claude
   - Create upload manifest with priorities
   - Generate analysis prompts based on content

### Phase 2: Advanced Features

1. **Smart Extraction**
   - Extract structured data (dates, contacts, action items)
   - Identify document types and relationships
   - Create knowledge graph of email content

2. **Security Enhancements**
   - Enhanced malware detection
   - PII detection and redaction options
   - Audit trail generation

3. **Performance Optimization**
   - Streaming processing for large attachments
   - Parallel MIME parsing
   - Intelligent caching system

### Phase 3: Integration Features

1. **Claude API Integration**
   - Direct upload to Claude Projects
   - Batch analysis automation
   - Result aggregation

2. **Workflow Automation**
   - Watch folder monitoring
   - Scheduled processing
   - Webhook notifications

3. **Analytics Dashboard**
   - Processing statistics
   - Error analysis
   - Performance metrics

## Testing Guidelines

### Test Categories

1. **Unit Tests**: Individual component functionality
2. **Integration Tests**: Component interaction
3. **Security Tests**: Malicious input handling
4. **Performance Tests**: Large file and batch processing
5. **Edge Case Tests**: Unusual MIME structures and encodings

### Test Data Management

- Use `scripts/test_email_generator.py` for synthetic test data
- Store real email samples in `tests/fixtures/` (gitignored)
- Document edge cases discovered in Basic-Memory

## Code Style and Standards

### Python Standards

- **Style**: Black formatter with 88-character line length
- **Type Hints**: Required for all public functions
- **Docstrings**: Google style for all modules, classes, and functions
- **Imports**: isort with Black compatibility

### Security Requirements

- Input validation on all external data
- Path traversal prevention
- Size limit enforcement
- Secure temporary file handling

### Performance Guidelines

- Lazy loading for large files
- Streaming processing where possible
- Efficient memory usage for batch operations
- Progress indicators for long-running tasks

## Deployment Considerations

### Package Distribution

- PyPI package: `enterprise-email-parser`
- Conda package: `email-parser`
- Docker image for containerized deployment

### Configuration Management

- Environment variables for sensitive settings
- YAML configuration files for complex options
- Command-line overrides for all settings

### Monitoring and Logging

- Structured logging (JSON format option)
- Performance metrics collection
- Error reporting integration
- Processing audit trails

## Maintenance Protocol

### Regular Tasks

1. **Weekly**: Review and archive old development files
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Performance profiling and optimization
4. **Annually**: Major version planning and roadmap update

### Documentation Updates

- Keep README.md synchronized with features
- Update API documentation on changes
- Maintain CHANGELOG.md for all releases
- Document decisions in Basic-Memory

## Emergency Procedures

### Corruption Recovery

1. Check `archive/` for recent versions
2. Use git history for code recovery
3. Restore from Basic-Memory for design decisions
4. Rebuild from test suite if needed

### Performance Degradation

1. Profile with `cProfile` or `py-spy`
2. Check for memory leaks with `tracemalloc`
3. Review recent changes in archive
4. Implement incremental optimization

### Security Incident

1. Immediately disable affected features
2. Archive compromised versions
3. Audit all recent file operations
4. Document incident and resolution

## Communication Protocols

### Progress Updates

- Use Basic-Memory for development notes
- Update project documentation regularly
- Create summary reports for major milestones

### Issue Tracking

- Document bugs with reproduction steps
- Link fixes to original issue descriptions
- Maintain knowledge base of solutions

### Feature Requests

- Evaluate against project goals
- Document technical feasibility
- Plan implementation approach
- Update roadmap accordingly

---

**Last Updated**: 2025-06-21
**Version**: 1.0.0
**Maintainer**: alexanderpresto
