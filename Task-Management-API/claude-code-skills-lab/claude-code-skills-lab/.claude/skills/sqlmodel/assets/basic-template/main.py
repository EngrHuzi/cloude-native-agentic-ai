"""
FastAPI + SQLModel Basic Template

A minimal FastAPI application with SQLModel for database operations.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from database import engine
from routes import hero_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup"""
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="FastAPI + SQLModel Template",
    description="A basic template for FastAPI with SQLModel",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(hero_router)


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "Welcome to FastAPI + SQLModel Template"}
