# Contributing to Enterprise Email Parser

Thank you for your interest in contributing to the Enterprise Email Parser project! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a Code of Conduct that sets expectations for participation. By participating, you are expected to uphold this code. Please report unacceptable behaviour to project maintainers.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on our issue tracker with:

- A clear, descriptive title
- A detailed description of the issue, including steps to reproduce
- The expected behaviour and what actually happened
- Any relevant logs, screenshots, or other supporting information
- Your environment information (Python version, OS, etc.)

### Suggesting Enhancements

We welcome enhancement suggestions! Please submit them as issues with:

- A clear, descriptive title
- A detailed description of the enhancement
- Explanation of why this enhancement would be useful
- Any relevant examples, mock-ups, or reference implementations

### Pull Requests

We actively welcome pull requests:

1. Fork the repository and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure your code follows the project's style guide (using Black and isort)
4. Ensure all tests pass
5. Make sure your code is fully typed and passes mypy checks
6. Include appropriate documentation updates
7. Submit a pull request with a clear description of the changes

#### Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate
2. Update any examples or unit tests to demonstrate the new functionality
3. Maintain or increase the test coverage percentage
4. The PR will be merged once you have the sign-off of at least one maintainer

## Development Environment Setup

```bash
# Fork and clone the repository
git clone https://github.com/alexanderpresto/email-parser.git
cd email-parser

# Option 1: Create development environment with Anaconda
conda env create -f environment.yml
conda activate email-parser-dev

# Option 2: Create development environment with pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install for development
pip install -e ".[dev,test,docs]"
```

## Development Workflow

### Running Tests

```bash
# Run the full test suite
pytest

# Run with coverage
pytest --cov=email_parser

# Run specific test categories
pytest tests/test_mime_parsing.py
```

### Code Quality

All code must:

- Be formatted with Black (line length 100)
- Have imports sorted with isort
- Pass mypy static type checking
- Pass security checks with Bandit
- Have appropriate docstrings in the Google format

Automated tools:

```bash
# Format code
black email_parser tests

# Sort imports
isort email_parser tests

# Run type checking
mypy email_parser

# Run security checks
bandit -r email_parser
```

### Documentation

- All public API functions must have Google-style docstrings
- New features must be documented in the appropriate guides
- Update examples for significant API changes

Build documentation locally:

```bash
cd docs
make html
```

## Release Process

1. Update the changelog with all significant changes
2. Update version numbers in:
   - `pyproject.toml`
   - `email_parser/__init__.py`
   - Documentation
3. Create a new GitHub release with a tag matching the version
4. CI/CD will automatically publish to PyPI

## Style Guide

### Python Code Style

- Follow PEP 8 with Black formatting (100 character line length)
- Use [Google style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Use type annotations for all functions
- Prefer composition over inheritance
- Follow the [Zen of Python](https://www.python.org/dev/peps/pep-0020/)

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line
- Consider starting the commit message with an applicable emoji:
  - ✨ (sparkles) for new features
  - 🐛 (bug) for bug fixes
  - 📝 (memo) for documentation updates
  - ♻️ (recycle) for refactoring
  - 🧪 (test tube) for adding tests
  - 🔧 (wrench) for configuration changes

### Branch Naming

- `feature/short-description` for new features
- `bugfix/issue-number-short-description` for bug fixes
- `docs/short-description` for documentation changes
- `refactor/short-description` for code refactoring

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have any questions, please reach out to the project maintainers or ask in a GitHub issue.

Thank you for contributing to the Enterprise Email Parser project!
