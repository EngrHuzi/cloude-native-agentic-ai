from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="FastAPI Basic Template",
    description="A basic FastAPI application template",
    version="1.0.0"
)


# Pydantic models
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class ItemResponse(Item):
    id: int


# In-memory storage (replace with database in production)
items_db: dict[int, dict] = {}
item_counter = 0


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to FastAPI!",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/items/", response_model=ItemResponse, status_code=201)
async def create_item(item: Item):
    """Create a new item."""
    global item_counter
    item_counter += 1

    item_data = item.model_dump()
    item_data["id"] = item_counter
    items_db[item_counter] = item_data

    return item_data


@app.get("/items/", response_model=List[ItemResponse])
async def list_items(skip: int = 0, limit: int = 100):
    """List all items with pagination."""
    items = list(items_db.values())
    return items[skip : skip + limit]


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get an item by ID."""
    if item_id not in items_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")

    return items_db[item_id]


@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: Item):
    """Update an item."""
    if item_id not in items_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = item.model_dump()
    item_data["id"] = item_id
    items_db[item_id] = item_data

    return item_data


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in items_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")

    del items_db[item_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
