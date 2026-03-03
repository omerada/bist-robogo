# Source: Doc 03 §4 — Pydantic strategy şemaları
"""Strateji şemaları."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class StrategyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    strategy_type: str
    parameters: dict = Field(default_factory=dict)
    symbols: list[str] = Field(default_factory=list)
    index_filter: str | None = None
    timeframe: str = "1d"
    risk_params: dict = Field(default_factory=dict)


class StrategyResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    strategy_type: str
    parameters: dict
    symbols: list
    index_filter: str | None = None
    timeframe: str
    is_active: bool
    is_paper: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SignalResponse(BaseModel):
    id: UUID
    strategy_id: UUID
    symbol: str
    signal_type: SignalType
    confidence: Decimal
    price: Decimal
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None
    indicators: dict
    is_executed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
