from fastapi import FastAPI

app = FastAPI(title="HireSight API Gateway", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "service": "api-gateway"}
