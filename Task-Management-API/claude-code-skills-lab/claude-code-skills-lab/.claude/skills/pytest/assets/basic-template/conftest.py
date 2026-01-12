"""
Shared fixtures and configuration for pytest tests.

This file is automatically loaded by pytest and makes fixtures
available to all tests in the project.
"""
import pytest


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "id": 1,
        "name": "Test Item",
        "active": True
    }


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content")
    return file_path


# Add your project-specific fixtures below
