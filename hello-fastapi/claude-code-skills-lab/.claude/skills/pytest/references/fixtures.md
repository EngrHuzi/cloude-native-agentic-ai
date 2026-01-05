# Pytest Fixtures Guide

## Overview

Fixtures are functions that provide data, objects, or resources to tests. They enable test setup/teardown, dependency injection, and resource sharing across tests.

## Fixture Scopes

Control fixture lifecycle with scopes:

```python
@pytest.fixture(scope="function")  # Default: runs per test
def user():
    return User()

@pytest.fixture(scope="class")  # Runs once per test class
def database():
    return Database.connect()

@pytest.fixture(scope="module")  # Runs once per module
def app_config():
    return load_config()

@pytest.fixture(scope="session")  # Runs once per test session
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()
```

## Common Fixture Patterns

### Setup and Teardown

```python
@pytest.fixture
def temp_database():
    # Setup
    db = Database.create_temp()
    db.initialize()

    # Provide to test
    yield db

    # Teardown
    db.cleanup()
    db.delete()
```

### Fixture Chaining

```python
@pytest.fixture
def database():
    return Database.connect()

@pytest.fixture
def user_repository(database):
    return UserRepository(database)

def test_create_user(user_repository):
    user = user_repository.create("test@example.com")
    assert user.email == "test@example.com"
```

### Parametrized Fixtures

```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    db = Database.connect(request.param)
    yield db
    db.disconnect()

def test_query(database):
    # Runs 3 times with different databases
    result = database.query("SELECT 1")
    assert result is not None
```

### Autouse Fixtures

```python
@pytest.fixture(autouse=True)
def reset_state():
    """Runs automatically before each test"""
    State.reset()
```

### Factory Fixtures

```python
@pytest.fixture
def make_user():
    users = []

    def _make_user(name, email):
        user = User(name, email)
        users.append(user)
        return user

    yield _make_user

    # Cleanup all created users
    for user in users:
        user.delete()

def test_multiple_users(make_user):
    user1 = make_user("Alice", "alice@example.com")
    user2 = make_user("Bob", "bob@example.com")
    assert user1.id != user2.id
```

## Built-in Fixtures

### tmp_path

```python
def test_file_operations(tmp_path):
    # tmp_path is a pathlib.Path object
    file = tmp_path / "test.txt"
    file.write_text("Hello")
    assert file.read_text() == "Hello"
```

### monkeypatch

```python
def test_environment_variable(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    assert os.getenv("API_KEY") == "test-key"
```

### capsys

```python
def test_output(capsys):
    print("Hello World")
    captured = capsys.readouterr()
    assert captured.out == "Hello World\n"
```

### request

```python
@pytest.fixture
def custom_fixture(request):
    # Access test information
    test_name = request.node.name
    marker = request.node.get_closest_marker("custom")

    return {"test": test_name, "marker": marker}
```

## Best Practices

1. **Use descriptive fixture names** that explain what they provide
2. **Limit fixture scope** to the minimum needed
3. **Avoid fixture overuse** - not everything needs to be a fixture
4. **Document complex fixtures** with docstrings
5. **Place shared fixtures** in conftest.py
6. **Keep fixtures simple** - complex logic should be in helper functions
