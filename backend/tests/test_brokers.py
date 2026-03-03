"""Broker bağlantı yönetimi testleri — schemas, model, API, CollectAPI."""

import pytest
from uuid import uuid4


pytestmark = pytest.mark.asyncio(loop_scope="session")


# ═══════════════════════════════════════════
#  1. BROKER SCHEMA TESTLERİ
# ═══════════════════════════════════════════


class TestBrokerSchemas:
    """Broker Pydantic şema doğrulama testleri."""

    def test_broker_connection_create_paper(self):
        from app.schemas.broker import BrokerConnectionCreate
        data = BrokerConnectionCreate(
            broker_name="paper",
            credentials={},
            is_paper_trading=True,
        )
        assert data.broker_name == "paper"
        assert data.is_paper_trading is True
        assert data.label == ""

    def test_broker_connection_create_with_label(self):
        from app.schemas.broker import BrokerConnectionCreate
        data = BrokerConnectionCreate(
            broker_name="is_yatirim",
            credentials={"api_key": "test123", "api_secret": "secret"},
            label="İŞ Yatırım Hesabım",
        )
        assert data.label == "İŞ Yatırım Hesabım"
        assert data.credentials["api_key"] == "test123"

    def test_broker_connection_create_invalid_broker(self):
        from app.schemas.broker import BrokerConnectionCreate
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            BrokerConnectionCreate(
                broker_name="invalid_broker",
                credentials={},
            )

    def test_broker_connection_update_partial(self):
        from app.schemas.broker import BrokerConnectionUpdate
        data = BrokerConnectionUpdate(is_active=False)
        assert data.is_active is False
        assert data.credentials is None
        assert data.label is None

    def test_broker_connection_response(self):
        from app.schemas.broker import BrokerConnectionResponse
        data = BrokerConnectionResponse(
            id=uuid4(),
            broker_name="paper",
            is_active=True,
            is_paper_trading=True,
            label="Paper",
            status="connected",
            last_connected_at=None,
            created_at="2026-03-01T10:00:00Z",
            updated_at="2026-03-01T10:00:00Z",
        )
        assert data.broker_name == "paper"
        assert data.status == "connected"

    def test_broker_test_result(self):
        from app.schemas.broker import BrokerTestResult
        data = BrokerTestResult(
            success=True,
            broker_name="paper",
            message="Bağlantı başarılı",
            latency_ms=12.5,
        )
        assert data.success is True
        assert data.latency_ms == 12.5

    def test_broker_quote_response(self):
        from app.schemas.broker import BrokerQuoteResponse
        data = BrokerQuoteResponse(
            symbol="THYAO",
            price=287.50,
            bid=287.30,
            ask=287.70,
            volume=5000000,
            source="paper",
        )
        assert data.symbol == "THYAO"
        assert data.price == 287.50

    def test_broker_info(self):
        from app.schemas.broker import BrokerInfo
        data = BrokerInfo(
            name="paper",
            display_name="Paper Trading",
            description="Test",
            requires_credentials=False,
            credential_fields=[],
            is_available=True,
        )
        assert data.is_available is True
        assert data.requires_credentials is False

    def test_broker_registry(self):
        from app.schemas.broker import BROKER_REGISTRY
        assert "paper" in BROKER_REGISTRY
        assert "is_yatirim" in BROKER_REGISTRY
        assert "gedik" in BROKER_REGISTRY
        assert BROKER_REGISTRY["paper"].is_available is True
        assert BROKER_REGISTRY["is_yatirim"].is_available is False

    def test_broker_type_enum(self):
        from app.schemas.broker import BrokerType
        assert BrokerType.PAPER == "paper"
        assert BrokerType.IS_YATIRIM == "is_yatirim"
        assert BrokerType.GEDIK == "gedik"

    def test_broker_status_enum(self):
        from app.schemas.broker import BrokerStatus
        assert BrokerStatus.CONNECTED == "connected"
        assert BrokerStatus.DISCONNECTED == "disconnected"
        assert BrokerStatus.ERROR == "error"
        assert BrokerStatus.PENDING == "pending"

    def test_broker_connection_list_response(self):
        from app.schemas.broker import BrokerConnectionListResponse, BrokerConnectionResponse
        resp = BrokerConnectionListResponse(
            items=[
                BrokerConnectionResponse(
                    id=uuid4(),
                    broker_name="paper",
                    is_active=True,
                    is_paper_trading=True,
                    label="Paper",
                    status="connected",
                    created_at="2026-03-01T10:00:00Z",
                    updated_at="2026-03-01T10:00:00Z",
                )
            ],
            total=1,
        )
        assert resp.total == 1
        assert len(resp.items) == 1


# ═══════════════════════════════════════════
#  2. BROKER MODEL TESTLERİ
# ═══════════════════════════════════════════


class TestBrokerModel:
    """BrokerConnection ORM model testleri."""

    def test_broker_connection_repr(self):
        from app.models.broker import BrokerConnection
        conn = BrokerConnection(
            id=uuid4(),
            user_id=uuid4(),
            broker_name="paper",
            encrypted_credentials=b"",
            is_active=True,
        )
        repr_str = repr(conn)
        assert "paper" in repr_str
        assert "True" in repr_str

    def test_broker_connection_table_name(self):
        from app.models.broker import BrokerConnection
        assert BrokerConnection.__tablename__ == "broker_connections"

    def test_broker_connection_defaults(self):
        from app.models.broker import BrokerConnection
        conn = BrokerConnection(
            id=uuid4(),
            user_id=uuid4(),
            broker_name="gedik",
            encrypted_credentials=b"test",
        )
        assert conn.broker_name == "gedik"


# ═══════════════════════════════════════════
#  3. COLLECTAPI CLIENT TESTLERİ
# ═══════════════════════════════════════════


class TestCollectAPIClient:
    """CollectAPI client testleri."""

    def test_parse_stock_to_quote_basic(self):
        from app.core.collectapi_client import CollectAPIClient
        stock = {
            "code": "THYAO",
            "text": "Türk Hava Yolları",
            "lastprice": "287.50",
            "rate": "2.14",
            "hacim": "5000000",
            "min": "280.00",
            "max": "290.00",
        }
        result = CollectAPIClient.parse_stock_to_quote(stock)
        assert result["symbol"] == "THYAO"
        assert result["price"] == 287.50
        assert result["volume"] == 5000000

    def test_parse_stock_to_quote_turkish_format(self):
        from app.core.collectapi_client import CollectAPIClient
        stock = {
            "code": "GARAN",
            "text": "Garanti BBVA",
            "lastprice": "123,45",
            "rate": "1.5",
            "hacim": "1.234.567",
            "min": "120,00",
            "max": "125,00",
        }
        result = CollectAPIClient.parse_stock_to_quote(stock)
        assert result["symbol"] == "GARAN"
        assert result["price"] == 123.45

    def test_parse_stock_to_quote_missing_fields(self):
        from app.core.collectapi_client import CollectAPIClient
        stock = {"code": "TEST"}
        result = CollectAPIClient.parse_stock_to_quote(stock)
        assert result["symbol"] == "TEST"
        assert result["price"] == 0
        assert result["volume"] == 0

    def test_parse_stock_to_quote_invalid_values(self):
        from app.core.collectapi_client import CollectAPIClient
        stock = {
            "code": "BAD",
            "lastprice": "invalid",
            "hacim": "abc",
        }
        result = CollectAPIClient.parse_stock_to_quote(stock)
        assert result["symbol"] == "BAD"
        assert result["price"] == 0

    def test_client_init_default(self):
        from app.core.collectapi_client import CollectAPIClient
        client = CollectAPIClient()
        assert client.api_key == ""
        assert client.TIMEOUT == 30

    def test_client_init_with_key(self):
        from app.core.collectapi_client import CollectAPIClient
        client = CollectAPIClient(api_key="test-key-123")
        assert client.api_key == "test-key-123"


# ═══════════════════════════════════════════
#  4. BROKER API TESTLERİ
# ═══════════════════════════════════════════


class TestBrokerAPI:
    """Broker REST API endpoint testleri."""

    async def test_get_available_brokers_no_auth(self, client):
        """Broker bilgileri kimlik doğrulaması olmadan erişilebilir."""
        resp = await client.get("/api/v1/brokers/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        brokers = data["data"]["brokers"]
        assert len(brokers) >= 5
        paper = next(b for b in brokers if b["name"] == "paper")
        assert paper["is_available"] is True

    async def test_list_connections_unauthenticated(self, client):
        """Kimlik doğrulaması olmadan bağlantı listesi 403 dönmeli."""
        resp = await client.get("/api/v1/brokers/connections")
        assert resp.status_code == 403

    async def test_create_paper_connection(self, auth_client):
        """Paper trading bağlantısı oluşturma."""
        resp = await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "paper",
            "credentials": {},
            "is_paper_trading": True,
            "label": "Test Paper",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["broker_name"] == "paper"
        assert data["data"]["is_paper_trading"] is True
        assert data["data"]["label"] == "Test Paper"
        assert data["data"]["status"] == "connected"

    async def test_create_and_list_connections(self, auth_client):
        """Bağlantı oluştur ve listele."""
        # Oluştur
        await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "paper",
            "credentials": {},
            "label": "List Test",
        })
        # Listele
        resp = await auth_client.get("/api/v1/brokers/connections")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["total"] >= 1
        assert len(data["data"]["items"]) >= 1

    async def test_create_and_get_detail(self, auth_client):
        """Bağlantı oluştur ve detay al."""
        create_resp = await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "paper",
            "credentials": {},
            "label": "Detail Test",
        })
        conn_id = create_resp.json()["data"]["id"]

        resp = await auth_client.get(f"/api/v1/brokers/connections/{conn_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == conn_id

    async def test_create_and_update(self, auth_client):
        """Bağlantı oluştur ve güncelle."""
        create_resp = await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "paper",
            "credentials": {},
            "label": "Update Test",
        })
        conn_id = create_resp.json()["data"]["id"]

        resp = await auth_client.put(f"/api/v1/brokers/connections/{conn_id}", json={
            "label": "Güncellenmiş Etiket",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["label"] == "Güncellenmiş Etiket"

    async def test_create_and_test_connection(self, auth_client):
        """Broker bağlantı testi."""
        create_resp = await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "paper",
            "credentials": {},
            "label": "Test Connection",
        })
        conn_id = create_resp.json()["data"]["id"]

        resp = await auth_client.post(f"/api/v1/brokers/connections/{conn_id}/test")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        test_result = data["data"]
        assert test_result["broker_name"] == "paper"
        assert test_result["success"] is True
        assert test_result["latency_ms"] is not None

    async def test_create_and_get_quote(self, auth_client):
        """Broker üzerinden fiyat alma."""
        create_resp = await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "paper",
            "credentials": {},
            "label": "Quote Test",
        })
        conn_id = create_resp.json()["data"]["id"]

        resp = await auth_client.get(f"/api/v1/brokers/connections/{conn_id}/quote/THYAO")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["symbol"] == "THYAO"
        assert data["data"]["price"] > 0
        assert data["data"]["source"] == "paper"

    async def test_get_connection_not_found(self, auth_client):
        """Var olmayan bağlantı 404 dönmeli."""
        fake_id = str(uuid4())
        resp = await auth_client.get(f"/api/v1/brokers/connections/{fake_id}")
        assert resp.status_code == 404

    async def test_create_and_delete(self, auth_client):
        """Bağlantı oluştur ve sil."""
        create_resp = await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "paper",
            "credentials": {},
            "label": "Silinecek",
        })
        conn_id = create_resp.json()["data"]["id"]

        # Sil
        resp = await auth_client.delete(f"/api/v1/brokers/connections/{conn_id}")
        assert resp.status_code == 204

        # Silinmiş mi kontrol et
        resp = await auth_client.get(f"/api/v1/brokers/connections/{conn_id}")
        assert resp.status_code == 404

    async def test_create_invalid_broker_type(self, auth_client):
        """Geçersiz broker tipi 422 dönmeli."""
        resp = await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "nonexistent",
            "credentials": {},
        })
        assert resp.status_code == 422

    async def test_create_and_deactivate(self, auth_client):
        """Bağlantı oluştur ve deaktif et."""
        create_resp = await auth_client.post("/api/v1/brokers/connections", json={
            "broker_name": "paper",
            "credentials": {},
            "label": "Deaktif Test",
        })
        conn_id = create_resp.json()["data"]["id"]

        resp = await auth_client.put(f"/api/v1/brokers/connections/{conn_id}", json={
            "is_active": False,
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is False
        assert resp.json()["data"]["status"] == "disconnected"


# ═══════════════════════════════════════════
#  5. MARKET TASKS TESTLERİ
# ═══════════════════════════════════════════


class TestMarketTasks:
    """Market Celery task testleri."""

    def test_fetch_live_prices_task_exists(self):
        from app.tasks.market_tasks import fetch_live_prices
        assert fetch_live_prices is not None
        assert fetch_live_prices.name == "app.tasks.market_tasks.fetch_live_prices"

    def test_fetch_indices_task_exists(self):
        from app.tasks.market_tasks import fetch_indices
        assert fetch_indices is not None
        assert fetch_indices.name == "app.tasks.market_tasks.fetch_indices"

    def test_celery_beat_schedule_has_live_price(self):
        from app.tasks.celery_app import celery_app
        schedule = celery_app.conf.beat_schedule
        assert "live-price-update" in schedule
        assert schedule["live-price-update"]["task"] == "app.tasks.market_tasks.fetch_live_prices"

    def test_celery_beat_schedule_has_live_index(self):
        from app.tasks.celery_app import celery_app
        schedule = celery_app.conf.beat_schedule
        assert "live-index-update" in schedule
        assert schedule["live-index-update"]["task"] == "app.tasks.market_tasks.fetch_indices"
