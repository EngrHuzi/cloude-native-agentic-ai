"""
API route handlers for Todo Management
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import (
    Todo,
    TodoCreate,
    TodoRead,
    TodoUpdate,
    TodoSummary,
    TodoStatus,
    TodoPriority
)
from database import get_async_session


router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoRead, status_code=201)
async def create_todo(
    todo: TodoCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new todo"""
    db_todo = Todo.model_validate(todo)
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo


@router.get("/", response_model=List[TodoRead])
async def read_todos(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    status: TodoStatus | None = None,
    priority: TodoPriority | None = None,
    session: AsyncSession = Depends(get_async_session)
):
    """Get all todos with optional filtering and pagination"""
    query = select(Todo)

    # Apply filters
    if status:
        query = query.where(Todo.status == status)
    if priority:
        query = query.where(Todo.priority == priority)

    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(Todo.created_at.desc())

    result = await session.execute(query)
    todos = result.scalars().all()
    return todos


@router.get("/summary", response_model=TodoSummary)
async def get_todo_summary(
    session: AsyncSession = Depends(get_async_session)
):
    """Get summary statistics of todos"""
    # Total count
    total_query = select(func.count(Todo.id))
    total_result = await session.execute(total_query)
    total = total_result.scalar() or 0

    # Count by status
    todo_query = select(func.count(Todo.id)).where(Todo.status == TodoStatus.TODO)
    todo_result = await session.execute(todo_query)
    todo_count = todo_result.scalar() or 0

    in_progress_query = select(func.count(Todo.id)).where(Todo.status == TodoStatus.IN_PROGRESS)
    in_progress_result = await session.execute(in_progress_query)
    in_progress_count = in_progress_result.scalar() or 0

    completed_query = select(func.count(Todo.id)).where(Todo.status == TodoStatus.COMPLETED)
    completed_result = await session.execute(completed_query)
    completed_count = completed_result.scalar() or 0

    # High priority count
    high_priority_query = select(func.count(Todo.id)).where(Todo.priority == TodoPriority.HIGH)
    high_priority_result = await session.execute(high_priority_query)
    high_priority_count = high_priority_result.scalar() or 0

    # Overdue count
    now = datetime.utcnow()
    overdue_query = select(func.count(Todo.id)).where(
        Todo.due_date < now,
        Todo.status != TodoStatus.COMPLETED
    )
    overdue_result = await session.execute(overdue_query)
    overdue_count = overdue_result.scalar() or 0

    return TodoSummary(
        total=total,
        todo=todo_count,
        in_progress=in_progress_count,
        completed=completed_count,
        high_priority=high_priority_count,
        overdue=overdue_count
    )


@router.get("/{todo_id}", response_model=TodoRead)
async def read_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific todo by ID"""
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Update a todo"""
    db_todo = await session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_data = todo_update.model_dump(exclude_unset=True)

    # Update fields
    for key, value in todo_data.items():
        setattr(db_todo, key, value)

    # Update timestamp
    db_todo.updated_at = datetime.utcnow()

    # If status changed to completed, set completed_at
    if todo_update.status == TodoStatus.COMPLETED and db_todo.completed_at is None:
        db_todo.completed_at = datetime.utcnow()
    # If status changed from completed, clear completed_at
    elif todo_update.status and todo_update.status != TodoStatus.COMPLETED:
        db_todo.completed_at = None

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a todo"""
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    await session.delete(todo)
    await session.commit()
    return {"message": "Todo deleted successfully", "id": todo_id}


@router.post("/{todo_id}/complete", response_model=TodoRead)
async def complete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Mark a todo as completed"""
    db_todo = await session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db_todo.status = TodoStatus.COMPLETED
    db_todo.completed_at = datetime.utcnow()
    db_todo.updated_at = datetime.utcnow()

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo
