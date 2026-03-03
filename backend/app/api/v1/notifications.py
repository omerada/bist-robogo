# Source: Doc 02 §2.9 — Notification endpoints
"""Bildirim endpoint'leri."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_notifications():
    """Bildirimleri listeler."""
    return {"success": True, "data": []}


@router.put("/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Bildirimi okundu olarak işaretler."""
    return {"success": True, "data": None}


@router.put("/read-all")
async def mark_all_read():
    """Tüm bildirimleri okundu olarak işaretler."""
    return {"success": True, "data": None}
