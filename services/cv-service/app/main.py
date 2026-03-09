from fastapi import FastAPI

from app.api.routes.cv_route import cv_router

app = FastAPI(title="HireSight CV Service", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "cv-service"}


app.include_router(cv_router)
