# Database Migrations with Alembic

Guide for managing database schema changes using Alembic with SQLModel.

## Table of Contents
- Setup and Installation
- Creating Migrations
- Applying Migrations
- Common Migration Operations
- Best Practices
- Troubleshooting

## Setup and Installation

### Install Alembic

```bash
# Add alembic with uv
uv add alembic
```

### Initialize Alembic

Use the provided script:

```bash
uv run python scripts/init_alembic.py --database-url "sqlite:///./database.db"
```

Or manually:

```bash
alembic init alembic
```

### Configure env.py for SQLModel

Update `alembic/env.py` to use SQLModel metadata:

```python
from sqlmodel import SQLModel

# Import all your models so Alembic can detect them
from app.models import Hero, Team, User, etc.

# Use SQLModel's metadata
target_metadata = SQLModel.metadata
```

### Configure Database URL

In `alembic.ini`:

```ini
sqlalchemy.url = sqlite:///./database.db
# or
sqlalchemy.url = postgresql://user:password@localhost/dbname
```

Or use environment variables (recommended):

```python
# In alembic/env.py
from os import environ

config.set_main_option('sqlalchemy.url', environ.get('DATABASE_URL'))
```

## Creating Migrations

### Auto-generate Migration from Model Changes

```bash
alembic revision --autogenerate -m "Add user table"
```

This compares your SQLModel models with the current database schema and generates migration code.

### Create Empty Migration (Manual)

```bash
alembic revision -m "Custom migration"
```

### Migration File Structure

```python
"""Add user table

Revision ID: abc123
Revises: xyz789
Create Date: 2024-01-01 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision = 'abc123'
down_revision = 'xyz789'  # Previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Operations to apply the migration
    pass


def downgrade():
    # Operations to reverse the migration
    pass
```

## Applying Migrations

### Upgrade to Latest Version

```bash
alembic upgrade head
```

### Upgrade to Specific Version

```bash
alembic upgrade abc123
```

### Upgrade One Step

```bash
alembic upgrade +1
```

### Downgrade One Step

```bash
alembic downgrade -1
```

### Downgrade to Specific Version

```bash
alembic downgrade xyz789
```

### View Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

## Common Migration Operations

### Create Table

```python
def upgrade():
    op.create_table(
        'hero',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('secret_name', sa.String(length=100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['team.id']),
    )
    op.create_index('ix_hero_name', 'hero', ['name'])


def downgrade():
    op.drop_index('ix_hero_name', table_name='hero')
    op.drop_table('hero')
```

### Add Column

```python
def upgrade():
    op.add_column('hero', sa.Column('email', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('hero', 'email')
```

### Modify Column

```python
def upgrade():
    # Change column type
    op.alter_column('hero', 'age',
                    existing_type=sa.Integer(),
                    type_=sa.SmallInteger(),
                    existing_nullable=True)

    # Make column non-nullable (fill nulls first!)
    op.execute('UPDATE hero SET email = "" WHERE email IS NULL')
    op.alter_column('hero', 'email',
                    existing_type=sa.String(length=255),
                    nullable=False)


def downgrade():
    op.alter_column('hero', 'email',
                    existing_type=sa.String(length=255),
                    nullable=True)

    op.alter_column('hero', 'age',
                    existing_type=sa.SmallInteger(),
                    type_=sa.Integer(),
                    existing_nullable=True)
```

### Rename Column

```python
def upgrade():
    op.alter_column('hero', 'secret_name', new_column_name='alias')


def downgrade():
    op.alter_column('hero', 'alias', new_column_name='secret_name')
```

### Add Index

```python
def upgrade():
    op.create_index('ix_hero_email', 'hero', ['email'], unique=True)


def downgrade():
    op.drop_index('ix_hero_email', table_name='hero')
```

### Add Foreign Key

```python
def upgrade():
    op.create_foreign_key(
        'fk_hero_team_id',
        'hero', 'team',
        ['team_id'], ['id']
    )


def downgrade():
    op.drop_constraint('fk_hero_team_id', 'hero', type_='foreignkey')
```

