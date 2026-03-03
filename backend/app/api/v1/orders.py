# Source: Doc 02 §2.3 + Doc 03 §3.4 — Order endpoints
"""Emir endpoint'leri."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_orders():
    """Emirleri listeler."""
    return {"success": True, "data": [], "meta": None}


@router.post("/")
async def create_order():
    """Yeni emir oluşturur."""
    return {"success": True, "data": None}


@router.get("/{order_id}")
async def get_order(order_id: str):
    """Emir detayını döner."""
    return {"success": True, "data": None}


@router.delete("/{order_id}")
async def cancel_order(order_id: str):
    """Emir iptal eder."""
    return {"success": True, "data": None}
