# Source: Doc 07 §12 — Service pattern — Trading
"""Emir oluşturma, doğrulama ve broker iletişimi iş mantığı."""

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.brokers.base import BrokerOrderStatus
from app.brokers.factory import get_broker
from app.models.order import Order
from app.repositories.order_repository import OrderRepository, TradeRepository
from app.repositories.portfolio_repository import PortfolioRepository, PositionRepository
from app.schemas.order import OrderCreateRequest, OrderResponse

logger = logging.getLogger(__name__)

# Paper trading başlangıç bakiyesi (₺)
INITIAL_CASH = 100_000.0

# Sabit komisyon oranı (%0.2)
COMMISSION_RATE = 0.002


class TradingService:
    """Emir oluşturma, validasyon, broker gönderim ve pozisyon güncelleme."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.trade_repo = TradeRepository(db)
        self.position_repo = PositionRepository(db)
        self.portfolio_repo = PortfolioRepository(db)

    # ── Emir İşlemleri ──

    async def create_order(self, user_id: UUID, req: OrderCreateRequest) -> Order:
        """Emir oluştur → doğrula → broker'a gönder → pozisyon güncelle."""

        # 1. Portföy kontrol (yoksa oluştur)
        portfolio = await self.portfolio_repo.get_or_create(user_id, INITIAL_CASH)

        # 2. Ön doğrulama
        await self._validate_order(user_id, portfolio, req)

        # 3. DB'ye emir kaydı
        order = await self.order_repo.create_order(
            user_id=user_id,
            symbol=req.symbol,
            side=req.side.value,
            order_type=req.order_type.value,
            quantity=req.quantity,
            price=float(req.price) if req.price else None,
            time_in_force=req.time_in_force.value,
            is_paper=True,  # Faz 1: sadece paper
            strategy_id=req.strategy_id,
        )

        # 4. Broker'a gönder (Paper)
        try:
            broker = get_broker("paper")
            result = await broker.submit_order(
                symbol=req.symbol,
                side=req.side.value,
                order_type=req.order_type.value,
                quantity=req.quantity,
                price=Decimal(str(req.price)) if req.price else None,
            )

            order.broker_order_id = result.broker_order_id
            order.status = result.status.value

            if result.status == BrokerOrderStatus.FILLED:
                order.filled_quantity = result.filled_quantity
                order.filled_price = float(result.filled_price) if result.filled_price else None
                order.commission = float(result.filled_price or 0) * result.filled_quantity * COMMISSION_RATE

                # Trade kaydı oluştur
                await self.trade_repo.create_trade(
                    user_id=user_id,
                    order_id=order.id,
                    symbol=req.symbol,
                    side=req.side.value,
                    quantity=result.filled_quantity,
                    price=float(result.filled_price) if result.filled_price else 0,
                    commission=order.commission,
                    executed_at=datetime.utcnow(),
                )

                # Pozisyon güncelle
                await self._update_position(
                    user_id=user_id,
                    symbol=req.symbol,
                    side=req.side.value,
                    quantity=result.filled_quantity,
                    price=float(result.filled_price) if result.filled_price else 0,
                )

                # Portföy güncelle
                await self._update_portfolio(user_id, portfolio, order)

        except ValueError as e:
            # Fiyat bulunamadı vb.
            order.status = "rejected"
            order.rejection_reason = str(e)
            logger.warning("Order rejected: %s", e)

        await self.db.flush()
        return order

    async def get_orders(
        self,
        user_id: UUID,
        status: str | None = None,
        symbol: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Order], int]:
        """Kullanıcının emirlerini listele."""
        skip = (page - 1) * per_page
        orders = await self.order_repo.get_by_user(user_id, status=status, symbol=symbol, skip=skip, limit=per_page)
        total = await self.order_repo.count_by_user(user_id, status=status)
        return orders, total

    async def get_order(self, user_id: UUID, order_id: UUID) -> Order | None:
        """Tek emir detayı."""
        order = await self.order_repo.get_by_id(order_id)
        if order and order.user_id == user_id:
            return order
        return None

    async def cancel_order(self, user_id: UUID, order_id: UUID) -> Order | None:
        """Emir iptal et."""
        order = await self.order_repo.get_by_id(order_id)
        if not order or order.user_id != user_id:
            return None

        if order.status not in ("pending", "submitted"):
            return None

        order.status = "cancelled"
        await self.db.flush()

        logger.info("Order cancelled: %s", order_id)
        return order

    # ── Private Helpers ──

    async def _validate_order(self, user_id: UUID, portfolio, req: OrderCreateRequest) -> None:
        """Emir ön doğrulama: bakiye, miktar, sembol kontrolü."""
        from decimal import Decimal as D

        if req.quantity <= 0:
            raise ValueError("Miktar 0'dan büyük olmalı")

        # Alış emrinde yeterli bakiye var mı? (tahmini kontrol)
        if req.side.value == "buy":
            estimated_cost = D(str(req.quantity)) * D(str(req.price or 1000))
            cash = D(str(portfolio.cash_balance))
            if cash < estimated_cost:
                raise ValueError(
                    f"Yetersiz bakiye: ₺{cash:.2f} mevcut, "
                    f"₺{estimated_cost:.2f} gerekli"
                )

        # Satış emrinde yeterli pozisyon var mı?
        if req.side.value == "sell":
            position = await self.position_repo.get_by_user_symbol(user_id, req.symbol)
            if not position or position.quantity < req.quantity:
                available = position.quantity if position else 0
                raise ValueError(
                    f"Yetersiz pozisyon: {available} lot mevcut, {req.quantity} lot gerekli"
                )

    async def _update_position(
        self,
        user_id: UUID,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
    ) -> None:
        """Pozisyon güncelle veya oluştur."""
        position = await self.position_repo.get_by_user_symbol(user_id, symbol)

        from decimal import Decimal as D

        d_price = D(str(price))
        d_qty = D(str(quantity))

        if side == "buy":
            if position:
                # Mevcut pozisyona ekle — ortalama maliyet güncelle
                total_cost = D(str(position.avg_entry_price)) * D(str(position.quantity)) + d_price * d_qty
                new_qty = D(str(position.quantity)) + d_qty
                position.avg_entry_price = total_cost / new_qty
                position.quantity = new_qty
                position.current_price = d_price
            else:
                # Yeni pozisyon
                position = await self.position_repo.create(
                    user_id=user_id,
                    symbol=symbol.upper(),
                    side="long",
                    quantity=quantity,
                    avg_entry_price=price,
                    current_price=price,
                    realized_pnl=0,
                )
        elif side == "sell":
            if position:
                # PnL hesapla
                pnl = (d_price - D(str(position.avg_entry_price))) * d_qty
                position.realized_pnl = D(str(position.realized_pnl or 0)) + pnl
                position.quantity = D(str(position.quantity)) - d_qty
                position.current_price = d_price

                if position.quantity <= 0:
                    # Pozisyon kapatıldı
                    position.quantity = D("0")
                    position.closed_at = datetime.utcnow()

        await self.db.flush()

    async def _update_portfolio(self, user_id: UUID, portfolio, order: Order) -> None:
        """Portföy bakiye ve değer güncelleme."""
        from decimal import Decimal as D

        trade_value = D(str(order.filled_price or 0)) * D(str(order.filled_quantity or 0))
        commission = D(str(order.commission or 0))

        if order.side == "buy":
            portfolio.cash_balance = D(str(portfolio.cash_balance)) - trade_value - commission
            portfolio.invested_value = D(str(portfolio.invested_value)) + trade_value
        elif order.side == "sell":
            portfolio.cash_balance = D(str(portfolio.cash_balance)) + trade_value - commission
            portfolio.invested_value = max(D("0"), D(str(portfolio.invested_value)) - trade_value)

        portfolio.total_value = D(str(portfolio.cash_balance)) + D(str(portfolio.invested_value))
        await self.db.flush()
