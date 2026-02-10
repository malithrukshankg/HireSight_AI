from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.userRoute import userRouter
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

app.include_router(userRouter)

