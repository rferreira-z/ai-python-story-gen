"""LangGraph worker main entry point.

Run with: python -m worker.main

This worker process runs independently from the FastAPI API,
using PostgresSaver for durable state persistence.
"""

import asyncio
import logging
import signal
import sys
from typing import NoReturn

from worker.core.checkpointer import get_checkpointer
from worker.core.config import settings
from worker.graphs import create_example_graph

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class GracefulShutdown:
    """Handle graceful shutdown on SIGTERM/SIGINT."""

    def __init__(self) -> None:
        self.shutdown_requested = False

    def request_shutdown(self, signum: int, frame: object) -> None:
        """Signal handler for graceful shutdown."""
        logger.info("Shutdown requested (signal %d)", signum)
        self.shutdown_requested = True


async def run_example_workflow(thread_id: str = "example-thread-1") -> dict:
    """Run an example workflow to demonstrate the graph.

    Args:
        thread_id: Unique identifier for the conversation thread.
                  Used by checkpointer to persist/restore state.

    Returns:
        Final state after graph execution.
    """
    logger.info("Starting example workflow with thread_id: %s", thread_id)

    async with get_checkpointer() as checkpointer:
        # Create graph with checkpointer for persistence
        graph = create_example_graph(checkpointer)

        # Initial input
        initial_state = {
            "messages": [{"role": "user", "content": "Hello, start the workflow!"}],
            "step_count": 0,
            "should_continue": True,
        }

        # Run the graph
        config = {"configurable": {"thread_id": thread_id}}
        result = await graph.ainvoke(initial_state, config=config)  # type: ignore[arg-type]

        logger.info("Workflow complete. Final step count: %d", result.get("step_count", 0))
        logger.info("Messages: %d", len(result.get("messages", [])))

        return result


async def main() -> None:
    """Main entry point for the worker process.

    Sets up signal handlers and runs the example workflow.
    In production, this would be replaced with a task queue consumer.
    """
    logger.info("Starting %s", settings.worker_name)
    logger.info("Database URL: %s", settings.psycopg_database_url.split("@")[-1])  # Hide creds
    logger.info("Debug mode: %s", settings.debug)

    # Setup graceful shutdown
    shutdown = GracefulShutdown()
    signal.signal(signal.SIGTERM, shutdown.request_shutdown)
    signal.signal(signal.SIGINT, shutdown.request_shutdown)

    try:
        # Run example workflow
        # In production, replace with queue consumer loop
        result = await run_example_workflow()
        logger.info("Example workflow result: %s messages", len(result.get("messages", [])))

        # Keep running until shutdown (for demonstration)
        # In production, this would be a queue consumer loop
        logger.info("Worker idle. Press Ctrl+C to stop.")
        while not shutdown.shutdown_requested:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception:
        logger.exception("Worker error")
        raise
    finally:
        logger.info("Worker shutting down")


def cli() -> NoReturn:
    """CLI entry point."""
    try:
        asyncio.run(main())
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    cli()
