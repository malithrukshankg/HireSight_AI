from fastapi import FastAPI

from app.api.routes.agent_route import internal_agent_router

app = FastAPI(title="HireSight Agent Service", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "agent-service", "version": "0.1.0"}


app.include_router(internal_agent_router)
