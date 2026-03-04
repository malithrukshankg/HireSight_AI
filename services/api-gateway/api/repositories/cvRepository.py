import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CV


class CVRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_candidate_id(self, candidate_id: uuid.UUID) -> CV | None:
        result = await self.db.execute(select(CV).where(CV.candidate_id == candidate_id))
        return result.scalar_one_or_none()

    async def upsert_uploaded_cv(
        self,
        *,
        candidate_id: uuid.UUID,
        uploaded_by_user_id: uuid.UUID,
        s3_bucket: str,
        original_filename: str,
        content_type: str,
        size_bytes: int | None,
        file_type: str,
        s3_key: str,
    ) -> CV:
        existing = await self.find_by_candidate_id(candidate_id)
        if existing is None:
            cv = CV(
                candidate_id=candidate_id,
                uploaded_by_user_id=uploaded_by_user_id,
                file_name=original_filename,
                file_type=file_type,
                s3_bucket=s3_bucket,
                s3_key=s3_key,
                original_filename=original_filename,
                content_type=content_type,
                size_bytes=size_bytes,
            )
            self.db.add(cv)
            await self.db.commit()
            await self.db.refresh(cv)
            return cv

        existing.uploaded_by_user_id = uploaded_by_user_id
        existing.file_name = original_filename
        existing.file_type = file_type
        existing.s3_bucket = s3_bucket
        existing.s3_key = s3_key
        existing.original_filename = original_filename
        existing.content_type = content_type
        existing.size_bytes = size_bytes
        await self.db.commit()
        await self.db.refresh(existing)
        return existing
