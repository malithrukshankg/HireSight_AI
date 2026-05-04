from __future__ import annotations

import logging

from app.graph.matching_schema import NormalizedCV, NormalizedJD
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def _lower_list(items: list | None) -> list[str]:
    """Lowercase and strip each non-empty string in a list."""
    if not items:
        return []
    return [s for s in (str(item).lower().strip() for item in items) if s]


def _dedupe_ordered(lists: list[list[str]]) -> list[str]:
    """Concatenate lists, preserving order and removing duplicates."""
    seen: set[str] = set()
    result: list[str] = []
    for lst in lists:
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return result


def _normalize_jd(parsed: dict) -> dict:
    required = _lower_list(parsed.get("required_skills"))
    preferred = _lower_list(parsed.get("preferred_skills"))
    tools = _lower_list(parsed.get("tools_technologies"))
    keywords = _lower_list(parsed.get("domain_keywords"))
    qualifications = _lower_list(parsed.get("qualifications"))

    return NormalizedJD(
        required_skills=required,
        preferred_skills=preferred,
        tools_technologies=tools,
        domain_keywords=keywords,
        all_skills=_dedupe_ordered([required, preferred, tools]),
        qualifications=qualifications,
        seniority_level=(parsed.get("seniority_level") or "").lower().strip(),
        employment_type=(parsed.get("employment_type") or "").strip(),
        experience_requirements=(parsed.get("experience_requirements") or "").strip(),
        summary=(parsed.get("summary") or "").strip(),
    ).model_dump()


def _normalize_cv(parsed: dict) -> dict:
    skills = _lower_list(parsed.get("skills"))

    experience_titles: list[str] = []
    experience_descriptions: list[str] = []
    for exp in parsed.get("experience") or []:
        if not isinstance(exp, dict):
            continue
        title = (exp.get("title") or "").lower().strip()
        if title:
            experience_titles.append(title)
        desc = (exp.get("description") or "").strip()
        if desc:
            experience_descriptions.append(desc)

    education_degrees: list[str] = []
    for edu in parsed.get("education") or []:
        if not isinstance(edu, dict):
            continue
        degree = (edu.get("degree") or "").lower().strip()
        if degree:
            education_degrees.append(degree)

    return NormalizedCV(
        skills=skills,
        experience_titles=experience_titles,
        experience_descriptions=experience_descriptions,
        education_degrees=education_degrees,
        projects=_lower_list(parsed.get("projects")),
    ).model_dump()


async def normalize_inputs(state: AgentState) -> dict:
    job_id = state["job_id"]
    cv_id = state["cv_id"]
    request_id = state["request_id"]

    parsed_jd = state.get("parsed_jd")
    parsed_cv = state.get("parsed_cv")

    if parsed_jd is None or parsed_cv is None:
        missing = "parsed_jd" if parsed_jd is None else "parsed_cv"
        logger.error(
            "normalize_inputs: %s is None job_id=%s cv_id=%s request_id=%s",
            missing,
            job_id,
            cv_id,
            request_id,
        )
        return {
            "fatal_error": f"normalize_inputs: {missing} is missing",
            "steps_taken": state["steps_taken"] + ["normalize_inputs"],
        }

    normalized_jd = _normalize_jd(parsed_jd)
    normalized_cv = _normalize_cv(parsed_cv)

    logger.info(
        "normalize_inputs: jd_skills=%d cv_skills=%d job_id=%s cv_id=%s request_id=%s",
        len(normalized_jd.get("all_skills", [])),
        len(normalized_cv.get("skills", [])),
        job_id,
        cv_id,
        request_id,
    )

    return {
        "normalized_jd": normalized_jd,
        "normalized_cv": normalized_cv,
        "steps_taken": state["steps_taken"] + ["normalize_inputs"],
    }
