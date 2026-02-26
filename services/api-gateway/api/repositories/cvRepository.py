import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CV


class CVRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_uploaded_cv(
        self,
        *,
        candidate_id: uuid.UUID,
        uploaded_by_user_id: uuid.UUID,
        original_filename: str,
        file_type: str,
        s3_key: str,
    ) -> CV:
        result = await self.db.execute(select(CV).where(CV.candidate_id == candidate_id))
        existing = result.scalar_one_or_none()

        if existing is None:
            cv = CV(
                candidate_id=candidate_id,
                uploaded_by_user_id=uploaded_by_user_id,
                file_name=original_filename,
                file_type=file_type,
                s3_key=s3_key,
            )
            self.db.add(cv)
            await self.db.commit()
            await self.db.refresh(cv)
            return cv

        existing.uploaded_by_user_id = uploaded_by_user_id
        existing.file_name = original_filename
        existing.file_type = file_type
        existing.s3_key = s3_key
        await self.db.commit()
        await self.db.refresh(existing)
        return existing
