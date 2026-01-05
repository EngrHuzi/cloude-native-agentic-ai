"""
Unit tests for Todo CRUD operations
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTodoCreation:
    """Tests for creating todos"""

    async def test_create_todo(self, client: AsyncClient, sample_todo_data):
        """Test creating a basic todo"""
        response = await client.post("/todos/", json=sample_todo_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_todo_data["title"]
        assert data["description"] == sample_todo_data["description"]
        assert data["status"] == sample_todo_data["status"]
        assert data["priority"] == sample_todo_data["priority"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_todo_with_due_date(self, client: AsyncClient):
        """Test creating a todo with due date"""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        todo_data = {
            "title": "Todo with due date",
            "description": "Test",
            "status": "todo",
            "priority": "high",
            "due_date": due_date
        }

        response = await client.post("/todos/", json=todo_data)

        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is not None

    async def test_create_todo_minimal(self, client: AsyncClient):
        """Test creating a todo with minimal data"""
        todo_data = {
            "title": "Minimal Todo"
        }

        response = await client.post("/todos/", json=todo_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Todo"
        assert data["status"] == "todo"
        assert data["priority"] == "medium"

    async def test_create_todo_empty_title(self, client: AsyncClient):
        """Test that creating todo with empty title fails"""
        todo_data = {
            "title": ""
        }

        response = await client.post("/todos/", json=todo_data)
        assert response.status_code == 422


@pytest.mark.asyncio
class TestTodoReading:
    """Tests for reading todos"""

    async def test_read_todos_empty(self, client: AsyncClient):
        """Test reading todos when none exist"""
        response = await client.get("/todos/")

        assert response.status_code == 200
        assert response.json() == []

    async def test_read_todos_list(self, client: AsyncClient, sample_todo_data):
        """Test reading list of todos"""
        # Create 3 todos
        for i in range(3):
            todo = sample_todo_data.copy()
            todo["title"] = f"Todo {i+1}"
            await client.post("/todos/", json=todo)

        response = await client.get("/todos/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_read_todo_by_id(self, client: AsyncClient, sample_todo_data):
        """Test reading a specific todo by ID"""
        # Create todo
        create_response = await client.post("/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]

        # Read todo
        response = await client.get(f"/todos/{todo_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == sample_todo_data["title"]

    async def test_read_nonexistent_todo(self, client: AsyncClient):
        """Test reading a todo that doesn't exist"""
        response = await client.get("/todos/9999")
        assert response.status_code == 404

    async def test_filter_todos_by_status(self, client: AsyncClient):
        """Test filtering todos by status"""
        # Create todos with different statuses
        await client.post("/todos/", json={"title": "Todo 1", "status": "todo"})
        await client.post("/todos/", json={"title": "Todo 2", "status": "in_progress"})
        await client.post("/todos/", json={"title": "Todo 3", "status": "completed"})

        # Filter by status
        response = await client.get("/todos/?status=todo")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "todo"

    async def test_filter_todos_by_priority(self, client: AsyncClient):
        """Test filtering todos by priority"""
        # Create todos with different priorities
        await client.post("/todos/", json={"title": "Todo 1", "priority": "low"})
        await client.post("/todos/", json={"title": "Todo 2", "priority": "high"})
        await client.post("/todos/", json={"title": "Todo 3", "priority": "medium"})

        # Filter by priority
        response = await client.get("/todos/?priority=high")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"

    async def test_pagination(self, client: AsyncClient):
        """Test pagination of todos"""
        # Create 10 todos
        for i in range(10):
            await client.post("/todos/", json={"title": f"Todo {i+1}"})

        # Get first 5
        response = await client.get("/todos/?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Get next 5
        response = await client.get("/todos/?limit=5&offset=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


@pytest.mark.asyncio
class TestTodoUpdating:
    """Tests for updating todos"""

    async def test_update_todo_title(self, client: AsyncClient, sample_todo_data):
        """Test updating todo title"""
        # Create todo
        create_response = await client.post("/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]

        # Update title
        update_data = {"title": "Updated Title"}
        response = await client.patch(f"/todos/{todo_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == sample_todo_data["description"]  # Unchanged

    async def test_update_todo_status(self, client: AsyncClient, sample_todo_data):
        """Test updating todo status"""
        # Create todo
        create_response = await client.post("/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]

        # Update status
        update_data = {"status": "in_progress"}
        response = await client.patch(f"/todos/{todo_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    async def test_update_todo_to_completed(self, client: AsyncClient, sample_todo_data):
        """Test that updating to completed sets completed_at"""
        # Create todo
        create_response = await client.post("/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]

        # Update to completed
        update_data = {"status": "completed"}
        response = await client.patch(f"/todos/{todo_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    async def test_update_nonexistent_todo(self, client: AsyncClient):
        """Test updating a todo that doesn't exist"""
        update_data = {"title": "Updated"}
        response = await client.patch("/todos/9999", json=update_data)
        assert response.status_code == 404

    async def test_complete_todo_endpoint(self, client: AsyncClient, sample_todo_data):
        """Test the complete todo endpoint"""
        # Create todo
        create_response = await client.post("/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]

        # Complete todo
        response = await client.post(f"/todos/{todo_id}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None


@pytest.mark.asyncio
class TestTodoDeleting:
    """Tests for deleting todos"""

    async def test_delete_todo(self, client: AsyncClient, sample_todo_data):
        """Test deleting a todo"""
        # Create todo
        create_response = await client.post("/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]

        # Delete todo
        response = await client.delete(f"/todos/{todo_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Todo deleted successfully"

        # Verify deletion
        get_response = await client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

    async def test_delete_nonexistent_todo(self, client: AsyncClient):
        """Test deleting a todo that doesn't exist"""
        response = await client.delete("/todos/9999")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestTodoSummary:
    """Tests for todo summary endpoint"""

    async def test_summary_empty(self, client: AsyncClient):
        """Test summary when no todos exist"""
        response = await client.get("/todos/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["todo"] == 0
        assert data["in_progress"] == 0
        assert data["completed"] == 0

    async def test_summary_with_todos(self, client: AsyncClient):
        """Test summary with various todos"""
        # Create todos with different statuses and priorities
        await client.post("/todos/", json={"title": "T1", "status": "todo", "priority": "high"})
        await client.post("/todos/", json={"title": "T2", "status": "todo"})
        await client.post("/todos/", json={"title": "T3", "status": "in_progress"})
        await client.post("/todos/", json={"title": "T4", "status": "completed"})
        await client.post("/todos/", json={"title": "T5", "status": "completed", "priority": "high"})

        response = await client.get("/todos/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert data["todo"] == 2
        assert data["in_progress"] == 1
        assert data["completed"] == 2
        assert data["high_priority"] == 2


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Tests for health and root endpoints"""

    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint"""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    async def test_health_endpoint(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
