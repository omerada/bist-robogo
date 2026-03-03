"""Strateji API testleri — Sprint 2.1."""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


class TestStrategyAPI:
    """Strateji endpoint testleri."""

    # ── GET /api/v1/strategies (auth gerekli) ──

    async def test_list_strategies_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/strategies/")
        assert resp.status_code == 403

    async def test_list_strategies_empty(self, auth_client):
        """Boş strateji listesi."""
        resp = await auth_client.get("/api/v1/strategies/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["meta"]["total"] == 0

    # ── POST /api/v1/strategies ──

    async def test_create_strategy(self, auth_client):
        """Strateji oluştur."""
        resp = await auth_client.post(
            "/api/v1/strategies/",
            json={
                "name": "Test MA Cross",
                "strategy_type": "ma_crossover",
                "description": "Test strateji",
                "parameters": {"fast_period": 20, "slow_period": 50},
                "symbols": ["THYAO", "GARAN"],
                "timeframe": "1d",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        strategy = data["data"]
        assert strategy["name"] == "Test MA Cross"
        assert strategy["strategy_type"] == "ma_crossover"
        assert strategy["is_active"] is False
        assert strategy["is_paper"] is True
        assert "THYAO" in strategy["symbols"]

    async def test_create_strategy_missing_name(self, auth_client):
        """İsim olmadan → 422."""
        resp = await auth_client.post(
            "/api/v1/strategies/",
            json={"strategy_type": "rsi_reversal"},
        )
        assert resp.status_code == 422

    # ── GET /api/v1/strategies/{id} ──

    async def test_get_strategy_detail(self, auth_client):
        """Strateji detay."""
        # Önce oluştur
        create_resp = await auth_client.post(
            "/api/v1/strategies/",
            json={
                "name": "Detail Test",
                "strategy_type": "rsi_reversal",
                "parameters": {"rsi_period": 14, "oversold": 30, "overbought": 70},
            },
        )
        strategy_id = create_resp.json()["data"]["id"]

        # Detay çek
        resp = await auth_client.get(f"/api/v1/strategies/{strategy_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["id"] == strategy_id
        assert data["data"]["name"] == "Detail Test"

    async def test_get_strategy_not_found(self, auth_client):
        """Olmayan strateji → 404."""
        resp = await auth_client.get("/api/v1/strategies/00000000-0000-0000-0000-000000000001")
        assert resp.status_code == 404

    # ── PUT /api/v1/strategies/{id} ──

    async def test_update_strategy(self, auth_client):
        """Strateji güncelle."""
        create_resp = await auth_client.post(
            "/api/v1/strategies/",
            json={"name": "Update Test", "strategy_type": "ma_crossover"},
        )
        strategy_id = create_resp.json()["data"]["id"]

        resp = await auth_client.put(
            f"/api/v1/strategies/{strategy_id}",
            json={"name": "Updated Name", "symbols": ["ASELS"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["name"] == "Updated Name"
        assert "ASELS" in data["data"]["symbols"]

    # ── DELETE /api/v1/strategies/{id} ──

    async def test_delete_strategy(self, auth_client):
        """Strateji sil."""
        create_resp = await auth_client.post(
            "/api/v1/strategies/",
            json={"name": "Delete Test", "strategy_type": "ma_crossover"},
        )
        strategy_id = create_resp.json()["data"]["id"]

        resp = await auth_client.delete(f"/api/v1/strategies/{strategy_id}")
        assert resp.status_code == 204

        # Silinen strateji → 404
        resp = await auth_client.get(f"/api/v1/strategies/{strategy_id}")
        assert resp.status_code == 404

    # ── POST /api/v1/strategies/{id}/activate ──

    async def test_activate_strategy(self, auth_client):
        """Strateji aktifleştir."""
        create_resp = await auth_client.post(
            "/api/v1/strategies/",
            json={"name": "Activate Test", "strategy_type": "ma_crossover"},
        )
        strategy_id = create_resp.json()["data"]["id"]

        resp = await auth_client.post(f"/api/v1/strategies/{strategy_id}/activate")
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is True

    # ── POST /api/v1/strategies/{id}/deactivate ──

    async def test_deactivate_strategy(self, auth_client):
        """Strateji deaktifleştir."""
        create_resp = await auth_client.post(
            "/api/v1/strategies/",
            json={"name": "Deactivate Test", "strategy_type": "ma_crossover"},
        )
        strategy_id = create_resp.json()["data"]["id"]

        # Önce aktifleştir
        await auth_client.post(f"/api/v1/strategies/{strategy_id}/activate")
        # Sonra deaktifleştir
        resp = await auth_client.post(f"/api/v1/strategies/{strategy_id}/deactivate")
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is False

    # ── GET /api/v1/strategies/{id}/signals ──

    async def test_get_signals_empty(self, auth_client):
        """Boş sinyal listesi."""
        create_resp = await auth_client.post(
            "/api/v1/strategies/",
            json={"name": "Signals Test", "strategy_type": "ma_crossover"},
        )
        strategy_id = create_resp.json()["data"]["id"]

        resp = await auth_client.get(f"/api/v1/strategies/{strategy_id}/signals")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"] == []
        assert data["meta"]["total"] == 0

    # ── GET /api/v1/strategies/{id}/performance ──

    async def test_get_performance(self, auth_client):
        """Performans özeti."""
        create_resp = await auth_client.post(
            "/api/v1/strategies/",
            json={"name": "Perf Test", "strategy_type": "rsi_reversal"},
        )
        strategy_id = create_resp.json()["data"]["id"]

        resp = await auth_client.get(f"/api/v1/strategies/{strategy_id}/performance")
        assert resp.status_code == 200
        perf = resp.json()["data"]
        assert perf["strategy_id"] == strategy_id
        assert perf["total_signals"] == 0

    # ── Filtreleme Testleri ──

    async def test_list_strategies_filter_type(self, auth_client):
        """Strateji tipi filtresi."""
        resp = await auth_client.get(
            "/api/v1/strategies/",
            params={"strategy_type": "ma_crossover"},
        )
        assert resp.status_code == 200
        for s in resp.json()["data"]:
            assert s["strategy_type"] == "ma_crossover"

    async def test_list_strategies_filter_active(self, auth_client):
        """Aktiflik filtresi."""
        resp = await auth_client.get(
            "/api/v1/strategies/",
            params={"is_active": True},
        )
        assert resp.status_code == 200
        for s in resp.json()["data"]:
            assert s["is_active"] is True

    async def test_list_strategies_pagination(self, auth_client):
        """Sayfalama çalışıyor."""
        resp = await auth_client.get(
            "/api/v1/strategies/",
            params={"page": 1, "per_page": 2},
        )
        assert resp.status_code == 200
        meta = resp.json()["meta"]
        assert meta["page"] == 1
        assert meta["per_page"] == 2
