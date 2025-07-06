# Interactive CLI Mode - User Interface Mockups

## 1. Welcome Screen

### Default Welcome
```
╔══════════════════════════════════════════════════════════════════════╗
║                      Email Parser v2.2.0                             ║
║                     Interactive Mode                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  📧 Welcome to Email Parser Interactive Mode!                       ║
║                                                                      ║
║  What would you like to do?                                         ║
║                                                                      ║
║  [1] Process a single email                                         ║
║  [2] Batch process multiple emails                                  ║
║  [3] Quick scan (preview without processing)                        ║
║  [4] Configure settings                                             ║
║  [5] Exit                                                          ║
║                                                                      ║
║  💡 Tip: Press '?' at any time for help                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
Select option [1-5]: 
```

### First-Time User Welcome
```
╔══════════════════════════════════════════════════════════════════════╗
║                      Email Parser v2.2.0                             ║
║                  First Time Setup Detected                           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  👋 Welcome! Let's get you started with Email Parser.               ║
║                                                                      ║
║  This tool helps you:                                               ║
║  ✓ Extract content from email attachments                          ║
║  ✓ Convert PDFs, Word docs, and Excel files                        ║
║  ✓ Prepare content for AI/LLM processing                           ║
║                                                                      ║
║  Would you like to:                                                 ║
║  [1] See a quick demo                                               ║
║  [2] Configure API keys (for PDF conversion)                        ║
║  [3] Start processing emails                                        ║
║  [4] Learn more about features                                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
Select option [1-4]: 
```

## 2. Email Selection Interface

### Single Email Selection
```
╔══════════════════════════════════════════════════════════════════════╗
║                     Select Email to Process                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Enter email file path:                                             ║
║  > /home/user/emails/report.eml                                     ║
║                                                                      ║
║  Or drag and drop the file here (if terminal supports)             ║
║                                                                      ║
║  [Tab] Browse files  [Enter] Confirm  [Esc] Cancel                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### File Browser View
```
╔══════════════════════════════════════════════════════════════════════╗
║                         Browse Emails                                ║
╠══════════════════════════════════════════════════════════════════════╣
║ 📁 /home/user/emails/                                               ║
║ ├── 📧 invoice_2025_01.eml          (245 KB)  2025-01-15 09:30    ║
║ ├── 📧 meeting_notes.eml            (1.2 MB)  2025-01-14 14:22    ║
║ ├── 📧 quarterly_report.eml         (3.4 MB)  2025-01-13 16:45    ║
║ ├── 📧 newsletter_january.eml       (567 KB)  2025-01-12 08:15    ║
║ └── 📁 archived/                                                    ║
║                                                                      ║
║ [↑↓] Navigate  [Enter] Select  [Space] Preview  [Esc] Cancel      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 3. Email Scanning Output

### Detailed Scan Results
```
Scanning: quarterly_report.eml
[████████████████████████████████████████] 100% Complete

╔══════════════════════════════════════════════════════════════════════╗
║                      📧 Email Analysis Complete                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Subject: Q4 2024 Financial Report & Projections                    ║
║  From:    Sarah Chen <cfo@techcorp.com>                           ║
║  Date:    January 13, 2025 4:45 PM                                ║
║  Size:    3.4 MB                                                   ║
║                                                                      ║
║  📎 Attachments Found: 4                                            ║
║  ┌─────────────────────────────────────────────────────────────┐  ║
║  │ 1. Q4_Financial_Report.pdf          (1.8 MB)               │  ║
║  │    → Complex PDF with 24 pages                             │  ║
║  │    → Contains: Charts, Tables, Images                      │  ║
║  │    → Estimated OCR time: 30-45 seconds                     │  ║
║  │                                                             │  ║
║  │ 2. Revenue_Analysis.xlsx            (456 KB)               │  ║
║  │    → 5 worksheets detected                                 │  ║
║  │    → Contains: Pivot tables, Formulas                      │  ║
║  │    → Quick conversion available                            │  ║
║  │                                                             │  ║
║  │ 3. Executive_Summary.docx           (234 KB)               │  ║
║  │    → 12 pages with formatting                              │  ║
║  │    → Contains: Headers, Lists, Tables                      │  ║
║  │    → AI-ready chunking recommended                         │  ║
║  │                                                             │  ║
║  │ 4. Company_Logo.png                 (45 KB)                │  ║
║  │    → Image file (1200x400px)                               │  ║
║  │    → Direct extraction available                           │  ║
║  └─────────────────────────────────────────────────────────────┘  ║
║                                                                      ║
║  ⏱️  Total estimated processing time: 45-60 seconds                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Press [Enter] to see recommendations, or [S] to skip
```

