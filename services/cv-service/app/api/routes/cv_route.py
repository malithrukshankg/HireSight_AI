import uuid

from fastapi import APIRouter, File, Header, UploadFile
from fastapi.responses import Response

from app.api.controllers.cv_controller import CvController
from app.api.schemas.cv_schema import (
    CVAiContextResponse,
    CVByCandidateResponse,
    CVDetailResponse,
    CVExtractionResponse,
    CVStructuredExtractionResponse,
    CVUploadResponse,
)
from app.database import DBSession

cv_router = APIRouter(prefix="/cv", tags=["cv"])

internal_router = APIRouter(prefix="/internal", tags=["cv-internal"])


@cv_router.post("/upload", response_model=CVUploadResponse, status_code=201)
async def upload_cv(
    db: DBSession,
    file: UploadFile = File(...),
):
    return await CvController(db).upload_cv(file, principal={})


@internal_router.post("/upload-for-candidate", response_model=CVUploadResponse, status_code=201)
async def upload_for_candidate(
    db: DBSession,
    file: UploadFile = File(...),
    x_candidate_id: uuid.UUID = Header(alias="X-Candidate-Id"),
    x_user_id: uuid.UUID = Header(alias="X-User-Id"),
):
    return await CvController(db).upload_cv_for_candidate(
        file=file,
        candidate_id=x_candidate_id,
        uploaded_by_user_id=x_user_id,
    )


@internal_router.get("/by-candidate/{candidate_id}", response_model=CVByCandidateResponse)
async def get_by_candidate(
    candidate_id: uuid.UUID,
    db: DBSession,
):
    return await CvController(db).get_by_candidate_id(candidate_id)


@internal_router.get("/cv/{cv_id}", response_model=CVDetailResponse)
async def get_cv_detail(
    cv_id: uuid.UUID,
    db: DBSession,
):
    return await CvController(db).get_cv_detail(cv_id)


@internal_router.get("/cv/{cv_id}/ai-context", response_model=CVAiContextResponse)
async def get_cv_ai_context(
    cv_id: uuid.UUID,
    db: DBSession,
):
    """Return raw CV text, parsed profile, and parse metadata for agent-service consumption."""
    return await CvController(db).get_cv_ai_context(cv_id)


@internal_router.get("/cv/{cv_id}/file")
async def get_cv_file(
    cv_id: uuid.UUID,
    db: DBSession,
):
    file_bytes, content_type, filename = await CvController(db).get_cv_file(cv_id)
    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@internal_router.post("/extract/{cv_id}", response_model=CVExtractionResponse)
async def trigger_extraction(
    cv_id: uuid.UUID,
    db: DBSession,
):
    return await CvController(db).trigger_extraction(cv_id)


@internal_router.post(
    "/extract-structured/{cv_id}",
    response_model=CVStructuredExtractionResponse,
)
async def trigger_structured_extraction(
    cv_id: uuid.UUID,
    db: DBSession,
):
    return await CvController(db).trigger_structured_extraction(cv_id)
