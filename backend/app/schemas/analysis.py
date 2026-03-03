# Source: Doc 03 §3.6 — Pydantic trend analiz şemaları
"""Trend analiz şemaları."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class TrendPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendType(str, Enum):
    ALL = "all"
    DIP = "dip"
    BREAKOUT = "breakout"


class TrendAnalysisRequest(BaseModel):
    period: TrendPeriod = TrendPeriod.DAILY
    index: str = "ALL"
    type: TrendType = TrendType.ALL
    min_score: float = Field(default=0.6, ge=0, le=1)
    limit: int = Field(default=50, ge=1, le=200)


class TrendIndicators(BaseModel):
    """Trend adayı gösterge detayları."""
    sma_20: float | None = None
    sma_50: float | None = None
    ema_12: float | None = None
    bollinger_lower: float | None = None
    bollinger_upper: float | None = None
    adx: float | None = None
    stochastic_k: float | None = None
    macd_histogram: float | None = None
    obv_trend: str | None = None


class DipCandidateResponse(BaseModel):
    """Dip adayı hisse detayı."""
    symbol: str
    name: str
    price: Decimal
    change_pct: float = 0.0
    dip_score: float
    support_level: float | None = None
    resistance_level: float | None = None
    rsi: float | None = None
    macd_signal: str = "neutral"
    volume_ratio: float | None = None
    trend_status: str = "sideways"
    indicators: TrendIndicators = Field(default_factory=TrendIndicators)


class BreakoutCandidateResponse(BaseModel):
    """Kırılım adayı hisse detayı."""
    symbol: str
    name: str
    price: Decimal
    change_pct: float = 0.0
    breakout_score: float
    breakout_level: float | None = None
    target_price: float | None = None
    volume_surge: float | None = None
    trend_status: str = "sideways"
    indicators: TrendIndicators = Field(default_factory=TrendIndicators)


class TrendAnalysisMeta(BaseModel):
    """Trend analiz meta bilgileri."""
    total_dip_candidates: int = 0
    total_breakout_candidates: int = 0
    analysis_timestamp: datetime | None = None


class TrendAnalysisResponse(BaseModel):
    """Trend analiz tam response."""
    period: str
    index: str
    analysis_date: str
    dip_candidates: list[DipCandidateResponse] = []
    breakout_candidates: list[BreakoutCandidateResponse] = []


class TrendCandidateResponse(BaseModel):
    """Genel trend adayı (geriye uyumluluk)."""
    symbol: str
    name: str
    price: Decimal
    score: Decimal
    trend_status: str
    rsi: Decimal | None = None
    volume_ratio: Decimal | None = None
    indicators: dict = {}
