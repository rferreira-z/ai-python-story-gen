# Feature: LangGraph Worker with PostgresSaver Checkpointer

## Summary

Create an independent LangGraph worker process that runs alongside the FastAPI API in a monorepo structure. The worker will use PostgresSaver as its checkpointer for state persistence, sharing the same PostgreSQL database but operating as a completely separate process. This enables long-running, stateful AI agent workflows that can survive restarts and scale independently from the API.

## User Story

As a developer
I want to run LangGraph workflows independently from the FastAPI API
So that I can process long-running AI agent tasks without blocking API requests and with persistent state recovery

## Problem Statement

The current FastAPI application handles synchronous request-response patterns but lacks infrastructure for:
1. Long-running AI agent workflows that may take minutes to complete
2. Stateful conversation/task persistence across process restarts
3. Independent scaling of worker processes from API processes
4. Background processing that doesn't block API response times

## Solution Statement

Create a standalone LangGraph worker module within the monorepo that:
1. Runs as an independent Python process (`python -m worker.main`)
2. Uses `AsyncPostgresSaver` from `langgraph-checkpoint-postgres` for durable state persistence
3. Shares the PostgreSQL database configuration with the FastAPI app via common config
4. Provides a clean interface for defining and executing LangGraph StateGraphs
5. Includes example graph implementation to demonstrate the pattern

## Metadata

| Field            | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Type             | NEW_CAPABILITY                                                |
| Complexity       | MEDIUM                                                        |
| Systems Affected | Database, Configuration, Docker, Project Structure            |
| Dependencies     | langgraph>=1.0.6, langgraph-checkpoint-postgres>=3.0.3, psycopg[pool]>=3.2.0 |
| Estimated Tasks  | 12                                                            |

---

## UX Design

### Before State

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              BEFORE STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐            ║
║   │   Client    │ ──────► │  FastAPI    │ ──────► │  PostgreSQL │            ║
║   │   Request   │         │   (sync)    │         │   Database  │            ║
║   └─────────────┘         └─────────────┘         └─────────────┘            ║
║                                                                               ║
║   USER_FLOW:                                                                  ║
║   1. Client sends HTTP request                                                ║
║   2. FastAPI processes request synchronously                                  ║
║   3. Response returned to client                                              ║
║                                                                               ║
║   PAIN_POINT:                                                                 ║
║   - No support for long-running AI workflows                                  ║
║   - No state persistence for multi-turn conversations                         ║
║   - AI tasks would block API if integrated directly                           ║
║                                                                               ║
║   DATA_FLOW:                                                                  ║
║   Client → FastAPI → PostgreSQL → FastAPI → Client (blocking)                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### After State

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                               AFTER STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────┐         ┌─────────────┐                                     ║
║   │   Client    │ ──────► │  FastAPI    │ ──────┐                             ║
║   │   Request   │         │    API      │       │                             ║
║   └─────────────┘         └─────────────┘       │                             ║
║                                                  │                             ║
║                                                  ▼                             ║
║                                          ┌─────────────┐                       ║
║                                          │  PostgreSQL │                       ║
║                                          │  (shared)   │                       ║
║                                          └─────────────┘                       ║
║                                                  ▲                             ║
║   ┌─────────────┐         ┌─────────────┐       │                             ║
║   │   Task      │ ──────► │  LangGraph  │ ──────┘                             ║
║   │   Queue     │         │   Worker    │                                     ║
║   └─────────────┘         └─────────────┘                                     ║
║                                  │                                            ║
║                                  ▼                                            ║
║                          ┌─────────────────┐                                  ║
║                          │  PostgresSaver  │  ◄── Checkpointer tables         ║
║                          │  (persisted     │      (checkpoint_writes,         ║
��                          │   graph state)  │       checkpoint_blobs, etc.)    ║
║                          └─────────────────┘                                  ║
║                                                                               ║
║   USER_FLOW:                                                                  ║
║   1. API can trigger worker tasks via shared DB/queue (future)                ║
║   2. Worker runs LangGraph workflows independently                            ║
║   3. State persisted via PostgresSaver checkpointer                           ║
║   4. Worker can resume from any checkpoint after restart                      ║
║                                                                               ║
║   VALUE_ADD:                                                                  ║
║   - Independent scaling of API and worker processes                           ║
║   - Durable AI workflows that survive process restarts                        ║
║   - Clean separation of concerns (API vs AI processing)                       ║
║                                                                               ║
║   DATA_FLOW:                                                                  ║
║   Worker → LangGraph → PostgresSaver → PostgreSQL (async, non-blocking)       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Interaction Changes

