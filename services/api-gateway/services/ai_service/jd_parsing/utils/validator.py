from services.ai_service.shared.aiExceptions import StructuredOutputValidationError


MAX_DESCRIPTION_CHARS = 50000


def validate_jd_input(description: str, title: str | None = None) -> tuple[str, str | None]:
    clean_description = (description or "").strip()
    clean_title = title.strip() if title else None

    if not clean_description:
        raise StructuredOutputValidationError("Job description cannot be empty")

    if len(clean_description) > MAX_DESCRIPTION_CHARS:
        raise StructuredOutputValidationError(
            f"Job description is too long (max {MAX_DESCRIPTION_CHARS} chars)"
        )

    return clean_description, clean_title
