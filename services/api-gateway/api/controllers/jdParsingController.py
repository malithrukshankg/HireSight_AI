from fastapi import HTTPException

from api.schemas.jdParsingSchema import (
    JobDescriptionParseRequest,
    JobDescriptionParseResponse,
)
from services.ai_service.jd_parsing.orchestrator.jobDescriptionParsingOrchestrator import (
    JobDescriptionParsingOrchestrator,
)
from services.ai_service.shared.aiExceptions import (
    GeminiConfigurationError,
    GeminiInvocationError,
    StructuredOutputValidationError,
)


class JdParsingController:
    def __init__(self):
        self.orchestrator = JobDescriptionParsingOrchestrator()

    async def parse_description(
        self,
        payload: JobDescriptionParseRequest,
    ) -> JobDescriptionParseResponse:
        try:
            parsed = await self.orchestrator.parse_job_description(
                description=payload.description,
                title=payload.title,
            )
            return JobDescriptionParseResponse.model_validate(parsed.model_dump())
        except StructuredOutputValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except GeminiConfigurationError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except GeminiInvocationError as e:
            raise HTTPException(status_code=502, detail=str(e))
