from fastapi import FastAPI

from app.items.router import router as items_router

app = FastAPI(title="Core Service", version="1.0.0")

app.include_router(items_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "service": "core"}
