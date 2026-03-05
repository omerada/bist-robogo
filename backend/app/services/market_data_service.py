# Source: Doc 02 §2.2 — Market data service
"""Piyasa verisi iş mantığı katmanı."""

import json
from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import redis_manager
from app.models.market import BistIndex, Symbol
from app.repositories.market_repository import (
    IndexRepository,
    OHLCVRepository,
    SymbolRepository,
)
from app.schemas.market import OHLCVResponse, QuoteResponse, SymbolResponse

logger = structlog.get_logger()


class MarketDataService:
    """Piyasa verisi iş mantığı — repository pattern üzerinden."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.symbol_repo = SymbolRepository(db)
        self.index_repo = IndexRepository(db)
        self.ohlcv_repo = OHLCVRepository(db)

    # ── Sembol İşlemleri ──

    async def get_symbols(
        self,
        index_code: str | None = None,
        sector: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SymbolResponse], int]:
        """Sembol listesi + toplam sayı.

        Filtreleme: endeks kodu, sektör, arama.
        """
        if search:
            symbols = await self.symbol_repo.search(search, limit=limit)
            total = len(symbols)
        elif index_code:
            symbols = await self.index_repo.get_index_symbols(index_code)
            total = len(symbols)
            symbols = symbols[skip : skip + limit]
        elif sector:
            symbols = await self.symbol_repo.get_by_sector(sector)
            total = len(symbols)
            symbols = symbols[skip : skip + limit]
        else:
            symbols = await self.symbol_repo.get_active_symbols(skip=skip, limit=limit)
            total = await self.symbol_repo.get_active_count()

        return [SymbolResponse.model_validate(s) for s in symbols], total

    async def get_symbol_detail(self, ticker: str) -> SymbolResponse | None:
        """Tek sembol detayı."""
        symbol = await self.symbol_repo.get_by_ticker(ticker)
        if not symbol:
            return None
        return SymbolResponse.model_validate(symbol)

    # ── Endeks İşlemleri ──

    async def get_indices(self) -> list[dict]:
        """Aktif endeks listesi."""
        indices = await self.index_repo.get_active_indices()
        return [
            {
                "id": str(idx.id),
                "code": idx.code,
                "name": idx.name,
                "description": idx.description,
            }
            for idx in indices
        ]

    # ── Fiyat / Quote ──

    async def _get_quote_from_redis(self, ticker: str) -> dict | None:
        """Redis cache'ten canlı fiyat verisini oku."""
        try:
            raw = await redis_manager.get_cached(f"market:quote:{ticker.upper()}")
            if raw:
                return json.loads(raw)
        except Exception as exc:
            logger.warning("redis_quote_read_failed", ticker=ticker, error=str(exc))
        return None

    async def get_quote(self, ticker: str) -> QuoteResponse | None:
        """Anlık/son fiyat bilgisi.

        Öncelik sırası:
        1. Redis cache (canlı fiyat — CollectAPI'den Celery task ile güncellenir)
        2. TimescaleDB OHLCV tablosu (varsa geçmiş veriden son fiyat)
        3. Minimal sıfır değerli response
        """
        symbol = await self.symbol_repo.get_by_ticker(ticker)
        if not symbol:
            return None

        # 1) Redis cache — canlı veri
        redis_data = await self._get_quote_from_redis(ticker)
        if redis_data and float(redis_data.get("price", 0)) > 0:
            price = float(redis_data["price"])
            change_pct = float(redis_data.get("change_pct", 0))
            bid = float(redis_data.get("bid", price * 0.999))
            ask = float(redis_data.get("ask", price * 1.001))
            volume = int(redis_data.get("volume", 0))
            updated_at_str = redis_data.get("updated_at", "")

            try:
                updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else datetime.now(timezone.utc)
            except (ValueError, TypeError):
                updated_at = datetime.now(timezone.utc)

            # Önceki kapanış — varsa OHLCV'den al
            price_data = await self.ohlcv_repo.get_latest_price(ticker)
            close_prev = price_data["close_prev"] if price_data else price
            change = round(price - float(close_prev), 4) if price_data else 0

            return QuoteResponse(
                symbol=symbol.ticker,
                name=symbol.name,
                price=price,
                change=change,
                change_pct=change_pct,
                open=price_data["open"] if price_data else price,
                high=price_data["high"] if price_data else price,
                low=price_data["low"] if price_data else price,
                close_prev=close_prev,
                volume=volume,
                bid=bid,
                ask=ask,
                updated_at=updated_at,
            )

        # 2) OHLCV tablosundan son veri
        price_data = await self.ohlcv_repo.get_latest_price(ticker)
        if price_data:
            return QuoteResponse(
                symbol=symbol.ticker,
                name=symbol.name,
                price=price_data["price"],
                change=price_data["change"],
                change_pct=price_data["change_pct"],
                open=price_data["open"],
                high=price_data["high"],
                low=price_data["low"],
                close_prev=price_data["close_prev"],
                volume=price_data["volume"],
                bid=price_data["price"] * 0.999,
                ask=price_data["price"] * 1.001,
                updated_at=datetime.fromisoformat(price_data["updated_at"]),
            )

        # 3) Hiç veri yok — minimal response
        return QuoteResponse(
            symbol=symbol.ticker,
            name=symbol.name,
            price=0,
            change=0,
            change_pct=0,
            open=0,
            high=0,
            low=0,
            close_prev=0,
            volume=0,
            bid=0,
            ask=0,
            updated_at=datetime.now(timezone.utc),
        )

    # ── OHLCV ──

    async def get_ohlcv(
        self,
        ticker: str,
        interval: str = "1d",
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 250,
    ) -> list[dict]:
        """OHLCV zaman serisi verisi."""
        # Sembol doğrulama
        symbol = await self.symbol_repo.get_by_ticker(ticker)
        if not symbol:
            return []

        return await self.ohlcv_repo.get_ohlcv(
            symbol=ticker,
            interval=interval,
            start=start,
            end=end,
            limit=limit,
        )

    # ── Sektörler ──

    async def get_sectors(self) -> list[str]:
        """Benzersiz sektör listesi."""
        return await self.symbol_repo.get_sectors()

    # ── EOD Veri Çekme ve Kaydetme ──

    async def fetch_and_store_eod_data(self) -> dict:
        """CollectAPI'den tüm BIST hisse verilerini çekip OHLCV tablosuna kaydeder.

        Returns:
            {"count": int, "errors": int}
        """
        from app.core.collectapi_client import CollectAPIClient

        client = CollectAPIClient()
        try:
            stocks = await client.get_all_stocks()
            if not stocks:
                logger.warning("eod_no_data_from_collectapi")
                return {"count": 0, "errors": 0}

            now = datetime.now(timezone.utc)
            count = 0
            errors = 0

            for stock in stocks:
                try:
                    parsed = CollectAPIClient.parse_stock_to_quote(stock)
                    code = stock.get("code", "").upper()
                    if not code or parsed["price"] <= 0:
                        continue

                    await self.ohlcv_repo.upsert_daily(
                        symbol=code,
                        time=now,
                        open_price=parsed["price"],
                        high=parsed["high"] or parsed["price"],
                        low=parsed["low"] or parsed["price"],
                        close=parsed["price"],
                        volume=parsed["volume"],
                    )
                    count += 1
                except Exception as exc:
                    errors += 1
                    logger.warning("eod_store_failed", symbol=code, error=str(exc))

            await self.db.commit()
            logger.info("eod_data_stored", count=count, errors=errors)
            return {"count": count, "errors": errors}

        finally:
            await client.close()
