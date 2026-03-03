# Source: Doc 03 §2.6 — strategies, Doc 03 §2.7 — signals
"""Strateji ve sinyal ORM modelleri."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Strategy(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "strategies"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    strategy_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    symbols: Mapped[list] = mapped_column(JSONB, default=list)
    index_filter: Mapped[str | None] = mapped_column(String(20), nullable=True)
    timeframe: Mapped[str] = mapped_column(String(10), default="1d")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_paper: Mapped[bool] = mapped_column(Boolean, default=True)
    risk_params: Mapped[dict] = mapped_column(JSONB, default=dict)

    # İlişkiler
    user: Mapped["User"] = relationship(back_populates="strategies")  # noqa: F821
    signals: Mapped[list[Signal]] = relationship(back_populates="strategy", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship(back_populates="strategy")  # noqa: F821
    backtest_runs: Mapped[list["BacktestRun"]] = relationship(back_populates="strategy")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Strategy {self.name}>"


class Signal(Base, UUIDMixin):
    __tablename__ = "signals"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(10), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    stop_loss: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    take_profit: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    indicators: Mapped[dict] = mapped_column(JSONB, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    is_executed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    strategy: Mapped[Strategy] = relationship(back_populates="signals")

    def __repr__(self) -> str:
        return f"<Signal {self.symbol} {self.signal_type}>"
