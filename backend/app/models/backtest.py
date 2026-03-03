# Source: Doc 03 §2.13 — backtest_runs, backtest_trades
"""Backtest ORM modelleri."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin


class BacktestRun(Base, UUIDMixin):
    __tablename__ = "backtest_runs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    strategy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    symbols: Mapped[list] = mapped_column(JSONB, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_capital: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    commission_rate: Mapped[float] = mapped_column(Numeric(8, 6), default=0.001)
    slippage_rate: Mapped[float] = mapped_column(Numeric(8, 6), default=0.0005)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # Sonuçlar
    total_return: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    cagr: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    sharpe_ratio: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    sortino_ratio: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    win_rate: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    profit_factor: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    total_trades: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_trade_pnl: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    avg_holding_days: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    equity_curve: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    strategy: Mapped["Strategy"] = relationship(back_populates="backtest_runs")  # noqa: F821
    trades: Mapped[list[BacktestTrade]] = relationship(back_populates="backtest_run", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BacktestRun {self.name or self.id}>"


class BacktestTrade(Base, UUIDMixin):
    __tablename__ = "backtest_trades"

    backtest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    entry_price: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    exit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exit_price: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    pnl: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    pnl_pct: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    holding_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    signal_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    # İlişkiler
    backtest_run: Mapped[BacktestRun] = relationship(back_populates="trades")
