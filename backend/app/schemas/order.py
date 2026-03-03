# Source: Doc 03 §4 — Pydantic order şemaları
"""Emir şemaları."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"


class OrderStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILL = "partial_fill"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(str, Enum):
    DAY = "day"
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"


class OrderCreateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, examples=["THYAO"])
    side: OrderSide
    order_type: OrderType
    quantity: int = Field(..., gt=0)
    price: Decimal | None = Field(None, gt=0)
    stop_loss: Decimal | None = Field(None, gt=0)
    take_profit: Decimal | None = Field(None, gt=0)
    time_in_force: TimeInForce = TimeInForce.DAY
    strategy_id: UUID | None = None


class OrderResponse(BaseModel):
    id: UUID
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Decimal | None = None
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None
    status: OrderStatus
    filled_quantity: int
    filled_price: Decimal | None = None
    commission: Decimal
    is_paper: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
