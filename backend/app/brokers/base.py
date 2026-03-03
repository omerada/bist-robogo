"""Broker adapter abstract base class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class BrokerOrderStatus(str, Enum):
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIAL_FILL = "partial_fill"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class BrokerOrderResult:
    broker_order_id: str
    status: BrokerOrderStatus
    filled_quantity: int
    filled_price: Decimal | None
    message: str = ""


@dataclass
class BrokerQuote:
    symbol: str
    price: Decimal
    bid: Decimal
    ask: Decimal
    volume: int


class AbstractBroker(ABC):
    """Tüm broker adapter'ların implement etmesi gereken arayüz."""

    @abstractmethod
    async def connect(self) -> bool:
        """Broker'a bağlan. Başarılıysa True döner."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Broker bağlantısını kapat."""
        pass

    @abstractmethod
    async def submit_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: int,
        price: Decimal | None = None,
        stop_price: Decimal | None = None,
    ) -> BrokerOrderResult:
        """Emir gönder."""
        pass

    @abstractmethod
    async def cancel_order(self, broker_order_id: str) -> BrokerOrderResult:
        """Emir iptal et."""
        pass

    @abstractmethod
    async def get_order_status(self, broker_order_id: str) -> BrokerOrderResult:
        """Emir durumu sorgula."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> BrokerQuote:
        """Anlık fiyat bilgisi al."""
        pass

    @abstractmethod
    async def get_positions(self) -> list[dict]:
        """Açık pozisyonları al."""
        pass
