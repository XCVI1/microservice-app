from fastapi import FastAPI

from app.auth.router import router as auth_router

app = FastAPI(title="Auth Service", version="1.0.0")

app.include_router(auth_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "service": "auth"}
