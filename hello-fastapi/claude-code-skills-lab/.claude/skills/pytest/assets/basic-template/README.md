# Pytest Basic Template

This template provides a starting point for pytest testing in your Python project.

## Files Included

- `pytest.ini` - Pytest configuration
- `conftest.py` - Shared fixtures and setup
- `test_example.py` - Example test file with common patterns

## Usage

1. Copy these files to your project
2. Place test files in a `tests/` directory
3. Update `conftest.py` with your project-specific fixtures
4. Run tests with `pytest`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=your_package

# Run specific tests
pytest tests/test_example.py

# Run tests matching a pattern
pytest -k "test_basic"

# Run with verbose output
pytest -v
```
