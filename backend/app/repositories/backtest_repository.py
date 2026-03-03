# Source: Doc 07 §12.2 pattern — Backtest repository
"""Backtest veritabanı erişim katmanı."""

import logging
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.backtest import BacktestRun, BacktestTrade
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class BacktestRunRepository(BaseRepository[BacktestRun]):
    """BacktestRun CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(BacktestRun, db)

    async def get_by_user(
        self,
        user_id: UUID,
        status: str | None = None,
        strategy_id: UUID | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[BacktestRun]:
        """Kullanıcının backtest'lerini listele."""
        stmt = select(BacktestRun).where(BacktestRun.user_id == user_id)
        if status:
            stmt = stmt.where(BacktestRun.status == status)
        if strategy_id:
            stmt = stmt.where(BacktestRun.strategy_id == strategy_id)
        stmt = stmt.order_by(BacktestRun.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        status: str | None = None,
        strategy_id: UUID | None = None,
    ) -> int:
        """Kullanıcının backtest sayısını döndür."""
        stmt = select(func.count()).select_from(BacktestRun).where(BacktestRun.user_id == user_id)
        if status:
            stmt = stmt.where(BacktestRun.status == status)
        if strategy_id:
            stmt = stmt.where(BacktestRun.strategy_id == strategy_id)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_with_trades(self, backtest_id: UUID) -> BacktestRun | None:
        """Backtest ve trade'lerini birlikte getir."""
        stmt = (
            select(BacktestRun)
            .options(selectinload(BacktestRun.trades))
            .where(BacktestRun.id == backtest_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        backtest_id: UUID,
        status: str,
        **kwargs,
    ) -> None:
        """Backtest durumunu ve sonuçlarını raw UPDATE ile güncelle.

        Raw SQL update kullanılır — ORM nesnesine dokunmak
        async context'te MissingGreenlet lazy-load hatası verir.
        """
        values = {"status": status, **kwargs}
        stmt = (
            update(BacktestRun)
            .where(BacktestRun.id == backtest_id)
            .values(**values)
        )
        await self.db.execute(stmt)


class BacktestTradeRepository(BaseRepository[BacktestTrade]):
    """BacktestTrade CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(BacktestTrade, db)

    async def get_by_backtest(
        self,
        backtest_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BacktestTrade]:
        """Backtest'e ait trade'leri listele."""
        stmt = (
            select(BacktestTrade)
            .where(BacktestTrade.backtest_id == backtest_id)
            .order_by(BacktestTrade.entry_date)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_backtest(self, backtest_id: UUID) -> int:
        """Backtest'e ait trade sayısını döndür."""
        stmt = (
            select(func.count())
            .select_from(BacktestTrade)
            .where(BacktestTrade.backtest_id == backtest_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def bulk_create(self, trades: list[dict]) -> list[BacktestTrade]:
        """Toplu trade oluştur."""
        instances = [BacktestTrade(**t) for t in trades]
        self.db.add_all(instances)
        await self.db.flush()
        return instances
