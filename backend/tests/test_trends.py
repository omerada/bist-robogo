"""Trend analiz API testleri — Sprint 2.1."""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


class TestTrendAPI:
    """Trend analiz endpoint testleri."""

    # ── GET /api/v1/analysis/trends ──

    async def test_get_trends_default(self, client):
        """Varsayılan parametrelerle trend analizi."""
        resp = await client.get("/api/v1/analysis/trends")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "data" in data
        assert "period" in data["data"]
        assert "dip_candidates" in data["data"]
        assert "breakout_candidates" in data["data"]
        assert data["data"]["period"] == "daily"

    async def test_get_trends_with_filters(self, client):
        """Filtrelerle trend analizi."""
        resp = await client.get(
            "/api/v1/analysis/trends",
            params={
                "period": "daily",
                "index": "ALL",
                "type": "dip",
                "min_score": 0.5,
                "limit": 10,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["index"] == "ALL"

    async def test_get_trends_breakout_only(self, client):
        """Sadece kırılım adayları."""
        resp = await client.get(
            "/api/v1/analysis/trends",
            params={"type": "breakout", "min_score": 0.3},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    async def test_get_trends_invalid_period(self, client):
        """Geçersiz periyot → 422."""
        resp = await client.get(
            "/api/v1/analysis/trends",
            params={"period": "invalid"},
        )
        assert resp.status_code == 422

    async def test_get_trends_invalid_min_score(self, client):
        """min_score aralık dışı → 422."""
        resp = await client.get(
            "/api/v1/analysis/trends",
            params={"min_score": 1.5},
        )
        assert resp.status_code == 422

    async def test_get_trends_meta_has_counts(self, client):
        """Meta bilgisinde aday sayıları var."""
        resp = await client.get("/api/v1/analysis/trends")
        assert resp.status_code == 200
        data = resp.json()
        meta = data.get("meta", {})
        assert "total_dip_candidates" in meta
        assert "total_breakout_candidates" in meta
        assert "analysis_timestamp" in meta

    async def test_get_trends_response_structure(self, client):
        """Response yapı kontrolü."""
        resp = await client.get("/api/v1/analysis/trends")
        assert resp.status_code == 200
        data = resp.json()
        analysis = data["data"]
        assert "analysis_date" in analysis
        assert isinstance(analysis["dip_candidates"], list)
        assert isinstance(analysis["breakout_candidates"], list)

    # ── GET /api/v1/analysis/sectors ──

    async def test_get_sectors(self, client):
        """Sektörel analiz placeholder döner."""
        resp = await client.get("/api/v1/analysis/sectors")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    async def test_get_trends_weekly(self, client):
        """Haftalık periyot ile analiz."""
        resp = await client.get(
            "/api/v1/analysis/trends",
            params={"period": "weekly"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["period"] == "weekly"

    async def test_get_trends_limit(self, client):
        """Limit parametresi çalışıyor."""
        resp = await client.get(
            "/api/v1/analysis/trends",
            params={"limit": 5, "min_score": 0.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]["dip_candidates"]) <= 5
        assert len(data["data"]["breakout_candidates"]) <= 5
