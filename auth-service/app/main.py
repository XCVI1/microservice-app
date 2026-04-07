from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import router as auth_router
from app.core.database import get_db

app = FastAPI(title="Auth Service", version="1.0.0")
Instrumentator().instrument(app).expose(app)
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health/live", tags=["system"])
async def liveness():
    return {"status": "ok", "service": "auth"}


@app.get("/health/ready", tags=["system"])
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="db unavailable")
