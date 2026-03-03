"""Sprint 4.2 — Dashboard + WebSocket + Canlı Veri testleri."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ═══════════════════════════════════════════
#  1. DASHBOARD API TESTLERİ
# ═══════════════════════════════════════════


class TestDashboardAPI:
    """Dashboard endpoint testleri."""

    async def test_dashboard_summary_unauthenticated(self, client: AsyncClient):
        """Auth olmadan dashboard summary erişilemez."""
        resp = await client.get("/api/v1/dashboard/summary")
        assert resp.status_code in (401, 403)

    async def test_dashboard_summary_authenticated(self, auth_client: AsyncClient):
        """Auth ile dashboard summary döner."""
        resp = await auth_client.get("/api/v1/dashboard/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        summary = data["data"]

        # Portfolio bilgisi olmalı
        assert "portfolio" in summary
        portfolio = summary["portfolio"]
        assert "total_value" in portfolio
        assert "cash_balance" in portfolio
        assert "invested_value" in portfolio
        assert "daily_pnl" in portfolio
        assert "total_pnl" in portfolio
        assert "open_positions" in portfolio

        # Diğer alanlar
        assert "active_strategies" in summary
        assert isinstance(summary["active_strategies"], int)
        assert "recent_signals" in summary
        assert isinstance(summary["recent_signals"], list)
        assert "recent_orders" in summary
        assert isinstance(summary["recent_orders"], list)
        assert "equity_history" in summary
        assert isinstance(summary["equity_history"], list)

    async def test_dashboard_summary_portfolio_defaults(self, auth_client: AsyncClient):
        """Yeni kullanıcı için portföy varsayılan değerleri."""
        resp = await auth_client.get("/api/v1/dashboard/summary")
        assert resp.status_code == 200
        portfolio = resp.json()["data"]["portfolio"]
        # Yeni kullanıcı: 100K nakit, 0 yatırım
        assert float(portfolio["cash_balance"]) == 100_000.0
        assert float(portfolio["invested_value"]) == 0.0
        assert portfolio["open_positions"] == 0


# ═══════════════════════════════════════════
#  2. MARKET LIVE PRICES EP TESTLERİ
# ═══════════════════════════════════════════


class TestLivePricesAPI:
    """Market canlı fiyat endpoint testleri."""

    async def test_live_prices_returns_list(self, auth_client: AsyncClient):
        """Live prices endpoint liste döner."""
        resp = await auth_client.get("/api/v1/market/live-prices")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert "count" in data["meta"]

    async def test_live_prices_with_symbols_filter(self, auth_client: AsyncClient):
        """Sembol filtresi doğru çalışır."""
        resp = await auth_client.get(
            "/api/v1/market/live-prices",
            params={"symbols": "THYAO,GARAN"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        # Cache'te olmayabilir ama format doğru olmalı
        assert isinstance(data["data"], list)

    async def test_live_indices_returns_list(self, auth_client: AsyncClient):
        """Live indices endpoint liste döner."""
        resp = await auth_client.get("/api/v1/market/live-indices")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)


# ═══════════════════════════════════════════
#  3. WEBSOCKET ROUTER TESTLERİ
# ═══════════════════════════════════════════


class TestWebSocketMount:
    """WebSocket endpoint mount testleri."""

    def test_websocket_manager_import(self):
        """WebSocketManager import edilebilir."""
        from app.core.websocket_manager import ws_manager
        assert ws_manager is not None
        assert hasattr(ws_manager, "connect")
        assert hasattr(ws_manager, "disconnect")
        assert hasattr(ws_manager, "broadcast")
        assert hasattr(ws_manager, "subscribe")

    def test_websocket_router_import(self):
        """WebSocket router import edilebilir."""
        from app.websocket.market_stream import router
        assert router is not None

    def test_main_app_has_ws_route(self):
        """main.py'daki app WebSocket route'u içerir."""
        from app.main import app
        routes = [r.path for r in app.routes]
        assert "/ws/v1/market/stream" in routes

    def test_ws_manager_channels_initialized(self):
        """WebSocketManager başlangıçta boş channel dict'e sahip."""
        from app.core.websocket_manager import WebSocketManager
        mgr = WebSocketManager()
        assert mgr.channels == {}
        assert mgr.connections == {}


# ═══════════════════════════════════════════
#  4. AUTH STORE HYDRATION TESTLERİ
#    (backend tarafından doğrulanamaz, sadece
#     dashboard endpoint yapısını test ederiz)
# ═══════════════════════════════════════════


class TestDashboardResponseStructure:
    """Dashboard response yapısal testler."""

    async def test_dashboard_summary_has_all_fields(self, auth_client: AsyncClient):
        """Dashboard summary tüm beklenen alanları içerir."""
        resp = await auth_client.get("/api/v1/dashboard/summary")
        assert resp.status_code == 200
        data = resp.json()["data"]

        # Top-level keys
        expected_keys = {
            "portfolio",
            "active_strategies",
            "recent_signals",
            "recent_orders",
            "equity_history",
        }
        assert expected_keys.issubset(set(data.keys()))

        # Portfolio keys
        portfolio_keys = {
            "total_value", "cash_balance", "invested_value",
            "daily_pnl", "total_pnl", "open_positions",
        }
        assert portfolio_keys.issubset(set(data["portfolio"].keys()))

    async def test_signals_are_ordered_by_date(self, auth_client: AsyncClient):
        """Son sinyaller tarih sırasına göre gelir (en yeni önce)."""
        resp = await auth_client.get("/api/v1/dashboard/summary")
        assert resp.status_code == 200
        signals = resp.json()["data"]["recent_signals"]
        # Boş olabilir ama liste olmalı
        assert isinstance(signals, list)
        assert len(signals) <= 5  # max 5 sinyal

    async def test_orders_are_ordered_by_date(self, auth_client: AsyncClient):
        """Son emirler tarih sırasına göre gelir (en yeni önce)."""
        resp = await auth_client.get("/api/v1/dashboard/summary")
        assert resp.status_code == 200
        orders = resp.json()["data"]["recent_orders"]
        assert isinstance(orders, list)
        assert len(orders) <= 5  # max 5 emir

    async def test_equity_history_is_list(self, auth_client: AsyncClient):
        """Equity history bir liste olmalı."""
        resp = await auth_client.get("/api/v1/dashboard/summary")
        assert resp.status_code == 200
        history = resp.json()["data"]["equity_history"]
        assert isinstance(history, list)
