from __future__ import annotations

import logging

from app.graph.matching_schema import MatchingInput, MatchingOutput, NormalizedCV, NormalizedJD
from app.graph.state import AgentState

logger = logging.getLogger(__name__)

# v1 scoring weights - must sum to 1.0
_W_REQUIRED = 0.60
_W_PREFERRED = 0.25
_W_OVERALL = 0.15


def _cv_skill_set(cv: NormalizedCV) -> set[str]:
    """All lowercased CV signals available for matching."""
    return set(cv.skills) | set(cv.experience_titles) | set(cv.projects)


def _coverage(jd_skills: list[str], cv_signals: set[str]) -> tuple[float, list[str], list[str]]:
    """Return (score, matched, unmatched) for a list of JD skills against CV signals.

    A JD skill is considered matched when the CV contains it as a substring or
    the CV signal contains the JD skill as a substring - e.g. "fastapi" matches
    "senior fastapi developer".  Exact match is also caught by this rule.
    """
    if not jd_skills:
        return 1.0, [], []

    matched: list[str] = []
    unmatched: list[str] = []

    for skill in jd_skills:
        hit = any(skill in signal or signal in skill for signal in cv_signals)
        (matched if hit else unmatched).append(skill)

    score = len(matched) / len(jd_skills)
    return score, matched, unmatched


def _score(jd: NormalizedJD, cv: NormalizedCV) -> MatchingOutput:
    cv_signals = _cv_skill_set(cv)

    req_score, matched_req, unmatched_req = _coverage(jd.required_skills, cv_signals)
    pref_score, matched_pref, _ = _coverage(jd.preferred_skills, cv_signals)
    overall_score, _, _ = _coverage(jd.all_skills, cv_signals)

    weighted = (
        req_score * _W_REQUIRED
        + pref_score * _W_PREFERRED
        + overall_score * _W_OVERALL
    )

    return MatchingOutput(
        required_skills_coverage=round(req_score, 4),
        preferred_skills_coverage=round(pref_score, 4),
        overall_skills_coverage=round(overall_score, 4),
        overall=round(weighted, 4),
        matched_required=matched_req,
        matched_preferred=matched_pref,
        unmatched_required=unmatched_req,
    )


async def run_matching_analysis(state: AgentState) -> dict:
    job_id = state["job_id"]
    cv_id = state["cv_id"]
    request_id = state["request_id"]

    normalized_jd = state.get("normalized_jd")
    normalized_cv = state.get("normalized_cv")

    if normalized_jd is None or normalized_cv is None:
        missing = "normalized_jd" if normalized_jd is None else "normalized_cv"
        logger.error(
            "run_matching_analysis: %s is None job_id=%s cv_id=%s request_id=%s",
            missing, job_id, cv_id, request_id,
        )
        return {
            "fatal_error": f"run_matching_analysis: {missing} is missing",
            "steps_taken": state["steps_taken"] + ["run_matching_analysis"],
        }

    matching_input = MatchingInput(
        job_id=job_id,
        cv_id=cv_id,
        request_id=request_id,
        jd=NormalizedJD(**normalized_jd),
        cv=NormalizedCV(**normalized_cv),
    )

    result = _score(matching_input.jd, matching_input.cv)

    logger.info(
        "run_matching_analysis: overall=%.4f required=%.4f preferred=%.4f "
        "job_id=%s cv_id=%s request_id=%s",
        result.overall,
        result.required_skills_coverage,
        result.preferred_skills_coverage,
        job_id, cv_id, request_id,
    )

    return {
        "matching_result": result.model_dump(),
        "match_score": result.overall,
        "steps_taken": state["steps_taken"] + ["run_matching_analysis"],
    }
