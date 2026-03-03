# Source: Doc 03 §4 — Pydantic backtest şemaları
"""Backtest şemaları."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class BacktestRunRequest(BaseModel):
    """Backtest başlatma isteği."""

    strategy_id: UUID
    name: str | None = Field(None, max_length=255)
    parameters: dict = Field(default_factory=dict)
    symbols: list[str] = Field(..., min_length=1)
    start_date: date
    end_date: date
    initial_capital: Decimal = Field(default=Decimal("1000000"))
    commission_rate: Decimal = Field(default=Decimal("0.001"))
    slippage_rate: Decimal = Field(default=Decimal("0.0005"))


class BacktestTradeResponse(BaseModel):
    """Backtest trade detayı."""

    id: UUID
    backtest_id: UUID
    symbol: str
    side: str
    entry_date: date
    entry_price: Decimal
    exit_date: date | None = None
    exit_price: Decimal | None = None
    quantity: int
    pnl: Decimal | None = None
    pnl_pct: Decimal | None = None
    holding_days: int | None = None
    signal_metadata: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class BacktestResultResponse(BaseModel):
    """Backtest sonuç özeti."""

    id: UUID
    strategy_id: UUID
    name: str | None = None
    status: str
    parameters: dict = Field(default_factory=dict)
    symbols: list = Field(default_factory=list)
    start_date: date
    end_date: date
    initial_capital: Decimal
    commission_rate: Decimal
    slippage_rate: Decimal
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


class BacktestDetailResponse(BacktestResultResponse):
    """Backtest detay — trade listesi ile birlikte."""

    trades: list[BacktestTradeResponse] = Field(default_factory=list)


class BacktestRequest(BaseModel):
    """Geriye uyumluluk — eski şema adı."""

    strategy_id: UUID
    parameters: dict = Field(default_factory=dict)
    symbols: list[str]
    start_date: date
    end_date: date
    initial_capital: Decimal = Field(default=Decimal("1000000"))
    commission_rate: Decimal = Field(default=Decimal("0.001"))
    slippage_rate: Decimal = Field(default=Decimal("0.0005"))

