# Pytest Parametrization Guide

## Overview

Parametrization allows running the same test with different input values, reducing code duplication and improving test coverage.

## Basic Parametrization

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

## Multiple Parameters

```python
@pytest.mark.parametrize("base,exponent,expected", [
    (2, 2, 4),
    (2, 3, 8),
    (3, 2, 9),
    (5, 0, 1),
])
def test_power(base, exponent, expected):
    assert base ** exponent == expected
```

## Named Test Cases

Use `pytest.param()` with `id` for readable test names:

```python
@pytest.mark.parametrize("input,expected", [
    pytest.param(2, 4, id="even"),
    pytest.param(3, 9, id="odd"),
    pytest.param(0, 0, id="zero"),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

## Parametrized Fixtures

```python
@pytest.fixture(params=[
    {"driver": "chrome", "headless": True},
    {"driver": "firefox", "headless": False},
])
def browser(request):
    config = request.param
    return WebDriver(config["driver"], headless=config["headless"])

def test_browser_navigation(browser):
    browser.navigate("https://example.com")
    assert browser.current_url == "https://example.com"
```

## Multiple Parametrize Decorators

Combine parameters for Cartesian product:

```python
@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_combinations(x, y):
    # Runs 4 times: (0,2), (0,3), (1,2), (1,3)
    assert x + y >= 2
```

## Parametrization with Marks

Apply marks to specific test cases:

```python
@pytest.mark.parametrize("value", [
    1,
    10,
    pytest.param(1000, marks=pytest.mark.slow),
    pytest.param(10000, marks=pytest.mark.skip(reason="Too large")),
])
def test_process(value):
    assert process(value) > 0
```

## Using pytest.param for Complex Cases

```python
@pytest.mark.parametrize("input,expected,should_raise", [
    pytest.param(10, 2, False, id="valid_division"),
    pytest.param(10, 0, True, id="division_by_zero",
                 marks=pytest.mark.xfail(raises=ZeroDivisionError)),
])
def test_division(input, expected, should_raise):
    if should_raise:
        with pytest.raises(ZeroDivisionError):
            input / expected
    else:
        assert input / expected == 5
```

## Indirect Parametrization

Use fixtures with indirect parametrization:

```python
@pytest.fixture
def database(request):
    db = Database(request.param)
    yield db
    db.close()

@pytest.mark.parametrize("database", ["sqlite", "postgres"], indirect=True)
def test_query(database):
    result = database.query("SELECT 1")
    assert result is not None
```

## Loading Test Data from Files

```python
def load_test_data():
    return [
        ({"username": "alice", "age": 30}, True),
        ({"username": "bob", "age": 17}, False),
        ({"username": "charlie", "age": 25}, True),
    ]

@pytest.mark.parametrize("user_data,is_adult", load_test_data())
def test_age_verification(user_data, is_adult):
    assert verify_adult(user_data) == is_adult
```

## Best Practices

1. **Use descriptive IDs** for test cases to identify failures quickly
2. **Group related test cases** together in parametrization
3. **Keep parameter lists readable** - consider external data files for large datasets
4. **Use pytest.param()** for complex parametrization needs
5. **Combine with fixtures** for powerful test setups
6. **Don't over-parametrize** - sometimes separate tests are clearer
