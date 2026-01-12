# Pytest Basic Template

This template provides a starting point for pytest testing in your Python project.

## Files Included

- `pytest.ini` - Pytest configuration
- `conftest.py` - Shared fixtures and setup
- `test_example.py` - Example test file with common patterns

## Usage

1. Copy these files to your project
2. Install pytest with uv:
   ```bash
   uv add --dev pytest pytest-cov
   ```
3. Place test files in a `tests/` directory
4. Update `conftest.py` with your project-specific fixtures
5. Run tests with `uv run pytest`

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=your_package

# Run specific tests
uv run pytest tests/test_example.py

# Run tests matching a pattern
uv run pytest -k "test_basic"

# Run with verbose output
uv run pytest -v
```
