# Source: Doc 07 §12.2 pattern — Notification repository
"""Bildirim veritabanı erişim katmanı."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class NotificationRepository(BaseRepository[Notification]):
    """Notification CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_by_user(
        self,
        user_id: UUID,
        is_read: bool | None = None,
        channel: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Notification]:
        """Kullanıcının bildirimlerini listele."""
        stmt = select(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
        if channel:
            stmt = stmt.where(Notification.channel == channel)
        stmt = stmt.order_by(Notification.sent_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        is_read: bool | None = None,
    ) -> int:
        """Kullanıcının bildirim sayısı."""
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
        )
        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def count_unread(self, user_id: UUID) -> int:
        """Okunmamış bildirim sayısı."""
        return await self.count_by_user(user_id, is_read=False)

    async def mark_read(self, notification_id: UUID) -> None:
        """Bildirimi okundu olarak işaretle (raw UPDATE)."""
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id)
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)

    async def mark_all_read(self, user_id: UUID) -> int:
        """Tüm bildirimleri okundu yap. Güncellenen sayısını döner."""
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        return result.rowcount
