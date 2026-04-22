import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.repositories.cv_repository import CVRepository
from app.api.schemas.cv_schema import (
    CVAiContextResponse,
    CVByCandidateResponse,
    CVDetailResponse,
    CVExtractionResponse,
    CVStructuredExtractionResponse,
)
from app.api.services.cv_service import (
    CVExtractionError,
    CVNotFoundError,
    CVS3UploadError,
    CVValidationError,
    CvService,
)


class CvController:
    def __init__(self, db: AsyncSession):
        self.repo = CVRepository(db)
        self.service = CvService(self.repo)

    async def upload_cv(self, file: UploadFile, principal: dict) -> dict:
        try:
            return await self.service.upload_cv(file, principal)
        except CVValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except CVS3UploadError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def upload_cv_for_candidate(
        self,
        *,
        file: UploadFile,
        candidate_id: uuid.UUID,
        uploaded_by_user_id: uuid.UUID,
    ) -> dict:
        try:
            return await self.service.upload_cv_for_candidate(
                file=file,
                candidate_id=candidate_id,
                uploaded_by_user_id=uploaded_by_user_id,
            )
        except CVValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except CVS3UploadError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_candidate_id(self, candidate_id: uuid.UUID) -> CVByCandidateResponse:
        cv = await self.repo.find_by_candidate_id(candidate_id)
        if cv is None:
            raise HTTPException(status_code=404, detail="CV not found for candidate")
        return CVByCandidateResponse(
            id=cv.id,
            candidate_id=cv.candidate_id,
            s3_key=cv.s3_key or "",
            bucket=cv.s3_bucket or "",
            original_filename=cv.original_filename or "",
            content_type=cv.content_type or "",
            file_size_bytes=cv.size_bytes,
            created_at=cv.created_at,
        )

    async def trigger_extraction(self, cv_id: uuid.UUID) -> CVExtractionResponse:
        try:
            result = await self.service.trigger_extraction_for_existing_cv(cv_id)
            return CVExtractionResponse.model_validate(result)
        except CVNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except CVValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except (CVS3UploadError, CVExtractionError) as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def trigger_structured_extraction(
        self, cv_id: uuid.UUID
    ) -> CVStructuredExtractionResponse:
        try:
            result = await self.service.extract_structured_profile_for_existing_cv(cv_id)
            return CVStructuredExtractionResponse.model_validate(result)
        except CVNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except CVValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except CVExtractionError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_cv_ai_context(self, cv_id: uuid.UUID) -> CVAiContextResponse:
        try:
            result = await self.service.get_cv_ai_context(cv_id)
            return CVAiContextResponse.model_validate(result)
        except CVNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def get_cv_detail(self, cv_id: uuid.UUID) -> CVDetailResponse:
        try:
            result = await self.service.get_cv_detail(cv_id)
            return CVDetailResponse.model_validate(result)
        except CVNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except CVValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_cv_file(self, cv_id: uuid.UUID) -> tuple[bytes, str, str]:
        try:
            return await self.service.get_cv_file(cv_id)
        except CVNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except CVValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except CVS3UploadError as e:
            raise HTTPException(status_code=500, detail=str(e))
