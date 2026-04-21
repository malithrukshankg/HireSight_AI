from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.cvRoute import cvRouter
from api.routers.internalAiRoute import internalAiRouter
from api.routers.internalJobsRoute import internalJobsRouter
from api.routers.jobRoute import jobRouter
from api.routers.meRoute import meRouter
from api.routers.organizationRoute import organizationRouter
from api.routers.userRoute import userRouter
from auth.auth0 import get_current_principal
from config import settings
from core.redis_client import close_redis, init_redis
from services.ai_service.shared.geminiClient import close_shared_gemini_sdk_client_async


app = FastAPI(title="HireSight API Gateway", version="0.1.0")

cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]


@app.get("/health")
def health():
    return {"status": "Okay", "service": "api-gateway"}


@app.on_event("startup")
async def on_startup() -> None:
    await init_redis()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await close_shared_gemini_sdk_client_async()
    await close_redis()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/private")
async def private_route(principal: dict = Depends(get_current_principal)):
    return {
        "message": "Authenticated!",
        "sub": principal.get("sub"),
        "aud": principal.get("aud"),
        "iss": principal.get("iss"),
        "claims": principal,
    }

app.include_router(userRouter)
app.include_router(meRouter)
app.include_router(organizationRouter)
app.include_router(jobRouter)
app.include_router(cvRouter)
app.include_router(internalAiRouter)
app.include_router(internalJobsRouter)

