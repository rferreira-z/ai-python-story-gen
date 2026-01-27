"""Base graph types and utilities for LangGraph workflows."""

import logging
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

# Configure logging for graphs
logger = logging.getLogger("worker.graphs")


class BaseState(TypedDict, total=False):
    """Base state for LangGraph workflows.

    Uses add_messages reducer for the messages field to properly
    handle message accumulation across graph nodes.
    """

    messages: Annotated[list[dict], add_messages]


class MessageState(TypedDict):
    """State containing a list of messages with add_messages reducer.

    This is the recommended state type for conversational workflows.
    The add_messages reducer properly handles message deduplication
    and ordering.
    """

    messages: Annotated[list[dict], add_messages]


# Re-export commonly used graph components
__all__ = [
    "BaseState",
    "MessageState",
    "add_messages",
    "logger",
]
