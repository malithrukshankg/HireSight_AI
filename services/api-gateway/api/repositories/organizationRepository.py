import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Organization
from models.organizations import PlanEnum
from models.recruiter_organization import RecruiterOrganization


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, plan: PlanEnum = PlanEnum.free) -> Organization:
        """Create a new organization."""
        org = Organization(name=name, plan=plan)
        self.db.add(org)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def find_by_id(self, id: uuid.UUID) -> Organization | None:
        """Find an organization by ID."""
        result = await self.db.execute(select(Organization).where(Organization.id == id))
        return result.scalar_one_or_none()

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[Organization]:
        """List all organizations with optional pagination."""
        result = await self.db.execute(
            select(Organization).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def update(self, org: Organization, **kwargs) -> Organization:
        """Update organization fields. Only non-None kwargs are applied."""
        for key, value in kwargs.items():
            if value is not None and hasattr(org, key):
                setattr(org, key, value)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def delete(self, org: Organization) -> None:
        """Delete an organization."""
        await self.db.delete(org)
        await self.db.commit()

    async def link_user(self, user_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        """Create RecruiterOrganization link between user and organization."""
        ro = RecruiterOrganization(user_id=user_id, organization_id=organization_id)
        self.db.add(ro)
        await self.db.commit()
