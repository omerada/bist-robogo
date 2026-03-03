# Source: Doc 03 §3.7 — Pydantic risk şemaları
"""Risk şemaları."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatusResponse(BaseModel):
    overall_risk: RiskLevel
    daily_loss: Decimal
    daily_loss_limit: Decimal
    open_positions: int
    max_positions: int
    rules_active: int
    recent_events: list[dict] = []


class RiskRuleResponse(BaseModel):
    id: UUID
    rule_type: str
    value: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RiskRuleUpdate(BaseModel):
    value: dict | None = None
    is_active: bool | None = None


class RiskEventResponse(BaseModel):
    """Risk olayı yanıt şeması."""
    id: UUID
    user_id: UUID
    event_type: str
    rule_id: UUID | None = None
    details: dict
    created_at: datetime

    model_config = {"from_attributes": True}