### Quick Scan Summary
```
✓ Scan Complete: quarterly_report.eml

📊 Quick Summary:
• 4 attachments (2.5 MB total)
• 1 PDF, 1 Excel, 1 Word doc, 1 image
• Estimated processing: ~1 minute
• Recommended profile: "comprehensive"

[P]rocess now  [D]etailed view  [S]kip  [?]Help
```

## 4. Processing Recommendations

### Detailed Recommendations
```
╔══════════════════════════════════════════════════════════════════════╗
║                    🤖 Processing Recommendations                     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Based on your email content, we recommend:                         ║
║                                                                      ║
║  ✅ PDF Conversion (HIGH PRIORITY)                                  ║
║     • Complex document with mixed content                           ║
║     • Enable MistralAI OCR for best results                        ║
║     • Extract both text and images                                 ║
║                                                                      ║
║  ✅ Excel Conversion (RECOMMENDED)                                  ║
║     • Convert to CSV format                                        ║
║     • Preserve all worksheets                                      ║
║     • Maintain formulas as values                                  ║
║                                                                      ║
║  ✅ DOCX Conversion (RECOMMENDED)                                   ║
║     • Convert to markdown format                                   ║
║     • Enable AI chunking (2000 tokens)                            ║
║     • Preserve formatting metadata                                 ║
║                                                                      ║
║  ⚡ Quick Actions:                                                  ║
║  [1] Use "Comprehensive" profile (all features)                    ║
║  [2] Use "AI-Ready" profile (optimized for LLMs)                   ║
║  [3] Use "Quick" profile (basic extraction)                        ║
║  [4] Customize settings                                            ║
║                                                                      ║
║  💰 Estimated API cost: ~$0.03 (MistralAI OCR)                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
Select option [1-4]: 
```

### Custom Settings Interface
```
╔══════════════════════════════════════════════════════════════════════╗
║                      Customize Processing Settings                   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  📄 PDF Processing:                                                 ║
║     [✓] Enable conversion                                           ║
║     [✓] Use MistralAI OCR                                          ║
║     Extraction mode: (a)ll ← [t]ext only  [i]mages only           ║
║     Image quality: [======75%======] ← → to adjust                 ║
║                                                                      ║
║  📊 Excel Processing:                                               ║
║     [✓] Enable conversion                                           ║
║     [✓] Convert all sheets                                         ║
║     [ ] Preserve formulas                                          ║
║                                                                      ║
║  📝 DOCX Processing:                                                ║
║     [✓] Enable conversion                                           ║
║     [✓] AI-ready chunking                                          ║
║     Chunk size: [====2000 tokens====] ← → to adjust                ║
║     Chunk strategy: (s)emantic ← [f]ixed  [p]aragraph             ║
║     [✓] Extract images                                             ║
║     [✓] Preserve styles                                            ║
║                                                                      ║
║  [Space] Toggle  [↑↓] Navigate  [Enter] Confirm  [Esc] Cancel     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 5. Progress Indicators

### Detailed Progress View
```
╔══════════════════════════════════════════════════════════════════════╗
║                    Processing: quarterly_report.eml                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Overall Progress:                                                  ║
║  [████████████████████░░░░░░░░░░░░░░] 55% | 2.4/4.3 MB           ║
║                                                                      ║
║  ✅ Email Parsing .......................... Complete (2s)         ║
║  ✅ Metadata Extraction .................... Complete (1s)         ║
║  ⏳ PDF Conversion (Q4_Financial_Report.pdf)                       ║
║     └─ [███████████░░░░░░░░░] Page 15/24 | OCR in progress       ║
║  ⏸️  Excel Conversion ...................... Pending               ║
║  ⏸️  DOCX Conversion ....................... Pending               ║
║                                                                      ║
║  📊 Current Operation: Extracting charts from page 15              ║
║                                                                      ║
║  System Resources:                                                  ║
║  CPU: [██░░░░░░░░] 23%  Memory: [███░░░░░░░] 287/1024 MB         ║
║                                                                      ║
║  Time: 00:23 elapsed | ~00:37 remaining                            ║
║                                                                      ║
║  [P]ause  [C]ancel  [V]erbose logs                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Compact Progress View
```
Processing quarterly_report.eml...
[████████████░░░░░░░░] 60% | PDF: page 15/24 | 00:23/01:00 | 287 MB
```

