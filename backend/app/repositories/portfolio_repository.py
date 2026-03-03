# Source: Doc 07 §12.2 pattern — Portfolio/Position repository
"""Portföy ve pozisyon veritabanı erişim katmanı."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio, PortfolioSnapshot, Position
from app.repositories.base import BaseRepository


class PositionRepository(BaseRepository[Position]):
    """Position CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(Position, db)

    async def get_by_user_symbol(self, user_id: UUID, symbol: str) -> Position | None:
        """Kullanıcının belirli semboldeki pozisyonunu getir."""
        stmt = select(Position).where(
            Position.user_id == user_id,
            Position.symbol == symbol.upper(),
            Position.closed_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_open_positions(self, user_id: UUID) -> list[Position]:
        """Kullanıcının açık pozisyonlarını listele."""
        stmt = (
            select(Position)
            .where(Position.user_id == user_id, Position.closed_at.is_(None))
            .order_by(Position.opened_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_open(self, user_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Position)
            .where(Position.user_id == user_id, Position.closed_at.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()


class PortfolioRepository(BaseRepository[Portfolio]):
    """Portfolio CRUD."""

    def __init__(self, db: AsyncSession):
        super().__init__(Portfolio, db)

    async def get_by_user(self, user_id: UUID) -> Portfolio | None:
        stmt = select(Portfolio).where(Portfolio.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: UUID, initial_cash: float = 100000.0) -> Portfolio:
        """Portföy yoksa oluştur, varsa mevcut olanı döndür."""
        portfolio = await self.get_by_user(user_id)
        if portfolio:
            return portfolio

        portfolio = Portfolio(
            user_id=user_id,
            total_value=initial_cash,
            cash_balance=initial_cash,
            invested_value=0,
            daily_pnl=0,
            total_pnl=0,
        )
        self.db.add(portfolio)
        await self.db.flush()
        return portfolio


class SnapshotRepository(BaseRepository[PortfolioSnapshot]):
    """PortfolioSnapshot CRUD."""

    def __init__(self, db: AsyncSession):
        super().__init__(PortfolioSnapshot, db)

    async def get_by_user(
        self,
        user_id: UUID,
        limit: int = 30,
    ) -> list[PortfolioSnapshot]:
        stmt = (
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.user_id == user_id)
            .order_by(PortfolioSnapshot.snapshot_date.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
