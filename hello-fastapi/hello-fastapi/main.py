from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# In-memory database for items
items_db = {}
item_id_counter = {"value": 1}


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int = 0


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def read_hello(name: str):
    return {"message": f"Hello {name}"}


# CRUD Operations

@app.post("/items", status_code=201)
async def create_item(item: Item):
    """Create a new item."""
    item_id = item_id_counter["value"]
    items_db[item_id] = item.model_dump()
    item_id_counter["value"] += 1
    return {"id": item_id, **items_db[item_id]}


@app.get("/items")
async def read_items():
    """Get all items."""
    return {
        "items": [{"id": id, **item} for id, item in items_db.items()],
        "total": len(items_db)
    }


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """Get a specific item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items_db[item_id]}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update an existing item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update only provided fields
    stored_item = items_db[item_id]
    update_data = item_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        stored_item[key] = value

    return {"id": item_id, **stored_item}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item = items_db.pop(item_id)
    return {"message": "Item deleted successfully", "item": {"id": item_id, **deleted_item}}
