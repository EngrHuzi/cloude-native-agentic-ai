"""
Database configuration and session management
"""
from sqlmodel import Session, create_engine

# Database URL - change this for your database
DATABASE_URL = "sqlite:///./database.db"
# For PostgreSQL:
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)


def get_session():
    """Dependency for getting database sessions"""
    with Session(engine) as session:
        yield session
