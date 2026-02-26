from fastapi import APIRouter, Depends, File, UploadFile

from api.controllers.cvController import CvController
from api.schemas.cvSchema import CVUploadResponse
from database import DBSession
from auth.auth0 import get_current_principal


cvRouter = APIRouter(prefix="/cv", tags=["cv"])


@cvRouter.post("/upload", response_model=CVUploadResponse, status_code=201)
async def upload_cv(
    db: DBSession,
    file: UploadFile = File(...),
    principal: dict = Depends(get_current_principal),
):
    return await CvController(db).upload_cv(file, principal)
