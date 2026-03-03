"""Market endpoint testleri — semboller, endeksler, sektörler."""

from datetime import date

import pytest
import pytest_asyncio

from app.models.market import BistIndex, IndexComponent, Symbol

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── fixture ─────────────────────────────────────────────────────────
@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def market_data(db):
    """Her test öncesi 2 sembol, 1 endeks ve 1 index_component oluşturur."""
    s1 = Symbol(ticker="THYAO", name="Türk Hava Yolları", sector="Havacılık", is_active=True)
    s2 = Symbol(ticker="AKBNK", name="Akbank", sector="Bankacılık", is_active=True)
    db.add_all([s1, s2])
    await db.flush()

    idx = BistIndex(code="XU030", name="BIST 30", description="BIST 30 Endeksi", is_active=True)
    db.add(idx)
    await db.flush()

    comp = IndexComponent(index_id=idx.id, symbol_id=s1.id, weight=0.05, added_at=date.today())
    db.add(comp)
    await db.flush()

    return s1, s2, idx


# ── /symbols ────────────────────────────────────────────────────────
async def test_list_symbols(client, db):
    resp = await client.get("/api/v1/market/symbols")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) >= 2
    assert body["meta"]["total"] >= 2


async def test_list_symbols_search(client, db):
    resp = await client.get("/api/v1/market/symbols", params={"search": "THYAO"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(s["ticker"] == "THYAO" for s in data)


async def test_list_symbols_sector_filter(client, db):
    resp = await client.get("/api/v1/market/symbols", params={"sector": "Bankacılık"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert all(s["sector"] == "Bankacılık" for s in data)


async def test_list_symbols_index_filter(client, db):
    resp = await client.get("/api/v1/market/symbols", params={"index_code": "XU030"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    tickers = [s["ticker"] for s in body["data"]]
    assert "THYAO" in tickers


async def test_list_symbols_pagination(client, db):
    resp = await client.get("/api/v1/market/symbols", params={"page": 1, "per_page": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 1
    assert body["meta"]["per_page"] == 1
    assert body["meta"]["total_pages"] >= 2


# ── /symbols/{ticker} ──────────────────────────────────────────────
async def test_get_symbol_detail(client, db):
    resp = await client.get("/api/v1/market/symbols/THYAO")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["ticker"] == "THYAO"
    assert data["name"] == "Türk Hava Yolları"


async def test_get_symbol_not_found(client, db):
    resp = await client.get("/api/v1/market/symbols/NONEXIST")
    assert resp.status_code == 404


# ── /symbols/{ticker}/quote ────────────────────────────────────────
async def test_get_quote(client, db):
    resp = await client.get("/api/v1/market/symbols/THYAO/quote")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["symbol"] == "THYAO"
    assert "price" in data
    assert "change" in data


async def test_get_quote_not_found(client, db):
    resp = await client.get("/api/v1/market/symbols/NONEXIST/quote")
    assert resp.status_code == 404


# ── /symbols/{ticker}/history ──────────────────────────────────────
async def test_get_history(client, db):
    resp = await client.get("/api/v1/market/symbols/THYAO/history")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


async def test_get_history_invalid_interval(client, db):
    resp = await client.get("/api/v1/market/symbols/THYAO/history", params={"interval": "3x"})
    assert resp.status_code == 422  # validation error


# ── /indices ────────────────────────────────────────────────────────
async def test_list_indices(client, db):
    resp = await client.get("/api/v1/market/indices")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    codes = [i["code"] for i in body["data"]]
    assert "XU030" in codes


# ── /sectors ────────────────────────────────────────────────────────
async def test_list_sectors(client, db):
    resp = await client.get("/api/v1/market/sectors")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert "Havacılık" in body["data"]
    assert "Bankacılık" in body["data"]
