from fastapi import APIRouter, Depends

from api.controllers.jdParsingController import JdParsingController
from api.schemas.jdParsingSchema import (
    JobDescriptionParseRequest,
    JobDescriptionParseResponse,
)
from auth.auth0 import require_admin_or_recruiter

internalAiRouter = APIRouter(prefix="/internal/ai", tags=["ai"])


@internalAiRouter.post(
    "/jobs/parse-description",
    response_model=JobDescriptionParseResponse,
)
async def parse_job_description(
    payload: JobDescriptionParseRequest,
    principal: dict = Depends(require_admin_or_recruiter),
):
    _ = principal
    return await JdParsingController().parse_description(payload)
