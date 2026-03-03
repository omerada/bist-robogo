# Source: Doc 03 §2.10 — positions, Doc 03 §2.11 — portfolios, portfolio_snapshots
"""Portföy, pozisyon ve snapshot ORM modelleri."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin


class Position(Base, UUIDMixin):
    __tablename__ = "positions"
    __table_args__ = (UniqueConstraint("user_id", "symbol"),)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # long, short
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_entry_price: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    current_price: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    unrealized_pnl: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    realized_pnl: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    stop_loss: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    take_profit: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    strategy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Position {self.symbol} {self.side} {self.quantity}>"


class Portfolio(Base, UUIDMixin):
    __tablename__ = "portfolios"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    total_value: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False, default=0)
    cash_balance: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False, default=0)
    invested_value: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False, default=0)
    daily_pnl: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    total_pnl: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # İlişkiler
    user: Mapped["User"] = relationship(back_populates="portfolio")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Portfolio user={self.user_id}>"


class PortfolioSnapshot(Base, UUIDMixin):
    __tablename__ = "portfolio_snapshots"
    __table_args__ = (UniqueConstraint("user_id", "snapshot_date"),)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_value: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    cash_balance: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    invested_value: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    daily_pnl: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    positions_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
