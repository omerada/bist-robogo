# Source: Doc 07 §12.2 pattern — Order/Trade repository
"""Emir ve işlem veritabanı erişim katmanı."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, Trade
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Order CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def get_by_user(
        self,
        user_id: UUID,
        status: str | None = None,
        symbol: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Order]:
        """Kullanıcının emirlerini filtreli listele."""
        stmt = select(Order).where(Order.user_id == user_id)

        if status:
            stmt = stmt.where(Order.status == status)
        if symbol:
            stmt = stmt.where(Order.symbol == symbol.upper())

        stmt = stmt.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Order).where(Order.user_id == user_id)
        if status:
            stmt = stmt.where(Order.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_active_orders(self, user_id: UUID) -> list[Order]:
        """Bekleyen / kısmi dolu emirler."""
        stmt = (
            select(Order)
            .where(
                Order.user_id == user_id,
                Order.status.in_(["pending", "submitted", "partial_fill"]),
            )
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_order(
        self,
        user_id: UUID,
        symbol: str,
        side: str,
        order_type: str,
        quantity: int,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: str = "day",
        is_paper: bool = True,
        strategy_id: UUID | None = None,
    ) -> Order:
        """Yeni emir oluştur."""
        order = Order(
            user_id=user_id,
            symbol=symbol.upper(),
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
            status="pending",
            filled_quantity=0,
            commission=0,
            is_paper=is_paper,
            strategy_id=strategy_id,
        )
        self.db.add(order)
        await self.db.flush()
        return order


class TradeRepository(BaseRepository[Trade]):
    """Trade CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(Trade, db)

    async def get_by_order(self, order_id: UUID) -> list[Trade]:
        stmt = select(Trade).where(Trade.order_id == order_id).order_by(Trade.executed_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: UUID,
        symbol: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Trade]:
        stmt = select(Trade).where(Trade.user_id == user_id)
        if symbol:
            stmt = stmt.where(Trade.symbol == symbol.upper())
        stmt = stmt.order_by(Trade.executed_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_trade(
        self,
        user_id: UUID,
        order_id: UUID,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        commission: float = 0,
        pnl: float | None = None,
        executed_at: datetime | None = None,
    ) -> Trade:
        """Yeni trade kaydı oluştur."""
        trade = Trade(
            user_id=user_id,
            order_id=order_id,
            symbol=symbol.upper(),
            side=side,
            quantity=quantity,
            price=price,
            commission=commission,
            pnl=pnl,
            executed_at=executed_at or datetime.utcnow(),
        )
        self.db.add(trade)
        await self.db.flush()
        return trade
