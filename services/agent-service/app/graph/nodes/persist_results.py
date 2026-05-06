from __future__ import annotations

import logging

import httpx

from app.clients.gateway_client import GatewayClient
from app.graph.node_logger import get_node_logger
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def persist_results(state: AgentState) -> dict:
    log = get_node_logger(logger, state, "persist_results")
    candidate_id = state.get("candidate_id")
    matching_result = state.get("matching_result")
    match_score = state.get("match_score")

    log.info("persisting match result candidate_id=%s", candidate_id)

    if candidate_id is None:
        log.warning("no candidate_id in state, skipping persist")
        return {"steps_taken": state["steps_taken"] + ["persist_results"]}

    if matching_result is None or match_score is None:
        log.warning("no matching_result in state, skipping persist")
        return {"steps_taken": state["steps_taken"] + ["persist_results"]}

    try:
        await GatewayClient().save_match_result(
            candidate_id=candidate_id,
            match_score=match_score,
            scores_json=matching_result,
        )
        log.info("saved match_score=%.4f candidate_id=%s", match_score, candidate_id)
    except httpx.HTTPStatusError as exc:
        log.error("api-gateway returned HTTP %s", exc.response.status_code)
        return {
            "fatal_error": f"Failed to persist match result: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["persist_results"],
        }
    except httpx.RequestError as exc:
        log.error("request error: %s", exc)
        return {
            "fatal_error": f"Failed to persist match result: {exc}",
            "steps_taken": state["steps_taken"] + ["persist_results"],
        }

    return {"steps_taken": state["steps_taken"] + ["persist_results"]}
