# Source: Doc 02 §2.8 — Trend analysis endpoints
"""Trend analizi endpoint'leri."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/candidates")
async def get_trend_candidates():
    """Trend adayı hisseleri döner."""
    return {"success": True, "data": []}


@router.post("/analyze")
async def analyze_trends():
    """Trend analizi başlatır."""
    return {"success": True, "data": None}


@router.get("/sectors")
async def get_sector_analysis():
    """Sektörel analiz döner."""
    return {"success": True, "data": []}
