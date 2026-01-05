# Using NeonDB with Todo Management API

NeonDB is a serverless PostgreSQL database that's perfect for this project. No need to install PostgreSQL locally!

## Step 1: Get Your NeonDB Connection String

1. Go to [NeonDB Console](https://console.neon.tech)
2. Sign up or log in (free tier available)
3. Create a new project or use existing one
4. Click on your project
5. Go to **Dashboard** → **Connection Details**
6. Copy the **Connection string**

Your connection string will look like:
```
postgresql://username:password@ep-cool-project-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

## Step 2: Configure Your Application

Create a `.env` file in the project root:

```bash
# From the project directory
cd todo-management-api

# Create .env file
cp .env.example .env
```

Edit `.env` and paste your NeonDB connection string:

```bash
# Database Configuration
DATABASE_URL=postgresql://your-user:your-password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require

# Development settings
DEBUG=True
```

**Important**: Replace the entire URL with your actual NeonDB connection string!

## Step 3: Run the Application

That's it! No need to install PostgreSQL locally.

```bash
# Run the app
uv run fastapi dev main.py
```

The application will:
1. Connect to your NeonDB database
2. Automatically create all tables on startup
3. Be ready to use at http://localhost:8000

## Step 4: Verify Connection

Visit http://localhost:8000/docs and create a todo:

```json
{
  "title": "Test NeonDB connection",
  "description": "This should save to my NeonDB database!",
  "priority": "high"
}
```

## Running Tests with NeonDB

The tests use an in-memory SQLite database by default (faster), but you can test against NeonDB:

```bash
# Tests will still use SQLite (recommended for speed)
uv run pytest -v

# The actual app uses your NeonDB connection
uv run fastapi dev main.py
```

## NeonDB Features You Get

- ✅ **Serverless**: No server management
- ✅ **Auto-scaling**: Scales to zero when not in use
- ✅ **Branching**: Create database branches for testing
- ✅ **SSL by default**: Secure connections
- ✅ **Free tier**: 0.5 GB storage, 3 GB data transfer/month
- ✅ **Backups**: Automatic point-in-time restore
- ✅ **Global**: Multiple regions available

## Viewing Your Data

You can view your data in NeonDB:

1. Go to [NeonDB Console](https://console.neon.tech)
2. Select your project
3. Click **SQL Editor**
4. Run queries:

```sql
-- See all todos
SELECT * FROM todos;

-- Count todos by status
SELECT status, COUNT(*) FROM todos GROUP BY status;

-- See recent todos
SELECT title, status, created_at
FROM todos
ORDER BY created_at DESC
LIMIT 10;
```

## Production Deployment

NeonDB is production-ready! For production:

1. Use the **Production** branch in NeonDB
2. Set environment variables in your hosting platform:
   ```bash
   DATABASE_URL=your-neondb-connection-string
   DEBUG=False
   ```
3. Deploy your app (Vercel, Railway, Fly.io, etc.)

## Database Migrations with NeonDB

If you need to use Alembic migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply to NeonDB
alembic upgrade head
```

The migrations will run directly against your NeonDB database.

## Troubleshooting

### Connection Error: "SSL required"

Make sure your connection string includes `?sslmode=require`:
```
postgresql://user:pass@host/db?sslmode=require
```

### Connection Timeout

NeonDB scales to zero when inactive. First connection after inactivity may take 1-2 seconds. This is normal!

### "Database does not exist"

NeonDB creates a default database called `neondb`. Use that, or create a new database in the NeonDB console.

## Cost-Free Development

With NeonDB's free tier, you get:
- 0.5 GB storage (plenty for thousands of todos)
- 3 GB data transfer/month
- Unlimited compute hours
- **No credit card required**

Perfect for development and small production apps! 🚀

---

**Need help?** Check the [NeonDB Documentation](https://neon.tech/docs/introduction)
