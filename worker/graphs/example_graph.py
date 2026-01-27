"""Example StateGraph demonstrating LangGraph patterns.

This module provides a simple multi-step graph that demonstrates:
- Async node functions
- State management with TypedDict
- Conditional edges for routing
- Checkpointer integration for persistence
"""

import logging
from typing import Annotated, Literal, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

logger = logging.getLogger(__name__)


class ExampleState(TypedDict):
    """State for the example graph.

    Attributes:
        messages: List of messages with add_messages reducer
        step_count: Number of processing steps completed
        should_continue: Whether to continue processing
    """

    messages: Annotated[list[dict], add_messages]
    step_count: int
    should_continue: bool


async def input_node(state: ExampleState) -> dict:
    """Process initial input.

    This node receives the initial state and prepares it for processing.
    """
    logger.info("Input node: Processing input")
    return {
        "messages": [{"role": "system", "content": "Input received and validated"}],
        "step_count": state.get("step_count", 0) + 1,
        "should_continue": True,
    }


async def process_node(state: ExampleState) -> dict:
    """Main processing node.

    Performs the core work of the graph. In a real implementation,
    this would call an LLM or perform complex computations.
    """
    logger.info("Process node: Step %d", state.get("step_count", 0))

    # Simulate processing - in production, call LLM here
    step = state.get("step_count", 0) + 1

    return {
        "messages": [{"role": "assistant", "content": f"Processing complete (step {step})"}],
        "step_count": step,
        "should_continue": step < 3,  # Continue for up to 3 steps
    }


async def output_node(state: ExampleState) -> dict:
    """Finalize output.

    This node prepares the final response after processing is complete.
    """
    logger.info("Output node: Finalizing with %d steps", state.get("step_count", 0))
    return {
        "messages": [
            {
                "role": "assistant",
                "content": f"Workflow complete after {state.get('step_count', 0)} steps",
            }
        ],
    }


def should_continue(state: ExampleState) -> Literal["process", "output"]:
    """Determine whether to continue processing or output results.

    This is a conditional edge function that routes based on state.
    """
    if state.get("should_continue", False):
        return "process"
    return "output"


def create_example_graph(
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """Create and compile the example graph.

    Args:
        checkpointer: Optional checkpointer for state persistence.
                     Pass AsyncPostgresSaver for durable persistence.

    Returns:
        Compiled StateGraph ready for invocation.

    Example:
        ```python
        async with get_checkpointer() as checkpointer:
            graph = create_example_graph(checkpointer)
            result = await graph.ainvoke(
                {"messages": [{"role": "user", "content": "Hello"}]},
                config={"configurable": {"thread_id": "thread-1"}}
            )
        ```
    """
    # Build the graph
    builder = StateGraph(ExampleState)

    # Add nodes
    builder.add_node("input", input_node)
    builder.add_node("process", process_node)
    builder.add_node("output", output_node)

    # Add edges
    builder.add_edge(START, "input")
    builder.add_conditional_edges("input", should_continue)
    builder.add_conditional_edges("process", should_continue)
    builder.add_edge("output", END)

    # Compile with optional checkpointer
    return builder.compile(checkpointer=checkpointer)


# Export for convenient access
__all__ = ["ExampleState", "create_example_graph"]
