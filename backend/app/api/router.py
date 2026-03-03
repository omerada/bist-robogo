"""Tüm API v1 router'larını birleştirir."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.market import router as market_router
from app.api.v1.orders import router as orders_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.strategies import router as strategies_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.risk import router as risk_router
from app.api.v1.trends import router as trends_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.ai import router as ai_router
from app.api.v1.brokers import router as brokers_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(strategies_router, prefix="/strategies", tags=["strategies"])
api_router.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
api_router.include_router(risk_router, prefix="/risk", tags=["risk"])
api_router.include_router(trends_router, prefix="/analysis", tags=["trends"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(brokers_router, prefix="/brokers", tags=["brokers"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
