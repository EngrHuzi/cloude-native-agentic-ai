"""
Todo Management API - FastAPI Application

A complete REST API for managing todo items with:
- CRUD operations
- Status and priority management
- Due date tracking
- Summary statistics
- PostgreSQL database with async support
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from database import async_engine
from routes import router as todo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Cleanup on shutdown
    await async_engine.dispose()


app = FastAPI(
    title="Todo Management API",
    description="A complete REST API for managing todo items with PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todo_router)


@app.get("/", tags=["root"])
async def read_root():
    """Health check and API information"""
    return {
        "message": "Welcome to Todo Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
