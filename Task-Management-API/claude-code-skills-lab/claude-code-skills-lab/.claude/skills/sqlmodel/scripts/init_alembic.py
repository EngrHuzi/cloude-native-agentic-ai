#!/usr/bin/env python3
"""
Alembic Migration Initializer for SQLModel

Sets up Alembic for database migrations with SQLModel configuration.

Usage:
    python init_alembic.py [options]

Examples:
    python init_alembic.py
    python init_alembic.py --database-url "postgresql://user:pass@localhost/db"
"""

import argparse
import os
import subprocess
from pathlib import Path


ENV_PY_TEMPLATE = '''"""Alembic environment configuration for SQLModel"""
from logging.config import fileConfig
from sqlmodel import SQLModel
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import all your models here so Alembic can detect them
# from app.models import User, Post, etc.

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get the metadata from SQLModel
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {{}}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''


def init_alembic(database_url: str = None):
    """Initialize Alembic for the project"""

    # Check if alembic is installed
    try:
        import alembic
    except ImportError:
        print("Error: Alembic is not installed. Install it with: pip install alembic")
        return False

    # Check if already initialized
    if Path("alembic").exists():
        print("Warning: alembic directory already exists. Skipping initialization.")
        return True

    # Initialize alembic
    print("Initializing Alembic...")
    subprocess.run(["alembic", "init", "alembic"], check=True)

    # Update env.py with SQLModel-specific configuration
    env_py_path = Path("alembic/env.py")
    if env_py_path.exists():
        print("Updating env.py for SQLModel...")
        env_py_path.write_text(ENV_PY_TEMPLATE)

    # Update alembic.ini with database URL if provided
    if database_url:
        alembic_ini_path = Path("alembic.ini")
        if alembic_ini_path.exists():
            content = alembic_ini_path.read_text()
            content = content.replace(
                "sqlalchemy.url = driver://user:pass@localhost/dbname",
                f"sqlalchemy.url = {database_url}"
            )
            alembic_ini_path.write_text(content)
            print(f"Updated database URL in alembic.ini")

    print("\nAlembic initialized successfully!")
    print("\nNext steps:")
    print("1. Import all your models in alembic/env.py")
    print("2. Create your first migration: alembic revision --autogenerate -m 'Initial migration'")
    print("3. Apply migrations: alembic upgrade head")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Initialize Alembic for SQLModel migrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --database-url "sqlite:///./database.db"
  %(prog)s --database-url "postgresql://user:password@localhost/mydb"
        """
    )

    parser.add_argument(
        "--database-url",
        help="Database URL for alembic.ini (default: sqlite:///./database.db)"
    )

    args = parser.parse_args()

    database_url = args.database_url or "sqlite:///./database.db"

    success = init_alembic(database_url)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
