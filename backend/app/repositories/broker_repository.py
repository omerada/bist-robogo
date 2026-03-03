"""Broker bağlantı veri erişim katmanı."""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broker import BrokerConnection
from app.repositories.base import BaseRepository


class BrokerRepository(BaseRepository[BrokerConnection]):
    """BrokerConnection modeli için özelleştirilmiş repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(BrokerConnection, db)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[BrokerConnection]:
        """Kullanıcının broker bağlantılarını listeler."""
        stmt = (
            select(BrokerConnection)
            .where(BrokerConnection.user_id == user_id)
            .order_by(BrokerConnection.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(self, user_id: UUID) -> int:
        """Kullanıcının toplam bağlantı sayısını döner."""
        stmt = (
            select(func.count())
            .select_from(BrokerConnection)
            .where(BrokerConnection.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_user_connection(
        self,
        user_id: UUID,
        connection_id: UUID,
    ) -> BrokerConnection | None:
        """Kullanıcının belirli bir bağlantısını getirir."""
        stmt = (
            select(BrokerConnection)
            .where(
                BrokerConnection.id == connection_id,
                BrokerConnection.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_broker(
        self,
        user_id: UUID,
        broker_name: str,
    ) -> BrokerConnection | None:
        """Kullanıcının belirli bir broker'daki aktif bağlantısını getirir."""
        stmt = (
            select(BrokerConnection)
            .where(
                BrokerConnection.user_id == user_id,
                BrokerConnection.broker_name == broker_name,
                BrokerConnection.is_active.is_(True),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_all_for_broker(
        self,
        user_id: UUID,
        broker_name: str,
    ) -> int:
        """Kullanıcının belirli bir broker'daki tüm bağlantılarını deaktif eder."""
        from sqlalchemy import update

        stmt = (
            update(BrokerConnection)
            .where(
                BrokerConnection.user_id == user_id,
                BrokerConnection.broker_name == broker_name,
            )
            .values(is_active=False)
        )
        result = await self.db.execute(stmt)
        return result.rowcount
