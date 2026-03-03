# Source: Doc 03 §4 — Pydantic market şemaları
"""Piyasa verisi şemaları."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class SymbolResponse(BaseModel):
    id: UUID
    ticker: str
    name: str
    sector: str | None = None
    industry: str | None = None
    market_cap: int | None = None
    lot_size: int = 1
    is_active: bool

    model_config = {"from_attributes": True}


class SymbolDetailResponse(SymbolResponse):
    """Sembol detay — quote bilgisi ile zenginleştirilmiş."""
    free_float_rate: float | None = None
    meta: dict = {}


class IndexResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str | None = None


class QuoteResponse(BaseModel):
    symbol: str
    name: str
    price: Decimal
    change: Decimal
    change_pct: Decimal
    open: Decimal
    high: Decimal
    low: Decimal
    close_prev: Decimal
    volume: int
    bid: Decimal
    ask: Decimal
    updated_at: datetime


class OHLCVResponse(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class OHLCVMeta(BaseModel):
    symbol: str
    interval: str
    count: int


class SymbolSearchQuery(BaseModel):
    """Sembol arama/filtreleme parametreleri."""
    search: str | None = None
    index_code: str | None = Field(None, description="Endeks kodu: XU030, XU100, XKTUM")
    sector: str | None = None
    page: int = Field(1, ge=1)
    per_page: int = Field(30, ge=1, le=100)


class OHLCVQuery(BaseModel):
    """OHLCV sorgu parametreleri."""
    interval: str = Field("1d", pattern=r"^(1m|5m|15m|1h|1d|1w|1M)$")
    start: datetime | None = None
    end: datetime | None = None
    limit: int = Field(250, ge=1, le=1000)
