# Source: Doc 02 §2.3 + Doc 03 §3.4 — Order endpoints
"""Emir endpoint'leri."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse, PaginationMeta
from app.schemas.order import OrderCreateRequest, OrderResponse
from app.services.trading_service import TradingService

router = APIRouter()


def get_trading_service(db: AsyncSession = Depends(get_db)) -> TradingService:
    return TradingService(db)


@router.get("/", response_model=APIResponse)
async def list_orders(
    status: str | None = Query(None, description="Emir durumu filtresi"),
    symbol: str | None = Query(None, description="Sembol filtresi"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    service: TradingService = Depends(get_trading_service),
):
    """Kullanıcının emirlerini listeler."""
    orders, total = await service.get_orders(
        user_id=user.id,
        status=status,
        symbol=symbol,
        page=page,
        per_page=per_page,
    )
    total_pages = (total + per_page - 1) // per_page

    return APIResponse(
        success=True,
        data=[OrderResponse.model_validate(o).model_dump() for o in orders],
        meta=PaginationMeta(page=page, per_page=per_page, total=total, total_pages=total_pages),
    )


@router.post("/", response_model=APIResponse, status_code=201)
async def create_order(
    req: OrderCreateRequest,
    user: User = Depends(get_current_user),
    service: TradingService = Depends(get_trading_service),
):
    """Yeni emir oluşturur (Paper Trading)."""
    try:
        order = await service.create_order(user_id=user.id, req=req)
        await service.db.commit()
        await service.db.refresh(order)
        return APIResponse(
            success=True,
            data=OrderResponse.model_validate(order).model_dump(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=APIResponse)
async def get_order(
    order_id: UUID,
    user: User = Depends(get_current_user),
    service: TradingService = Depends(get_trading_service),
):
    """Emir detayını döner."""
    order = await service.get_order(user.id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Emir bulunamadı")
    return APIResponse(
        success=True,
        data=OrderResponse.model_validate(order).model_dump(),
    )


@router.delete("/{order_id}", response_model=APIResponse)
async def cancel_order(
    order_id: UUID,
    user: User = Depends(get_current_user),
    service: TradingService = Depends(get_trading_service),
):
    """Emir iptal eder."""
    order = await service.cancel_order(user.id, order_id)
    if not order:
        raise HTTPException(status_code=400, detail="Emir iptal edilemedi (bulunamadı veya zaten işlenmiş)")
    await service.db.commit()
    await service.db.refresh(order)
    return APIResponse(
        success=True,
        data=OrderResponse.model_validate(order).model_dump(),
    )
