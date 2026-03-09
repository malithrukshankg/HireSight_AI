from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.repositories.cv_repository import CVRepository
from app.api.services.cv_service import CVS3UploadError, CVValidationError, CvService


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
