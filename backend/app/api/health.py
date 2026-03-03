# Source: Doc 07 §10.2 — Health Check (Doc 11 Tutarsızlık #4: /health kullan)
"""Sağlık kontrolü endpoint'leri."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import redis_manager
from app.database import get_db

health_router = APIRouter()


@health_router.get("/health")
async def health_check():
    """Basit health check — uygulama çalışıyor mu?"""
    return {"status": "healthy"}


@health_router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check — tüm bağımlılıklar hazır mı?"""
    checks = {}

    # PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # Redis
    try:
        if redis_manager.client:
            await redis_manager.client.ping()
            checks["redis"] = "ok"
        else:
            checks["redis"] = "not connected"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
    }
