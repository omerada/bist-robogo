# Source: Doc 07 §12.2 pattern — Risk repository
"""Risk kuralları ve olayları veritabanı erişim katmanı."""

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk import RiskEvent, RiskRule
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class RiskRuleRepository(BaseRepository[RiskRule]):
    """RiskRule CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(RiskRule, db)

    async def get_by_id(self, id: UUID) -> RiskRule | None:
        """Override: select tabanlı — session.get() async test uyumsuzluğunu önler."""
        result = await self.db.execute(
            select(RiskRule).where(RiskRule.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: UUID,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[RiskRule]:
        """Kullanıcının risk kurallarını listele."""
        stmt = select(RiskRule).where(RiskRule.user_id == user_id)
        if is_active is not None:
            stmt = stmt.where(RiskRule.is_active == is_active)
        stmt = stmt.order_by(RiskRule.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        is_active: bool | None = None,
    ) -> int:
        """Kullanıcının aktif kural sayısı."""
        stmt = (
            select(func.count())
            .select_from(RiskRule)
            .where(RiskRule.user_id == user_id)
        )
        if is_active is not None:
            stmt = stmt.where(RiskRule.is_active == is_active)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_by_type(
        self, user_id: UUID, rule_type: str
    ) -> RiskRule | None:
        """Belirli tipte kuralı getir."""
        stmt = (
            select(RiskRule)
            .where(RiskRule.user_id == user_id, RiskRule.rule_type == rule_type)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_rules(self, user_id: UUID) -> list[RiskRule]:
        """Aktif kuralları getir."""
        return await self.get_by_user(user_id, is_active=True)

    async def ensure_defaults(self, user_id: UUID) -> list[RiskRule]:
        """Kullanıcı için varsayılan kuralları oluştur (yoksa)."""
        existing = await self.get_by_user(user_id)
        if existing:
            return existing

        defaults = [
            {"rule_type": "max_position_count", "value": {"limit": 10}},
            {"rule_type": "max_position_size_pct", "value": {"limit": 20.0}},
            {"rule_type": "daily_loss_limit_pct", "value": {"limit": 5.0}},
            {"rule_type": "max_order_value", "value": {"limit": 50000.0}},
            {"rule_type": "stop_loss_required", "value": {"enabled": True, "default_pct": 5.0}},
            {"rule_type": "max_sector_exposure_pct", "value": {"limit": 40.0}},
            {"rule_type": "min_cash_reserve_pct", "value": {"limit": 10.0}},
            {"rule_type": "max_daily_trades", "value": {"limit": 20}},
            {"rule_type": "max_leverage", "value": {"limit": 1.0}},
        ]
        rules = []
        for d in defaults:
            rule = await self.create(user_id=user_id, **d)
            rules.append(rule)
        return rules


class RiskEventRepository(BaseRepository[RiskEvent]):
    """RiskEvent CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(RiskEvent, db)

    async def get_by_user(
        self,
        user_id: UUID,
        event_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[RiskEvent]:
        """Kullanıcının risk olaylarını listele."""
        stmt = select(RiskEvent).where(RiskEvent.user_id == user_id)
        if event_type:
            stmt = stmt.where(RiskEvent.event_type == event_type)
        stmt = stmt.order_by(RiskEvent.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        event_type: str | None = None,
    ) -> int:
        """Kullanıcının olay sayısı."""
        stmt = (
            select(func.count())
            .select_from(RiskEvent)
            .where(RiskEvent.user_id == user_id)
        )
        if event_type:
            stmt = stmt.where(RiskEvent.event_type == event_type)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_recent(self, user_id: UUID, limit: int = 10) -> list[RiskEvent]:
        """Son olayları getir."""
        return await self.get_by_user(user_id, limit=limit)
