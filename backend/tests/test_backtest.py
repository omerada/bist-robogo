"""Backtest API testleri — Sprint 2.2."""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


class TestBacktestAPI:
    """Backtest endpoint testleri."""

    # ── GET /api/v1/backtest (auth gerekli) ──

    async def test_list_backtests_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/backtest/")
        assert resp.status_code == 403

    async def test_list_backtests_empty(self, auth_client):
        """Boş backtest listesi."""
        resp = await auth_client.get("/api/v1/backtest/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["meta"]["total"] == 0

    # ── POST /api/v1/backtest/run ──

    async def test_run_backtest_unauthenticated(self, client):
        """Auth olmadan backtest çalıştırma → 403."""
        resp = await client.post("/api/v1/backtest/run", json={})
        assert resp.status_code == 403

    async def test_run_backtest_invalid_strategy(self, auth_client):
        """Geçersiz strateji ID → 400."""
        resp = await auth_client.post(
            "/api/v1/backtest/run",
            json={
                "strategy_id": "00000000-0000-0000-0000-000000000000",
                "symbols": ["THYAO"],
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
            },
        )
        assert resp.status_code == 400

    async def test_run_backtest_no_symbols(self, auth_client):
        """Sembol listesi boş → 422."""
        resp = await auth_client.post(
            "/api/v1/backtest/run",
            json={
                "strategy_id": "00000000-0000-0000-0000-000000000000",
                "symbols": [],
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
            },
        )
        assert resp.status_code == 422

    async def test_run_backtest_with_strategy(self, auth_client):
        """Strateji oluşturup backtest çalıştır (veri yoksa completed/0 trade)."""
        # Önce strateji oluştur
        strategy_resp = await auth_client.post(
            "/api/v1/strategies/",
            json={
                "name": "Backtest Test MA",
                "strategy_type": "ma_crossover",
                "parameters": {"fast_period": 10, "slow_period": 30},
                "symbols": ["THYAO"],
                "timeframe": "1d",
            },
        )
        assert strategy_resp.status_code == 201
        strategy_id = strategy_resp.json()["data"]["id"]

        # Backtest çalıştır
        resp = await auth_client.post(
            "/api/v1/backtest/run",
            json={
                "strategy_id": strategy_id,
                "name": "Test Backtest 1",
                "symbols": ["THYAO"],
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "initial_capital": 100000,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        bt = data["data"]
        assert bt["status"] == "completed"
        assert bt["name"] == "Test Backtest 1"
        assert bt["strategy_id"] == strategy_id

    async def test_run_backtest_invalid_dates(self, auth_client):
        """Başlangıç > Bitiş → 400."""
        # Strateji al
        list_resp = await auth_client.get("/api/v1/strategies/")
        strategies = list_resp.json()["data"]
        if not strategies:
            pytest.skip("Strateji bulunamadı")
        strategy_id = strategies[0]["id"]

        resp = await auth_client.post(
            "/api/v1/backtest/run",
            json={
                "strategy_id": strategy_id,
                "symbols": ["THYAO"],
                "start_date": "2024-12-01",
                "end_date": "2024-01-01",
            },
        )
        assert resp.status_code == 400

    # ── GET /api/v1/backtest/{id} ──

    async def test_get_backtest_not_found(self, auth_client):
        """Olmayan backtest → 404."""
        resp = await auth_client.get(
            "/api/v1/backtest/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    async def test_get_backtest_detail(self, auth_client):
        """Backtest detay getir."""
        # Listeden ilk backtest'i al
        list_resp = await auth_client.get("/api/v1/backtest/")
        backtests = list_resp.json()["data"]
        if not backtests:
            pytest.skip("Backtest bulunamadı")
        bt_id = backtests[0]["id"]

        resp = await auth_client.get(f"/api/v1/backtest/{bt_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["id"] == bt_id

    # ── GET /api/v1/backtest/{id}/detail ──

    async def test_get_backtest_detail_with_trades(self, auth_client):
        """Backtest detay (trade'lerle birlikte)."""
        list_resp = await auth_client.get("/api/v1/backtest/")
        backtests = list_resp.json()["data"]
        if not backtests:
            pytest.skip("Backtest bulunamadı")
        bt_id = backtests[0]["id"]

        resp = await auth_client.get(f"/api/v1/backtest/{bt_id}/detail")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "trades" in data["data"]
        assert isinstance(data["data"]["trades"], list)

    # ── GET /api/v1/backtest/{id}/trades ──

    async def test_get_backtest_trades(self, auth_client):
        """Backtest trade listesi."""
        list_resp = await auth_client.get("/api/v1/backtest/")
        backtests = list_resp.json()["data"]
        if not backtests:
            pytest.skip("Backtest bulunamadı")
        bt_id = backtests[0]["id"]

        resp = await auth_client.get(f"/api/v1/backtest/{bt_id}/trades")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert "total" in data["meta"]

    # ── GET /api/v1/backtest/{id}/equity-curve ──

    async def test_get_equity_curve(self, auth_client):
        """Backtest equity curve."""
        list_resp = await auth_client.get("/api/v1/backtest/")
        backtests = list_resp.json()["data"]
        if not backtests:
            pytest.skip("Backtest bulunamadı")
        bt_id = backtests[0]["id"]

        resp = await auth_client.get(f"/api/v1/backtest/{bt_id}/equity-curve")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    async def test_get_equity_curve_not_found(self, auth_client):
        """Olmayan backtest equity curve → 404."""
        resp = await auth_client.get(
            "/api/v1/backtest/00000000-0000-0000-0000-000000000000/equity-curve"
        )
        assert resp.status_code == 404

    # ── DELETE /api/v1/backtest/{id} ──

    async def test_delete_backtest_not_found(self, auth_client):
        """Olmayan backtest silme → 404."""
        resp = await auth_client.delete(
            "/api/v1/backtest/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    async def test_delete_backtest(self, auth_client):
        """Backtest sil."""
        # Yeni backtest oluştur silmek için
        list_resp = await auth_client.get("/api/v1/strategies/")
        strategies = list_resp.json()["data"]
        if not strategies:
            pytest.skip("Strateji bulunamadı")
        strategy_id = strategies[0]["id"]

        create_resp = await auth_client.post(
            "/api/v1/backtest/run",
            json={
                "strategy_id": strategy_id,
                "name": "Silinecek BT",
                "symbols": ["GARAN"],
                "start_date": "2023-06-01",
                "end_date": "2023-12-31",
            },
        )
        assert create_resp.status_code == 201
        bt_id = create_resp.json()["data"]["id"]

        # Sil
        resp = await auth_client.delete(f"/api/v1/backtest/{bt_id}")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        # Tekrar getir → 404
        resp2 = await auth_client.get(f"/api/v1/backtest/{bt_id}")
        assert resp2.status_code == 404

    # ── Pagination & Filter ──

    async def test_list_backtests_with_filter(self, auth_client):
        """Status filtresi ile listeleme."""
        resp = await auth_client.get("/api/v1/backtest/?status=completed")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        for bt in data["data"]:
            assert bt["status"] == "completed"

    async def test_list_backtests_pagination(self, auth_client):
        """Sayfalama parametreleri."""
        resp = await auth_client.get("/api/v1/backtest/?page=1&per_page=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["page"] == 1
        assert data["meta"]["per_page"] == 5
