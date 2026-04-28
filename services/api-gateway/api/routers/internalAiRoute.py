from fastapi import APIRouter

from api.controllers.jdParsingController import JdParsingController
from api.schemas.jdParsingSchema import (
    JobDescriptionParseRequest,
    JobDescriptionParseResponse,
)

internalAiRouter = APIRouter(prefix="/internal/ai", tags=["ai"])


@internalAiRouter.post(
    "/jobs/parse-description",
    response_model=JobDescriptionParseResponse,
)
async def parse_job_description(payload: JobDescriptionParseRequest):
    """Parse a job description via Gemini (internal use only, no auth required)."""
    return await JdParsingController().parse_description(payload)
