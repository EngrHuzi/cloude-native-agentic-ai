---
name: pytest
description: Comprehensive Python testing framework guide using uv package manager. Covers test creation, fixtures, parametrization, debugging, and best practices. Use when Claude needs to work with pytest for (1) Setting up pytest with 'uv add --dev pytest', (2) Writing unit tests or integration tests, (3) Using fixtures and parametrization, (4) Running tests with 'uv run pytest' and coverage, (5) Debugging test failures, (6) Configuring pytest or CI/CD integration, or any other pytest-related tasks.
---

# pytest Testing Guide

This skill provides comprehensive guidance for working with the pytest testing framework.

## Quick Start

### Installation

Install pytest in your project using uv:

```bash
# Add pytest as dev dependency
uv add --dev pytest pytest-cov

# Or add with async support
uv add --dev pytest pytest-cov pytest-asyncio
```

### Basic Test Structure

Create test files following the `test_*.py` or `*_test.py` naming convention:

```python
# test_example.py
def add(x, y):
    return x + y

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
```

Run tests:

```bash
uv run pytest
uv run pytest -v  # verbose output
uv run pytest test_example.py  # specific file
uv run pytest -k "test_add"  # pattern matching
```

## Core Workflows

### Writing Effective Tests

**Use descriptive test names:**
```python
def test_user_registration_creates_new_account():
    # Test implementation
```

**Structure tests with Arrange-Act-Assert:**
```python
def test_calculate_total_with_discount():
    # Arrange
    cart = ShoppingCart()
    cart.add_item("Book", 20.00)

    # Act
    total = cart.calculate_total(discount=0.10)

    # Assert
    assert total == 18.00
```

**Use assert for all assertions:**
```python
def test_user_validation():
    user = User("john@example.com")
    assert user.is_valid()
    assert user.email == "john@example.com"
    assert len(user.username) > 0
```

### Using Fixtures

Fixtures provide reusable test setup. For detailed fixture patterns and examples, see [references/fixtures.md](references/fixtures.md).

**Basic fixture:**
```python
import pytest

@pytest.fixture
def sample_user():
    return User(name="Test User", email="test@example.com")

def test_user_name(sample_user):
    assert sample_user.name == "Test User"
```

**Fixture with setup/teardown:**
```python
@pytest.fixture
def database():
    db = Database.connect()
    yield db
    db.disconnect()
```

### Parametrization

Run the same test with multiple inputs. For advanced parametrization techniques, see [references/parametrization.md](references/parametrization.md).

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

### Testing Exceptions

```python
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

### Running Tests with Coverage

Use the `scripts/run_with_coverage.sh` script or run manually:

```bash
uv run pytest --cov=mypackage --cov-report=html --cov-report=term
```

## Configuration

### pytest.ini

Create a `pytest.ini` file in your project root:

```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### conftest.py

Create `conftest.py` for shared fixtures and configuration:

```python
import pytest

@pytest.fixture(scope="session")
def app_config():
    return {
        "database": "test.db",
        "debug": True
    }
```

## Advanced Features

### Markers

Mark tests for selective execution:

```python
@pytest.mark.slow
def test_complex_computation():
    # Long-running test

# Run only fast tests
# uv run pytest -m "not slow"
```

### Temporary Files and Directories

Use built-in `tmp_path` fixture:

```python
def test_file_processing(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")
    assert process_file(test_file) == "HELLO WORLD"
```

### Mocking and Patching

```python
from unittest.mock import Mock, patch

def test_api_call():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        result = fetch_data()
        assert result["status"] == "ok"
```

## Debugging Tests

For detailed debugging strategies, see [references/debugging.md](references/debugging.md).

**Run with print statements:**
```bash
uv run pytest -s  # Disable output capture
```

**Drop into debugger on failure:**
```bash
uv run pytest --pdb  # Use Python debugger
```

**Show local variables:**
```bash
uv run pytest -l  # Show locals in tracebacks
```

## Best Practices

For comprehensive best practices, see [references/best-practices.md](references/best-practices.md).

- **One assertion per test** (when possible) for clarity
- **Use fixtures** instead of setup/teardown methods
- **Keep tests independent** - no shared state
- **Test behavior, not implementation**
- **Use descriptive names** that explain what is being tested
- **Organize tests** to mirror source code structure

## Useful Plugins

For a curated list of recommended plugins, see [references/plugins.md](references/plugins.md).

## Scripts

- `scripts/init_pytest.sh` - Initialize pytest in a new project
- `scripts/run_with_coverage.sh` - Run tests with coverage reporting
- `scripts/generate_test_template.py` - Generate test file template

## Assets

- `assets/basic-template/` - Basic pytest project structure with configuration files
