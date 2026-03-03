# Source: Doc 02 §2.9 — Bildirim servisi
"""Bildirim yönetimi iş mantığı katmanı."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    NotificationResponse,
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Bildirim CRUD + in-app yönetimi."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_repo = NotificationRepository(db)

    # ── Listeleme ──

    async def list_notifications(
        self,
        user_id: UUID,
        is_read: bool | None = None,
        channel: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[NotificationResponse], int]:
        """Kullanıcının bildirimlerini listele."""
        notifications = await self.notification_repo.get_by_user(
            user_id, is_read=is_read, channel=channel, skip=skip, limit=limit
        )
        total = await self.notification_repo.count_by_user(user_id, is_read=is_read)
        return [NotificationResponse.model_validate(n) for n in notifications], total

    async def get_unread_count(self, user_id: UUID) -> int:
        """Okunmamış bildirim sayısını döner."""
        return await self.notification_repo.count_unread(user_id)

    # ── Okundu İşaretleme ──

    async def mark_read(self, user_id: UUID, notification_id: UUID) -> None:
        """Tek bildirimi okundu yap."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            raise ValueError("Bildirim bulunamadı")
        await self.notification_repo.mark_read(notification_id)
        await self.db.commit()

    async def mark_all_read(self, user_id: UUID) -> int:
        """Tüm bildirimleri okundu yap. Güncellenen sayıyı döner."""
        count = await self.notification_repo.mark_all_read(user_id)
        await self.db.commit()
        return count

    # ── Bildirim Oluşturma ──

    async def create_notification(
        self,
        user_id: UUID,
        type: str,
        title: str,
        body: str,
        channel: str = "in_app",
        metadata: dict | None = None,
    ) -> NotificationResponse:
        """Yeni bildirim oluştur."""
        notification = await self.notification_repo.create(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            channel=channel,
            metadata_=metadata or {},
        )
        await self.db.commit()

        # Tazele
        refreshed = await self.notification_repo.get_by_id(notification.id)
        return NotificationResponse.model_validate(refreshed)

    # ── Silme ──

    async def delete_notification(self, user_id: UUID, notification_id: UUID) -> None:
        """Bildirimi sil."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            raise ValueError("Bildirim bulunamadı")
        await self.notification_repo.delete(notification)
        await self.db.commit()
