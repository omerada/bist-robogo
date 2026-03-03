# Source: Sprint 1.3 — Trading & Portfolio endpoint testleri
"""Emir oluşturma, portföy yönetimi ve pozisyon testleri."""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── Portfolio Tests ──


async def test_portfolio_summary_unauthenticated(client):
    """GET /api/v1/portfolio/summary — kimliksiz → 403."""
    response = await client.get(
        "/api/v1/portfolio/summary",
        headers={},  # No auth
    )
    assert response.status_code == 403


async def test_portfolio_summary_initial(auth_client):
    """GET /api/v1/portfolio/summary — ilk portföy ₺100K."""
    response = await auth_client.get("/api/v1/portfolio/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    summary = data["data"]
    assert float(summary["total_value"]) == 100_000.0
    assert float(summary["cash_balance"]) == 100_000.0
    assert float(summary["invested_value"]) == 0.0
    assert summary["open_positions"] == 0


async def test_portfolio_positions_empty(auth_client):
    """GET /api/v1/portfolio/positions — başlangıçta boş."""
    response = await auth_client.get("/api/v1/portfolio/positions")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []


async def test_portfolio_history_empty(auth_client):
    """GET /api/v1/portfolio/history — başlangıçta boş."""
    response = await auth_client.get("/api/v1/portfolio/history")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []


# ── Order Creation Tests ──


async def test_create_order_unauthenticated(client):
    """POST /api/v1/orders/ — kimliksiz → 403."""
    response = await client.post(
        "/api/v1/orders/",
        json={
            "symbol": "THYAO",
            "side": "buy",
            "order_type": "market",
            "quantity": 10,
        },
        headers={},
    )
    assert response.status_code == 403


async def test_create_buy_order(auth_client):
    """POST /api/v1/orders/ — alış emri oluştur → filled."""
    response = await auth_client.post(
        "/api/v1/orders/",
        json={
            "symbol": "THYAO",
            "side": "buy",
            "order_type": "market",
            "quantity": 10,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True

    order = data["data"]
    assert order["symbol"] == "THYAO"
    assert order["side"] == "buy"
    assert order["order_type"] == "market"
    assert order["quantity"] == 10
    assert order["status"] == "filled"
    assert order["filled_quantity"] == 10
    assert order["is_paper"] is True
    assert float(order["filled_price"]) > 0
    assert float(order["commission"]) > 0


async def test_portfolio_after_buy(auth_client):
    """Alış sonrası portföy nakit azalmış, yatırım artmış olmalı."""
    response = await auth_client.get("/api/v1/portfolio/summary")
    data = response.json()["data"]
    assert float(data["cash_balance"]) < 100_000.0
    assert float(data["invested_value"]) > 0
    assert data["open_positions"] == 1


async def test_position_after_buy(auth_client):
    """Alış sonrası THYAO pozisyonu olmalı."""
    response = await auth_client.get("/api/v1/portfolio/positions")
    data = response.json()["data"]
    assert len(data) == 1

    pos = data[0]
    assert pos["symbol"] == "THYAO"
    assert pos["side"] == "long"
    assert pos["quantity"] == 10
    assert float(pos["avg_entry_price"]) > 0


async def test_create_additional_buy(auth_client):
    """Aynı sembolden tekrar alış — pozisyon miktarı artar."""
    response = await auth_client.post(
        "/api/v1/orders/",
        json={
            "symbol": "THYAO",
            "side": "buy",
            "order_type": "market",
            "quantity": 5,
        },
    )
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "filled"

    # Pozisyon artık 15 lot olmalı
    pos_response = await auth_client.get("/api/v1/portfolio/positions")
    positions = pos_response.json()["data"]
    assert len(positions) == 1
    assert positions[0]["quantity"] == 15


async def test_create_sell_order(auth_client):
    """Satış emri — kısmi satış başarılı."""
    response = await auth_client.post(
        "/api/v1/orders/",
        json={
            "symbol": "THYAO",
            "side": "sell",
            "order_type": "market",
            "quantity": 5,
        },
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "filled"
    assert data["side"] == "sell"

    # Pozisyon 10 lot'a düşmüş olmalı
    pos_response = await auth_client.get("/api/v1/portfolio/positions")
    positions = pos_response.json()["data"]
    assert len(positions) == 1
    assert positions[0]["quantity"] == 10


async def test_create_sell_exceeding_position(auth_client):
    """Mevcut pozisyondan fazla satış → hata."""
    response = await auth_client.post(
        "/api/v1/orders/",
        json={
            "symbol": "THYAO",
            "side": "sell",
            "order_type": "market",
            "quantity": 9999,
        },
    )
    assert response.status_code == 400


async def test_create_order_zero_quantity(auth_client):
    """Sıfır miktar → 422 validation error."""
    response = await auth_client.post(
        "/api/v1/orders/",
        json={
            "symbol": "THYAO",
            "side": "buy",
            "order_type": "market",
            "quantity": 0,
        },
    )
    assert response.status_code == 422


async def test_create_order_negative_quantity(auth_client):
    """Negatif miktar → 422."""
    response = await auth_client.post(
        "/api/v1/orders/",
        json={
            "symbol": "THYAO",
            "side": "buy",
            "order_type": "market",
            "quantity": -10,
        },
    )
    assert response.status_code == 422


# ── Order Listing & Detail ──


async def test_list_orders(auth_client):
    """GET /api/v1/orders/ — emir listesi."""
    response = await auth_client.get("/api/v1/orders/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 3  # buy + buy + sell en az
    assert data["meta"]["total"] >= 3


async def test_list_orders_status_filter(auth_client):
    """GET /api/v1/orders/?status=filled — filtreli liste."""
    response = await auth_client.get("/api/v1/orders/?status=filled")
    assert response.status_code == 200
    orders = response.json()["data"]
    for order in orders:
        assert order["status"] == "filled"


async def test_list_orders_symbol_filter(auth_client):
    """GET /api/v1/orders/?symbol=THYAO — sembol filtre."""
    response = await auth_client.get("/api/v1/orders/?symbol=THYAO")
    assert response.status_code == 200
    orders = response.json()["data"]
    for order in orders:
        assert order["symbol"] == "THYAO"


async def test_get_order_detail(auth_client):
    """GET /api/v1/orders/{id} — tek emir detayı."""
    # Önce liste al, ilk emri seç
    list_resp = await auth_client.get("/api/v1/orders/")
    orders = list_resp.json()["data"]
    assert len(orders) > 0

    order_id = orders[0]["id"]
    response = await auth_client.get(f"/api/v1/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == order_id


async def test_get_order_not_found(auth_client):
    """GET /api/v1/orders/{id} — mevcut olmayan emir → 404."""
    response = await auth_client.get(
        "/api/v1/orders/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


# ── Order Cancellation ──


async def test_cancel_filled_order(auth_client):
    """DELETE /api/v1/orders/{id} — dolu emir iptal edilemez → 400."""
    list_resp = await auth_client.get("/api/v1/orders/?status=filled")
    orders = list_resp.json()["data"]
    assert len(orders) > 0

    filled_id = orders[0]["id"]
    response = await auth_client.delete(f"/api/v1/orders/{filled_id}")
    assert response.status_code == 400


# ── Limit Order ──


async def test_create_limit_order(auth_client):
    """POST — limit emir oluştur."""
    response = await auth_client.post(
        "/api/v1/orders/",
        json={
            "symbol": "GARAN",
            "side": "buy",
            "order_type": "limit",
            "quantity": 50,
            "price": "25.50",
        },
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["symbol"] == "GARAN"
    assert data["order_type"] == "limit"
    # Paper broker fills all orders
    assert data["status"] in ("filled", "pending", "submitted")
