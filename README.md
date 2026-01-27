# FastAPI PostgreSQL Application

A production-ready FastAPI backend with PostgreSQL (SQL + pgvector), user management, and JWT authentication.

## Features

- **FastAPI** with async support
- **PostgreSQL** with pgvector extension for vector similarity search
- **JWT Authentication** with access and refresh tokens
- **User Management** - complete CRUD operations
- **Repository-Service Pattern** - clean separation of concerns
- **Argon2 Password Hashing** - OWASP 2025 recommended
- **Docker Compose** - containerized development environment
- **Alembic Migrations** - async database migrations
- **Pydantic v2** - request/response validation
- **LangGraph Worker** - independent AI workflow processing with PostgreSQL checkpointing

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py           # Pydantic settings
│   ├── database.py         # Async SQLAlchemy setup
│   ├── security.py         # JWT and password hashing
│   └── exceptions.py       # Custom HTTP exceptions
├── models/
│   └── user.py             # SQLAlchemy User model
├── schemas/
│   ├── user.py             # User Pydantic schemas
│   └── auth.py             # Auth Pydantic schemas
├── repositories/
│   └── user.py             # User database operations
├── services/
│   ├── user.py             # User business logic
│   └── auth.py             # Auth business logic
├── api/
│   ├── deps.py             # Dependency injection
│   └── v1/
│       ├── router.py       # API v1 router
│       ├── auth.py         # Auth endpoints
│       ├── users.py        # User endpoints
│       └── health.py       # Health check
└── migrations/             # Alembic migrations

worker/                     # Independent LangGraph worker
├── main.py                 # Worker entry point
├── core/
│   ├── config.py           # Worker settings
│   └── checkpointer.py     # AsyncPostgresSaver setup
└── graphs/
    ├── base.py             # Base graph types
    └── example_graph.py    # Example StateGraph
```

## Requirements

- Python 3.11+
- Docker and Docker Compose (for PostgreSQL)

## Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
uv venv .venv --python 3.12
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Generate a secure secret key
openssl rand -hex 32
# Update SECRET_KEY in .env with the generated value
```

### 3. Start PostgreSQL

```bash
docker compose up -d db
```

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start the Application

```bash
uvicorn app.main:app --reload
```

The API is now available at http://localhost:8000

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

| Method | Endpoint              | Description                    |
| ------ | --------------------- | ------------------------------ |
| POST   | `/api/v1/auth/register` | Register a new user          |
| POST   | `/api/v1/auth/login`    | Login (returns JWT tokens)   |
| POST   | `/api/v1/auth/refresh`  | Refresh access token         |

### Users

| Method | Endpoint              | Description                    | Auth Required |
| ------ | --------------------- | ------------------------------ | ------------- |
| GET    | `/api/v1/users/me`    | Get current user profile       | Yes           |
| PUT    | `/api/v1/users/me`    | Update current user profile    | Yes           |
| GET    | `/api/v1/users`       | List all users                 | Admin         |
| GET    | `/api/v1/users/{id}`  | Get user by ID                 | Admin         |
| PUT    | `/api/v1/users/{id}`  | Update user by ID              | Admin         |
| DELETE | `/api/v1/users/{id}`  | Delete user by ID              | Admin         |

### Health

| Method | Endpoint              | Description                    |
| ------ | --------------------- | ------------------------------ |
| GET    | `/api/v1/health`      | Basic health check             |
| GET    | `/api/v1/health/db`   | Health check with DB status    |

## Usage Examples

### Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword123", "full_name": "John Doe"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

### Access Protected Endpoint

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Lint Code

```bash
ruff check .
ruff check --fix .  # Auto-fix issues
```

### Type Check

```bash
mypy app --ignore-missing-imports
```

### Create New Migration

```bash
alembic revision --autogenerate -m "description"
```

## Docker

### Development (with hot reload)

```bash
docker compose up
```

### Build Production Image

```bash
docker build -t fastapi-app .
```

## Environment Variables

| Variable                    | Description                        | Default                  |
| --------------------------- | ---------------------------------- | ------------------------ |
| `APP_NAME`                  | Application name                   | FastAPI App              |
| `DEBUG`                     | Enable debug mode                  | false                    |
| `API_V1_PREFIX`             | API v1 URL prefix                  | /api/v1                  |
| `DATABASE_URL`              | PostgreSQL connection URL          | (required)               |
| `DATABASE_ECHO`             | Log SQL queries                    | false                    |
| `SECRET_KEY`                | JWT signing key                    | (required for production)|
| `ALGORITHM`                 | JWT algorithm                      | HS256                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime            | 30                       |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime             | 7                        |

## LangGraph Worker

The project includes an independent LangGraph worker for running AI workflows with persistent state.

### Architecture

```
┌─────────────┐         ┌─────────────┐
│  FastAPI    │         │  LangGraph  │
│    API      │         │   Worker    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       └───────────┬───────────┘
                   │
           ┌───────┴───────┐
           │  PostgreSQL   │
           │  (shared DB)  │
           └───────────────┘
```

- **Independent processes**: API and worker run separately
- **Shared database**: Both use the same PostgreSQL instance
- **Persistent state**: Worker uses PostgresSaver checkpointer for durable graph state

### Running the Worker

```bash
# Start PostgreSQL first
docker compose up -d db

# Run the worker
python -m worker.main
```

### With Docker Compose

```bash
# Start all services (db, app, worker)
docker compose up
```

### Creating Custom Graphs

1. Create a new file in `worker/graphs/`:

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.base import BaseCheckpointSaver

class MyState(TypedDict):
    messages: Annotated[list[dict], add_messages]

async def my_node(state: MyState) -> dict:
    return {"messages": [{"role": "assistant", "content": "Hello!"}]}

def create_my_graph(checkpointer: BaseCheckpointSaver | None = None):
    builder = StateGraph(MyState)
    builder.add_node("my_node", my_node)
    builder.add_edge(START, "my_node")
    builder.add_edge("my_node", END)
    return builder.compile(checkpointer=checkpointer)
```

2. Use the graph with the checkpointer:

```python
from worker.core.checkpointer import get_checkpointer
from worker.graphs.my_graph import create_my_graph

async def run():
    async with get_checkpointer() as checkpointer:
        graph = create_my_graph(checkpointer)
        result = await graph.ainvoke(
            {"messages": [{"role": "user", "content": "Hi"}]},
            config={"configurable": {"thread_id": "my-thread"}}
        )
```

### Worker Environment Variables

| Variable                | Description                  | Default           |
| ----------------------- | ---------------------------- | ----------------- |
| `WORKER_NAME`           | Worker instance name         | langgraph-worker  |
| `CHECKPOINTER_POOL_SIZE`| PostgreSQL connection pool   | 5                 |
| `DATABASE_URL`          | PostgreSQL connection URL    | (same as app)     |
| `DEBUG`                 | Enable debug logging         | false             |

## Security Notes

- Always use a strong, unique `SECRET_KEY` in production
- Configure CORS appropriately for your deployment
- Consider adding rate limiting for production use
- Enable HTTPS in production (use Traefik or nginx as reverse proxy)

## License

MIT
