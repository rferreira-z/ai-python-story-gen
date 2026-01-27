"""AsyncPostgresSaver checkpointer setup and management."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from worker.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_checkpointer() -> AsyncGenerator[AsyncPostgresSaver, None]:
    """Create and manage AsyncPostgresSaver lifecycle.

    This context manager:
    1. Creates an AsyncConnectionPool with required settings
    2. Initializes AsyncPostgresSaver with the pool
    3. Calls setup() to create checkpoint tables if needed
    4. Yields the checkpointer for use
    5. Properly closes the pool on exit

    IMPORTANT: psycopg connections MUST have:
    - autocommit=True: Required for setup() to commit checkpoint tables
    - row_factory=dict_row: Required because PostgresSaver uses dict access
    """
    connection_kwargs = {
        "autocommit": True,
        "row_factory": dict_row,
    }

    logger.info(
        "Initializing checkpointer pool with size %d",
        settings.checkpointer_pool_size,
    )

    pool = AsyncConnectionPool(
        conninfo=settings.psycopg_database_url,
        min_size=1,
        max_size=settings.checkpointer_pool_size,
        open=False,
        kwargs=connection_kwargs,
    )

    try:
        await pool.open()
        logger.info("Connection pool opened")

        checkpointer = AsyncPostgresSaver(pool)  # type: ignore[arg-type]

        # Setup creates checkpoint tables if they don't exist
        logger.info("Running checkpointer setup (creates tables if needed)")
        await checkpointer.setup()
        logger.info("Checkpointer setup complete")

        yield checkpointer

    finally:
        await pool.close()
        logger.info("Connection pool closed")
