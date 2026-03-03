# Source: Doc 03 §2.3 — broker_connections
"""Broker bağlantı ORM modeli."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, LargeBinary, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class BrokerConnection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "broker_connections"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    broker_name: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_credentials: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_paper_trading: Mapped[bool] = mapped_column(Boolean, default=False)
    last_connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # İlişkiler
    user: Mapped["User"] = relationship(back_populates="broker_connections")  # noqa: F821

    def __repr__(self) -> str:
        return f"<BrokerConnection {self.broker_name}>"
