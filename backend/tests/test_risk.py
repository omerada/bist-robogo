"""Risk API testleri — Sprint 2.3."""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


class TestRiskAPI:
    """Risk endpoint testleri."""

    # ── GET /api/v1/risk/status ──

    async def test_risk_status_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/risk/status")
        assert resp.status_code == 403

    async def test_risk_status_authenticated(self, auth_client):
        """Risk durumunu getir (varsayılan kurallar otomatik oluşturulur)."""
        resp = await auth_client.get("/api/v1/risk/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        status = data["data"]
        assert status["overall_risk"] in ["low", "moderate", "high", "critical"]
        assert "daily_loss" in status
        assert "daily_loss_limit" in status
        assert "open_positions" in status
        assert "max_positions" in status
        assert "rules_active" in status
        assert isinstance(status["recent_events"], list)

    # ── GET /api/v1/risk/rules ──

    async def test_list_rules_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/risk/rules")
        assert resp.status_code == 403

    async def test_list_rules_defaults_created(self, auth_client):
        """Varsayılan 9 risk kuralı oluşturulmuş olmalı."""
        resp = await auth_client.get("/api/v1/risk/rules")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        rules = data["data"]
        assert len(rules) == 9
        assert data["meta"]["total"] == 9

        rule_types = {r["rule_type"] for r in rules}
        expected = {
            "max_position_count",
            "max_position_size_pct",
            "daily_loss_limit_pct",
            "max_order_value",
            "stop_loss_required",
            "max_sector_exposure_pct",
            "min_cash_reserve_pct",
            "max_daily_trades",
            "max_leverage",
        }
        assert rule_types == expected

    async def test_list_rules_all_active(self, auth_client):
        """Varsayılan kuralların hepsi aktif olmalı."""
        resp = await auth_client.get("/api/v1/risk/rules")
        rules = resp.json()["data"]
        for rule in rules:
            assert rule["is_active"] is True

    async def test_list_rules_have_required_fields(self, auth_client):
        """Her kuralda gerekli alanlar olmalı."""
        resp = await auth_client.get("/api/v1/risk/rules")
        rules = resp.json()["data"]
        for rule in rules:
            assert "id" in rule
            assert "rule_type" in rule
            assert "value" in rule
            assert "is_active" in rule
            assert "created_at" in rule
            assert "updated_at" in rule

    # ── PUT /api/v1/risk/rules/{id} ──

    async def test_update_rule_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.put(
            "/api/v1/risk/rules/00000000-0000-0000-0000-000000000000",
            json={"value": {"limit": 5}},
        )
        assert resp.status_code == 403

    async def test_update_rule_not_found(self, auth_client):
        """Olmayan kural → 404."""
        resp = await auth_client.put(
            "/api/v1/risk/rules/00000000-0000-0000-0000-000000000000",
            json={"value": {"limit": 5}},
        )
        assert resp.status_code == 404

    async def test_update_rule_value(self, auth_client):
        """Kural değerini güncelle."""
        # Önce kuralları al
        list_resp = await auth_client.get("/api/v1/risk/rules")
        rules = list_resp.json()["data"]
        max_pos_rule = next(
            r for r in rules if r["rule_type"] == "max_position_count"
        )
        rule_id = max_pos_rule["id"]

        # Güncelle
        resp = await auth_client.put(
            f"/api/v1/risk/rules/{rule_id}",
            json={"value": {"limit": 15}},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["value"]["limit"] == 15

    async def test_update_rule_toggle_active(self, auth_client):
        """Kuralı deaktif/aktif yap."""
        list_resp = await auth_client.get("/api/v1/risk/rules")
        rules = list_resp.json()["data"]
        rule = next(r for r in rules if r["rule_type"] == "max_leverage")
        rule_id = rule["id"]

        # Deaktif yap
        resp = await auth_client.put(
            f"/api/v1/risk/rules/{rule_id}",
            json={"is_active": False},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is False

        # Tekrar aktif yap
        resp2 = await auth_client.put(
            f"/api/v1/risk/rules/{rule_id}",
            json={"is_active": True},
        )
        assert resp2.status_code == 200
        assert resp2.json()["data"]["is_active"] is True

    async def test_update_rule_value_and_active(self, auth_client):
        """Hem value hem is_active aynı anda güncelle."""
        list_resp = await auth_client.get("/api/v1/risk/rules")
        rules = list_resp.json()["data"]
        rule = next(r for r in rules if r["rule_type"] == "daily_loss_limit_pct")
        rule_id = rule["id"]

        resp = await auth_client.put(
            f"/api/v1/risk/rules/{rule_id}",
            json={"value": {"limit": 3.0}, "is_active": True},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["value"]["limit"] == 3.0
        assert data["is_active"] is True

    # ── GET /api/v1/risk/events ──

    async def test_list_events_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/risk/events")
        assert resp.status_code == 403

    async def test_list_events_empty(self, auth_client):
        """Olay listesi (başlangıçta boş)."""
        resp = await auth_client.get("/api/v1/risk/events")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert "total" in data["meta"]

    async def test_list_events_pagination(self, auth_client):
        """Olay sayfalama parametreleri."""
        resp = await auth_client.get("/api/v1/risk/events?page=1&per_page=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["page"] == 1
        assert data["meta"]["per_page"] == 5

    async def test_list_events_filter_by_type(self, auth_client):
        """Olay tipi filtresi."""
        resp = await auth_client.get("/api/v1/risk/events?event_type=rule_violation")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    # ── Risk Status — Consistency ──

    async def test_risk_status_reflects_rule_changes(self, auth_client):
        """Kural güncellemesi sonrası risk durumu tutarlı olmalı."""
        # Kuralları al
        list_resp = await auth_client.get("/api/v1/risk/rules")
        rules = list_resp.json()["data"]
        active_count = sum(1 for r in rules if r["is_active"])

        # Status kontrol
        status_resp = await auth_client.get("/api/v1/risk/status")
        status = status_resp.json()["data"]
        assert status["rules_active"] == active_count
