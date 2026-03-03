# Source: Doc 02 §2.6 — Backtest endpoints
"""Backtest endpoint'leri."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
async def run_backtest():
    """Yeni backtest başlatır."""
    return {"success": True, "data": None}


@router.get("/")
async def list_backtests():
    """Backtest sonuçlarını listeler."""
    return {"success": True, "data": []}


@router.get("/{backtest_id}")
async def get_backtest(backtest_id: str):
    """Backtest detayını döner."""
    return {"success": True, "data": None}
