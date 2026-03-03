# Source: Doc 02 §2.9 — Notification endpoints
"""Bildirim endpoint'leri."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def list_notifications(
    is_read: bool | None = None,
    channel: str | None = None,
    page: int = 1,
    per_page: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bildirimleri listeler."""
    service = NotificationService(db)
    skip = (page - 1) * per_page
    notifications, total = await service.list_notifications(
        user.id, is_read=is_read, channel=channel, skip=skip, limit=per_page
    )
    return APIResponse(
        success=True,
        data=[n.model_dump() for n in notifications],
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        },
    )


@router.get("/unread-count")
async def get_unread_count(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Okunmamış bildirim sayısını döner."""
    service = NotificationService(db)
    count = await service.get_unread_count(user.id)
    return APIResponse(success=True, data={"count": count})


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bildirimi okundu olarak işaretler."""
    service = NotificationService(db)
    try:
        await service.mark_read(user.id, notification_id)
        return APIResponse(success=True, data=None)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/read-all")
async def mark_all_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Tüm bildirimleri okundu olarak işaretler."""
    service = NotificationService(db)
    count = await service.mark_all_read(user.id)
    return APIResponse(success=True, data={"updated": count})


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bildirimi siler."""
    service = NotificationService(db)
    try:
        await service.delete_notification(user.id, notification_id)
        return APIResponse(success=True, data=None)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
