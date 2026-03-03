# Source: Doc 02 §2.7 — Backtest endpoints
"""Backtest endpoint'leri — çalıştır, listele, detay, trade listesi, equity curve."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.backtest import (
    BacktestDetailResponse,
    BacktestResultResponse,
    BacktestRunRequest,
    BacktestTradeResponse,
)
from app.schemas.common import APIResponse, PaginationMeta
from app.services.backtest_service import BacktestService

router = APIRouter()


@router.post("/run", response_model=APIResponse[BacktestResultResponse], status_code=201)
async def run_backtest(
    body: BacktestRunRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Yeni backtest oluştur ve çalıştır.

    1. Backtest kaydı pending olarak oluşturulur
    2. Simülasyon çalıştırılır
    3. Sonuçlar döner
    """
    service = BacktestService(db)
    try:
        # Önce kayıt oluştur
        backtest = await service.create_backtest(user_id=user.id, data=body)
        # Senkron çalıştır (küçük veri setleri için)
        result = await service.run_backtest(backtest.id)
        return APIResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=APIResponse[list[BacktestResultResponse]])
async def list_backtests(
    status: str | None = Query(None, description="pending|running|completed|failed"),
    strategy_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Kullanıcının backtest sonuçlarını listeler."""
    service = BacktestService(db)
    skip = (page - 1) * per_page
    backtests, total = await service.list_backtests(
        user_id=user.id,
        status=status,
        strategy_id=strategy_id,
        skip=skip,
        limit=per_page,
    )
    return APIResponse(
        success=True,
        data=backtests,
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=(total + per_page - 1) // per_page,
        ),
    )


@router.get("/{backtest_id}", response_model=APIResponse[BacktestResultResponse])
async def get_backtest(
    backtest_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Backtest sonuç özetini döner."""
    service = BacktestService(db)
    result = await service.get_backtest(backtest_id)
    if not result:
        raise HTTPException(status_code=404, detail="Backtest bulunamadı")
    return APIResponse(success=True, data=result)


@router.get(
    "/{backtest_id}/detail",
    response_model=APIResponse[BacktestDetailResponse],
)
async def get_backtest_detail(
    backtest_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Backtest detayını trade listesi ile birlikte döner."""
    service = BacktestService(db)
    result = await service.get_backtest_detail(backtest_id)
    if not result:
        raise HTTPException(status_code=404, detail="Backtest bulunamadı")
    return APIResponse(success=True, data=result)


@router.get(
    "/{backtest_id}/trades",
    response_model=APIResponse[list[BacktestTradeResponse]],
)
async def get_backtest_trades(
    backtest_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Backtest trade listesini döner."""
    service = BacktestService(db)
    skip = (page - 1) * per_page
    trades, total = await service.get_backtest_trades(
        backtest_id=backtest_id, skip=skip, limit=per_page
    )
    return APIResponse(
        success=True,
        data=trades,
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=(total + per_page - 1) // per_page,
        ),
    )


@router.get("/{backtest_id}/equity-curve", response_model=APIResponse[dict])
async def get_equity_curve(
    backtest_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Backtest equity curve verisini döner."""
    service = BacktestService(db)
    curve = await service.get_equity_curve(backtest_id)
    if curve is None:
        raise HTTPException(status_code=404, detail="Backtest bulunamadı")
    return APIResponse(success=True, data=curve)


@router.delete("/{backtest_id}", response_model=APIResponse)
async def delete_backtest(
    backtest_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Backtest'i siler."""
    service = BacktestService(db)
    try:
        deleted = await service.delete_backtest(backtest_id, user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Backtest bulunamadı")
        return APIResponse(success=True, data=None)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

