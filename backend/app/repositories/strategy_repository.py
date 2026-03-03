# Source: Doc 07 §12.2 pattern — Strategy repository
"""Strateji ve sinyal veritabanı erişim katmanı."""

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.strategy import Signal, Strategy
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class StrategyRepository(BaseRepository[Strategy]):
    """Strategy CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(Strategy, db)

    async def get_by_user(
        self,
        user_id: UUID,
        strategy_type: str | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Strategy]:
        """Kullanıcının stratejilerini listele."""
        stmt = select(Strategy).where(Strategy.user_id == user_id)

        if strategy_type:
            stmt = stmt.where(Strategy.strategy_type == strategy_type)
        if is_active is not None:
            stmt = stmt.where(Strategy.is_active == is_active)

        stmt = stmt.order_by(Strategy.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        strategy_type: str | None = None,
        is_active: bool | None = None,
    ) -> int:
        """Kullanıcının strateji sayısı."""
        stmt = select(func.count()).select_from(Strategy).where(Strategy.user_id == user_id)
        if strategy_type:
            stmt = stmt.where(Strategy.strategy_type == strategy_type)
        if is_active is not None:
            stmt = stmt.where(Strategy.is_active == is_active)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_with_signals(self, strategy_id: UUID) -> Strategy | None:
        """Strateji + sinyallerini eager load et."""
        stmt = (
            select(Strategy)
            .where(Strategy.id == strategy_id)
            .options(selectinload(Strategy.signals))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_strategy(self, strategy_id: UUID, user_id: UUID) -> Strategy | None:
        """Kullanıcıya ait stratejiyi getir."""
        stmt = select(Strategy).where(Strategy.id == strategy_id, Strategy.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class SignalRepository(BaseRepository[Signal]):
    """Signal CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(Signal, db)

    async def get_by_strategy(
        self,
        strategy_id: UUID,
        signal_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Signal]:
        """Stratejinin sinyallerini listele."""
        stmt = select(Signal).where(Signal.strategy_id == strategy_id)

        if signal_type:
            stmt = stmt.where(Signal.signal_type == signal_type)

        stmt = stmt.order_by(Signal.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_strategy(self, strategy_id: UUID) -> int:
        stmt = select(func.count()).select_from(Signal).where(Signal.strategy_id == strategy_id)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_latest_signal(self, strategy_id: UUID, symbol: str) -> Signal | None:
        """Strateji + sembol için en son sinyal."""
        stmt = (
            select(Signal)
            .where(Signal.strategy_id == strategy_id, Signal.symbol == symbol)
            .order_by(Signal.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
