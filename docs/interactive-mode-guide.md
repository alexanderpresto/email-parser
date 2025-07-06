# Interactive Mode Guide

## Overview

Email Parser's Interactive Mode provides an intuitive, guided interface for processing emails with smart recommendations, real-time progress tracking, and pre-configured processing profiles.

## Getting Started

### Prerequisites

Interactive mode requires additional dependencies:

```bash
pip install rich prompt-toolkit
```

### Launching Interactive Mode

```bash
# Start interactive mode
python -m email_parser --interactive

# Or use the short flag
python -m email_parser -i
```

## Features

### 1. Email Content Scanning

Interactive mode automatically scans your emails to:

- **Detect Attachments**: Identifies PDFs, Word docs, Excel files, and images
- **Analyze Complexity**: Estimates processing time and resource requirements
- **Generate Recommendations**: Suggests optimal processing settings

### 2. Smart Processing Profiles

Choose from pre-configured profiles optimized for different scenarios:

#### 🚀 Quick Processing
- **Best for**: Simple emails with minimal attachments
- **Features**: Fast processing, basic conversions only
- **Time**: Fastest processing speed

#### 📊 Comprehensive  
- **Best for**: Balanced processing with all features
- **Features**: All conversions enabled, optimal quality
- **Time**: Moderate processing time

#### 🤖 AI-Ready
- **Best for**: Content intended for AI/LLM processing
- **Features**: Semantic chunking, clean markdown output
- **Time**: Optimized for AI consumption

#### 🗄️ Archive Mode
- **Best for**: Important documents requiring maximum quality
- **Features**: Highest quality settings, complete preservation
- **Time**: Longest processing time

#### 🔧 Development
- **Best for**: Testing and debugging
- **Features**: Verbose logging, debug information
- **Time**: Variable (includes profiling overhead)

### 3. Real-Time Progress Tracking

Interactive mode provides detailed progress information:

- **Overall Progress**: Shows completion percentage and time estimates
- **Task Breakdown**: Displays current operations (PDF OCR, DOCX conversion, etc.)
- **Resource Monitoring**: Tracks memory and CPU usage
- **Rich Visuals**: Uses progress bars, spinners, and color coding

### 4. Intelligent Recommendations

The system analyzes your email content and provides recommendations:

#### Profile Recommendations
- Suggests optimal profiles based on attachment types and complexity
- Considers file sizes, content types, and processing goals

#### Converter Settings
- **PDF Processing**: Recommends OCR modes based on content complexity
- **DOCX Conversion**: Suggests chunking strategies for large documents  
- **Excel Handling**: Advises on multi-sheet processing

#### Performance Optimizations
- Memory limit adjustments for large files
- Parallel processing recommendations
- Resource usage warnings

#### Security Considerations
- Alerts for large or potentially risky attachments
- Malware scanning recommendations
- File size and type warnings

## User Interface

### Welcome Screen

```
╔══════════════════════════════════════════════════════════════╗
║                   Email Parser v2.2.0                        ║
║                  Interactive Mode                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📧 Welcome to Email Parser Interactive Mode!               ║
║                                                              ║
║  What would you like to do?                                 ║
║                                                              ║
║  [1] Process a single email                                 ║
║  [2] Batch process multiple emails                          ║
║  [3] Quick scan (preview without processing)                ║
║  [4] Configure settings                                     ║
║  [5] Exit                                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Email Analysis Results

```
📧 Email Analysis Complete
─────────────────────────────────────────────────────────

Subject: Q4 2024 Financial Report
From:    cfo@company.com  
Date:    January 13, 2025 4:45 PM
Size:    3.4 MB

📎 Attachments Found: 3

  1. Q4_Financial_Report.pdf (1.8 MB)
     Type: PDF
     Features: Charts, Tables, Images
     
  2. Revenue_Analysis.xlsx (456 KB) 
     Type: XLSX
     Features: Pivot tables, Formulas
     
  3. Executive_Summary.docx (234 KB)
     Type: DOCX  
     Features: Headers, Lists, Tables

⏱️  Estimated processing time: 45-60 seconds
```

### Processing Recommendations

```
🤖 Processing Recommendations
─────────────────────────────────────────────────────────

Based on the email content, we recommend:

  ✓ Use 'Comprehensive' profile for balanced processing
  ✓ Enable MistralAI OCR for PDF with mixed content  
  ✓ Enable DOCX chunking for AI-ready output
  ✓ Convert Excel to CSV format

📋 Suggested Profile: 'comprehensive'
💰 Estimated API cost: ~$0.03 (MistralAI OCR)
```

### Progress Display

```
Processing: quarterly_report.eml

Overall Progress:
[████████████░░░░░░░░] 60% | 3/5 tasks | ETA: 00:25

Current Tasks:
✓ Email parsing complete
✓ Metadata extraction complete  
▶ Converting PDF (page 3/10)...
  └─ [██████░░░░] 60% | Processing images...
○ Converting Excel spreadsheet
○ Converting DOCX document

