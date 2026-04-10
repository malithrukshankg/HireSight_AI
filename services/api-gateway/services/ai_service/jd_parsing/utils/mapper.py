from services.ai_service.jd_parsing.schemas.parsedJobDescription import ParsedJobDescription


def _clean_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    cleaned: list[str] = []
    for value in values:
        item = (value or "").strip()
        if not item:
            continue
        normalized = item.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(item)
    return cleaned


def normalize_parsed_job_description(parsed: ParsedJobDescription) -> ParsedJobDescription:
    payload = parsed.model_dump()

    payload["summary"] = (payload.get("summary") or "").strip()
    payload["experience_requirements"] = (payload.get("experience_requirements") or "").strip()
    payload["seniority_level"] = (payload.get("seniority_level") or "").strip()
    payload["employment_type"] = (payload.get("employment_type") or "").strip()

    for key in (
        "responsibilities",
        "required_skills",
        "preferred_skills",
        "qualifications",
        "tools_technologies",
        "domain_keywords",
    ):
        payload[key] = _clean_list(payload.get(key) or [])

    return ParsedJobDescription.model_validate(payload)
