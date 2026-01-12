#!/usr/bin/env python3
"""
Generate CRUD endpoints for a FastAPI model.

Usage:
    python generate-crud.py <model_name> [--fields field1:type field2:type ...]

Example:
    python generate-crud.py User --fields name:str email:str age:int
"""

import sys
from pathlib import Path


def generate_crud(model_name: str, fields: list[tuple[str, str]]):
    """Generate CRUD router for a model."""

    model_lower = model_name.lower()
    fields_str = "\n    ".join([f"{name}: {typ}" for name, typ in fields])

    # Pydantic schema
    schema = f'''from pydantic import BaseModel
from typing import Optional


class {model_name}Base(BaseModel):
    {fields_str}


class {model_name}Create({model_name}Base):
    pass


class {model_name}Update(BaseModel):
    {chr(10).join([f"    {name}: Optional[{typ}] = None" for name, typ in fields])}


class {model_name}Response({model_name}Base):
    id: int

    class Config:
        from_attributes = True
'''

    # Router
    router = f'''from fastapi import APIRouter, HTTPException, status
from typing import List
from .schemas import {model_name}Create, {model_name}Update, {model_name}Response

router = APIRouter(
    prefix="/{model_lower}s",
    tags=["{model_lower}s"]
)

# In-memory storage (replace with database)
{model_lower}_db = {{}}
{model_lower}_counter = 0


@router.post("/", response_model={model_name}Response, status_code=status.HTTP_201_CREATED)
async def create_{model_lower}({model_lower}: {model_name}Create):
    """Create a new {model_lower}."""
    global {model_lower}_counter
    {model_lower}_counter += 1
    {model_lower}_data = {model_lower}.model_dump()
    {model_lower}_data["id"] = {model_lower}_counter
    {model_lower}_db[{model_lower}_counter] = {model_lower}_data
    return {model_lower}_data


@router.get("/", response_model=List[{model_name}Response])
async def list_{model_lower}s(skip: int = 0, limit: int = 100):
    """List all {model_lower}s."""
    items = list({model_lower}_db.values())
    return items[skip : skip + limit]


@router.get("/{{{{item_id}}}}", response_model={model_name}Response)
async def get_{model_lower}(item_id: int):
    """Get a {model_lower} by ID."""
    if item_id not in {model_lower}_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{model_name} not found"
        )
    return {model_lower}_db[item_id]


@router.put("/{{{{item_id}}}}", response_model={model_name}Response)
async def update_{model_lower}(item_id: int, {model_lower}_update: {model_name}Update):
    """Update a {model_lower}."""
    if item_id not in {model_lower}_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{model_name} not found"
        )

    stored_{model_lower} = {model_lower}_db[item_id]
    update_data = {model_lower}_update.model_dump(exclude_unset=True)
    stored_{model_lower}.update(update_data)
    return stored_{model_lower}


@router.delete("/{{{{item_id}}}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{model_lower}(item_id: int):
    """Delete a {model_lower}."""
    if item_id not in {model_lower}_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{model_name} not found"
        )
    del {model_lower}_db[item_id]
'''

    # Create output directory
    output_dir = Path(f"{model_lower}_router")
    output_dir.mkdir(exist_ok=True)

    # Write files
    (output_dir / "schemas.py").write_text(schema)
    (output_dir / "router.py").write_text(router)
    (output_dir / "__init__.py").write_text("")

    print(f"✓ Generated CRUD router for {model_name}")
    print(f"  Location: {output_dir}/")
    print(f"\nAdd to your main.py:")
    print(f"  from {model_lower}_router.router import router as {model_lower}_router")
    print(f"  app.include_router({model_lower}_router)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    model_name = sys.argv[1]
    fields = []

    # Parse fields
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--fields":
            i += 1
            while i < len(sys.argv) and ":" in sys.argv[i]:
                name, typ = sys.argv[i].split(":")
                fields.append((name, typ))
                i += 1
        else:
            i += 1

    if not fields:
        fields = [("name", "str"), ("description", "str")]
        print(f"No fields specified, using defaults: {fields}")

    generate_crud(model_name, fields)


if __name__ == "__main__":
    main()