### Batch Processing Progress
```
╔══════════════════════════════════════════════════════════════════════╗
║                       Batch Processing Progress                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Processing 12 emails from /home/user/emails/                       ║
║                                                                      ║
║  Overall: [████████░░░░░░░░░░░░] 4/12 emails | 33%               ║
║                                                                      ║
║  ✅ invoice_2025_01.eml ............... Complete (15s)            ║
║  ✅ meeting_notes.eml ................. Complete (42s)            ║
║  ✅ newsletter_january.eml ............ Complete (8s)             ║
║  ⏳ quarterly_report.eml                                           ║
║     └─ [████████████░░░░░░░░] 60% | Converting attachments       ║
║  ⏸️  budget_proposal.eml ............... Pending                  ║
║  ⏸️  contract_draft.eml ................ Pending                  ║
║  ⏸️  presentation_deck.eml ............. Pending                  ║
║  ... and 5 more                                                    ║
║                                                                      ║
║  Success: 3 | Warnings: 0 | Errors: 0                             ║
║  Estimated time remaining: ~4 minutes                              ║
║                                                                      ║
║  [Enter] View details  [S]kip current  [P]ause  [C]ancel all     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 6. Results Display

### Processing Complete - Success
```
╔══════════════════════════════════════════════════════════════════════╗
║                    ✅ Processing Complete!                           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Email: quarterly_report.eml                                        ║
║  Duration: 47 seconds                                               ║
║  Output: /home/user/output/quarterly_report/                        ║
║                                                                      ║
║  📊 Results Summary:                                                ║
║  ├── ✓ Email text extracted (4.2 KB)                              ║
║  ├── ✓ Metadata saved (metadata.json)                             ║
║  ├── ✓ PDF converted:                                             ║
║  │   ├── Text: Q4_Financial_Report.md (124 KB)                   ║
║  │   └── Images: 12 extracted to converted_pdf/images/           ║
║  ├── ✓ Excel converted:                                           ║
║  │   └── 5 CSV files in converted_excel/                         ║
║  └── ✓ DOCX converted:                                            ║
║      ├── Text: Executive_Summary.md (45 KB)                      ║
║      └── Chunks: 8 files in chunks/ (AI-ready)                   ║
║                                                                      ║
║  📁 Total output size: 1.8 MB (23 files)                          ║
║                                                                      ║
║  What's next?                                                       ║
║  [O]pen output folder  [P]rocess another  [B]atch mode  [E]xit   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Processing Complete - With Warnings
```
╔══════════════════════════════════════════════════════════════════════╗
║                 ⚠️  Processing Complete with Warnings                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Email: complex_report.eml                                          ║
║  Duration: 1 minute 23 seconds                                      ║
║                                                                      ║
║  ✅ Successful:                                                     ║
║  • Email text extracted                                             ║
║  • Excel files converted (3/3)                                      ║
║  • DOCX converted with chunking                                     ║
║                                                                      ║
║  ⚠️  Warnings:                                                       ║
║  • PDF conversion: 2 pages had OCR issues                          ║
║    - Page 7: Low quality scan, partial text extracted             ║
║    - Page 15: Handwritten content not recognized                  ║
║  • 1 corrupted image skipped (IMG_broken.jpg)                     ║
║                                                                      ║
║  💡 Suggestions:                                                    ║
║  • Re-scan pages 7 and 15 at higher resolution                    ║
║  • Check original PDF quality                                       ║
║                                                                      ║
║  [V]iew detailed log  [R]etry with different settings  [C]ontinue ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 7. Error Handling

### API Key Configuration
```
╔══════════════════════════════════════════════════════════════════════╗
║                    ⚠️  API Key Required                              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  PDF conversion requires a MistralAI API key.                       ║
║                                                                      ║
║  You can:                                                           ║
║  [1] Enter API key now (recommended)                               ║
║  [2] Skip PDF conversion                                            ║
║  [3] Save key to environment file                                  ║
║  [4] Learn more about MistralAI                                    ║
║                                                                      ║
║  Note: API keys are never stored in plain text                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
Select option [1-4]: 1

