import uuid

from database import DBSession
from fastapi import APIRouter, Depends, HTTPException, Query

from api.controllers.organizationController import OrganizationController
from api.schemas.organizationSchema import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
)
from auth.auth0 import require_admin_or_recruiter

organizationRouter = APIRouter(prefix="/organizations", tags=["organizations"])


@organizationRouter.post("", response_model=OrganizationRead, status_code=201)
async def create_organization(
    payload: OrganizationCreate,
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """Create a new organization. Admin or recruiter only."""
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in token")
    return await OrganizationController(db).create(payload, auth0_sub)


@organizationRouter.get("", response_model=list[OrganizationRead])
async def list_organizations(
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all organizations. Admin or recruiter only."""
    return await OrganizationController(db).list_all(limit=limit, offset=offset)


@organizationRouter.get("/me", response_model=list[OrganizationRead])
async def list_my_organizations(
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """List organizations linked to the current user. Admin or recruiter only."""
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in token")
    return await OrganizationController(db).list_for_current_user(auth0_sub)


@organizationRouter.get("/{id}", response_model=OrganizationRead)
async def get_organization(
    id: uuid.UUID,
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """Get an organization by ID. Admin or recruiter only."""
    return await OrganizationController(db).get_by_id(id)


@organizationRouter.patch("/{id}", response_model=OrganizationRead)
async def update_organization(
    id: uuid.UUID,
    payload: OrganizationUpdate,
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """Update an organization. Admin or recruiter only."""
    return await OrganizationController(db).update(id, payload)


@organizationRouter.delete("/{id}", status_code=204)
async def delete_organization(
    id: uuid.UUID,
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """Delete an organization. Admin or recruiter only."""
    await OrganizationController(db).delete(id)
