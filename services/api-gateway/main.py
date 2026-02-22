from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routers.userRoute import userRouter
from api.routers.meRoute import meRouter
from api.routers.organizationRoute import organizationRouter
from auth.auth0 import get_current_principal


app = FastAPI(title="HireSight API Gateway", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "api-gateway"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev; add production origin(s) as needed
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

