"""
Example test file demonstrating pytest patterns.
"""
import pytest


# Basic test
def test_basic_assertion():
    """Test with simple assertion."""
    assert 1 + 1 == 2


# Test using fixture
def test_with_fixture(sample_data):
    """Test using a fixture from conftest.py."""
    assert sample_data["name"] == "Test Item"
    assert sample_data["active"] is True


# Parametrized test
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_parametrized(input, expected):
    """Test with multiple parameter sets."""
    assert input * 2 == expected


# Test with marker
@pytest.mark.slow
def test_marked_as_slow():
    """Test marked as slow."""
    # Simulate slow operation
    import time
    time.sleep(0.1)
    assert True


# Test exception
def test_exception():
    """Test that exception is raised."""
    with pytest.raises(ZeroDivisionError):
        _ = 1 / 0


# Test class
class TestExample:
    """Group related tests in a class."""

    def test_method_one(self):
        """First test in class."""
        assert True

    def test_method_two(self, sample_data):
        """Test using fixture in class."""
        assert "id" in sample_data
