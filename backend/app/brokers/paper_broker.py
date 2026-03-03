"""Paper trading broker — gerçek emir göndermeden simülasyon yapar."""

from decimal import Decimal
from uuid import uuid4

import structlog

from app.brokers.base import (
    AbstractBroker,
    BrokerOrderResult,
    BrokerOrderStatus,
    BrokerQuote,
)
from app.core.redis_client import redis_manager

logger = structlog.get_logger()


class PaperBroker(AbstractBroker):
    """Paper trading simülasyonu.

    - Tüm emirler anında 'filled' olur.
    - Fiyat Redis cache'ten alınır (gerçek piyasa fiyatı).
    - Slippage simülasyonu: mevcut fiyata %0.05 eklenir/çıkarılır.
    """

    SLIPPAGE_RATE = Decimal("0.0005")  # %0.05

    async def connect(self) -> bool:
        logger.info("paper_broker_connected")
        return True

    async def disconnect(self) -> None:
        logger.info("paper_broker_disconnected")

    async def submit_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: int,
        price: Decimal | None = None,
        stop_price: Decimal | None = None,
    ) -> BrokerOrderResult:
        """Paper order — anında fill."""

        # Redis'ten gerçek fiyatı al
        quote = await self.get_quote(symbol)
        fill_price = quote.price

        # Slippage uygula
        if side == "buy":
            fill_price = fill_price * (1 + self.SLIPPAGE_RATE)
        else:
            fill_price = fill_price * (1 - self.SLIPPAGE_RATE)

        # Limit order ise fiyat kontrolü
        if order_type == "limit" and price:
            if side == "buy" and quote.price > price:
                return BrokerOrderResult(
                    broker_order_id=str(uuid4()),
                    status=BrokerOrderStatus.SUBMITTED,
                    filled_quantity=0,
                    filled_price=None,
                    message="Limit fiyat bekleniyor",
                )
            if side == "sell" and quote.price < price:
                return BrokerOrderResult(
                    broker_order_id=str(uuid4()),
                    status=BrokerOrderStatus.SUBMITTED,
                    filled_quantity=0,
                    filled_price=None,
                    message="Limit fiyat bekleniyor",
                )

        return BrokerOrderResult(
            broker_order_id=f"PAPER-{uuid4().hex[:12].upper()}",
            status=BrokerOrderStatus.FILLED,
            filled_quantity=quantity,
            filled_price=fill_price,
            message="Paper trade executed",
        )

    async def cancel_order(self, broker_order_id: str) -> BrokerOrderResult:
        return BrokerOrderResult(
            broker_order_id=broker_order_id,
            status=BrokerOrderStatus.CANCELLED,
            filled_quantity=0,
            filled_price=None,
            message="Paper order cancelled",
        )

    async def get_order_status(self, broker_order_id: str) -> BrokerOrderResult:
        return BrokerOrderResult(
            broker_order_id=broker_order_id,
            status=BrokerOrderStatus.FILLED,
            filled_quantity=0,
            filled_price=None,
        )

    async def get_quote(self, symbol: str) -> BrokerQuote:
        """Redis cache'ten fiyat bilgisi al."""
        import json

        cached = await redis_manager.get_cached(f"market:quote:{symbol}")
        if cached:
            data = json.loads(cached)
            return BrokerQuote(
                symbol=symbol,
                price=Decimal(str(data["price"])),
                bid=Decimal(str(data.get("bid", data["price"]))),
                ask=Decimal(str(data.get("ask", data["price"]))),
                volume=data.get("volume", 0),
            )
        raise ValueError(f"Fiyat bilgisi bulunamadı: {symbol}")

    async def get_positions(self) -> list[dict]:
        return []
