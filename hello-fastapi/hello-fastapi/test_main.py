"""
Pytest tests for FastAPI CRUD operations.
"""
import pytest
from fastapi.testclient import TestClient
from main import app, items_db, item_id_counter


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset the in-memory database before each test."""
    items_db.clear()
    item_id_counter["value"] = 1
    yield
    items_db.clear()
    item_id_counter["value"] = 1


# CREATE Tests

def test_create_item_success(client):
    """Test creating a new item successfully."""
    item_data = {
        "name": "Laptop",
        "description": "High-performance laptop",
        "price": 999.99,
        "quantity": 10
    }
    response = client.post("/items", json=item_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Laptop"
    assert data["description"] == "High-performance laptop"
    assert data["price"] == 999.99
    assert data["quantity"] == 10


def test_create_item_minimal_fields(client):
    """Test creating an item with only required fields."""
    item_data = {
        "name": "Mouse",
        "price": 25.50
    }
    response = client.post("/items", json=item_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Mouse"
    assert data["description"] is None
    assert data["price"] == 25.50
    assert data["quantity"] == 0


def test_create_multiple_items(client):
    """Test creating multiple items with auto-incrementing IDs."""
    items = [
        {"name": "Item1", "price": 10.0},
        {"name": "Item2", "price": 20.0},
        {"name": "Item3", "price": 30.0}
    ]

    for idx, item in enumerate(items, start=1):
        response = client.post("/items", json=item)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == idx
        assert data["name"] == f"Item{idx}"


def test_create_item_invalid_data(client):
    """Test creating an item with invalid data."""
    item_data = {
        "name": "Invalid Item"
        # Missing required 'price' field
    }
    response = client.post("/items", json=item_data)
    assert response.status_code == 422  # Unprocessable Entity


# READ Tests

def test_read_all_items_empty(client):
    """Test reading all items when database is empty."""
    response = client.get("/items")

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_read_all_items_with_data(client):
    """Test reading all items when database has items."""
    # Create test items
    test_items = [
        {"name": "Item1", "price": 10.0},
        {"name": "Item2", "price": 20.0},
        {"name": "Item3", "price": 30.0}
    ]

    for item in test_items:
        client.post("/items", json=item)

    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_read_single_item_success(client):
    """Test reading a single item by ID."""
    # Create an item
    item_data = {"name": "Keyboard", "price": 75.00, "quantity": 5}
    create_response = client.post("/items", json=item_data)
    item_id = create_response.json()["id"]

    # Read the item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Keyboard"
    assert data["price"] == 75.00
    assert data["quantity"] == 5


def test_read_single_item_not_found(client):
    """Test reading a non-existent item."""
    response = client.get("/items/999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not found"


# UPDATE Tests

def test_update_item_all_fields(client):
    """Test updating all fields of an item."""
    # Create an item
    item_data = {"name": "Old Name", "price": 100.0, "quantity": 5}
    create_response = client.post("/items", json=item_data)
    item_id = create_response.json()["id"]

    # Update all fields
    update_data = {
        "name": "New Name",
        "description": "Updated description",
        "price": 150.0,
        "quantity": 10
    }
    response = client.put(f"/items/{item_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "New Name"
    assert data["description"] == "Updated description"
    assert data["price"] == 150.0
    assert data["quantity"] == 10


def test_update_item_partial_fields(client):
    """Test updating only some fields of an item."""
    # Create an item
    item_data = {
        "name": "Original",
        "description": "Original description",
        "price": 100.0,
        "quantity": 5
    }
    create_response = client.post("/items", json=item_data)
    item_id = create_response.json()["id"]

    # Update only price
    update_data = {"price": 200.0}
    response = client.put(f"/items/{item_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Original"  # Unchanged
    assert data["description"] == "Original description"  # Unchanged
    assert data["price"] == 200.0  # Updated
    assert data["quantity"] == 5  # Unchanged


def test_update_item_not_found(client):
    """Test updating a non-existent item."""
    update_data = {"name": "New Name", "price": 50.0}
    response = client.put("/items/999", json=update_data)

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not found"


# DELETE Tests

def test_delete_item_success(client):
    """Test deleting an item successfully."""
    # Create an item
    item_data = {"name": "To Delete", "price": 50.0}
    create_response = client.post("/items", json=item_data)
    item_id = create_response.json()["id"]

    # Delete the item
    response = client.delete(f"/items/{item_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Item deleted successfully"
    assert data["item"]["id"] == item_id
    assert data["item"]["name"] == "To Delete"

    # Verify item is deleted
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_item_not_found(client):
    """Test deleting a non-existent item."""
    response = client.delete("/items/999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not found"


def test_delete_item_and_verify_list(client):
    """Test that deleted item is removed from items list."""
    # Create multiple items
    for i in range(3):
        client.post("/items", json={"name": f"Item{i+1}", "price": 10.0 * (i+1)})

    # Delete the second item
    client.delete("/items/2")

    # Verify items list
    response = client.get("/items")
    data = response.json()
    assert data["total"] == 2
    item_ids = [item["id"] for item in data["items"]]
    assert 2 not in item_ids
    assert 1 in item_ids
    assert 3 in item_ids


# Integration Tests

@pytest.mark.parametrize("item_data,expected_name,expected_price", [
    ({"name": "Item A", "price": 10.0}, "Item A", 10.0),
    ({"name": "Item B", "price": 20.0, "quantity": 5}, "Item B", 20.0),
    ({"name": "Item C", "price": 30.0, "description": "Test"}, "Item C", 30.0),
])
def test_create_item_parametrized(client, item_data, expected_name, expected_price):
    """Test creating items with different data combinations."""
    response = client.post("/items", json=item_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == expected_name
    assert data["price"] == expected_price


def test_full_crud_workflow(client):
    """Test complete CRUD workflow for an item."""
    # CREATE
    item_data = {
        "name": "Workflow Item",
        "description": "Testing full workflow",
        "price": 100.0,
        "quantity": 10
    }
    create_response = client.post("/items", json=item_data)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    # READ (single)
    read_response = client.get(f"/items/{item_id}")
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "Workflow Item"

    # UPDATE
    update_data = {"price": 150.0, "quantity": 15}
    update_response = client.put(f"/items/{item_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 150.0
    assert update_response.json()["quantity"] == 15

    # READ (verify update)
    verify_response = client.get(f"/items/{item_id}")
    assert verify_response.json()["price"] == 150.0

    # DELETE
    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 200

    # READ (verify deletion)
    final_response = client.get(f"/items/{item_id}")
    assert final_response.status_code == 404


def test_multiple_items_management(client):
    """Test managing multiple items simultaneously."""
    # Create 5 items
    created_ids = []
    for i in range(5):
        response = client.post("/items", json={
            "name": f"Item {i+1}",
            "price": 10.0 * (i + 1)
        })
        created_ids.append(response.json()["id"])

    # Verify all items exist
    all_items_response = client.get("/items")
    assert all_items_response.json()["total"] == 5

    # Update item 3
    client.put(f"/items/{created_ids[2]}", json={"price": 999.99})

    # Delete items 2 and 4
    client.delete(f"/items/{created_ids[1]}")
    client.delete(f"/items/{created_ids[3]}")

    # Verify final state
    final_response = client.get("/items")
    assert final_response.json()["total"] == 3

    # Verify updated item
    item_3_response = client.get(f"/items/{created_ids[2]}")
    assert item_3_response.json()["price"] == 999.99
