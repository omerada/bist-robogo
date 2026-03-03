# Source: Doc 02 §2.5 — Strategy endpoints
"""Strateji endpoint'leri."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_strategies():
    """Stratejileri listeler."""
    return {"success": True, "data": []}


@router.post("/")
async def create_strategy():
    """Yeni strateji oluşturur."""
    return {"success": True, "data": None}


@router.get("/{strategy_id}")
async def get_strategy(strategy_id: str):
    """Strateji detayını döner."""
    return {"success": True, "data": None}


@router.post("/{strategy_id}/activate")
async def activate_strategy(strategy_id: str):
    """Stratejiyi aktifleştirir."""
    return {"success": True, "data": None}
