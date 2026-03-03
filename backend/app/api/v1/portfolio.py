# Source: Doc 02 §2.8 + Doc 03 §3.5 — Portfolio endpoints
"""Portföy endpoint'leri."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
async def get_portfolio_summary():
    """Portföy özeti döner."""
    return {"success": True, "data": None}


@router.get("/positions")
async def list_positions():
    """Açık pozisyonları listeler."""
    return {"success": True, "data": []}
