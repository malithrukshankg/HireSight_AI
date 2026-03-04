import uuid

from database import DBSession
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from api.controllers.jobController import JobController
from api.schemas.jobSchema import JobApplyResponse, JobCreate, JobRead, JobUpdate
from auth.auth0 import (
    get_principal_role,
    require_admin_or_recruiter,
    require_authenticated_user,
)
from models.jobs import JobStatusEnum

jobRouter = APIRouter(prefix="/jobs", tags=["jobs"])


@jobRouter.post("", response_model=JobRead, status_code=201)
async def create_job(
    payload: JobCreate,
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """Create a new job. User must be a member of the organization. Admin or recruiter only."""
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in token")
    return await JobController(db).create(payload, auth0_sub)


@jobRouter.get("", response_model=list[JobRead])
async def list_jobs(
    db: DBSession,
    principal: dict = Depends(require_authenticated_user),
    organization_id: uuid.UUID | None = Query(None),
    status: JobStatusEnum | None = Query(None),
    query: str | None = Query(None),
    location: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    sort: str = Query("recent"),
):
    """List jobs with optional filters. Candidate can only view open jobs."""
    role = get_principal_role(principal)
    effective_status = JobStatusEnum.open if role == "candidate" else status
    offset = (page - 1) * page_size
    return await JobController(db).list_all(
        limit=page_size,
        offset=offset,
        organization_id=organization_id,
        status=effective_status,
        query=query,
        location=location,
        sort=sort,
        role=role,
    )


@jobRouter.get("/me", response_model=list[JobRead])
async def list_my_jobs(
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """List jobs created by the current user. Admin or recruiter only."""
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in token")
    return await JobController(db).list_for_current_user(auth0_sub)


@jobRouter.get("/{id}", response_model=JobRead)
async def get_job(
    id: uuid.UUID,
    db: DBSession,
    principal: dict = Depends(require_authenticated_user),
):
    """Get a job by ID. Candidate can only view open jobs."""
    job = await JobController(db).get_by_id(id)
    role = get_principal_role(principal)
    if role == "candidate" and job.status != JobStatusEnum.open:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@jobRouter.post("/{id}/apply", response_model=JobApplyResponse, status_code=201)
async def apply_job(
    id: uuid.UUID,
    db: DBSession,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str | None = Form(None),
    cv_file: UploadFile | None = File(None),
    principal: dict = Depends(require_authenticated_user),
):
    """Apply to an open job by upserting candidate and CV records."""
    role = get_principal_role(principal)
    if role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply to jobs")
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in token")
    return await JobController(db).apply(
        job_id=id,
        auth0_sub=auth0_sub,
        email=email,
        full_name=full_name,
        phone=phone,
        cv_file=cv_file,
    )


@jobRouter.patch("/{id}", response_model=JobRead)
async def update_job(
    id: uuid.UUID,
    payload: JobUpdate,
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """Update a job. User must be a member of the job's organization. Admin or recruiter only."""
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in token")
    return await JobController(db).update(id, payload, auth0_sub)


@jobRouter.delete("/{id}", status_code=204)
async def delete_job(
    id: uuid.UUID,
    db: DBSession,
    principal: dict = Depends(require_admin_or_recruiter),
):
    """Delete a job. User must be a member of the job's organization. Admin or recruiter only."""
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in token")
    await JobController(db).delete(id, auth0_sub)
