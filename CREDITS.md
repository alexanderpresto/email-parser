# Credits and Acknowledgments

## Inspiration and Design Influences

### PDF to Markdown Conversion Feature

The PDF to Markdown conversion functionality in Email Parser v2.0 was inspired by:

- **[obsidian-marker](https://github.com/l3-n0x/obsidian-marker)** by [l3-n0x](https://github.com/l3-n0x)
  - MistralAI OCR integration approach
  - Extraction mode design (text/images/all)
  - Configuration structure for PDF processing
  - Error handling patterns for API interactions

While our implementation is independently developed and tailored specifically for email processing workflows, we gratefully acknowledge the insights gained from studying their excellent open-source work.

## Dependencies and Libraries

This project relies on several outstanding open-source libraries:

### Core Dependencies
- **[pypdf2](https://github.com/py-pdf/pypdf2)** - PDF file handling and validation
- **[MistralAI SDK](https://github.com/mistralai/mistral-sdk)** - OCR capabilities for PDF conversion
- **[mammoth](https://github.com/mwilliamson/python-mammoth)** - DOCX to HTML conversion
- **[beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)** - HTML parsing and manipulation
- **[python-docx](https://python-docx.readthedocs.io/)** - Enhanced DOCX metadata extraction
- **[tiktoken](https://github.com/openai/tiktoken)** - Token counting for AI-ready chunking
- **[pandas](https://pandas.pydata.org/)** - Excel file processing and CSV conversion
- **[openpyxl](https://openpyxl.readthedocs.io/)** - Excel file reading
- **[Pillow](https://python-pillow.org/)** - Image processing and validation
- **[chardet](https://github.com/chardet/chardet)** - Character encoding detection
- **[prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/)** - Interactive CLI interface

### Development Tools
- **[pytest](https://pytest.org/)** - Testing framework
- **[Black](https://github.com/psf/black)** - Code formatting
- **[mypy](https://mypy-lang.org/)** - Static type checking
- **[isort](https://pycqa.github.io/isort/)** - Import sorting
- **[bandit](https://bandit.readthedocs.io/)** - Security linting

## Special Thanks

- The Python community for maintaining excellent email parsing standards
- The MistralAI team for providing powerful OCR capabilities
- All contributors to the open-source libraries we depend on
- The Obsidian community for fostering innovation in document processing

## License Compliance

All dependencies and inspirations are used in compliance with their respective licenses. This project is released under the MIT License, ensuring compatibility with all incorporated ideas and dependencies.

---

*If you believe your work has influenced this project and should be acknowledged here, please open an issue or submit a pull request.*