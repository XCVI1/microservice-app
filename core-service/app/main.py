from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator
from app.items.router import router as items_router
from app.core.database import get_db

app = FastAPI(title="Core Service!", version="1.0.0")
Instrumentator().instrument(app).expose(app)
app.include_router(items_router, prefix="/api/v1")

@app.get("/health/live", tags=["system"])
async def liveness():
    return {"status": "ok", "service": "core"}

@app.get("/health/ready", tags=["system"])
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="db unavailable")