### Data Migration

```python
from alembic import op
from sqlalchemy import orm
from sqlmodel import Session, select
from app.models import Hero


def upgrade():
    # Get database connection
    bind = op.get_bind()
    session = Session(bind=bind)

    # Update data
    heroes = session.exec(select(Hero)).all()
    for hero in heroes:
        hero.updated_at = datetime.utcnow()

    session.commit()


def downgrade():
    # Reverse data changes if possible
    pass
```

## Best Practices

### 1. Always Review Auto-Generated Migrations

Auto-generate is helpful but not perfect. Always review and test:

```bash
alembic revision --autogenerate -m "Add field"
# Review alembic/versions/xxx_add_field.py before applying!
```

### 2. Import All Models Before Generating

Ensure all models are imported in `alembic/env.py`:

```python
# alembic/env.py
from app.models import Hero, Team, User, Product  # Import all models!
```

### 3. Test Migrations in Development First

```bash
# Create migration
alembic revision --autogenerate -m "Add user email"

# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Re-upgrade
alembic upgrade head
```

### 4. Use Descriptive Migration Messages

```bash
# Bad
alembic revision -m "update"

# Good
alembic revision -m "Add user email field with unique constraint"
```

### 5. Handle Data Carefully When Changing Nullable Fields

```python
def upgrade():
    # Step 1: Add column as nullable
    op.add_column('hero', sa.Column('email', sa.String(255), nullable=True))

    # Step 2: Populate existing rows
    op.execute("UPDATE hero SET email = 'default@example.com' WHERE email IS NULL")

    # Step 3: Make non-nullable
    op.alter_column('hero', 'email', nullable=False)


def downgrade():
    op.drop_column('hero', 'email')
```

### 6. Create Separate Migrations for Data and Schema

```bash
# First: Schema change
alembic revision -m "Add email column"

# Second: Data migration
alembic revision -m "Populate email for existing users"
```

### 7. Use Transactions for Data Migrations

```python
def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Your data migration
        heroes = session.exec(select(Hero)).all()
        for hero in heroes:
            hero.status = "active"
        session.commit()
    except Exception:
        session.rollback()
        raise
```

### 8. Never Modify Existing Migrations

Once a migration is applied in production, never modify it. Create a new migration instead.

### 9. Keep Migrations Small and Focused

```bash
# Bad - one big migration
alembic revision -m "Add users, teams, and products"

# Good - separate migrations
alembic revision -m "Add users table"
alembic revision -m "Add teams table"
alembic revision -m "Add products table"
```

### 10. Use Environment-Specific Settings

```python
# alembic/env.py
from os import environ

if environ.get('TESTING'):
    # Skip certain migrations in tests
    pass
```

## Troubleshooting

### Migration Detects No Changes

```bash
# Ensure all models are imported in env.py
# Check that SQLModel metadata is used:
target_metadata = SQLModel.metadata
```

### "Table already exists" Error

```bash
# Mark current state without running migrations:
alembic stamp head

# Or create new migration from current state:
alembic revision --autogenerate -m "Initial migration from existing db"
```

### Rollback Failed Migration

```bash
# If upgrade fails, manually mark as not applied:
alembic downgrade -1

# Or edit alembic_version table directly (last resort):
# UPDATE alembic_version SET version_num='previous_revision';
```

### Multiple Heads (Branched History)

```bash
# View heads
alembic heads

# Merge branches
alembic merge heads -m "Merge migration branches"
```

### Reset All Migrations (Development Only!)

```bash
# Drop all tables
# Re-run migrations from scratch
alembic upgrade head
```

## Production Deployment Workflow

```bash
# 1. Generate migration in development
alembic revision --autogenerate -m "Add feature X"

# 2. Review and test migration
alembic upgrade head
alembic downgrade -1
alembic upgrade head

# 3. Commit migration file to version control
git add alembic/versions/xxx_add_feature_x.py
git commit -m "Add migration for feature X"

# 4. Deploy to staging
git pull
alembic upgrade head

# 5. Test in staging

# 6. Deploy to production
git pull
alembic upgrade head
```
