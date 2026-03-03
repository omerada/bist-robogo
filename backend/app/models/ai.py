# Source: Doc 10 §Faz 3 Sprint 3.3 — AI deneyleri ve performans modelleri
"""AI A/B test deneyleri, sonuçları ve analiz logları ORM modelleri."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class AIExperiment(Base, UUIDMixin, TimestampMixin):
    """A/B test deneyi — iki modeli aynı semboller üzerinde karşılaştırır."""

    __tablename__ = "ai_experiments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_a: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # ör: google/gemini-2.5-flash
    model_b: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # ör: openai/gpt-4o
    symbols: Mapped[list] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, running, completed, failed
    config: Mapped[dict] = mapped_column(
        JSONB, default=dict
    )  # temperature, max_tokens vb.
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<AIExperiment {self.name} [{self.status}]>"


class AIExperimentResult(Base, UUIDMixin):
    """A/B test deney sonucu — her sembol × model kombinasyonu için bir kayıt."""

    __tablename__ = "ai_experiment_results"

    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_experiments.id", ondelete="CASCADE"),
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    model_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # hangi model üretmiş
    action: Mapped[str] = mapped_column(String(10), nullable=False)  # buy/sell/hold
    confidence: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # low/medium/high
    score: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0)  # 0.0-1.0
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)  # API yanıt süresi
    token_usage: Mapped[dict] = mapped_column(
        JSONB, default=dict
    )  # prompt_tokens, completion_tokens
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<AIExperimentResult {self.symbol} {self.model_id} → {self.action}>"


class AIAnalysisLog(Base, UUIDMixin):
    """AI analiz performans logu — her analiz çağrısını kaydeder."""

    __tablename__ = "ai_analysis_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(10), nullable=False)  # buy/sell/hold
    confidence: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # low/medium/high
    score: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0)
    actual_price_change: Mapped[float | None] = mapped_column(
        Numeric(10, 4), nullable=True
    )  # gerçekleşen fiyat değişimi %
    is_correct: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )  # sonradan doldurulan doğruluk bayrağı
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    token_usage: Mapped[dict] = mapped_column(JSONB, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<AIAnalysisLog {self.symbol} {self.model_id} {self.action}>"
