# Source: Doc 03 §4 — Pydantic market şemaları
"""Piyasa verisi şemaları."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class SymbolResponse(BaseModel):
    id: UUID
    ticker: str
    name: str
    sector: str | None = None
    industry: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


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
    time: datetime
    symbol: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    vwap: Decimal | None = None