Memory: 124 MB | CPU: 23% | Time Elapsed: 00:35
```

## Workflows

### Single Email Processing

1. **Launch Interactive Mode**
   ```bash
   python -m email_parser -i
   ```

2. **Select "Process a single email"**

3. **Choose Email File**
   - Enter file path or use file browser
   - Supports drag-and-drop in compatible terminals

4. **Review Scan Results**
   - Examine detected attachments
   - Note complexity and time estimates
   - Review any warnings

5. **Accept Recommendations or Customize**
   - Use suggested profile for optimal results
   - Customize settings if needed
   - Configure output directory

6. **Monitor Progress**
   - Watch real-time progress updates
   - View current operations
   - Monitor resource usage

7. **Review Results**
   - Examine processing summary
   - Open output directory
   - Process additional emails or exit

### Batch Processing

1. **Select "Batch process multiple emails"**

2. **Choose Input Directory**
   - Select folder containing email files
   - System scans for .eml and .msg files

3. **Select Processing Profile**
   - Choose profile suitable for all emails
   - Consider the most complex email in the batch

4. **Configure Output**
   - Set base output directory
   - Each email gets its own subdirectory

5. **Monitor Batch Progress**
   - View overall progress across all files
   - See current file being processed
   - Track success/failure rates

6. **Review Batch Summary**
   - Total files processed
   - Success and failure counts
   - Total processing time

### Quick Scan

1. **Select "Quick scan (preview without processing)"**

2. **Choose Email File**

3. **Review Analysis**
   - See attachment details without processing
   - Get processing recommendations
   - Estimate costs and time

4. **Decide Next Steps**
   - Process immediately with recommended settings
   - Return to main menu
   - Exit application

## Configuration and Settings

### Display Preferences

- **Progress Style**: Choose between rich graphics or simple text
- **Color Themes**: Enable/disable colored output
- **Verbosity**: Control amount of information displayed

### Processing Profiles

- **View Profiles**: See all available processing profiles
- **Create Custom**: Build your own processing profile
- **Edit Existing**: Modify custom profiles
- **Import/Export**: Share profiles between systems

### API Configuration

- **MistralAI Setup**: Configure API key for PDF processing
- **Cost Monitoring**: Track API usage and costs
- **Rate Limiting**: Manage API call frequency

## Advanced Features

### Custom Profiles

Create custom processing profiles for specific use cases:

```
Profile: "legal_documents"
Description: "Optimized for legal document processing"
Settings:
  - High-quality PDF OCR
  - Style preservation for DOCX
  - Metadata extraction
  - Archive-quality output
```

### Keyboard Shortcuts

- **Ctrl+C**: Cancel current operation
- **?**: Show context-sensitive help
- **Tab**: Auto-complete file paths
- **↑↓**: Navigate through options
- **Enter**: Select current option
- **Esc**: Go back to previous menu

### File Browser Integration

When available, interactive mode supports:

- **File Drag-and-Drop**: Drop email files directly into terminal
- **Path Completion**: Tab completion for file paths
- **Recent Files**: Quick access to recently processed emails

## Troubleshooting

### Common Issues

#### Missing Dependencies
```
Error: Interactive mode requires additional dependencies
Solution: pip install rich prompt-toolkit
```

#### API Key Not Configured
```
Error: MistralAI API key required for PDF conversion
Solution: Set MISTRALAI_API_KEY environment variable
```

#### Large File Processing
```
Warning: File exceeds memory limits
Solution: 
  - Increase memory limit in settings
  - Process attachments individually
  - Use 'quick' profile for faster processing
```

#### Terminal Compatibility
```
Issue: Progress bars not displaying correctly
Solution:
  - Use simple progress mode
  - Update terminal software
  - Check terminal color support
```

### Performance Tips

1. **Memory Management**
   - Close other applications before processing large files
   - Increase memory limits for complex documents
   - Use batch processing for multiple small files

2. **Processing Speed**
   - Use 'quick' profile for simple emails
   - Enable parallel processing on multi-core systems
   - Consider 'text-only' mode for large PDFs

3. **API Costs**
   - Review PDF extraction modes
   - Use 'text' mode when images aren't needed
   - Monitor usage in API configuration

## Integration with Existing Workflows

### Command Line Compatibility

Interactive mode is fully compatible with existing CLI commands:

```bash
# Traditional command line
python -m email_parser process --input email.eml --output output/

# Interactive mode 
python -m email_parser -i
```

### Configuration Files

Interactive mode respects existing configuration files while allowing temporary overrides through profiles.

### Output Compatibility

All output formats remain the same:
- Email text extraction
- PDF markdown conversion
- DOCX structured output
- Excel CSV conversion
- Metadata JSON files

## Getting Help

### Built-in Help

- Press **?** at any time for context-sensitive help
- Use the help menu option for detailed information
- Check the settings for configuration guides

### Documentation

- Full documentation: `docs/`
- API reference: `docs/api/`
- Examples: `docs/examples/`

### Support

- Report issues: GitHub Issues
- Feature requests: Discussions
- Community: Discord/Slack channels

## What's Next

Interactive mode represents Phase 3.5 of the Email Parser roadmap. Future enhancements include:

- **Web UI Integration**: Browser-based interface
- **Plugin System**: Custom processing extensions  
- **Cloud Processing**: Remote processing capabilities
- **AI Assistant**: Natural language processing commands
- **Collaborative Features**: Shared processing workflows

---

*Email Parser Interactive Mode - Making email processing intuitive and intelligent.*