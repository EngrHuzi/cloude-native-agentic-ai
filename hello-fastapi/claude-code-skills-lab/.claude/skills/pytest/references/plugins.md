# Useful Pytest Plugins

## Essential Plugins

### pytest-cov (Coverage Reporting)

**Installation:**
```bash
pip install pytest-cov
```

**Usage:**
```bash
pytest --cov=mypackage --cov-report=html --cov-report=term
pytest --cov=mypackage --cov-report=xml  # For CI/CD
```

**Features:**
- Code coverage measurement
- Multiple report formats (HTML, XML, terminal)
- Branch coverage support
- Coverage thresholds

### pytest-xdist (Parallel Execution)

**Installation:**
```bash
pip install pytest-xdist
```

**Usage:**
```bash
pytest -n auto  # Use all CPU cores
pytest -n 4  # Use 4 workers
```

**Features:**
- Run tests in parallel
- Distribute tests across multiple CPUs
- Significant speed improvements for large test suites

### pytest-mock (Mocking Helpers)

**Installation:**
```bash
pip install pytest-mock
```

**Usage:**
```python
def test_with_mocker(mocker):
    mock = mocker.patch('module.function')
    mock.return_value = 42
    assert function_using_mock() == 42
```

**Features:**
- Simplified mocking with mocker fixture
- Automatic cleanup
- spy() for partial mocking

## Testing Specific Frameworks

### pytest-django (Django Testing)

**Installation:**
```bash
pip install pytest-django
```

**Features:**
- Django database fixtures
- Django settings management
- Client fixtures for testing views
- Admin user creation

**Usage:**
```python
@pytest.mark.django_db
def test_user_creation(client):
    response = client.get('/users/')
    assert response.status_code == 200
```

### pytest-flask (Flask Testing)

**Installation:**
```bash
pip install pytest-flask
```

**Features:**
- Flask application fixtures
- Client fixtures
- Context management

**Usage:**
```python
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
```

### pytest-asyncio (Async Testing)

**Installation:**
```bash
pip install pytest-asyncio
```

**Usage:**
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result == expected
```

## Code Quality Plugins

### pytest-flake8 (Linting)

**Installation:**
```bash
pip install pytest-flake8
```

**Usage:**
```bash
pytest --flake8
```

**Features:**
- Run flake8 checks as tests
- Fail tests on linting errors
- Configurable rules

### pytest-mypy (Type Checking)

**Installation:**
```bash
pip install pytest-mypy
```

**Usage:**
```bash
pytest --mypy
```

**Features:**
- Run mypy type checks as tests
- Configurable strictness
- Cache support

## Test Organization

### pytest-randomly (Random Test Order)

**Installation:**
```bash
pip install pytest-randomly
```

**Features:**
- Randomize test execution order
- Detect order-dependent tests
- Reproducible with seed

**Usage:**
```bash
pytest  # Automatically randomizes
pytest --randomly-seed=12345  # Use specific seed
```

### pytest-ordering (Control Test Order)

**Installation:**
```bash
pip install pytest-ordering
```

**Usage:**
```python
@pytest.mark.order(1)
def test_first():
    pass

@pytest.mark.order(2)
def test_second():
    pass
```

## Output and Reporting

### pytest-html (HTML Reports)

**Installation:**
```bash
pip install pytest-html
```

**Usage:**
```bash
pytest --html=report.html --self-contained-html
```

**Features:**
- Beautiful HTML test reports
- Screenshots and logs
- Self-contained reports

### pytest-json-report (JSON Reports)

**Installation:**
```bash
pip install pytest-json-report
```

**Usage:**
```bash
pytest --json-report --json-report-file=report.json
```

**Features:**
- Machine-readable test results
- Detailed test metadata
- Integration with dashboards

### pytest-sugar (Better Output)

**Installation:**
```bash
pip install pytest-sugar
```

**Features:**
- Progress bar
- Real-time failure display
- Better visual output

## Development Helpers

### pytest-watch (Auto-rerun)

**Installation:**
```bash
pip install pytest-watch
```

**Usage:**
```bash
ptw  # Watch and re-run tests on file changes
```

**Features:**
- Automatically rerun tests
- Watch file changes
- Development workflow optimization

### pytest-testmon (Smart Rerun)

**Installation:**
```bash
pip install pytest-testmon
```

**Usage:**
```bash
pytest --testmon  # Only run affected tests
```

**Features:**
- Track which tests cover which code
- Run only relevant tests after changes
- Faster development cycle

### pytest-timeout (Timeout Tests)

**Installation:**
```bash
pip install pytest-timeout
```

**Usage:**
```python
@pytest.mark.timeout(5)  # 5 second timeout
def test_with_timeout():
    pass
```

**Configuration:**
```ini
[pytest]
timeout = 300  # Default 5 minute timeout
```

## Data and Fixtures

### pytest-factoryboy (Factory Pattern)

**Installation:**
```bash
pip install pytest-factoryboy
```

**Usage:**
```python
from pytest_factoryboy import register
from factories import UserFactory

register(UserFactory)

def test_user(user):  # Automatically available
    assert user.email
```

### pytest-freezegun (Mock Time)

**Installation:**
```bash
pip install pytest-freezegun
```

**Usage:**
```python
@pytest.mark.freeze_time("2024-01-01")
def test_with_frozen_time():
    assert datetime.now().year == 2024
```

### pytest-env (Environment Variables)

**Installation:**
```bash
pip install pytest-env
```

**Configuration:**
```ini
[pytest]
env =
    DATABASE_URL=sqlite:///test.db
    DEBUG=true
```

## Performance Testing

### pytest-benchmark (Benchmarking)

**Installation:**
```bash
pip install pytest-benchmark
```

**Usage:**
```python
def test_performance(benchmark):
    result = benchmark(function_to_test)
    assert result > 0
```

**Features:**
- Performance regression testing
- Statistical analysis
- Comparison reports

## Debugging Tools

### pytest-pdb (Enhanced Debugging)

Built-in, use with:
```bash
pytest --pdb  # Drop to debugger on failure
pytest --trace  # Start debugger at test start
```

### pytest-print (Print Debugging)

**Installation:**
```bash
pip install pytest-print
```

**Features:**
- Enhanced print output
- Automatic formatting
- Better visibility of print statements

## CI/CD Integration

### pytest-github-actions-annotate-failures

**Installation:**
```bash
pip install pytest-github-actions-annotate-failures
```

**Features:**
- Annotate failures in GitHub Actions
- Better CI/CD visibility
- Automatic configuration

## Plugin Selection Guide

**Minimum Setup:**
- pytest-cov

**Development Setup:**
- pytest-cov
- pytest-mock
- pytest-sugar
- pytest-watch

**Production Setup:**
- pytest-cov
- pytest-xdist
- pytest-timeout
- pytest-html or pytest-json-report

**Framework-Specific:**
- Add pytest-django for Django
- Add pytest-flask for Flask
- Add pytest-asyncio for async code

## Installing Common Plugin Sets

```bash
# Basic testing
pip install pytest pytest-cov pytest-mock

# Development workflow
pip install pytest pytest-cov pytest-sugar pytest-watch

# CI/CD
pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-html

# Django
pip install pytest pytest-django pytest-cov pytest-factoryboy

# Flask
pip install pytest pytest-flask pytest-cov pytest-mock
```
