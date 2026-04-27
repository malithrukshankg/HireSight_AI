from __future__ import annotations

import logging

from langgraph.checkpoint.memory import MemorySaver
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
    """Route after validate_jd_parse: skip to normalize_inputs if parse is fresh."""
    return "normalize_inputs" if state["jd_parse_valid"] else "parse_jd"


def _cv_routing(state: AgentState) -> str:
    """Route after validate_cv_parse: skip to normalize_inputs if parse is fresh."""
    return "normalize_inputs" if state["cv_parse_valid"] else "parse_cv"


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

    # --- Conditional: reuse fresh parse or trigger re-parse ---
    builder.add_conditional_edges(
        "validate_jd_parse",
        _jd_routing,
        {"parse_jd": "parse_jd", "normalize_inputs": "normalize_inputs"},
    )
    builder.add_conditional_edges(
        "validate_cv_parse",
        _cv_routing,
        {"parse_cv": "parse_cv", "normalize_inputs": "normalize_inputs"},
    )

    # --- Re-parse paths rejoin at normalize_inputs ---
    # LangGraph fan-in: normalize_inputs waits for both branches before firing.
    builder.add_edge("parse_jd", "normalize_inputs")
    builder.add_edge("parse_cv", "normalize_inputs")

    # --- Sequential tail ---
    builder.add_edge("normalize_inputs", "run_matching_analysis")
    builder.add_edge("run_matching_analysis", "persist_results")
    builder.add_edge("persist_results", END)

    # --- Error terminal (reachable in Phase 3 when nodes set fatal_error) ---
    builder.add_edge("handle_error", END)

    return builder


# Module-level compiled graph used by AgentOrchestrator.
# MemorySaver is in-process and lost on restart -- suitable for Phase 2 development only.
compiled_graph = build_graph().compile(checkpointer=MemorySaver())
