# Source: Doc 03 §3.6 — Pydantic trend analiz şemaları
"""Trend analiz şemaları."""

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class TrendPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendAnalysisRequest(BaseModel):
    period: TrendPeriod = TrendPeriod.DAILY
    index: str = "ALL"
    type: str = "all"  # all, dip, breakout
    min_score: float = Field(default=0.6, ge=0, le=1)
    limit: int = Field(default=50, ge=1, le=200)


class TrendCandidateResponse(BaseModel):
    symbol: str
    name: str
    price: Decimal
    score: Decimal
    trend_status: str
    rsi: Decimal | None = None
    volume_ratio: Decimal | None = None
    indicators: dict = {}
