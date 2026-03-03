# Source: Doc 02 §2.8 + Doc 03 §3.5 — Portfolio endpoints
"""Portföy endpoint'leri."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter()


def get_portfolio_service(db: AsyncSession = Depends(get_db)) -> PortfolioService:
    return PortfolioService(db)


@router.get("/summary", response_model=APIResponse)
async def get_portfolio_summary(
    user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    """Portföy özeti döner."""
    summary = await service.get_summary(user.id)
    return APIResponse(success=True, data=summary.model_dump())


@router.get("/positions", response_model=APIResponse)
async def list_positions(
    user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    """Açık pozisyonları listeler."""
    positions = await service.get_positions(user.id)
    return APIResponse(success=True, data=[p.model_dump() for p in positions])


@router.get("/history", response_model=APIResponse)
async def get_portfolio_history(
    limit: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    """Portföy değer geçmişi (günlük snapshot'lar)."""
    history = await service.get_history(user.id, limit=limit)
    return APIResponse(success=True, data=history)
