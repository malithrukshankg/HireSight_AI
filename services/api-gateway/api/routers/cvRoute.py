import httpx

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.clients.cv_client import CvClient
from api.schemas.cvSchema import CVUploadResponse
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
