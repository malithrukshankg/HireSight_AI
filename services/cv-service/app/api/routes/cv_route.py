import uuid

from fastapi import APIRouter, File, Header, UploadFile

from app.api.controllers.cv_controller import CvController
from app.api.schemas.cv_schema import CVByCandidateResponse, CVUploadResponse
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
