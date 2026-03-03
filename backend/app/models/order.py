# Source: Doc 03 §2.8 — orders, Doc 03 §2.9 — trades
"""Emir ve işlem ORM modelleri."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Order(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "orders"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    strategy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=True)
    signal_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("signals.id"), nullable=True)
    broker_conn_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("broker_connections.id"), nullable=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # buy, sell
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    stop_price: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    time_in_force: Mapped[str] = mapped_column(String(10), default="day")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    filled_quantity: Mapped[int] = mapped_column(Integer, default=0)
    filled_price: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    commission: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    broker_order_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_paper: Mapped[bool] = mapped_column(Boolean, default=False)

    # İlişkiler
    user: Mapped["User"] = relationship(back_populates="orders")  # noqa: F821
    strategy: Mapped["Strategy | None"] = relationship(back_populates="orders")  # noqa: F821
    trades: Mapped[list[Trade]] = relationship(back_populates="order")

    def __repr__(self) -> str:
        return f"<Order {self.symbol} {self.side} {self.status}>"


class Trade(Base, UUIDMixin):
    __tablename__ = "trades"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    commission: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    pnl: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    order: Mapped[Order] = relationship(back_populates="trades")

    def __repr__(self) -> str:
        return f"<Trade {self.symbol} {self.side} {self.quantity}>"