| Location               | Before                  | After                               | User Impact                                    |
| ---------------------- | ----------------------- | ----------------------------------- | ---------------------------------------------- |
| Project Structure      | Single `app/` directory | `app/` + `worker/` directories      | Clear monorepo separation                      |
| Process Management     | Single uvicorn process  | uvicorn + worker process            | Independent scaling                            |
| Database               | App tables only         | App tables + checkpoint tables      | Persistent graph state                         |
| Docker Compose         | 2 services (db, app)    | 3 services (db, app, worker)        | Full orchestration                             |
| Configuration          | App-only settings       | Shared settings + worker settings   | Unified config management                      |

---

## Mandatory Reading

**CRITICAL: Implementation agent MUST read these files before starting any task:**

| Priority | File                           | Lines   | Why Read This                                    |
| -------- | ------------------------------ | ------- | ------------------------------------------------ |
| P0       | `app/core/config.py`           | all     | Pattern for Pydantic settings - MIRROR exactly   |
| P0       | `app/core/database.py`         | all     | Async SQLAlchemy pattern - understand connection |
| P1       | `pyproject.toml`               | all     | Dependencies structure to UPDATE                 |
| P1       | `docker-compose.yml`           | all     | Service orchestration to UPDATE                  |
| P2       | `app/main.py`                  | all     | FastAPI app structure for comparison             |
| P2       | `app/migrations/env.py`        | all     | Alembic async pattern for reference              |

**External Documentation:**

