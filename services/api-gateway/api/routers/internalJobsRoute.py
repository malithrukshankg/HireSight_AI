import uuid

from database import DBSession
from fastapi import APIRouter

from api.controllers.jobController import JobController
from api.schemas.internalJobAiContextSchema import JobAiContextResponse

internalJobsRouter = APIRouter(prefix="/internal/jobs", tags=["internal"])


@internalJobsRouter.get("/{job_id}/ai-context", response_model=JobAiContextResponse)
async def get_job_ai_context(job_id: uuid.UUID, db: DBSession):
    """Return raw JD text, parsed JD output, and parse metadata for agent-service consumption."""
    return await JobController(db).get_ai_context(job_id)
