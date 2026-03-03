# Source: Doc 03 §3.9 — Pydantic bildirim şemaları
"""Bildirim şemaları."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """Bildirim yanıt şeması."""
    id: UUID
    user_id: UUID
    type: str
    title: str
    body: str
    channel: str
    is_read: bool
    metadata_: dict = {}
    sent_at: datetime
    read_at: datetime | None = None

    model_config = {"from_attributes": True}


class NotificationUnreadCount(BaseModel):
    """Okunmamış bildirim sayısı."""
    count: int
