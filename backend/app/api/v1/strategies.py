# Source: Doc 02 §2.5 — Strategy endpoints
"""Strateji endpoint'leri."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse, PaginationMeta
from app.schemas.strategy import StrategyCreateRequest, StrategyUpdateRequest
from app.services.strategy_service import StrategyService

router = APIRouter()


def get_strategy_service(db: AsyncSession = Depends(get_db)) -> StrategyService:
    return StrategyService(db)


@router.get("/", response_model=APIResponse)
async def list_strategies(
    strategy_type: str | None = Query(None, description="Strateji tipi filtresi"),
    is_active: bool | None = Query(None, description="Aktiflik filtresi"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Kullanıcının stratejilerini listeler."""
    skip = (page - 1) * per_page
    strategies, total = await service.list_strategies(
        user_id=user.id,
        strategy_type=strategy_type,
        is_active=is_active,
        skip=skip,
        limit=per_page,
    )
    total_pages = (total + per_page - 1) // per_page

    return APIResponse(
        success=True,
        data=[s.model_dump() for s in strategies],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.post("/", response_model=APIResponse, status_code=201)
async def create_strategy(
    data: StrategyCreateRequest,
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Yeni strateji oluşturur."""
    strategy = await service.create_strategy(user_id=user.id, data=data)
    return APIResponse(success=True, data=strategy.model_dump())


@router.get("/{strategy_id}", response_model=APIResponse)
async def get_strategy(
    strategy_id: UUID,
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Strateji detayını döner."""
    strategy = await service.get_strategy(strategy_id, user.id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strateji bulunamadı")
    return APIResponse(success=True, data=strategy.model_dump())


@router.put("/{strategy_id}", response_model=APIResponse)
async def update_strategy(
    strategy_id: UUID,
    data: StrategyUpdateRequest,
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Strateji günceller."""
    strategy = await service.update_strategy(strategy_id, user.id, data)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strateji bulunamadı")
    return APIResponse(success=True, data=strategy.model_dump())


@router.delete("/{strategy_id}", status_code=204)
async def delete_strategy(
    strategy_id: UUID,
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Strateji siler."""
    deleted = await service.delete_strategy(strategy_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Strateji bulunamadı")


@router.post("/{strategy_id}/activate", response_model=APIResponse)
async def activate_strategy(
    strategy_id: UUID,
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Stratejiyi aktifleştirir."""
    strategy = await service.activate_strategy(strategy_id, user.id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strateji bulunamadı")
    return APIResponse(success=True, data=strategy.model_dump())


@router.post("/{strategy_id}/deactivate", response_model=APIResponse)
async def deactivate_strategy(
    strategy_id: UUID,
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Stratejiyi deaktifleştirir."""
    strategy = await service.deactivate_strategy(strategy_id, user.id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strateji bulunamadı")
    return APIResponse(success=True, data=strategy.model_dump())


@router.get("/{strategy_id}/signals", response_model=APIResponse)
async def get_strategy_signals(
    strategy_id: UUID,
    signal_type: str | None = Query(None, description="Sinyal tipi: buy, sell, hold"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Strateji sinyallerini listeler."""
    skip = (page - 1) * per_page
    result = await service.get_signals(
        strategy_id=strategy_id,
        user_id=user.id,
        signal_type=signal_type,
        skip=skip,
        limit=per_page,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Strateji bulunamadı")

    signals, total = result
    total_pages = (total + per_page - 1) // per_page

    return APIResponse(
        success=True,
        data=[s.model_dump() for s in signals],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{strategy_id}/performance", response_model=APIResponse)
async def get_strategy_performance(
    strategy_id: UUID,
    user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Strateji performans özetini döner."""
    performance = await service.get_performance(strategy_id, user.id)
    if not performance:
        raise HTTPException(status_code=404, detail="Strateji bulunamadı")
    return APIResponse(success=True, data=performance.model_dump())
