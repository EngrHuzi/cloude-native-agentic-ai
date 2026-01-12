#!/usr/bin/env python3
"""
FastAPI CRUD Endpoint Generator for SQLModel

Generates complete CRUD endpoints for a SQLModel with proper typing,
error handling, and FastAPI best practices.

Usage:
    python generate_crud.py <model_name> [options]

Examples:
    python generate_crud.py User
    python generate_crud.py Post --output api/routes/posts.py
"""

import sys
import argparse


CRUD_TEMPLATE = '''"""
{model_name} CRUD API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from database import get_session
from models import {model_name}, {model_name}Create, {model_name}Update


router = APIRouter(prefix="/{plural_name}", tags=["{plural_name}"])


@router.post("/", response_model={model_name})
def create_{singular_name}(
    {singular_name}: {model_name}Create,
    session: Session = Depends(get_session)
):
    """Create a new {singular_name}"""
    db_{singular_name} = {model_name}.model_validate({singular_name})
    session.add(db_{singular_name})
    session.commit()
    session.refresh(db_{singular_name})
    return db_{singular_name}


@router.get("/", response_model=List[{model_name}])
def read_{plural_name}(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    """Get all {plural_name} with pagination"""
    {plural_name} = session.exec(
        select({model_name}).offset(offset).limit(limit)
    ).all()
    return {plural_name}


@router.get("/{{id}}", response_model={model_name})
def read_{singular_name}(
    id: int,
    session: Session = Depends(get_session)
):
    """Get a specific {singular_name} by ID"""
    {singular_name} = session.get({model_name}, id)
    if not {singular_name}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return {singular_name}


@router.patch("/{{id}}", response_model={model_name})
def update_{singular_name}(
    id: int,
    {singular_name}_update: {model_name}Update,
    session: Session = Depends(get_session)
):
    """Update a {singular_name}"""
    db_{singular_name} = session.get({model_name}, id)
    if not db_{singular_name}:
        raise HTTPException(status_code=404, detail="{model_name} not found")

    {singular_name}_data = {singular_name}_update.model_dump(exclude_unset=True)
    for key, value in {singular_name}_data.items():
        setattr(db_{singular_name}, key, value)

    session.add(db_{singular_name})
    session.commit()
    session.refresh(db_{singular_name})
    return db_{singular_name}


@router.delete("/{{id}}")
def delete_{singular_name}(
    id: int,
    session: Session = Depends(get_session)
):
    """Delete a {singular_name}"""
    {singular_name} = session.get({model_name}, id)
    if not {singular_name}:
        raise HTTPException(status_code=404, detail="{model_name} not found")

    session.delete({singular_name})
    session.commit()
    return {{"message": "{model_name} deleted successfully"}}
'''


SCHEMA_MODELS_TEMPLATE = '''"""
{model_name} schema models for request/response validation
"""
from typing import Optional
from sqlmodel import SQLModel


class {model_name}Base(SQLModel):
    """Base properties shared across all {model_name} schemas"""
    # Add your base fields here
    pass


class {model_name}Create({model_name}Base):
    """Properties to receive via API on creation"""
    pass


class {model_name}Update(SQLModel):
    """Properties to receive via API on update (all optional)"""
    # Add updateable fields here as Optional types
    pass


class {model_name}Read({model_name}Base):
    """Properties to return via API"""
    id: int
'''


def pluralize(word: str) -> str:
    """Simple pluralization (English)"""
    if word.endswith('y'):
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    else:
        return word + 's'


def generate_crud_code(model_name: str, include_schemas: bool = False) -> str:
    """Generate CRUD endpoint code"""
    singular_name = model_name.lower()
    plural_name = pluralize(singular_name)

    code = CRUD_TEMPLATE.format(
        model_name=model_name,
        singular_name=singular_name,
        plural_name=plural_name
    )

    if include_schemas:
        schema_code = SCHEMA_MODELS_TEMPLATE.format(model_name=model_name)
        code = schema_code + "\n\n" + code

    return code


def main():
    parser = argparse.ArgumentParser(
        description="Generate FastAPI CRUD endpoints for SQLModel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s User
  %(prog)s Post --output api/routes/posts.py
  %(prog)s Hero --schemas
        """
    )

    parser.add_argument("model_name", help="Name of the SQLModel class")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--schemas",
        action="store_true",
        help="Include schema models (Create, Update, Read) in output"
    )

    args = parser.parse_args()

    # Generate the code
    code = generate_crud_code(
        model_name=args.model_name,
        include_schemas=args.schemas
    )

    # Output the code
    if args.output:
        with open(args.output, 'w') as f:
            f.write(code)
        print(f"CRUD endpoints generated successfully: {args.output}")
    else:
        print(code)


if __name__ == "__main__":
    main()
