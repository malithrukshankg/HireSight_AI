from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from database import DBSession
from auth.auth0 import get_current_principal


cvRouter = APIRouter(prefix="/cv", tags=["cv"])


@cvRouter.post("/upload", status_code=201)
async def upload_cv(
    db: DBSession,
    file: UploadFile = File(...),
    principal: dict = Depends(get_current_principal),
):
    """
    Step 2 router contract only:
    - Accept multipart/form-data with field name 'file'
    - Authentication and DB dependencies are wired
    Business logic (validation, S3 upload, DB persist) is implemented in Step 3.
    """
    _ = (db, file, principal)
    raise HTTPException(status_code=501, detail="CV upload service not implemented yet")
