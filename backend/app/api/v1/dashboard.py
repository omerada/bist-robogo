"""Dashboard özet endpoint'leri — tek çağrıda tüm kritik verileri döner."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.order import Order
from app.models.strategy import Strategy, Signal
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter()


def get_portfolio_service(db: AsyncSession = Depends(get_db)) -> PortfolioService:
    return PortfolioService(db)


@router.get("/summary", response_model=APIResponse)
async def get_dashboard_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """Dashboard ana özeti — portföy, strateji, sinyal, emir bilgileri.

    Frontend dashboard'ı bu tek endpoint ile doldurur.
    """
    # 1) Portföy özeti
    portfolio = await portfolio_service.get_summary(user.id)

    # 2) Aktif strateji sayısı
    active_strategies_result = await db.execute(
        select(func.count())
        .select_from(Strategy)
        .where(Strategy.user_id == user.id, Strategy.is_active.is_(True))
    )
    active_strategy_count = active_strategies_result.scalar() or 0

    # 3) Son 5 sinyal (strateji üzerinden user_id filtresi)
    recent_signals_result = await db.execute(
        select(Signal)
        .join(Strategy, Signal.strategy_id == Strategy.id)
        .where(Strategy.user_id == user.id)
        .order_by(Signal.created_at.desc())
        .limit(5)
    )
    signals = recent_signals_result.scalars().all()
    recent_signals = [
        {
            "id": str(s.id),
            "symbol": s.symbol,
            "signal_type": s.signal_type,
            "confidence": float(s.confidence) if s.confidence else 0,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in signals
    ]

    # 4) Son 5 emir
    recent_orders_result = await db.execute(
        select(Order)
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
        .limit(5)
    )
    orders = recent_orders_result.scalars().all()
    recent_orders = [
        {
            "id": str(o.id),
            "symbol": o.symbol,
            "side": o.side,
            "order_type": o.order_type,
            "quantity": o.quantity,
            "price": float(o.price) if o.price else None,
            "status": o.status,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]

    # 5) Portföy geçmişi (equity curve için son 30 gün)
    history = await portfolio_service.get_history(user.id, limit=30)

    return APIResponse(
        success=True,
        data={
            "portfolio": portfolio.model_dump(),
            "active_strategies": active_strategy_count,
            "recent_signals": recent_signals,
            "recent_orders": recent_orders,
            "equity_history": history,
        },
    )
