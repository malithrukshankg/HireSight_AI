from __future__ import annotations

import logging

import httpx

from app.clients.gateway_client import GatewayClient
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def persist_results(state: AgentState) -> dict:
    job_id = state["job_id"]
    cv_id = state["cv_id"]
    request_id = state["request_id"]
    candidate_id = state.get("candidate_id")
    matching_result = state.get("matching_result")
    match_score = state.get("match_score")

    logger.info(
        "persist_results: job_id=%s cv_id=%s candidate_id=%s request_id=%s",
        job_id,
        cv_id,
        candidate_id,
        request_id,
    )

    if candidate_id is None:
        logger.warning(
            "persist_results: no candidate_id in state, skipping persist job_id=%s cv_id=%s",
            job_id,
            cv_id,
        )
        return {"steps_taken": state["steps_taken"] + ["persist_results"]}

    if matching_result is None or match_score is None:
        logger.warning(
            "persist_results: no matching_result in state, skipping persist candidate_id=%s",
            candidate_id,
        )
        return {"steps_taken": state["steps_taken"] + ["persist_results"]}

    try:
        await GatewayClient().save_match_result(
            candidate_id=candidate_id,
            match_score=match_score,
            scores_json=matching_result,
        )
        logger.info(
            "persist_results: saved match_score=%.4f candidate_id=%s request_id=%s",
            match_score,
            candidate_id,
            request_id,
        )
    except httpx.HTTPStatusError as exc:
        logger.error(
            "persist_results: api-gateway returned %s for candidate_id=%s request_id=%s",
            exc.response.status_code,
            candidate_id,
            request_id,
        )
        return {
            "fatal_error": f"Failed to persist match result: HTTP {exc.response.status_code}",
            "steps_taken": state["steps_taken"] + ["persist_results"],
        }
    except httpx.RequestError as exc:
        logger.error(
            "persist_results: request error candidate_id=%s request_id=%s error=%s",
            candidate_id,
            request_id,
            exc,
        )
        return {
            "fatal_error": f"Failed to persist match result: {exc}",
            "steps_taken": state["steps_taken"] + ["persist_results"],
        }

    return {"steps_taken": state["steps_taken"] + ["persist_results"]}
