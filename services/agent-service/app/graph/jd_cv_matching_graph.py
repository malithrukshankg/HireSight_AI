from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.graph.nodes.fetch_cv_context import fetch_cv_context
from app.graph.nodes.fetch_jd_context import fetch_jd_context
from app.graph.nodes.handle_error import handle_error
from app.graph.nodes.load_request_context import load_request_context
from app.graph.nodes.normalize_inputs import normalize_inputs
from app.graph.nodes.parse_cv import parse_cv
from app.graph.nodes.parse_jd import parse_jd
from app.graph.nodes.persist_results import persist_results
from app.graph.nodes.run_matching_analysis import run_matching_analysis
from app.graph.nodes.validate_cv_parse import validate_cv_parse
from app.graph.nodes.validate_jd_parse import validate_jd_parse
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def _jd_routing(state: AgentState) -> str:
    """Route after validate_jd_parse.

    fatal_error (set by fetch_jd_context) takes priority.
    Otherwise: skip re-parse if the cached parse is still fresh.
    """
    if state.get("fatal_error"):
        return "handle_error"
    return "normalize_inputs" if state["jd_parse_valid"] else "parse_jd"


def _cv_routing(state: AgentState) -> str:
    """Route after validate_cv_parse.

    fatal_error (set by fetch_cv_context) takes priority.
    Otherwise: skip re-parse if the cached parse is still fresh.
    """
    if state.get("fatal_error"):
        return "handle_error"
    return "normalize_inputs" if state["cv_parse_valid"] else "parse_cv"


def _after_parse_routing(state: AgentState) -> str:
    """Route after parse_jd or parse_cv: abort on error, otherwise continue."""
    return "handle_error" if state.get("fatal_error") else "normalize_inputs"


def build_graph() -> StateGraph:
    """Build and return the uncompiled JD/CV matching StateGraph.

    Callers can compile with their own checkpointer:
        build_graph().compile(checkpointer=my_checkpointer)

    The module-level `compiled_graph` uses MemorySaver for development.
    Replace with AsyncPostgresSaver in Phase 5.
    """
    builder = StateGraph(AgentState)

    # --- Nodes ---
    builder.add_node("load_request_context", load_request_context)
    builder.add_node("fetch_jd_context", fetch_jd_context)
    builder.add_node("fetch_cv_context", fetch_cv_context)
    builder.add_node("validate_jd_parse", validate_jd_parse)
    builder.add_node("validate_cv_parse", validate_cv_parse)
    builder.add_node("parse_jd", parse_jd)
    builder.add_node("parse_cv", parse_cv)
    builder.add_node("normalize_inputs", normalize_inputs)
    builder.add_node("run_matching_analysis", run_matching_analysis)
    builder.add_node("persist_results", persist_results)
    builder.add_node("handle_error", handle_error)

    # --- Entry ---
    builder.add_edge(START, "load_request_context")

    # --- Fan-out: JD and CV branches run in parallel ---
    builder.add_edge("load_request_context", "fetch_jd_context")
    builder.add_edge("load_request_context", "fetch_cv_context")

    # --- Validate each parsed result ---
    builder.add_edge("fetch_jd_context", "validate_jd_parse")
    builder.add_edge("fetch_cv_context", "validate_cv_parse")

    # --- Conditional: abort on fatal_error, reuse fresh parse, or trigger re-parse ---
    builder.add_conditional_edges(
        "validate_jd_parse",
        _jd_routing,
        {
            "parse_jd": "parse_jd",
            "normalize_inputs": "normalize_inputs",
            "handle_error": "handle_error",
        },
    )
    builder.add_conditional_edges(
        "validate_cv_parse",
        _cv_routing,
        {
            "parse_cv": "parse_cv",
            "normalize_inputs": "normalize_inputs",
            "handle_error": "handle_error",
        },
    )

    # --- Re-parse paths rejoin at normalize_inputs (or abort on error) ---
    builder.add_conditional_edges(
        "parse_jd",
        _after_parse_routing,
        {"normalize_inputs": "normalize_inputs", "handle_error": "handle_error"},
    )
    builder.add_conditional_edges(
        "parse_cv",
        _after_parse_routing,
        {"normalize_inputs": "normalize_inputs", "handle_error": "handle_error"},
    )

    # --- Sequential tail ---
    builder.add_edge("normalize_inputs", "run_matching_analysis")
    builder.add_edge("run_matching_analysis", "persist_results")
    builder.add_edge("persist_results", END)

    # --- Error terminal ---
    builder.add_edge("handle_error", END)

    return builder


# Set at startup by main.py via set_compiled_graph().
# None until the app lifespan initialises the AsyncPostgresSaver checkpointer.
compiled_graph: Any = None


def set_compiled_graph(graph: Any) -> None:
    global compiled_graph
    compiled_graph = graph
