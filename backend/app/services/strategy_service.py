# Source: Doc 02 §2.5 — Strategy service
"""Strateji iş mantığı katmanı — CRUD, aktivasyon, sinyal yönetimi."""

import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategy import Signal, Strategy
from app.repositories.strategy_repository import SignalRepository, StrategyRepository
from app.schemas.strategy import (
    SignalResponse,
    StrategyCreateRequest,
    StrategyPerformanceResponse,
    StrategyResponse,
    StrategyUpdateRequest,
)

logger = logging.getLogger(__name__)


class StrategyService:
    """Strateji iş mantığı — CRUD, aktivasyon, sinyal yönetimi."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.strategy_repo = StrategyRepository(db)
        self.signal_repo = SignalRepository(db)

    # ── Strateji CRUD ──

    async def list_strategies(
        self,
        user_id: UUID,
        strategy_type: str | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[StrategyResponse], int]:
        """Kullanıcının stratejilerini listele."""
        strategies = await self.strategy_repo.get_by_user(
            user_id=user_id,
            strategy_type=strategy_type,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )
        total = await self.strategy_repo.count_by_user(
            user_id=user_id,
            strategy_type=strategy_type,
            is_active=is_active,
        )
        return [StrategyResponse.model_validate(s) for s in strategies], total

    async def create_strategy(
        self,
        user_id: UUID,
        data: StrategyCreateRequest,
    ) -> StrategyResponse:
        """Yeni strateji oluştur."""
        strategy = await self.strategy_repo.create(
            user_id=user_id,
            name=data.name,
            description=data.description,
            strategy_type=data.strategy_type,
            parameters=data.parameters,
            symbols=data.symbols,
            index_filter=data.index_filter,
            timeframe=data.timeframe,
            risk_params=data.risk_params,
            is_active=False,
            is_paper=True,
        )
        await self.db.commit()
        await self.db.refresh(strategy)
        logger.info(f"Strateji oluşturuldu: {strategy.name} (id={strategy.id})")
        return StrategyResponse.model_validate(strategy)

    async def get_strategy(
        self,
        strategy_id: UUID,
        user_id: UUID,
    ) -> StrategyResponse | None:
        """Strateji detayı."""
        strategy = await self.strategy_repo.get_user_strategy(strategy_id, user_id)
        if not strategy:
            return None
        return StrategyResponse.model_validate(strategy)

    async def update_strategy(
        self,
        strategy_id: UUID,
        user_id: UUID,
        data: StrategyUpdateRequest,
    ) -> StrategyResponse | None:
        """Strateji güncelle."""
        strategy = await self.strategy_repo.get_user_strategy(strategy_id, user_id)
        if not strategy:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            strategy = await self.strategy_repo.update(strategy, **update_data)
            await self.db.commit()
            await self.db.refresh(strategy)
            logger.info(f"Strateji güncellendi: {strategy.name} (id={strategy.id})")

        return StrategyResponse.model_validate(strategy)

    async def delete_strategy(
        self,
        strategy_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Strateji sil."""
        strategy = await self.strategy_repo.get_user_strategy(strategy_id, user_id)
        if not strategy:
            return False

        await self.strategy_repo.delete(strategy)
        await self.db.commit()
        logger.info(f"Strateji silindi: {strategy.name} (id={strategy_id})")
        return True

    # ── Aktivasyon ──

    async def activate_strategy(
        self,
        strategy_id: UUID,
        user_id: UUID,
    ) -> StrategyResponse | None:
        """Stratejiyi aktifleştir."""
        strategy = await self.strategy_repo.get_user_strategy(strategy_id, user_id)
        if not strategy:
            return None

        strategy = await self.strategy_repo.update(strategy, is_active=True)
        await self.db.commit()
        await self.db.refresh(strategy)
        logger.info(f"Strateji aktifleştirildi: {strategy.name}")
        return StrategyResponse.model_validate(strategy)

    async def deactivate_strategy(
        self,
        strategy_id: UUID,
        user_id: UUID,
    ) -> StrategyResponse | None:
        """Stratejiyi deaktifleştir."""
        strategy = await self.strategy_repo.get_user_strategy(strategy_id, user_id)
        if not strategy:
            return None

        strategy = await self.strategy_repo.update(strategy, is_active=False)
        await self.db.commit()
        await self.db.refresh(strategy)
        logger.info(f"Strateji deaktifleştirildi: {strategy.name}")
        return StrategyResponse.model_validate(strategy)

    # ── Sinyaller ──

    async def get_signals(
        self,
        strategy_id: UUID,
        user_id: UUID,
        signal_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[SignalResponse], int] | None:
        """Strateji sinyallerini listele."""
        strategy = await self.strategy_repo.get_user_strategy(strategy_id, user_id)
        if not strategy:
            return None

        signals = await self.signal_repo.get_by_strategy(
            strategy_id=strategy_id,
            signal_type=signal_type,
            skip=skip,
            limit=limit,
        )
        total = await self.signal_repo.count_by_strategy(strategy_id)
        return [SignalResponse.model_validate(s) for s in signals], total

    # ── Performans ──

    async def get_performance(
        self,
        strategy_id: UUID,
        user_id: UUID,
    ) -> StrategyPerformanceResponse | None:
        """Strateji performans özeti."""
        strategy = await self.strategy_repo.get_user_strategy(strategy_id, user_id)
        if not strategy:
            return None

        signals = await self.signal_repo.get_by_strategy(strategy_id, limit=1000)
        total_signals = len(signals)
        executed = [s for s in signals if s.is_executed]
        buys = [s for s in signals if s.signal_type == "buy"]
        sells = [s for s in signals if s.signal_type == "sell"]

        avg_confidence = (
            sum(float(s.confidence) for s in signals) / total_signals
            if total_signals > 0
            else 0.0
        )

        last_signal_at = signals[0].created_at if signals else None

        return StrategyPerformanceResponse(
            strategy_id=strategy_id,
            total_signals=total_signals,
            executed_signals=len(executed),
            buy_signals=len(buys),
            sell_signals=len(sells),
            win_rate=0.0,  # Backtest modülünde hesaplanacak
            total_pnl=Decimal("0"),  # Backtest modülünde hesaplanacak
            avg_confidence=round(avg_confidence, 4),
            last_signal_at=last_signal_at,
        )
