# Contributing to ARES

Thank you for your interest in contributing to ARES! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone <your-fork-url>
   cd "Sentinel-Local-BI Ares"
   ```

2. **Set up development environment**
   ```bash
   # Using Make (Linux/Mac)
   make dev-install
   
   # Or manually
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

3. **Run tests**
   ```bash
   make test
   # or
   pytest
   ```

## Code Style

### Formatting
- Use **Black** for code formatting (line length: 100)
- Use **Ruff** for linting
- Run `make format` before committing

### Type Hints
- Always use type hints for function parameters and return values
- Use `Optional[T]` for nullable types
- Use `List[T]`, `Dict[K, V]` from `typing` module

### Documentation
- Use docstrings for all public functions and classes
- Follow Google-style docstrings
- Include type information in docstrings

### Example
```python
def process_document(
    file_path: str,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Process a document and extract text.

    Args:
        file_path: Path to the document file
        options: Optional processing options

    Returns:
        Dictionary with extracted text and metadata
    """
    ...
```

## Testing

### Writing Tests
- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names: `test_function_name_scenario`

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_rag_engine.py

# With coverage
pytest --cov=src --cov-report=html
```

### Test Coverage
- Aim for >80% code coverage
- Focus on critical paths (RAG engine, PII masking, agents)

## Git Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## Project Structure

```
src/
├── api/          # FastAPI backend
├── core/         # Core functionality (RAG, agents)
├── security/     # Privacy & security (PII masking)
├── ui/           # Streamlit frontend
└── utils/        # Utility functions
```

## Areas for Contribution

### High Priority
- Performance optimizations
- Additional document format support
- Enhanced error handling
- More comprehensive tests

### Medium Priority
- UI/UX improvements
- Additional language support
- Advanced analytics
- Export functionality

### Low Priority
- Documentation improvements
- Code refactoring
- Dependency updates

## Questions?

- Review existing code for patterns
- Check the [README.md](README.md) for architecture details
- Open an issue for discussion

---

Thank you for contributing to ARES! 🛡️
