# Source: Doc 07 §24 (test) — Health check testleri
"""Health endpoint testleri."""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_health_check(client):
    """GET /health → 200 OK."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


async def test_ready_check(client):
    """GET /ready → 200 OK (DB + Redis bağlantısı)."""
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ready", "degraded")
    assert "checks" in data
