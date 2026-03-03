# Source: Doc 03 §4 — Pydantic portfolio şemaları
"""Portföy şemaları."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PositionResponse(BaseModel):
    id: UUID
    symbol: str
    side: str
    quantity: int
    avg_entry_price: Decimal
    current_price: Decimal | None = None
    unrealized_pnl: Decimal | None = None
    unrealized_pnl_pct: Decimal | None = None
    realized_pnl: Decimal
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None
    opened_at: datetime

    model_config = {"from_attributes": True}


class PortfolioSummaryResponse(BaseModel):
    total_value: Decimal
    cash_balance: Decimal
    invested_value: Decimal
    daily_pnl: Decimal
    daily_pnl_pct: Decimal | None = None
    total_pnl: Decimal
    total_pnl_pct: Decimal | None = None
    open_positions: int
