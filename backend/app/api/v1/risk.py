# Source: Doc 02 §2.7 — Risk management endpoints
"""Risk yönetimi endpoint'leri."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.risk import RiskRuleUpdate
from app.services.risk_service import RiskService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/status")
async def get_risk_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Genel risk durumunu döner."""
    service = RiskService(db)
    status = await service.get_status(user.id)
    return APIResponse(success=True, data=status.model_dump())


@router.get("/rules")
async def list_risk_rules(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Risk kurallarını listeler."""
    service = RiskService(db)
    rules = await service.list_rules(user.id)
    return APIResponse(
        success=True,
        data=[r.model_dump() for r in rules],
        meta={"total": len(rules)},
    )


@router.put("/rules/{rule_id}")
async def update_risk_rule(
    rule_id: UUID,
    body: RiskRuleUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Risk kuralını günceller."""
    service = RiskService(db)
    try:
        rule = await service.update_rule(user.id, rule_id, body)
        return APIResponse(success=True, data=rule.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/events")
async def list_risk_events(
    event_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Risk olaylarını listeler."""
    service = RiskService(db)
    skip = (page - 1) * per_page
    events, total = await service.list_events(
        user.id, event_type=event_type, skip=skip, limit=per_page
    )
    return APIResponse(
        success=True,
        data=[e.model_dump() for e in events],
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        },
    )