| Source                                                                                  | Section          | Why Needed                              |
| --------------------------------------------------------------------------------------- | ---------------- | --------------------------------------- |
| [langgraph-checkpoint-postgres v3.0.3](https://pypi.org/project/langgraph-checkpoint-postgres/) | Setup & Usage    | AsyncPostgresSaver configuration        |
| [LangGraph v1.0.6](https://pypi.org/project/langgraph/)                                 | StateGraph       | Graph compilation and async execution   |
| [psycopg3 Pool Docs](https://www.psycopg.org/psycopg3/docs/api/pool.html)               | AsyncConnectionPool | Async pool configuration             |
| [LangGraph Memory Docs](https://docs.langchain.com/oss/python/langgraph/add-memory)     | Checkpointing    | Memory/state persistence patterns       |

---

## Patterns to Mirror

**PYDANTIC_SETTINGS_PATTERN:**
```python
# SOURCE: app/core/config.py:6-31
# COPY THIS PATTERN:
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "FastAPI App"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"

settings = Settings()
```

**ASYNC_DATABASE_PATTERN:**
```python
# SOURCE: app/core/database.py:1-39
# COPY THIS PATTERN for understanding async engine creation:
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

**DOCKER_SERVICE_PATTERN:**
```yaml
# SOURCE: docker-compose.yml:18-30
# COPY THIS PATTERN for worker service:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-app_db}
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
      DEBUG: ${DEBUG:-true}
    depends_on:
      db:
        condition: service_healthy
```

**MAIN_ENTRY_PATTERN:**
```python
# SOURCE: app/main.py:1-30
# REFERENCE for worker entry point structure:
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

@app.get("/")
async def root() -> dict:
    return {"message": f"Welcome to {settings.app_name}"}
```

---

## Files to Change

| File                                | Action | Justification                                              |
| ----------------------------------- | ------ | ---------------------------------------------------------- |
| `pyproject.toml`                    | UPDATE | Add langgraph and checkpoint dependencies                  |
| `worker/__init__.py`                | CREATE | Worker package marker                                      |
| `worker/core/__init__.py`           | CREATE | Worker core subpackage marker                              |
| `worker/core/config.py`             | CREATE | Worker-specific configuration                              |
| `worker/core/checkpointer.py`       | CREATE | AsyncPostgresSaver setup and management                    |
| `worker/graphs/__init__.py`         | CREATE | Graphs subpackage marker                                   |
| `worker/graphs/base.py`             | CREATE | Base graph utilities and types                             |
| `worker/graphs/example_graph.py`    | CREATE | Example StateGraph implementation                          |
| `worker/main.py`                    | CREATE | Worker process entry point                                 |
| `docker-compose.yml`                | UPDATE | Add worker service definition                              |
| `.env.example`                      | UPDATE | Add worker-specific environment variables                  |
| `README.md`                         | UPDATE | Add worker documentation section                           |

---

## NOT Building (Scope Limits)

Explicit exclusions to prevent scope creep:

- **Task Queue Integration**: No Redis/Celery/RabbitMQ - future enhancement
- **API-Worker Communication**: No direct HTTP/gRPC between API and worker - use shared DB for now
- **Multiple Graph Types**: Only one example graph - users can add more following the pattern
- **LangChain Integration**: Pure LangGraph only - no LangChain chains/agents
- **Custom LLM Configuration**: No OpenAI/Anthropic setup - example uses mock nodes
- **Worker Scaling**: No Kubernetes/horizontal scaling config - single worker instance
- **Monitoring/Observability**: No LangSmith/Prometheus integration - future enhancement

---

## Step-by-Step Tasks

Execute in order. Each task is atomic and independently verifiable.

### Task 1: UPDATE `pyproject.toml` - Add LangGraph dependencies

- **ACTION**: ADD langgraph and checkpoint dependencies to project
- **IMPLEMENT**:
  ```toml
  # Add to dependencies list:
  "langgraph>=1.0.6",
  "langgraph-checkpoint-postgres>=3.0.3",
  "psycopg[pool]>=3.2.0",
  ```
- **MIRROR**: Existing dependency format in `pyproject.toml:6-18`
- **GOTCHA**: psycopg[pool] is separate from asyncpg - both needed (asyncpg for SQLAlchemy, psycopg for LangGraph)
- **VALIDATE**: `cd /Users/rff/Documents/projects/ai/ai-python-story-gen && .venv/bin/pip install -e .`

### Task 2: CREATE `worker/__init__.py` - Worker package marker

- **ACTION**: CREATE empty package marker file
- **IMPLEMENT**:
  ```python
  """LangGraph worker package for independent AI workflow processing."""
  ```
- **VALIDATE**: `python -c "import worker"`

### Task 3: CREATE `worker/core/__init__.py` - Core subpackage marker

- **ACTION**: CREATE empty package marker file
- **IMPLEMENT**:
  ```python
  """Worker core configuration and utilities."""
  ```
- **VALIDATE**: `python -c "from worker import core"`

### Task 4: CREATE `worker/core/config.py` - Worker configuration

- **ACTION**: CREATE Pydantic settings for worker process
- **IMPLEMENT**:
  - Extend/mirror `app/core/config.py` pattern
  - Add `worker_name` setting
  - Add `checkpointer_pool_size` setting (default 5)
  - Create database URL conversion for psycopg format (postgresql:// not postgresql+asyncpg://)
  - Property to get psycopg-compatible connection string
- **MIRROR**: `app/core/config.py:1-31` - exact same SettingsConfigDict pattern
- **IMPORTS**: `from pydantic_settings import BaseSettings, SettingsConfigDict`
- **GOTCHA**: LangGraph uses psycopg3 (postgresql://), FastAPI uses asyncpg (postgresql+asyncpg://) - need URL transformation
- **VALIDATE**: `.venv/bin/python -c "from worker.core.config import settings; print(settings.psycopg_database_url)"`

### Task 5: CREATE `worker/core/checkpointer.py` - AsyncPostgresSaver management

- **ACTION**: CREATE checkpointer factory and lifecycle management
- **IMPLEMENT**:
  - Async context manager for AsyncPostgresSaver
  - Use `AsyncConnectionPool` from psycopg_pool
  - Configure with `autocommit=True` and `row_factory=dict_row`
  - Include `.setup()` call on first use
  - Proper pool cleanup on exit
- **IMPORTS**:
  ```python
  from contextlib import asynccontextmanager
  from psycopg_pool import AsyncConnectionPool
  from psycopg.rows import dict_row
  from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
  ```
- **GOTCHA**: Must set `autocommit=True` on pool connections for setup() to work
- **GOTCHA**: Must use `row_factory=dict_row` - PostgresSaver uses dict access
- **VALIDATE**: `.venv/bin/python -c "from worker.core.checkpointer import get_checkpointer; print('OK')"`

### Task 6: CREATE `worker/graphs/__init__.py` - Graphs subpackage marker

- **ACTION**: CREATE package marker with exports
- **IMPLEMENT**:
  ```python
  """LangGraph graph definitions."""
  from worker.graphs.example_graph import create_example_graph

  __all__ = ["create_example_graph"]
  ```
- **VALIDATE**: `python -c "from worker.graphs import create_example_graph"`

### Task 7: CREATE `worker/graphs/base.py` - Base graph types and utilities

- **ACTION**: CREATE shared types and utilities for graphs
- **IMPLEMENT**:
  - TypedDict for base graph state
  - Logging setup for graphs
  - Common type aliases
- **IMPORTS**:
  ```python
  from typing import TypedDict, Annotated
  from langgraph.graph import StateGraph, START, END
  from langgraph.graph.message import add_messages
  import logging
  ```
- **VALIDATE**: `.venv/bin/python -c "from worker.graphs.base import BaseState; print('OK')"`

### Task 8: CREATE `worker/graphs/example_graph.py` - Example StateGraph

- **ACTION**: CREATE example graph demonstrating the pattern
- **IMPLEMENT**:
  - Simple multi-step graph (input → process → output)
  - Async node functions
  - State with messages list using `add_messages` reducer
  - Factory function returning compiled graph
  - Demonstrate conditional edges
- **MIRROR**: LangGraph official StateGraph pattern
- **IMPORTS**:
  ```python
  from typing import TypedDict, Annotated, Literal
  from langgraph.graph import StateGraph, START, END
  from langgraph.graph.message import add_messages
  from langgraph.checkpoint.base import BaseCheckpointSaver
  ```
- **GOTCHA**: Must call `.compile(checkpointer=checkpointer)` to enable persistence
- **VALIDATE**: `.venv/bin/python -c "from worker.graphs.example_graph import create_example_graph; g = create_example_graph(); print(g)"`

### Task 9: CREATE `worker/main.py` - Worker entry point

- **ACTION**: CREATE main entry point for worker process
- **IMPLEMENT**:
  - Async main function
  - Initialize checkpointer with setup
  - Load and compile graph with checkpointer
  - Example invocation loop (can be replaced with queue consumer)
  - Graceful shutdown handling
  - CLI entry point with `if __name__ == "__main__"`
- **MIRROR**: Structure similar to `app/main.py` but async-first
- **IMPORTS**:
  ```python
  import asyncio
  import logging
  import signal
  from worker.core.config import settings
  from worker.core.checkpointer import get_checkpointer
  from worker.graphs import create_example_graph
  ```
- **GOTCHA**: Use `asyncio.run()` for entry point, handle SIGTERM/SIGINT
- **VALIDATE**: `.venv/bin/python -m worker.main --help` or dry-run

### Task 10: UPDATE `docker-compose.yml` - Add worker service

- **ACTION**: ADD worker service definition
- **IMPLEMENT**:
  - New `worker` service
  - Same build context as app
  - Different command: `python -m worker.main`
  - Same environment variables as app
  - Depends on db health check
  - No port exposure needed (internal process)
- **MIRROR**: `docker-compose.yml:18-30` - app service pattern
- **GOTCHA**: Worker needs DATABASE_URL in psycopg format, not asyncpg format - handle in config
- **VALIDATE**: `docker-compose config` (validates syntax)

### Task 11: UPDATE `.env.example` - Add worker environment variables

- **ACTION**: ADD worker-specific environment variable documentation
- **IMPLEMENT**:
  ```
  # Worker Configuration
  WORKER_NAME="story-gen-worker"
  CHECKPOINTER_POOL_SIZE=5
  ```
- **MIRROR**: Existing environment variable format in `.env.example`
- **VALIDATE**: Visual inspection of file

### Task 12: UPDATE `README.md` - Add worker documentation

- **ACTION**: ADD section documenting the worker
- **IMPLEMENT**:
  - New "## LangGraph Worker" section
  - Running the worker locally
  - Running with Docker Compose
  - Creating new graphs
  - Architecture overview
- **MIRROR**: Existing README style and markdown format
- **VALIDATE**: Visual inspection, markdown lint

---

## Testing Strategy

### Unit Tests to Write

| Test File                           | Test Cases                                    | Validates                |
| ----------------------------------- | --------------------------------------------- | ------------------------ |
| `tests/worker/test_config.py`       | URL conversion, settings loading              | Worker configuration     |
| `tests/worker/test_example_graph.py`| Graph compilation, node execution, state flow | Example graph logic      |

### Integration Tests (Manual)

| Test                          | Steps                                                         | Expected Result                    |
| ----------------------------- | ------------------------------------------------------------- | ---------------------------------- |
| Worker starts                 | `python -m worker.main`                                       | Logs show initialization           |
| Checkpointer connects         | Worker connects to PostgreSQL                                 | No connection errors               |
| Graph executes                | Worker processes example input                                | State transitions logged           |
| State persists                | Restart worker, check checkpoint                              | Previous state recoverable         |
| Docker Compose                | `docker-compose up`                                           | All 3 services start               |

### Edge Cases Checklist

- [ ] Database not available - worker should retry or fail gracefully
- [ ] Invalid DATABASE_URL format - clear error message
- [ ] Checkpoint tables don't exist - setup() creates them
- [ ] Worker interrupted mid-execution - state should be recoverable
- [ ] Empty state input - graph should handle gracefully
- [ ] Concurrent workers (future) - checkpointer handles locking

---

## Validation Commands

**IMPORTANT**: All commands use the project's virtual environment.

### Level 1: STATIC_ANALYSIS

```bash
cd /Users/rff/Documents/projects/ai/ai-python-story-gen && \
.venv/bin/ruff check worker/ && \
.venv/bin/mypy worker/ --ignore-missing-imports
```

**EXPECT**: Exit 0, no errors or warnings

### Level 2: IMPORT_VALIDATION

```bash
cd /Users/rff/Documents/projects/ai/ai-python-story-gen && \
.venv/bin/python -c "
from worker.core.config import settings
from worker.core.checkpointer import get_checkpointer
from worker.graphs import create_example_graph
from worker.main import main
print('All imports successful')
"
```

**EXPECT**: "All imports successful" printed

### Level 3: DEPENDENCY_INSTALL

```bash
cd /Users/rff/Documents/projects/ai/ai-python-story-gen && \
.venv/bin/pip install -e . && \
.venv/bin/python -c "import langgraph; print(f'langgraph {langgraph.__version__}')"
```

**EXPECT**: langgraph version printed (1.0.6 or higher)

### Level 4: DOCKER_VALIDATION

```bash
cd /Users/rff/Documents/projects/ai/ai-python-story-gen && \
docker-compose config
```

**EXPECT**: Valid YAML output with 3 services (db, app, worker)

### Level 5: WORKER_DRY_RUN (requires PostgreSQL running)

```bash
cd /Users/rff/Documents/projects/ai/ai-python-story-gen && \
timeout 10 .venv/bin/python -m worker.main --dry-run || true
```

**EXPECT**: Worker initializes and exits cleanly (or timeout if no dry-run flag)

### Level 6: FULL_INTEGRATION (requires PostgreSQL running)

```bash
cd /Users/rff/Documents/projects/ai/ai-python-story-gen && \
docker-compose up -d db && \
sleep 5 && \
.venv/bin/python -m worker.main &
WORKER_PID=$! && \
sleep 5 && \
kill $WORKER_PID && \
docker-compose down
```

**EXPECT**: Worker starts, connects to DB, and shuts down gracefully

---

## Acceptance Criteria

- [ ] Worker runs as independent process: `python -m worker.main`
- [ ] PostgresSaver checkpointer initializes and creates tables
- [ ] Example graph compiles and executes with persistent state
- [ ] Worker and API can run simultaneously without conflict
- [ ] Docker Compose starts all 3 services successfully
- [ ] Static analysis passes (ruff, mypy)
- [ ] All imports work without errors
- [ ] Configuration loads from .env file correctly
- [ ] Database URL transforms correctly between asyncpg and psycopg formats

---

## Completion Checklist

- [ ] All 12 tasks completed in dependency order
- [ ] Each task validated immediately after completion
- [ ] Level 1: Static analysis (ruff + mypy) passes
- [ ] Level 2: All imports successful
- [ ] Level 3: Dependencies install correctly
- [ ] Level 4: Docker Compose config validates
- [ ] Level 5: Worker dry-run works (if implemented)
- [ ] Level 6: Full integration test passes
- [ ] All acceptance criteria met

---

## Risks and Mitigations

| Risk                                    | Likelihood | Impact | Mitigation                                              |
| --------------------------------------- | ---------- | ------ | ------------------------------------------------------- |
| psycopg3/asyncpg version conflicts      | LOW        | HIGH   | Pin specific compatible versions in pyproject.toml      |
| Checkpoint table schema changes         | LOW        | MED    | Use setup() which handles migrations                    |
| Connection pool exhaustion              | MED        | MED    | Configure reasonable pool_size, add connection timeout  |
| Worker crashes lose in-flight state     | MED        | LOW    | Checkpointer persists after each node - recoverable     |
| Docker network issues between services  | LOW        | MED    | Use docker-compose networking, health checks            |

---

## Notes

### Architecture Decisions

1. **Separate `worker/` directory**: Chosen over adding to `app/` to emphasize independence and enable separate deployment/scaling in the future.

2. **Shared database, separate connection methods**: FastAPI uses asyncpg via SQLAlchemy, worker uses psycopg3 directly via LangGraph. Both can coexist on same PostgreSQL instance.

3. **No task queue yet**: Initial implementation uses direct execution. Task queue (Redis, RabbitMQ, or PostgreSQL LISTEN/NOTIFY) can be added later for API-worker communication.

4. **Example graph is minimal**: Intentionally simple to demonstrate the pattern without introducing LLM dependencies. Production graphs would integrate with OpenAI/Anthropic/etc.

### Future Enhancements

- Add Redis-based task queue for API → Worker communication
- Add LangSmith integration for observability
- Add horizontal scaling with worker pool
- Add dead letter queue for failed tasks
- Add webhook callbacks for task completion notification

### References

- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/)
- [langgraph-checkpoint-postgres PyPI](https://pypi.org/project/langgraph-checkpoint-postgres/)
- [psycopg3 AsyncConnectionPool](https://www.psycopg.org/psycopg3/docs/api/pool.html)
- [LangGraph StateGraph Guide](https://realpython.com/langgraph-python/)
