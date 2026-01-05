# Pytest Best Practices

## Test Organization

### Directory Structure

```
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── module.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_module.py
    └── integration/
        └── test_api.py
```

### Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*`
- Fixtures: descriptive names (e.g., `user_repository`, `temp_database`)

## Writing Effective Tests

### Single Responsibility

Each test should verify one specific behavior:

```python
# Good
def test_user_creation_sets_email():
    user = User("test@example.com")
    assert user.email == "test@example.com"

def test_user_creation_generates_id():
    user = User("test@example.com")
    assert user.id is not None

# Avoid
def test_user_creation():
    user = User("test@example.com")
    assert user.email == "test@example.com"
    assert user.id is not None
    assert user.is_active is True
    assert len(user.username) > 0
```

### Descriptive Test Names

Test names should describe what they test:

```python
# Good
def test_empty_cart_returns_zero_total():
    cart = ShoppingCart()
    assert cart.total() == 0

# Avoid
def test_cart():
    cart = ShoppingCart()
    assert cart.total() == 0
```

### Arrange-Act-Assert Pattern

```python
def test_user_registration_sends_email():
    # Arrange
    email_service = Mock()
    user_service = UserService(email_service)

    # Act
    user_service.register("test@example.com")

    # Assert
    email_service.send.assert_called_once()
```

## Test Independence

### Avoid Shared State

```python
# Bad - shared state between tests
counter = 0

def test_increment():
    global counter
    counter += 1
    assert counter == 1

def test_increment_again():
    global counter
    counter += 1
    assert counter == 1  # Fails if test_increment runs first

# Good - isolated state
def test_counter_increment():
    counter = Counter()
    counter.increment()
    assert counter.value == 1

def test_counter_increment_again():
    counter = Counter()
    counter.increment()
    assert counter.value == 1
```

### Use Fixtures for Setup

```python
@pytest.fixture
def fresh_database():
    db = Database.create()
    yield db
    db.cleanup()

def test_user_creation(fresh_database):
    user = fresh_database.create_user("test@example.com")
    assert user.email == "test@example.com"
```

## Assertions

### Use Plain Assert

```python
# Good
assert user.is_active
assert len(users) == 5
assert response.status_code == 200

# Avoid unittest-style assertions
# self.assertTrue(user.is_active)
# self.assertEqual(len(users), 5)
```

### Provide Helpful Messages

```python
# Good
assert len(users) == 3, f"Expected 3 users but got {len(users)}"

# Better - pytest shows values automatically
assert len(users) == 3  # pytest will show actual vs expected
```

### Use pytest Utilities

```python
# Floating point comparison
assert result == pytest.approx(0.333, rel=1e-3)

# Exception testing
with pytest.raises(ValueError, match="Invalid email"):
    User("invalid-email")
```

## Fixtures

### Keep Fixtures Simple

```python
# Good
@pytest.fixture
def user():
    return User(email="test@example.com")

# Avoid complex logic in fixtures
@pytest.fixture
def complex_setup():
    # Too much logic
    config = load_config()
    db = Database.connect(config)
    cache = Cache.initialize()
    service = Service(db, cache)
    # ... more setup
    return service  # Too many responsibilities
```

### Use Appropriate Scope

```python
# Function scope (default) for test-specific setup
@pytest.fixture
def user():
    return User()

# Module scope for expensive, shareable resources
@pytest.fixture(scope="module")
def database():
    db = Database.connect()
    yield db
    db.disconnect()

# Session scope for one-time setup
@pytest.fixture(scope="session")
def app_config():
    return load_config_from_file()
```

## Mocking and Patching

### Mock External Dependencies

```python
def test_fetch_user_data():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"id": 1, "name": "Test"}
        result = fetch_user_data(1)
        assert result["name"] == "Test"
```

### Verify Interactions

```python
def test_user_service_calls_email_service():
    email_service = Mock()
    user_service = UserService(email_service)

    user_service.register("test@example.com")

    email_service.send_welcome_email.assert_called_once_with("test@example.com")
```

## Markers

### Organize Tests with Markers

```python
@pytest.mark.slow
def test_complex_computation():
    # Long-running test
    pass

@pytest.mark.integration
def test_database_integration():
    # Integration test
    pass

# Run specific tests
# pytest -m "not slow"
# pytest -m integration
```

### Skip and Xfail

```python
@pytest.mark.skip(reason="Feature not implemented")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_specific():
    pass

@pytest.mark.xfail(reason="Known bug #123")
def test_known_issue():
    pass
```

## Performance

### Avoid Unnecessary Setup

```python
# Bad - creates database for every test
@pytest.fixture
def database():
    return Database.connect()

# Good - reuse database across module
@pytest.fixture(scope="module")
def database():
    db = Database.connect()
    yield db
    db.disconnect()
```

### Use Markers to Skip Slow Tests

```python
@pytest.mark.slow
def test_performance_benchmark():
    # Only run when explicitly requested
    # pytest -m slow
    pass
```

## Code Coverage

### Aim for Meaningful Coverage

- Don't chase 100% coverage blindly
- Focus on critical business logic
- Test edge cases and error paths
- Exclude trivial code from coverage requirements

```ini
# pytest.ini or setup.cfg
[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Common Pitfalls

### Don't Test Implementation Details

```python
# Bad - tests internal implementation
def test_user_internal_state():
    user = User("test@example.com")
    assert user._email_normalized == "test@example.com"

# Good - tests public behavior
def test_user_email_getter():
    user = User("test@example.com")
    assert user.get_email() == "test@example.com"
```

### Avoid Fragile Tests

```python
# Bad - depends on specific order
def test_users_list():
    users = get_all_users()
    assert users[0].name == "Alice"  # Fragile

# Good - tests behavior, not order
def test_users_list_contains_alice():
    users = get_all_users()
    names = [u.name for u in users]
    assert "Alice" in names
```

### Don't Mock Everything

```python
# Bad - too much mocking
def test_user_service():
    mock_db = Mock()
    mock_cache = Mock()
    mock_email = Mock()
    mock_logger = Mock()
    # Test becomes meaningless
    service = UserService(mock_db, mock_cache, mock_email, mock_logger)

# Good - mock only external dependencies
def test_user_service():
    mock_email = Mock()  # External service
    db = InMemoryDatabase()  # Real, lightweight implementation
    service = UserService(db, mock_email)
```
