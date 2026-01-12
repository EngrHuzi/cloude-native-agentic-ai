#!/bin/bash
# Initialize pytest in a Python project

set -e

echo "Initializing pytest setup..."

# Install pytest and essential plugins
echo "Installing pytest and plugins..."
pip install -U pytest pytest-cov pytest-mock

# Create tests directory if it doesn't exist
if [ ! -d "tests" ]; then
    echo "Creating tests directory..."
    mkdir -p tests
    touch tests/__init__.py
fi

# Create pytest.ini if it doesn't exist
if [ ! -f "pytest.ini" ]; then
    echo "Creating pytest.ini..."
    cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov-report=term-missing
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
EOF
    echo "Created pytest.ini"
fi

# Create conftest.py if it doesn't exist
if [ ! -f "tests/conftest.py" ]; then
    echo "Creating tests/conftest.py..."
    cat > tests/conftest.py << 'EOF'
"""
Shared fixtures and configuration for pytest tests.
"""
import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "key": "value",
        "number": 42
    }


# Add your shared fixtures here
EOF
    echo "Created tests/conftest.py"
fi

# Create a sample test file if no tests exist
if [ ! -f "tests/test_sample.py" ]; then
    echo "Creating sample test file..."
    cat > tests/test_sample.py << 'EOF'
"""
Sample test file to verify pytest setup.
"""


def test_sample():
    """Sample test that always passes."""
    assert True


def test_sample_with_fixture(sample_data):
    """Sample test using a fixture."""
    assert sample_data["key"] == "value"
    assert sample_data["number"] == 42
EOF
    echo "Created tests/test_sample.py"
fi

echo ""
echo "Pytest setup complete!"
echo ""
echo "Next steps:"
echo "1. Run tests: pytest"
echo "2. Run with coverage: pytest --cov"
echo "3. Add your test files to the tests/ directory"
echo "4. Configure additional options in pytest.ini as needed"
