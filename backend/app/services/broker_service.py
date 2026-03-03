"""Broker bağlantı yönetimi servisi."""

import time
from datetime import datetime, timezone
from uuid import UUID, uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.brokers.factory import get_broker
from app.exceptions import ConflictException, NotFoundException
from app.models.broker import BrokerConnection
from app.repositories.broker_repository import BrokerRepository
from app.schemas.broker import (
    BROKER_REGISTRY,
    BrokerConnectionCreate,
    BrokerConnectionListResponse,
    BrokerConnectionResponse,
    BrokerConnectionUpdate,
    BrokerListInfo,
    BrokerQuoteResponse,
    BrokerStatus,
    BrokerTestResult,
)

logger = structlog.get_logger()


class BrokerService:
    """Broker bağlantı CRUD ve yönetim iş mantığı."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BrokerRepository(db)

    # ── CRUD ──

    async def create_connection(
        self,
        user_id: UUID,
        data: BrokerConnectionCreate,
    ) -> BrokerConnectionResponse:
        """Yeni broker bağlantısı oluşturur."""
        # Paper trading için credentials gereksiz
        if data.broker_name == "paper":
            encrypted = b""
        else:
            # Credential şifreleme (basit — prodüksiyonda Fernet/KMS kullanılmalı)
            import json
            encrypted = json.dumps(data.credentials).encode("utf-8")

        # Aynı broker'dan aktif bağlantı varsa deaktif et
        await self.repo.deactivate_all_for_broker(user_id, data.broker_name.value)

        conn = BrokerConnection(
            id=uuid4(),
            user_id=user_id,
            broker_name=data.broker_name.value,
            encrypted_credentials=encrypted,
            is_active=True,
            is_paper_trading=data.is_paper_trading or data.broker_name == "paper",
            label=data.label or data.broker_name.value,
            status="connected" if data.broker_name == "paper" else "pending",
        )
        self.db.add(conn)
        await self.db.flush()

        logger.info(
            "broker_connection_created",
            user_id=str(user_id),
            broker=data.broker_name.value,
        )
        return self._to_response(conn)

    async def list_connections(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> BrokerConnectionListResponse:
        """Kullanıcının broker bağlantılarını listeler."""
        skip = (page - 1) * per_page
        items = await self.repo.get_by_user(user_id, skip=skip, limit=per_page)
        total = await self.repo.count_by_user(user_id)
        return BrokerConnectionListResponse(
            items=[self._to_response(c) for c in items],
            total=total,
        )

    async def get_connection(
        self,
        user_id: UUID,
        connection_id: UUID,
    ) -> BrokerConnectionResponse:
        """Belirli bir bağlantı detayını getirir."""
        conn = await self.repo.get_user_connection(user_id, connection_id)
        if not conn:
            raise NotFoundException("Broker bağlantısı", str(connection_id))
        return self._to_response(conn)

    async def update_connection(
        self,
        user_id: UUID,
        connection_id: UUID,
        data: BrokerConnectionUpdate,
    ) -> BrokerConnectionResponse:
        """Broker bağlantısını günceller."""
        conn = await self.repo.get_user_connection(user_id, connection_id)
        if not conn:
            raise NotFoundException("Broker bağlantısı", str(connection_id))

        if data.credentials is not None:
            import json
            conn.encrypted_credentials = json.dumps(data.credentials).encode("utf-8")
        if data.is_paper_trading is not None:
            conn.is_paper_trading = data.is_paper_trading
        if data.is_active is not None:
            conn.is_active = data.is_active
            if not data.is_active:
                conn.status = "disconnected"
        if data.label is not None:
            conn.label = data.label

        await self.db.flush()
        await self.db.refresh(conn)
        logger.info(
            "broker_connection_updated",
            connection_id=str(connection_id),
        )
        return self._to_response(conn)

    async def delete_connection(
        self,
        user_id: UUID,
        connection_id: UUID,
    ) -> None:
        """Broker bağlantısını siler."""
        conn = await self.repo.get_user_connection(user_id, connection_id)
        if not conn:
            raise NotFoundException("Broker bağlantısı", str(connection_id))

        await self.repo.delete(conn)
        logger.info(
            "broker_connection_deleted",
            connection_id=str(connection_id),
        )

    # ── Test & Quote ──

    async def test_connection(
        self,
        user_id: UUID,
        connection_id: UUID,
    ) -> BrokerTestResult:
        """Broker bağlantısını test eder."""
        conn = await self.repo.get_user_connection(user_id, connection_id)
        if not conn:
            raise NotFoundException("Broker bağlantısı", str(connection_id))

        start = time.monotonic()
        try:
            broker = get_broker(conn.broker_name)
            connected = await broker.connect()
            latency = (time.monotonic() - start) * 1000

            if connected:
                conn.status = "connected"
                conn.last_connected_at = datetime.now(timezone.utc)
                await self.db.flush()
                await broker.disconnect()
                return BrokerTestResult(
                    success=True,
                    broker_name=conn.broker_name,
                    message="Bağlantı başarılı",
                    latency_ms=round(latency, 2),
                )
            else:
                conn.status = "error"
                await self.db.flush()
                return BrokerTestResult(
                    success=False,
                    broker_name=conn.broker_name,
                    message="Bağlantı kurulamadı",
                    latency_ms=round(latency, 2),
                )
        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            conn.status = "error"
            await self.db.flush()
            logger.error("broker_test_failed", error=str(exc))
            return BrokerTestResult(
                success=False,
                broker_name=conn.broker_name,
                message=f"Hata: {str(exc)}",
                latency_ms=round(latency, 2),
            )

    async def get_quote_via_broker(
        self,
        user_id: UUID,
        connection_id: UUID,
        symbol: str,
    ) -> BrokerQuoteResponse:
        """Broker üzerinden fiyat bilgisi alır."""
        conn = await self.repo.get_user_connection(user_id, connection_id)
        if not conn:
            raise NotFoundException("Broker bağlantısı", str(connection_id))

        broker = get_broker(conn.broker_name)
        await broker.connect()
        try:
            quote = await broker.get_quote(symbol)
            return BrokerQuoteResponse(
                symbol=quote.symbol,
                price=float(quote.price),
                bid=float(quote.bid),
                ask=float(quote.ask),
                volume=quote.volume,
                source=conn.broker_name,
            )
        finally:
            await broker.disconnect()

    # ── Broker Bilgileri ──

    @staticmethod
    def get_available_brokers() -> BrokerListInfo:
        """Desteklenen broker listesini döner."""
        return BrokerListInfo(brokers=list(BROKER_REGISTRY.values()))

    # ── Helpers ──

    @staticmethod
    def _to_response(conn: BrokerConnection) -> BrokerConnectionResponse:
        return BrokerConnectionResponse(
            id=conn.id,
            broker_name=conn.broker_name,
            is_active=conn.is_active,
            is_paper_trading=conn.is_paper_trading,
            label=getattr(conn, "label", "") or conn.broker_name,
            status=BrokerStatus(getattr(conn, "status", "disconnected")),
            last_connected_at=conn.last_connected_at,
            created_at=conn.created_at,
            updated_at=conn.updated_at,
        )
