# Source: Doc 02 §2.2 + Doc 03 §3.3 — Market data endpoints
"""Piyasa verisi endpoint'leri."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/symbols")
async def list_symbols():
    """Tüm aktif sembolleri listeler."""
    return {"success": True, "data": [], "meta": None}


@router.get("/symbols/{ticker}")
async def get_symbol(ticker: str):
    """Sembol detayını döner."""
    return {"success": True, "data": None}


@router.get("/quotes/{symbol}")
async def get_quote(symbol: str):
    """Anlık fiyat bilgisini döner."""
    return {"success": True, "data": None}


@router.get("/ohlcv/{symbol}")
async def get_ohlcv(symbol: str, timeframe: str = "1d", limit: int = 100):
    """OHLCV verisi döner."""
    return {"success": True, "data": []}
