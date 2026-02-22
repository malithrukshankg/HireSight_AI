import uuid

from api.repositories.organizationRepository import OrganizationRepository
from api.schemas.organizationSchema import OrganizationCreate, OrganizationUpdate
from models import Organization


class OrganizationService:
    def __init__(self, repo: OrganizationRepository):
        self.repo = repo

    async def create(self, payload: OrganizationCreate, user_id: uuid.UUID) -> Organization:
        """Create a new organization and link the creating user to it."""
        name = (payload.name or "").strip()
        if not name:
            raise ValueError("Organization name is required and cannot be empty")
        org = await self.repo.create(name=name, plan=payload.plan)
        await self.repo.link_user(user_id=user_id, organization_id=org.id)
        return org

    async def get_by_id(self, id: uuid.UUID) -> Organization:
        """Get an organization by ID. Raises ValueError if not found."""
        org = await self.repo.find_by_id(id)
        if org is None:
            raise ValueError("Organization not found")
        return org

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Organization]:
        """List all organizations with optional pagination."""
        if limit < 1 or limit > 500:
            raise ValueError("Limit must be between 1 and 500")
        if offset < 0:
            raise ValueError("Offset must be non-negative")
        return await self.repo.find_all(limit=limit, offset=offset)

    async def list_for_user(self, user_id: uuid.UUID) -> list[Organization]:
        """List organizations linked to this user via RecruiterOrganization."""
        return await self.repo.find_by_user_id(user_id)

    async def update(self, id: uuid.UUID, payload: OrganizationUpdate) -> Organization:
        """Update an organization. Raises ValueError if not found."""
        org = await self.repo.find_by_id(id)
        if org is None:
            raise ValueError("Organization not found")
        kwargs = {}
        if payload.name is not None:
            name = payload.name.strip()
            if not name:
                raise ValueError("Organization name cannot be empty")
            kwargs["name"] = name
        if payload.plan is not None:
            kwargs["plan"] = payload.plan
        if kwargs:
            return await self.repo.update(org, **kwargs)
        return org

    async def delete(self, id: uuid.UUID) -> None:
        """Delete an organization. Raises ValueError if not found."""
        org = await self.repo.find_by_id(id)
        if org is None:
            raise ValueError("Organization not found")
        await self.repo.delete(org)
