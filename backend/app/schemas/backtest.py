# Source: Doc 03 §4 — Pydantic backtest şemaları
"""Backtest şemaları."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    strategy_id: UUID
    parameters: dict = Field(default_factory=dict)
    symbols: list[str]
    start_date: date
    end_date: date
    initial_capital: Decimal = Field(default=Decimal("1000000"))
    commission_rate: Decimal = Field(default=Decimal("0.001"))
    slippage_rate: Decimal = Field(default=Decimal("0.0005"))


class BacktestResultResponse(BaseModel):
    id: UUID
    name: str | None = None
    status: str
    total_return: Decimal | None = None
    cagr: Decimal | None = None
    sharpe_ratio: Decimal | None = None
    sortino_ratio: Decimal | None = None
    max_drawdown: Decimal | None = None
    win_rate: Decimal | None = None
    profit_factor: Decimal | None = None
    total_trades: int | None = None
    avg_trade_pnl: Decimal | None = None
    avg_holding_days: Decimal | None = None
    equity_curve: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
