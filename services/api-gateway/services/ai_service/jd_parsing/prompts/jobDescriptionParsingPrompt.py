def build_jd_parsing_system_instruction() -> str:
    return (
        "You extract structured hiring information from job descriptions. "
        "Return only valid JSON with keys matching the expected schema. "
        "Do not add markdown fences or additional commentary. "
        "If information is missing, use empty string or empty arrays."
    )


def build_jd_parsing_user_prompt(*, description: str, title: str | None = None) -> str:
    title_line = f"Job title: {title.strip()}\n" if title and title.strip() else ""
    return (
        f"{title_line}"
        "Job description:\n"
        f"{description.strip()}\n\n"
        "Extract structured fields for summary, responsibilities, required_skills, "
        "preferred_skills, qualifications, experience_requirements, seniority_level, "
        "employment_type, tools_technologies, and domain_keywords."
    )
