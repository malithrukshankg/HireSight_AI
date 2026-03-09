from fastapi import APIRouter, File, UploadFile

from app.api.controllers.cv_controller import CvController
from app.api.schemas.cv_schema import CVUploadResponse
from app.database import DBSession

cv_router = APIRouter(prefix="/cv", tags=["cv"])


@cv_router.post("/upload", response_model=CVUploadResponse, status_code=201)
async def upload_cv(
    db: DBSession,
    file: UploadFile = File(...),
):
    return await CvController(db).upload_cv(file, principal={})
