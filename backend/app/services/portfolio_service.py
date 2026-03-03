# Source: Doc 07 §12 — Service pattern — Portfolio
"""Portföy ve pozisyon iş mantığı katmanı."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.portfolio_repository import (
    PortfolioRepository,
    PositionRepository,
    SnapshotRepository,
)
from app.schemas.portfolio import PortfolioSummaryResponse, PositionResponse

logger = logging.getLogger(__name__)

INITIAL_CASH = 100_000.0


class PortfolioService:
    """Portföy ve pozisyon yönetimi iş mantığı."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.portfolio_repo = PortfolioRepository(db)
        self.position_repo = PositionRepository(db)
        self.snapshot_repo = SnapshotRepository(db)

    # ── Portföy ──

    async def get_summary(self, user_id: UUID) -> PortfolioSummaryResponse:
        """Portföy özet bilgisi döner."""
        portfolio = await self.portfolio_repo.get_or_create(user_id, INITIAL_CASH)
        open_count = await self.position_repo.count_open(user_id)

        # PnL yüzdeleri
        initial = INITIAL_CASH
        daily_pnl_pct = (float(portfolio.daily_pnl) / initial * 100) if initial else 0
        total_pnl_pct = (float(portfolio.total_pnl) / initial * 100) if initial else 0

        return PortfolioSummaryResponse(
            total_value=portfolio.total_value,
            cash_balance=portfolio.cash_balance,
            invested_value=portfolio.invested_value,
            daily_pnl=portfolio.daily_pnl,
            daily_pnl_pct=round(daily_pnl_pct, 2),
            total_pnl=portfolio.total_pnl,
            total_pnl_pct=round(total_pnl_pct, 2),
            open_positions=open_count,
        )

    # ── Pozisyonlar ──

    async def get_positions(self, user_id: UUID) -> list[PositionResponse]:
        """Kullanıcının açık pozisyonlarını döner."""
        positions = await self.position_repo.get_open_positions(user_id)

        result = []
        for p in positions:
            unrealized_pnl = None
            unrealized_pnl_pct = None

            if p.current_price and p.avg_entry_price:
                unrealized_pnl = (p.current_price - p.avg_entry_price) * p.quantity
                unrealized_pnl_pct = (
                    (p.current_price - p.avg_entry_price) / p.avg_entry_price * 100
                )

            result.append(
                PositionResponse(
                    id=p.id,
                    symbol=p.symbol,
                    side=p.side,
                    quantity=p.quantity,
                    avg_entry_price=p.avg_entry_price,
                    current_price=p.current_price,
                    unrealized_pnl=round(unrealized_pnl, 2) if unrealized_pnl else 0,
                    unrealized_pnl_pct=round(unrealized_pnl_pct, 2) if unrealized_pnl_pct else 0,
                    realized_pnl=p.realized_pnl,
                    stop_loss=p.stop_loss,
                    take_profit=p.take_profit,
                    opened_at=p.opened_at,
                )
            )
        return result

    # ── Snapshot ──

    async def get_history(self, user_id: UUID, limit: int = 30) -> list[dict]:
        """Portföy geçmişi (günlük snapshot'lar)."""
        snapshots = await self.snapshot_repo.get_by_user(user_id, limit=limit)
        return [
            {
                "date": s.snapshot_date.isoformat(),
                "total_value": float(s.total_value),
                "cash_balance": float(s.cash_balance),
                "invested_value": float(s.invested_value),
                "daily_pnl": float(s.daily_pnl) if s.daily_pnl else 0,
                "positions_count": s.positions_count or 0,
            }
            for s in reversed(snapshots)  # Kronolojik sıra
        ]
