# Source: Doc 03 §2.4 — symbols, Doc 03 §2.5 — indices, index_components
"""Piyasa sembolleri ve endeks ORM modelleri."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin


class Symbol(Base, UUIDMixin):
    __tablename__ = "symbols"

    ticker: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    market_cap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    free_float_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    lot_size: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at",
        type_=__import__("sqlalchemy").DateTime(timezone=True),
        server_default=__import__("sqlalchemy").func.now(),
        onupdate=__import__("sqlalchemy").func.now(),
    )

    # İlişkiler
    index_components: Mapped[list[IndexComponent]] = relationship(back_populates="symbol")

    def __repr__(self) -> str:
        return f"<Symbol {self.ticker}>"


class BistIndex(Base, UUIDMixin):
    __tablename__ = "indices"

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at",
        type_=__import__("sqlalchemy").DateTime(timezone=True),
        server_default=__import__("sqlalchemy").func.now(),
        onupdate=__import__("sqlalchemy").func.now(),
    )

    # İlişkiler
    components: Mapped[list[IndexComponent]] = relationship(back_populates="index")

    def __repr__(self) -> str:
        return f"<BistIndex {self.code}>"


class IndexComponent(Base, UUIDMixin):
    __tablename__ = "index_components"
    __table_args__ = (UniqueConstraint("index_id", "symbol_id", "added_at"),)

    index_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indices.id", ondelete="CASCADE"), nullable=False
    )
    symbol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("symbols.id", ondelete="CASCADE"), nullable=False
    )
    weight: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    added_at: Mapped[date] = mapped_column(Date, nullable=False)
    removed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # İlişkiler
    index: Mapped[BistIndex] = relationship(back_populates="components")
    symbol: Mapped[Symbol] = relationship(back_populates="index_components")
