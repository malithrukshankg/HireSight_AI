import httpx
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

from api.clients.cv_client import CvClient
from api.repositories.candidateRepository import CandidateRepository
from api.repositories.organizationRepository import OrganizationRepository
from api.repositories.userRepository import UserRepository
from api.schemas.cvSchema import (
    CVExtractionResponse,
    CVProfileResponse,
    CVStructuredExtractionResponse,
    CVUploadResponse,
)
from database import DBSession
from auth.auth0 import get_current_principal

cvRouter = APIRouter(prefix="/cv", tags=["cv"])


@cvRouter.post("/upload", response_model=CVUploadResponse, status_code=201)
async def upload_cv(
    file: UploadFile = File(...),
    principal: dict = Depends(get_current_principal),
):
    _ = principal  # JWT validated by dependency
    client = CvClient()
    try:
        result = await client.upload_cv(file)
        return CVUploadResponse.model_validate(result)
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", str(e)) if e.response.text else str(e)
        except Exception:
            detail = e.response.text or str(e)
        raise HTTPException(status_code=e.response.status_code, detail=detail)


@cvRouter.post("/extract/{cv_id}", response_model=CVExtractionResponse)
async def trigger_extraction(
    cv_id: uuid.UUID,
    principal: dict = Depends(get_current_principal),
):
    _ = principal  # JWT validated by dependency
    client = CvClient()
    try:
        result = await client.trigger_extraction(cv_id)
        return CVExtractionResponse.model_validate(result)
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", str(e)) if e.response.text else str(e)
        except Exception:
            detail = e.response.text or str(e)
        raise HTTPException(status_code=e.response.status_code, detail=detail)


@cvRouter.post("/extract-structured/{cv_id}", response_model=CVStructuredExtractionResponse)
async def trigger_structured_extraction(
    cv_id: uuid.UUID,
    principal: dict = Depends(get_current_principal),
):
    _ = principal  # JWT validated by dependency
    client = CvClient()
    try:
        result = await client.trigger_structured_extraction(cv_id)
        return CVStructuredExtractionResponse.model_validate(result)
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", str(e)) if e.response.text else str(e)
        except Exception:
            detail = e.response.text or str(e)
        raise HTTPException(status_code=e.response.status_code, detail=detail)


async def _authorize_cv_access(
    db: DBSession,
    principal: dict,
    cv_detail: dict,
) -> None:
    auth0_sub = principal.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=400, detail="auth0_sub not found in token")

    user = await UserRepository(db).find_by_auth0_sub(auth0_sub)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    raw_candidate_id = cv_detail.get("candidate_id")
    if not raw_candidate_id:
        raise HTTPException(status_code=400, detail="CV candidate_id is missing")
    try:
        candidate_id = (
            raw_candidate_id if isinstance(raw_candidate_id, uuid.UUID) else uuid.UUID(raw_candidate_id)
        )
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid CV candidate_id")

    candidate = await CandidateRepository(db).find_by_id(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    is_member = await OrganizationRepository(db).user_is_org_member(
        user.id, candidate.organization_id
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="Forbidden")


@cvRouter.get("/{cv_id}/profile", response_model=CVProfileResponse)
async def get_cv_profile(
    cv_id: uuid.UUID,
    db: DBSession,
    principal: dict = Depends(get_current_principal),
):
    client = CvClient()
    try:
        result = await client.get_cv_detail(cv_id)
        await _authorize_cv_access(db, principal, result)
        return CVProfileResponse.model_validate(result)
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", str(e)) if e.response.text else str(e)
        except Exception:
            detail = e.response.text or str(e)
        raise HTTPException(status_code=e.response.status_code, detail=detail)


@cvRouter.get("/{cv_id}/file")
async def get_cv_file(
    cv_id: uuid.UUID,
    db: DBSession,
    principal: dict = Depends(get_current_principal),
):
    client = CvClient()
    try:
        cv_detail = await client.get_cv_detail(cv_id)
        await _authorize_cv_access(db, principal, cv_detail)
        file_bytes, media_type, content_disposition = await client.get_cv_file(cv_id)
        headers = {}
        if content_disposition:
            headers["Content-Disposition"] = content_disposition
        return Response(content=file_bytes, media_type=media_type, headers=headers)
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", str(e)) if e.response.text else str(e)
        except Exception:
            detail = e.response.text or str(e)
        raise HTTPException(status_code=e.response.status_code, detail=detail)
