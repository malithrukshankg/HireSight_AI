from fastapi import FastAPI
from fastapi.middleware import CORSMiddleware

app = FastAPI(title="HireSight API Gateway", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "api-gateway"}

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