Enter your MistralAI API key: ************************************
✓ API key validated successfully!
```

### Processing Error
```
╔══════════════════════════════════════════════════════════════════════╗
║                      ❌ Processing Error                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Failed to process: large_presentation.eml                          ║
║                                                                      ║
║  Error: Memory limit exceeded                                       ║
║  The email attachments (125 MB) exceed the configured limit.       ║
║                                                                      ║
║  Options:                                                           ║
║  [1] Increase memory limit temporarily                             ║
║  [2] Process attachments individually                              ║
║  [3] Skip large attachments                                        ║
║  [4] Use reduced quality settings                                  ║
║  [5] Cancel                                                         ║
║                                                                      ║
║  💡 Tip: You can adjust limits in Settings > Performance           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
Select option [1-5]: 
```

## 8. Settings and Configuration

### Main Settings Menu
```
╔══════════════════════════════════════════════════════════════════════╗
║                         Settings & Configuration                     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  [1] Processing Profiles                                            ║
║      Manage and customize processing profiles                       ║
║                                                                      ║
║  [2] API Configuration                                             ║
║      Configure MistralAI and other API keys                        ║
║                                                                      ║
║  [3] Performance Settings                                           ║
║      Memory limits, parallel processing, timeouts                   ║
║                                                                      ║
║  [4] Output Options                                                ║
║      File naming, directory structure, formats                      ║
║                                                                      ║
║  [5] Display Preferences                                            ║
║      Progress style, color themes, verbosity                       ║
║                                                                      ║
║  [6] Advanced Settings                                              ║
║      Security, logging, experimental features                       ║
║                                                                      ║
║  [0] Back to main menu                                             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
Select option [0-6]: 
```

### Profile Management
```
╔══════════════════════════════════════════════════════════════════════╗
║                       Processing Profiles                            ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Available Profiles:                                                ║
║                                                                      ║
║  [1] 🚀 Quick (Default)                                            ║
║      Fast processing, minimal conversions                          ║
║                                                                      ║
║  [2] 📊 Comprehensive                                              ║
║      All features enabled, balanced performance                     ║
║                                                                      ║
║  [3] 🤖 AI-Ready ← Currently Active                               ║
║      Optimized for LLM processing, semantic chunking              ║
║                                                                      ║
║  [4] 🗄️  Archive                                                    ║
║      Preserve everything, maximum quality                          ║
║                                                                      ║
║  [5] 🔧 Custom Profile 1                                           ║
║      Your custom settings                                          ║
║                                                                      ║
║  Actions:                                                           ║
║  [E]dit profile  [C]reate new  [D]elete  [S]et default           ║
║  [I]mport profile  [X]export profile  [B]ack                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
Select profile [1-5] or action: 
```

## 9. Help System

### Context-Sensitive Help
```
╔══════════════════════════════════════════════════════════════════════╗
║                          📚 Help - Email Scanning                    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Email scanning analyzes your email to:                            ║
║  • Detect all attachments and their types                          ║
║  • Estimate processing time and complexity                         ║
║  • Recommend optimal processing settings                           ║
║                                                                      ║
║  Attachment Types:                                                  ║
║  • PDF: Portable Document Format files                             ║
║  • DOCX: Microsoft Word documents                                  ║
║  • XLSX: Microsoft Excel spreadsheets                              ║
║  • Images: PNG, JPG, GIF formats                                   ║
║                                                                      ║
║  Keyboard Shortcuts:                                                ║
║  • Enter: Accept recommendation                                     ║
║  • C: Customize settings                                           ║
║  • S: Skip current item                                            ║
║  • ?: Show this help                                               ║
║  • Esc: Go back                                                    ║
║                                                                      ║
║  [M]ore topics  [T]utorial  [B]ack to scanning                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 10. Confirmation Dialogs

### Processing Confirmation
```
╔══════════════════════════════════════════════════════════════════════╗
║                      Confirm Processing Settings                     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Ready to process with these settings:                             ║
║                                                                      ║
║  Profile: AI-Ready                                                  ║
║  • ✓ PDF conversion with OCR (all content)                        ║
║  • ✓ Excel to CSV conversion                                      ║
║  • ✓ DOCX to Markdown with AI chunking                           ║
║  • ✓ Image extraction (quality: 85%)                              ║
║                                                                      ║
║  Estimated time: 45-60 seconds                                     ║
║  Estimated cost: ~$0.03 (API usage)                               ║
║                                                                      ║
║  Output directory:                                                  ║
║  /home/user/output/quarterly_report_2025-01-15_143022/            ║
║                                                                      ║
║  [Y]es, process  [N]o, go back  [S]ave these settings            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
Confirm [Y/n/s]: 
```

## Design Principles

1. **Clarity**: Every screen clearly shows what's happening
2. **Efficiency**: Common tasks require minimal interaction
3. **Flexibility**: Power users can customize everything
4. **Accessibility**: Works in all terminal environments
5. **Feedback**: Always show progress and status
6. **Recovery**: Graceful handling of errors with options
7. **Consistency**: Similar actions have similar interfaces
8. **Help**: Context-sensitive help always available