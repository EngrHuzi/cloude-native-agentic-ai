# Debugging Pytest Tests

## Command Line Options

### Verbose Output

```bash
pytest -v  # Verbose mode
pytest -vv  # Extra verbose mode
pytest -s  # Disable output capture (show print statements)
```

### Show Local Variables

```bash
pytest -l  # Show local variables in tracebacks
pytest --tb=long  # Long traceback format
pytest --tb=short  # Short traceback format
pytest --tb=line  # One line per failure
pytest --tb=native  # Python standard traceback
pytest --tb=no  # No traceback
```

### Stop on First Failure

```bash
pytest -x  # Stop after first failure
pytest --maxfail=3  # Stop after 3 failures
```

### Run Specific Tests

```bash
pytest test_module.py  # Run specific file
pytest test_module.py::test_function  # Run specific test
pytest test_module.py::TestClass::test_method  # Run specific method
pytest -k "user"  # Run tests matching pattern
pytest -k "not slow"  # Exclude tests matching pattern
```

## Interactive Debugging

### Drop into Debugger on Failure

```bash
pytest --pdb  # Drop into pdb on failure
pytest --pdbcls=IPython.terminal.debugger:Pdb  # Use IPython debugger
```

### Set Breakpoints in Tests

```python
def test_complex_logic():
    result = complex_calculation()
    import pdb; pdb.set_trace()  # Debugger breakpoint
    assert result == expected
```

### Using breakpoint()

```python
def test_with_breakpoint():
    user = create_user()
    breakpoint()  # Python 3.7+ built-in
    assert user.is_valid()
```

## Print Debugging

### Enable Print Output

```python
def test_with_prints():
    user = User("test@example.com")
    print(f"User created: {user}")  # Visible with -s flag
    print(f"User ID: {user.id}")
    assert user.is_valid()

# Run with: pytest -s
```

### Using capsys Fixture

```python
def test_output(capsys):
    print("Debug message")
    captured = capsys.readouterr()
    print(f"Captured output: {captured.out}")
```

## Logging

### Enable Logging Output

```bash
pytest --log-cli-level=DEBUG  # Show logs during test run
pytest --log-file=test.log  # Write logs to file
pytest --log-file-level=DEBUG  # Set file log level
```

### Configure Logging in Tests

```python
import logging

def test_with_logging(caplog):
    logger = logging.getLogger(__name__)
    logger.info("Starting test")

    result = process_data()

    logger.debug(f"Result: {result}")
    assert "Starting test" in caplog.text
```

## Inspecting Failures

### Show Failed Test Context

```python
def test_user_validation():
    user = User(name="", email="invalid")
    # pytest shows values when assertion fails
    assert user.is_valid(), f"User validation failed: {user}"
```

### Using pytest.approx for Floats

```python
def test_float_comparison():
    result = 0.1 + 0.2
    # Instead of: assert result == 0.3  # May fail
    assert result == pytest.approx(0.3)
```

### Custom Assertion Messages

```python
def test_with_message():
    users = get_users()
    assert len(users) > 0, (
        f"Expected at least one user, got {len(users)}. "
        f"Database might be empty."
    )
```

## Fixture Debugging

### Print Fixture Execution

```python
@pytest.fixture
def debug_fixture():
    print("SETUP: Creating resource")
    resource = create_resource()
    print(f"SETUP COMPLETE: {resource}")

    yield resource

    print("TEARDOWN: Cleaning up resource")
    resource.cleanup()
    print("TEARDOWN COMPLETE")
```

### Show Fixture Setup/Teardown

```bash
pytest --setup-show  # Display fixture setup/teardown
```

## Test Markers for Debugging

### Skip Tests Temporarily

```python
@pytest.mark.skip(reason="Debugging other tests")
def test_skip_for_now():
    pass

@pytest.mark.skipif(True, reason="Temporary skip")
def test_conditional_skip():
    pass
```

### Expected Failures

```python
@pytest.mark.xfail(reason="Known bug, investigating")
def test_known_issue():
    assert buggy_function() == expected_value
```

## Debugging Parametrized Tests

### Identify Failing Parameters

```python
@pytest.mark.parametrize("value", [
    pytest.param(1, id="one"),
    pytest.param(2, id="two"),
    pytest.param(3, id="three"),
])
def test_values(value):
    assert process(value) > 0

# Run specific parameter:
# pytest test_file.py::test_values[two]
```

## Common Debugging Scenarios

### Test Passes Individually, Fails in Suite

```bash
# Run in random order to find order dependencies
pytest --random-order

# Run tests in isolation
pytest --forked  # Requires pytest-forked plugin
```

### Intermittent Test Failures

```python
# Add more diagnostic output
def test_intermittent():
    import time
    start = time.time()

    result = async_operation()

    duration = time.time() - start
    print(f"Operation took {duration:.2f}s")

    assert result is not None, (
        f"Result was None after {duration:.2f}s. "
        f"May indicate timeout issue."
    )
```

### Debugging Mocks

```python
def test_mock_debugging():
    mock_service = Mock()

    # Enable verbose mock output
    mock_service.method.return_value = "test"

    result = function_using_service(mock_service)

    # Check what was called
    print(f"Mock called: {mock_service.method.called}")
    print(f"Call count: {mock_service.method.call_count}")
    print(f"Call args: {mock_service.method.call_args}")
    print(f"All calls: {mock_service.method.call_args_list}")

    mock_service.method.assert_called_once_with(expected_arg)
```

## Profiling Tests

### Find Slow Tests

```bash
pytest --durations=10  # Show 10 slowest tests
pytest --durations=0  # Show all test durations
```

### Profile Test Execution

```bash
# Using pytest-profiling plugin
pytest --profile

# Using pytest-benchmark plugin
pytest --benchmark-only
```

## Environment Debugging

### Show Test Environment

```python
def test_environment_info():
    import sys
    import os

    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"CWD: {os.getcwd()}")
    print(f"PATH: {os.environ.get('PATH')}")
```

### Debug Configuration

```bash
# Show pytest configuration
pytest --version
pytest --collect-only  # Show which tests would run
pytest --fixtures  # Show available fixtures
pytest --markers  # Show available markers
```

## Tips

1. **Start simple**: Use print statements and -s flag
2. **Use --pdb** for interactive exploration when tests fail
3. **Add --tb=short** for cleaner output
4. **Use -v** to see which test is running
5. **Add diagnostic prints** in fixtures
6. **Check fixture scope** if tests interfere with each other
7. **Use --lf** to run only last failed tests
8. **Use --ff** to run failures first
9. **Add meaningful assertion messages**
10. **Use logging** instead of print for production test code
