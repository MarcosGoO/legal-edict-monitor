# Contributing to Edict Guardian

Thank you for your interest in contributing to Edict Guardian! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members
- Accept constructive criticism gracefully

## Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+
- Redis 7+
- Git
- Tesseract OCR with Spanish language pack

### Initial Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/edict-guardian.git
cd edict-guardian

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Install spaCy Spanish model
python -m spacy download es_core_news_lg

# Copy environment template and configure
cp .env.example .env
# Edit .env with your local configuration

# Set up the database
# Create a PostgreSQL database named 'edict_guardian'
# Run migrations (when available)
alembic upgrade head
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_parser.py -v

# Run only fast tests
pytest -m "not slow"
```

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check the issue list to avoid duplicates. When creating a bug report, include:

1. **Clear title** - Summarize the bug concisely
2. **Description** - Detailed description of the issue
3. **Steps to reproduce** - Minimal code example
4. **Expected behavior** - What you expected to happen
5. **Actual behavior** - What actually happened
6. **Environment** - OS, Python version, package versions
7. **Logs/Screenshots** - If applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

1. **Clear title** - Describe the enhancement
2. **Motivation** - Why is this enhancement useful?
3. **Description** - Detailed description of the proposed feature
4. **Alternatives** - Any alternative solutions considered
5. **Additional context** - Any other relevant information

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes
6. Push to your fork
7. Open a Pull Request


### Code Quality Tools

We use the following tools (configured in `pyproject.toml`):

- **Ruff**: Linting and formatting
- **Mypy**: Static type checking
- **Bandit**: Security linting
- **Pre-commit**: Git hooks for code quality

Run all checks:

```bash
# Run ruff
ruff check .
ruff format .

# Run mypy
mypy app/

# Run pre-commit on all files
pre-commit run --all-files
```

### Code Organization

```
app/
├── api/            # API endpoints and routes
├── models/         # Database models
├── services/       # Business logic
├── schemas/        # Pydantic schemas
├── workers/        # Celery tasks
└── utils/          # Utility functions
```

### Documentation

- Use docstrings for all public modules, functions, classes, and methods
- Follow Google style docstrings:

```python
def process_document(pdf_path: Path) -> OCRResult:
    """
    Process a PDF document and extract text.
    
    Args:
        pdf_path: Path to the PDF file to process.
        
    Returns:
        OCRResult containing the extracted text and metadata.
        
    Raises:
        FileNotFoundError: If the PDF file does not exist.
        OCRError: If text extraction fails.
        
    Example:
        >>> result = process_document(Path("legal.pdf"))
        >>> print(result.text)
    """
```

## Commit Guidelines

### Commit Message Format

We follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```
feat(parser): add support for NIT check digit validation

- Implement Colombian NIT validation algorithm
- Add unit tests for validation
- Update documentation

Closes #123
```

```
fix(ocr): handle empty PDF pages gracefully

Previously, empty pages would cause OCR to fail with an exception.
Now they are skipped with a warning logged.
```

## Pull Request Process

1. **Create a branch** from `main` with a descriptive name
2. **Make your changes** following coding standards
3. **Add/update tests** for your changes
4. **Update documentation** if needed
5. **Run all checks** locally before pushing
6. **Push your branch** and create a PR
7. **Address review feedback** promptly


### Review Process

1. At least one approval required
2. All CI checks must pass
3. No unresolved conversations
4. Squash and merge is used

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_parser.py

# Specific test
pytest tests/test_parser.py::TestColombianEntityParser::test_extract_radicado_standard

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source structure
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common setup

```python
class TestColombianEntityParser:
    """Tests for ColombianEntityParser."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return ColombianEntityParser()
    
    def test_extract_radicado_standard(self, parser, sample_legal_text):
        """Test extraction of standard radicado format."""
        # Act
        result = parser.parse(sample_legal_text)
        
        # Assert
        assert len(result.radicados) >= 1
        assert result.radicados[0].entity_type == EntityType.RADICADO
```

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add inline comments for complex logic
- Update architecture docs for structural changes

### Building Documentation

```bash
# If using MkDocs (future)
mkdocs serve

# If using Sphinx (future)
cd docs && make html
```