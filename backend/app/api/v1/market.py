# Source: Doc 02 §2.2 + Doc 03 §3.3 — Market data endpoints
"""Piyasa verisi endpoint'leri."""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import redis_manager
from app.database import get_db
from app.schemas.common import APIResponse, PaginationMeta
from app.schemas.market import (
    IndexResponse,
    OHLCVMeta,
    OHLCVResponse,
    QuoteResponse,
    SymbolResponse,
)
from app.services.market_data_service import MarketDataService

router = APIRouter()


def get_market_service(db: AsyncSession = Depends(get_db)) -> MarketDataService:
    return MarketDataService(db)


@router.get("/symbols", response_model=APIResponse)
async def list_symbols(
    search: str | None = Query(None, description="Ticker veya isim araması"),
    index_code: str | None = Query(None, description="Endeks filtresi: XU030, XU100, XKTUM"),
    sector: str | None = Query(None, description="Sektör filtresi"),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    service: MarketDataService = Depends(get_market_service),
):
    """Aktif sembolleri listeler. Filtreleme: arama, endeks, sektör."""
    skip = (page - 1) * per_page
    symbols, total = await service.get_symbols(
        index_code=index_code,
        sector=sector,
        search=search,
        skip=skip,
        limit=per_page,
    )
    total_pages = (total + per_page - 1) // per_page

    return APIResponse(
        success=True,
        data=[s.model_dump() for s in symbols],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/symbols/{ticker}", response_model=APIResponse)
async def get_symbol(
    ticker: str,
    service: MarketDataService = Depends(get_market_service),
):
    """Sembol detayını döner."""
    symbol = await service.get_symbol_detail(ticker)
    if not symbol:
        raise HTTPException(status_code=404, detail=f"Sembol bulunamadı: {ticker}")
    return APIResponse(success=True, data=symbol.model_dump())


@router.get("/symbols/{ticker}/quote", response_model=APIResponse)
async def get_quote(
    ticker: str,
    service: MarketDataService = Depends(get_market_service),
):
    """Anlık/son fiyat bilgisi."""
    quote = await service.get_quote(ticker)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Sembol bulunamadı: {ticker}")
    return APIResponse(success=True, data=quote.model_dump())


@router.get("/symbols/{ticker}/history", response_model=APIResponse)
async def get_ohlcv(
    ticker: str,
    interval: str = Query("1d", regex=r"^(1m|5m|15m|1h|1d|1w|1M)$"),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(250, ge=1, le=1000),
    service: MarketDataService = Depends(get_market_service),
):
    """OHLCV zaman serisi verisi."""
    data = await service.get_ohlcv(
        ticker=ticker,
        interval=interval,
        start=start,
        end=end,
        limit=limit,
    )
    return APIResponse(
        success=True,
        data=data,
        meta={"symbol": ticker.upper(), "interval": interval, "count": len(data)},
    )


@router.get("/indices", response_model=APIResponse)
async def list_indices(
    service: MarketDataService = Depends(get_market_service),
):
    """Aktif endeks listesi (BIST30, BIST100, Katılım)."""
    indices = await service.get_indices()
    return APIResponse(success=True, data=indices)


@router.get("/sectors", response_model=APIResponse)
async def list_sectors(
    service: MarketDataService = Depends(get_market_service),
):
    """Benzersiz sektör listesi."""
    sectors = await service.get_sectors()
    return APIResponse(success=True, data=sectors)


@router.get("/live-prices", response_model=APIResponse)
async def get_live_prices(
    symbols: str | None = Query(None, description="Virgülle ayrılmış semboller: THYAO,GARAN,AKBNK"),
    service: MarketDataService = Depends(get_market_service),
):
    """Redis cache'ten canlı fiyatları toplu döner.

    Sembol belirtilmezse tüm cache'teki fiyatları döner (max 200).
    """
    result: list[dict] = []

    if symbols:
        ticker_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    else:
        # Tüm cache'teki quote key'lerini tara
        ticker_list = []
        if redis_manager.client:
            keys = []
            async for key in redis_manager.client.scan_iter("market:quote:*", count=200):
                keys.append(key)
                if len(keys) >= 200:
                    break
            ticker_list = [k.replace("market:quote:", "") for k in keys]

    for ticker in ticker_list:
        raw = await redis_manager.get_cached(f"market:quote:{ticker}")
        if raw:
            try:
                data = json.loads(raw)
                data["symbol"] = ticker
                result.append(data)
            except json.JSONDecodeError:
                pass

    return APIResponse(
        success=True,
        data=result,
        meta={"count": len(result)},
    )


@router.get("/live-indices", response_model=APIResponse)
async def get_live_indices():
    """Redis cache'ten canlı BIST endeks verilerini döner."""
    result: list[dict] = []

    if redis_manager.client:
        keys = []
        async for key in redis_manager.client.scan_iter("market:index:*", count=50):
            keys.append(key)

        for key in keys:
            raw = await redis_manager.get_cached(key)
            if raw:
                try:
                    data = json.loads(raw)
                    data["code"] = key.replace("market:index:", "")
                    result.append(data)
                except json.JSONDecodeError:
                    pass

    return APIResponse(success=True, data=result, meta={"count": len(result)})
